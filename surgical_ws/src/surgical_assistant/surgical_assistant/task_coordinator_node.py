#!/usr/bin/env python3
"""task_coordinator_node: orquesta voz + visión → movimientos MoveIt 2 del UFACTORY Lite 6.

Entradas : /surgical_command (SurgicalCommand), /instrument_pose (InstrumentPose), /hand_pose (PoseStamped)
Salidas  : metas a MoveIt 2 (move_group / compute_cartesian_path / execute_trajectory), servicios del
           gripper y /task_state (String) con el estado actual de la secuencia.

Secuencia `give_instrument`:
    abrir gripper → pre-agarre (OMPL) → descenso lineal → cerrar → ascenso lineal
    → esperar mano → punto de entrega (OMPL) → abrir gripper → inicio

SEGURIDAD:
  * `dry_run` está en TRUE por defecto: se calcula todo y se loguea, pero NO se envía movimiento.
  * El comando 'stop' cancela la meta MoveIt activa. Es un paro por software, NO sustituye al paro
    de emergencia físico del Lite 6.
  * La mano no se inserta como obstáculo en la escena de planificación (MVP): se mantiene una
    distancia de seguridad geométrica (`handover_standoff_m`) y baja velocidad.
"""
from __future__ import annotations

import math
import threading
import time
from typing import Dict, Optional, Tuple

import rclpy
from geometry_msgs.msg import Pose, PoseStamped
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from rclpy.time import Time
from std_msgs.msg import String
from tf2_ros import Buffer, TransformException, TransformListener

from surgical_interfaces.msg import InstrumentPose, SurgicalCommand
from surgical_assistant.geometry import (apply_transform, flange_from_tip, grasp_yaw_from_quat,
                                         handover_target, in_box, quat_from_rpy, tool_down_quat)
from surgical_assistant.nlu import INTENT_GIVE, INTENT_HOME, INTENT_RETURN, INTENT_STOP
from surgical_assistant.robot_clients import GripperClient, MoveItClient


def _make_pose(xyz, quat) -> Pose:
    p = Pose()
    p.position.x, p.position.y, p.position.z = (float(c) for c in xyz)
    p.orientation.x, p.orientation.y, p.orientation.z, p.orientation.w = (float(c) for c in quat)
    return p


class TaskCoordinatorNode(Node):
    def __init__(self) -> None:
        super().__init__('task_coordinator_node')

        # --- Parámetros ---------------------------------------------------------------
        self.declare_parameter('dry_run', True)
        self.declare_parameter('base_frame', 'link_base')
        self.declare_parameter('move_group', 'lite6')
        self.declare_parameter('ee_link', 'link_eef')
        self.declare_parameter('joint_names', ['joint1', 'joint2', 'joint3', 'joint4', 'joint5', 'joint6'])
        self.declare_parameter('move_group_action', 'move_action')
        self.declare_parameter('execute_action', 'execute_trajectory')
        self.declare_parameter('cartesian_service', 'compute_cartesian_path')
        self.declare_parameter('gripper_ns', 'auto')              # 'auto' o p. ej. '/xarm'
        self.declare_parameter('gripper_required', True)          # False: simulación sin driver real
        self.declare_parameter('gripper_wait_s', 1.5)
        self.declare_parameter('velocity_scale', 0.2)
        self.declare_parameter('acceleration_scale', 0.2)
        self.declare_parameter('planning_time_s', 5.0)
        # Geometría de agarre
        self.declare_parameter('approach_height_m', 0.10)
        self.declare_parameter('grasp_z_offset_m', -0.005)        # punta de mordazas respecto a la cara superior del instrumento
        self.declare_parameter('tcp_offset_m', 0.0)               # ee_link → centro de mordazas (eje Z herramienta)
        self.declare_parameter('grasp_yaw_offset_deg', 90.0)      # 90 = mordazas perpendiculares al instrumento
        # Entrega
        self.declare_parameter('handover_standoff_m', 0.15)
        self.declare_parameter('handover_height_offset_m', 0.05)
        self.declare_parameter('handover_rpy_deg', [180.0, 0.0, 0.0])   # 180,0,0 = herramienta hacia abajo
        self.declare_parameter('hand_wait_timeout_s', 5.0)
        # Límites y frescura
        self.declare_parameter('workspace_limits', [0.15, 0.45, -0.30, 0.30, 0.02, 0.45])  # xmin,xmax,ymin,ymax,zmin,zmax (ee_link, base)
        self.declare_parameter('max_instrument_age_s', 1.5)
        self.declare_parameter('max_hand_age_s', 1.0)
        self.declare_parameter('home_joints_rad', [0.0, 0.0, 0.0, 0.0, 0.0, 0.0])  # AJUSTAR a tu celda
        self.declare_parameter('return_home_after', True)

        p = self.get_parameter
        self.dry_run = bool(p('dry_run').value)
        self.base_frame = p('base_frame').value
        self.gripper_required = bool(p('gripper_required').value)
        self.gripper_wait = float(p('gripper_wait_s').value)
        self.approach_h = float(p('approach_height_m').value)
        self.grasp_dz = float(p('grasp_z_offset_m').value)
        self.tcp = float(p('tcp_offset_m').value)
        self.yaw_off = math.radians(float(p('grasp_yaw_offset_deg').value))
        self.standoff = float(p('handover_standoff_m').value)
        self.hand_dz = float(p('handover_height_offset_m').value)
        self.handover_q = quat_from_rpy(*(math.radians(a) for a in p('handover_rpy_deg').value))
        self.hand_wait = float(p('hand_wait_timeout_s').value)
        self.box = list(p('workspace_limits').value)
        self.max_inst_age = float(p('max_instrument_age_s').value)
        self.max_hand_age = float(p('max_hand_age_s').value)
        self.home_joints = list(p('home_joints_rad').value)
        self.return_home = bool(p('return_home_after').value)

        # --- Estado -------------------------------------------------------------------
        self._lock = threading.Lock()
        self._instr: Dict[str, Tuple[InstrumentPose, float]] = {}
        self._hand: Optional[Tuple[PoseStamped, float]] = None
        self._busy = False
        self._cancel = threading.Event()
        self._moveit_ready = False

        # --- ROS ----------------------------------------------------------------------
        self.cb = ReentrantCallbackGroup()
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.create_subscription(SurgicalCommand, '/surgical_command', self._on_command, 10,
                                 callback_group=self.cb)
        self.create_subscription(InstrumentPose, '/instrument_pose', self._on_instrument, 10,
                                 callback_group=self.cb)
        self.create_subscription(PoseStamped, '/hand_pose', self._on_hand, 10, callback_group=self.cb)
        self.state_pub = self.create_publisher(String, '/task_state', 10)

        self.moveit = MoveItClient(
            self, self.cb, p('move_group').value, p('ee_link').value, self.base_frame,
            p('joint_names').value, p('move_group_action').value, p('execute_action').value,
            p('cartesian_service').value, float(p('velocity_scale').value),
            float(p('acceleration_scale').value), float(p('planning_time_s').value))
        self.gripper = GripperClient(self, self.cb, p('gripper_ns').value)

        mode = 'DRY-RUN (sin movimiento)' if self.dry_run else 'MOVIMIENTO REAL'
        self.get_logger().info(f'Coordinador listo — modo: {mode}')
        self._state('IDLE')

    # ================================================================= callbacks
    def _on_instrument(self, msg: InstrumentPose) -> None:
        with self._lock:
            self._instr[msg.class_name] = (msg, time.monotonic())

    def _on_hand(self, msg: PoseStamped) -> None:
        with self._lock:
            self._hand = (msg, time.monotonic())

    def _on_command(self, msg: SurgicalCommand) -> None:
        self.get_logger().info(f'Comando: {msg.intent} "{msg.instrument_name}" (conf {msg.confidence:.2f})')
        if msg.intent == INTENT_STOP:
            self._abort()
            return
        with self._lock:
            if self._busy:
                self.get_logger().warn('Ocupado ejecutando otra tarea: comando ignorado.')
                return
            self._busy = True
        self._cancel.clear()
        self.moveit.clear_cancel()
        threading.Thread(target=self._run_task, args=(msg,), daemon=True).start()

    def _abort(self) -> None:
        self.get_logger().warn('STOP: cancelando tarea y metas MoveIt activas.')
        self._cancel.set()
        self.moveit.cancel()
        self._state('ABORTED')

    # ================================================================= tareas
    def _run_task(self, cmd: SurgicalCommand) -> None:
        try:
            if cmd.intent == INTENT_GIVE:
                ok, why = self._task_give(cmd.instrument_name)
            elif cmd.intent == INTENT_HOME:
                ok, why = self._task_home()
            elif cmd.intent == INTENT_RETURN:
                ok, why = False, 'return_instrument aún no implementado en el MVP'
            else:
                ok, why = False, f'intención no soportada: {cmd.intent}'
            if ok:
                self.get_logger().info('Tarea completada.')
                self._state('IDLE')
            else:
                self.get_logger().error(f'Tarea fallida: {why}')
                self._state(f'FAILED: {why}')
        except Exception as exc:  # noqa: BLE001 - nunca dejar _busy colgado
            self.get_logger().error(f'Excepción en la tarea: {exc!r}')
            self._state(f'FAILED: {exc}')
        finally:
            with self._lock:
                self._busy = False

    def _task_home(self) -> Tuple[bool, str]:
        return self._step('HOME', lambda: self.moveit.move_to_joints(self.home_joints))

    def _task_give(self, name: str) -> Tuple[bool, str]:
        if not name:
            return False, 'comando sin instrumento'
        self._state('PLANNING')
        grasp, err = self._plan_grasp(name)
        if grasp is None:
            return False, err
        pre_pose, grasp_pose = grasp
        if self._fresh_hand() is None:
            return False, 'mano no detectada (se exige antes de iniciar)'

        steps = [
            ('OPEN_GRIPPER', self._gripper_open),
            ('PRE_GRASP', lambda: self.moveit.move_to_pose(pre_pose)),
            ('DESCEND', lambda: self.moveit.move_linear(grasp_pose)),
            ('CLOSE_GRIPPER', self._gripper_close),
            ('LIFT', lambda: self.moveit.move_linear(pre_pose)),
            ('WAIT_HAND', self._wait_hand),
        ]
        for label, fn in steps:
            ok, why = self._step(label, fn)
            if not ok:
                return False, f'{label}: {why}'

        # La entrega se calcula con la mano más reciente, justo antes de moverse.
        handover, err = self._plan_handover()
        if handover is None:
            return False, f'HANDOVER: {err}'
        for label, fn in [
            ('HANDOVER', lambda: self.moveit.move_to_pose(handover)),
            ('RELEASE', self._gripper_open),
        ] + ([('RETURN_HOME', lambda: self.moveit.move_to_joints(self.home_joints))]
             if self.return_home else []):
            ok, why = self._step(label, fn)
            if not ok:
                return False, f'{label}: {why}'
        return True, ''

    # --------------------------------------------------------------- ejecución de pasos
    def _step(self, label: str, fn) -> Tuple[bool, str]:
        if self._cancel.is_set():
            return False, 'cancelado por el usuario'
        self._state(label)
        if self.dry_run:
            self.get_logger().info(f'[DRY-RUN] {label}')
            time.sleep(0.2)
            return True, ''
        if not self._moveit_ready:
            self.get_logger().info('Esperando servidores de MoveIt 2...')
            if not self.moveit.wait_ready(10.0):
                return False, 'MoveIt 2 (move_group) no disponible'
            self._moveit_ready = True
        return fn()

    def _gripper_open(self) -> Tuple[bool, str]:
        return self._gripper_action(self.gripper.open, 0.5)

    def _gripper_close(self) -> Tuple[bool, str]:
        return self._gripper_action(self.gripper.close, self.gripper_wait)

    def _gripper_action(self, fn, wait_s: float) -> Tuple[bool, str]:
        ok, why = fn()
        if not ok:
            if self.gripper_required:
                return False, why
            self.get_logger().warn(f'Gripper ignorado (gripper_required=false): {why}')
        time.sleep(wait_s)
        return True, ''

    def _wait_hand(self) -> Tuple[bool, str]:
        t0 = time.monotonic()
        while time.monotonic() - t0 < self.hand_wait:
            if self._cancel.is_set():
                return False, 'cancelado por el usuario'
            if self._fresh_hand() is not None:
                return True, ''
            time.sleep(0.1)
        return False, f'mano no detectada en {self.hand_wait:.0f} s (el robot sigue sosteniendo el instrumento)'

    # ================================================================= geometría
    def _to_base(self, frame_id: str, pos, quat):
        if frame_id == self.base_frame:  # los nodos de visión monoculares ya publican en link_base
            return tuple(float(c) for c in pos), tuple(float(c) for c in quat)
        try:
            tf = self.tf_buffer.lookup_transform(self.base_frame, frame_id, Time())
        except TransformException as exc:
            self.get_logger().error(f'TF {self.base_frame} ← {frame_id} no disponible: {exc}')
            return None
        t, r = tf.transform.translation, tf.transform.rotation
        return apply_transform((t.x, t.y, t.z), (r.x, r.y, r.z, r.w), pos, quat)

    def _fresh_hand(self):
        with self._lock:
            entry = self._hand
        if entry is None or time.monotonic() - entry[1] > self.max_hand_age:
            return None
        return entry[0]

    def _plan_grasp(self, name: str):
        with self._lock:
            entry = self._instr.get(name)
        if entry is None:
            return None, f'instrumento "{name}" no detectado'
        msg, ts = entry
        if time.monotonic() - ts > self.max_inst_age:
            return None, f'detección de "{name}" obsoleta (>{self.max_inst_age:.1f} s)'
        pos = (msg.pose.position.x, msg.pose.position.y, msg.pose.position.z)
        q = (msg.pose.orientation.x, msg.pose.orientation.y, msg.pose.orientation.z, msg.pose.orientation.w)
        base = self._to_base(msg.header.frame_id, pos, q)
        if base is None:
            return None, f'sin TF {self.base_frame} ← {msg.header.frame_id} (¿calibración del Paso 2 publicada?)'
        p_base, q_base = base

        yaw = grasp_yaw_from_quat(q_base, self.yaw_off)
        q_tool = tool_down_quat(yaw)
        tip = (p_base[0], p_base[1], p_base[2] + self.grasp_dz)
        grasp_xyz = flange_from_tip(tip, q_tool, self.tcp)
        pre_xyz = (grasp_xyz[0], grasp_xyz[1], grasp_xyz[2] + self.approach_h)

        for label, xyz in (('pre-agarre', pre_xyz), ('agarre', grasp_xyz)):
            if not in_box(xyz, self.box):
                return None, f'{label} {tuple(round(c, 3) for c in xyz)} fuera de workspace_limits {self.box}'
        self.get_logger().info(
            f'Agarre "{name}" en {self.base_frame}: instrumento={tuple(round(c, 3) for c in p_base)} '
            f'yaw_pinza={math.degrees(yaw):.1f}° → ee_link pre={tuple(round(c, 3) for c in pre_xyz)} '
            f'agarre={tuple(round(c, 3) for c in grasp_xyz)}')
        return (_make_pose(pre_xyz, q_tool), _make_pose(grasp_xyz, q_tool)), ''

    def _plan_handover(self):
        hand = self._fresh_hand()
        if hand is None:
            return None, 'mano no detectada'
        base = self._to_base(hand.header.frame_id,
                             (hand.pose.position.x, hand.pose.position.y, hand.pose.position.z),
                             (0.0, 0.0, 0.0, 1.0))
        if base is None:
            return None, 'sin TF para la mano'
        tip = handover_target(base[0], self.standoff, self.hand_dz)
        xyz = flange_from_tip(tip, self.handover_q, self.tcp)
        if not in_box(xyz, self.box):
            return None, f'punto de entrega {tuple(round(c, 3) for c in xyz)} fuera de workspace_limits'
        self.get_logger().info(f'Entrega: mano={tuple(round(c, 3) for c in base[0])} → '
                               f'ee_link={tuple(round(c, 3) for c in xyz)}')
        return _make_pose(xyz, self.handover_q), ''

    def _state(self, s: str) -> None:
        self.state_pub.publish(String(data=s))


def main(args=None) -> None:
    rclpy.init(args=args)
    node = TaskCoordinatorNode()
    executor = MultiThreadedExecutor(num_threads=4)
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
