"""Clientes de bajo nivel para MoveIt 2 (acciones/servicios nativos) y el gripper del Lite 6.

Se usan directamente las interfaces de move_group (no moveit_py) porque funcionan con la
instalación binaria de MoveIt 2 sin compilar nada extra. Todas las llamadas son BLOQUEANTES y
están pensadas para ejecutarse en un hilo de trabajo mientras un MultiThreadedExecutor sigue
atendiendo callbacks (ver task_coordinator_node).
"""
from __future__ import annotations

import threading
import time
from typing import Optional, Sequence, Tuple

from geometry_msgs.msg import Pose
from moveit_msgs.action import ExecuteTrajectory, MoveGroup
from moveit_msgs.msg import (BoundingVolume, Constraints, JointConstraint, MoveItErrorCodes,
                             MotionPlanRequest, OrientationConstraint, PlanningOptions,
                             PositionConstraint, RobotTrajectory)
from moveit_msgs.srv import GetCartesianPath
from rclpy.action import ActionClient
from rclpy.callback_groups import CallbackGroup
from rclpy.node import Node
from shape_msgs.msg import SolidPrimitive

try:  # xarm_msgs solo existe si xarm_ros2 está compilado en el workspace
    from xarm_msgs.srv import Call
except ImportError:  # pragma: no cover
    Call = None


class MoveItClient:
    def __init__(self, node: Node, cb_group: CallbackGroup, group: str, ee_link: str,
                 base_frame: str, joint_names: Sequence[str],
                 move_action: str = 'move_action', exec_action: str = 'execute_trajectory',
                 cartesian_srv: str = 'compute_cartesian_path',
                 vel_scale: float = 0.2, acc_scale: float = 0.2, planning_time: float = 5.0):
        self.node = node
        self.group = group
        self.ee_link = ee_link
        self.base_frame = base_frame
        self.joint_names = list(joint_names)
        self.vel = vel_scale
        self.acc = acc_scale
        self.planning_time = planning_time

        self._move = ActionClient(node, MoveGroup, move_action, callback_group=cb_group)
        self._exec = ActionClient(node, ExecuteTrajectory, exec_action, callback_group=cb_group)
        self._cart = node.create_client(GetCartesianPath, cartesian_srv, callback_group=cb_group)
        self._goal_handle = None
        self._cancelled = threading.Event()

    # ------------------------------------------------------------------ utilidades
    def wait_ready(self, timeout: float = 10.0) -> bool:
        ok = (self._move.wait_for_server(timeout_sec=timeout)
              and self._exec.wait_for_server(timeout_sec=timeout)
              and self._cart.wait_for_service(timeout_sec=timeout))
        return bool(ok)

    def clear_cancel(self) -> None:
        self._cancelled.clear()

    def cancel(self) -> None:
        """Cancela la meta activa (planificación o ejecución). No es un paro de emergencia certificado."""
        self._cancelled.set()
        gh = self._goal_handle
        if gh is not None:
            gh.cancel_goal_async()

    def _wait(self, future, timeout: float) -> bool:
        t0 = time.monotonic()
        while not future.done():
            if self._cancelled.is_set() or time.monotonic() - t0 > timeout:
                return False
            time.sleep(0.02)
        return True

    def _run_action(self, client: ActionClient, goal, result_timeout: float = 60.0):
        send = client.send_goal_async(goal)
        if not self._wait(send, 5.0):
            return None, 'cancelado o sin respuesta del servidor de acciones'
        gh = send.result()
        if gh is None or not gh.accepted:
            return None, 'meta rechazada por el servidor'
        self._goal_handle = gh
        res = gh.get_result_async()
        done = self._wait(res, result_timeout)
        self._goal_handle = None
        if not done:
            gh.cancel_goal_async()
            return None, 'cancelado o tiempo de espera agotado'
        return res.result().result, ''

    @staticmethod
    def _code_ok(code) -> bool:
        return code.val == MoveItErrorCodes.SUCCESS

    def _plan_options(self) -> PlanningOptions:
        opt = PlanningOptions()
        opt.plan_only = False
        opt.planning_scene_diff.is_diff = True
        opt.planning_scene_diff.robot_state.is_diff = True
        return opt

    def _base_request(self) -> MotionPlanRequest:
        req = MotionPlanRequest()
        req.group_name = self.group
        req.num_planning_attempts = 5
        req.allowed_planning_time = self.planning_time
        req.max_velocity_scaling_factor = self.vel
        req.max_acceleration_scaling_factor = self.acc
        req.start_state.is_diff = True  # arrancar desde el estado actual
        return req

    # ---------------------------------------------------------------------- movimientos
    def move_to_pose(self, pose: Pose, pos_tol: float = 0.002, ori_tol: float = 0.02) -> Tuple[bool, str]:
        """Planifica (OMPL) y ejecuta hacia una pose del `ee_link` expresada en `base_frame`."""
        req = self._base_request()

        pc = PositionConstraint()
        pc.header.frame_id = self.base_frame
        pc.link_name = self.ee_link
        sp = SolidPrimitive()
        sp.type = SolidPrimitive.SPHERE
        sp.dimensions = [pos_tol]
        bv = BoundingVolume()
        bv.primitives.append(sp)
        bv.primitive_poses.append(pose)
        pc.constraint_region = bv
        pc.weight = 1.0

        oc = OrientationConstraint()
        oc.header.frame_id = self.base_frame
        oc.link_name = self.ee_link
        oc.orientation = pose.orientation
        oc.absolute_x_axis_tolerance = ori_tol
        oc.absolute_y_axis_tolerance = ori_tol
        oc.absolute_z_axis_tolerance = ori_tol
        oc.weight = 1.0

        c = Constraints()
        c.position_constraints.append(pc)
        c.orientation_constraints.append(oc)
        req.goal_constraints.append(c)
        return self._send_move(req)

    def move_to_joints(self, joints: Sequence[float], tol: float = 0.01) -> Tuple[bool, str]:
        req = self._base_request()
        c = Constraints()
        for name, val in zip(self.joint_names, joints):
            jc = JointConstraint()
            jc.joint_name = name
            jc.position = float(val)
            jc.tolerance_above = tol
            jc.tolerance_below = tol
            jc.weight = 1.0
            c.joint_constraints.append(jc)
        req.goal_constraints.append(c)
        return self._send_move(req)

    def _send_move(self, req: MotionPlanRequest) -> Tuple[bool, str]:
        goal = MoveGroup.Goal()
        goal.request = req
        goal.planning_options = self._plan_options()
        result, err = self._run_action(self._move, goal)
        if result is None:
            return False, err
        if not self._code_ok(result.error_code):
            return False, f'MoveIt error_code={result.error_code.val}'
        return True, ''

    def move_linear(self, pose: Pose, max_step: float = 0.005,
                    min_fraction: float = 0.98) -> Tuple[bool, str]:
        """Trayectoria cartesiana en línea recta (descenso/ascenso de agarre) y ejecución."""
        if not self._cart.wait_for_service(timeout_sec=2.0):
            return False, 'servicio compute_cartesian_path no disponible'
        req = GetCartesianPath.Request()
        req.header.frame_id = self.base_frame
        req.start_state.is_diff = True
        req.group_name = self.group
        req.link_name = self.ee_link
        req.waypoints = [pose]
        req.max_step = max_step
        req.jump_threshold = 0.0
        req.avoid_collisions = True
        native_scaling = hasattr(req, 'max_velocity_scaling_factor')
        if native_scaling:  # disponible en versiones recientes de MoveIt 2
            req.max_velocity_scaling_factor = self.vel
            req.max_acceleration_scaling_factor = self.acc

        fut = self._cart.call_async(req)
        if not self._wait(fut, 10.0):
            return False, 'cancelado o sin respuesta de compute_cartesian_path'
        res = fut.result()
        if res.fraction < min_fraction:
            return False, f'trayectoria cartesiana incompleta ({res.fraction:.0%})'
        if not native_scaling and self.vel > 0.0:
            self._slow_down(res.solution, 1.0 / self.vel)

        goal = ExecuteTrajectory.Goal()
        goal.trajectory = res.solution
        result, err = self._run_action(self._exec, goal)
        if result is None:
            return False, err
        if not self._code_ok(result.error_code):
            return False, f'ExecuteTrajectory error_code={result.error_code.val}'
        return True, ''

    @staticmethod
    def _slow_down(traj: RobotTrajectory, factor: float) -> None:
        """Multiplica por `factor` la duración de la trayectoria (y reescala vel./acel.)."""
        for pt in traj.joint_trajectory.points:
            t = (pt.time_from_start.sec + pt.time_from_start.nanosec * 1e-9) * factor
            pt.time_from_start.sec = int(t)
            pt.time_from_start.nanosec = int((t - int(t)) * 1e9)
            pt.velocities = [v / factor for v in pt.velocities]
            pt.accelerations = [a / (factor * factor) for a in pt.accelerations]


class GripperClient:
    """Gripper del Lite 6 vía servicios xarm_msgs/srv/Call (open/close/stop_lite6_gripper).

    `ns='auto'` (por defecto) busca en el grafo ROS el servicio que termina en
    `/open_lite6_gripper` y usa su prefijo, de modo que funciona sea cual sea el namespace del
    driver de xarm_ros2 (p. ej. /xarm o /ufactory).
    """

    def __init__(self, node: Node, cb_group: CallbackGroup, ns: str = 'auto'):
        self.node = node
        self.cb_group = cb_group
        self.ns = ns
        self._clients = {}

    def _resolve_ns(self) -> Optional[str]:
        if self.ns != 'auto':
            return self.ns.rstrip('/')
        for name, _types in self.node.get_service_names_and_types():
            if name.endswith('/open_lite6_gripper'):
                return name[: -len('/open_lite6_gripper')]
        return None

    def _client(self, short: str):
        if Call is None:
            return None
        if short not in self._clients:
            ns = self._resolve_ns()
            if ns is None:
                return None
            self._clients[short] = self.node.create_client(
                Call, f'{ns}/{short}_lite6_gripper', callback_group=self.cb_group)
        return self._clients[short]

    def _call(self, short: str, timeout: float = 3.0) -> Tuple[bool, str]:
        cli = self._client(short)
        if cli is None:
            return False, 'servicio del gripper no encontrado (¿driver xarm_ros2 activo?)'
        if not cli.wait_for_service(timeout_sec=1.0):
            return False, f'servicio {cli.srv_name} no disponible'
        fut = cli.call_async(Call.Request())
        t0 = time.monotonic()
        while not fut.done():
            if time.monotonic() - t0 > timeout:
                return False, 'tiempo de espera agotado'
            time.sleep(0.02)
        ret = fut.result().ret
        return (ret == 0), ('' if ret == 0 else f'el driver devolvió ret={ret}')

    def open(self) -> Tuple[bool, str]:
        return self._call('open')

    def close(self) -> Tuple[bool, str]:
        return self._call('close')

    def stop(self) -> Tuple[bool, str]:
        return self._call('stop')
