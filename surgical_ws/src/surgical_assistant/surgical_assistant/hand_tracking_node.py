#!/usr/bin/env python3
"""hand_tracking_node: RGB-D → MediaPipe Hands → Landmark 9 (MCP del dedo medio) en 3D → /hand_pose.

La profundidad métrica sale de la imagen de profundidad alineada (la coordenada z de MediaPipe es
relativa y no se usa). La pose se publica en el marco óptico de la cámara con orientación identidad.
"""
from __future__ import annotations

import math
import os

import cv2
import rclpy
from cv_bridge import CvBridge
from geometry_msgs.msg import PoseStamped
from rclpy.node import Node
from sensor_msgs.msg import Image

from surgical_assistant.geometry import ema
from surgical_assistant.monocular_utils import ColorStream, PlaneProjector

LANDMARK_MIDDLE_MCP = 9


class _LegacyBackend:
    """mediapipe.solutions.hands (API clásica, modelos incluidos en el paquete)."""

    def __init__(self, max_hands, complexity, det_conf, track_conf):
        import mediapipe as mp

        self._mp = mp
        self._hands = mp.solutions.hands.Hands(
            static_image_mode=False, max_num_hands=max_hands, model_complexity=complexity,
            min_detection_confidence=det_conf, min_tracking_confidence=track_conf)

    def process(self, rgb):
        rgb.flags.writeable = False
        res = self._hands.process(rgb)
        out = []
        if res.multi_hand_landmarks:
            for lm, hd in zip(res.multi_hand_landmarks, res.multi_handedness):
                p = lm.landmark[LANDMARK_MIDDLE_MCP]
                out.append((p.x, p.y, float(hd.classification[0].score)))
        return out


class _TasksBackend:
    """mediapipe.tasks HandLandmarker (requiere el archivo hand_landmarker.task)."""

    def __init__(self, model_path, max_hands, det_conf, track_conf):
        import mediapipe as mp
        from mediapipe.tasks import python as mp_python
        from mediapipe.tasks.python import vision

        self._mp = mp
        opts = vision.HandLandmarkerOptions(
            base_options=mp_python.BaseOptions(model_asset_path=model_path),
            running_mode=vision.RunningMode.IMAGE, num_hands=max_hands,
            min_hand_detection_confidence=det_conf, min_tracking_confidence=track_conf)
        self._det = vision.HandLandmarker.create_from_options(opts)

    def process(self, rgb):
        img = self._mp.Image(image_format=self._mp.ImageFormat.SRGB, data=rgb)
        res = self._det.detect(img)
        out = []
        for lms, hd in zip(res.hand_landmarks, res.handedness):
            p = lms[LANDMARK_MIDDLE_MCP]
            out.append((p.x, p.y, float(hd[0].score)))
        return out


class HandTrackingNode(Node):
    def __init__(self) -> None:
        super().__init__('hand_tracking_node')

        self.declare_parameter('color_topic', '/image_raw')
        self.declare_parameter('camera_info_topic', '/camera_info')
        self.declare_parameter('base_frame', 'link_base')
        self.declare_parameter('hand_plane_z_m', 0.25)           # altura ASUMIDA del Landmark 9 en link_base
        self.declare_parameter('backend', 'auto')              # legacy | tasks
        self.declare_parameter('tasks_model_path', '')           # hand_landmarker.task (solo backend=tasks)
        self.declare_parameter('max_hands', 2)
        self.declare_parameter('model_complexity', 0)            # 0 = más rápido (CPU)
        self.declare_parameter('min_detection_confidence', 0.6)
        self.declare_parameter('min_tracking_confidence', 0.5)
        self.declare_parameter('select_hand', 'closest')         # closest (a la base del robot) | best (mayor score)
        self.declare_parameter('max_rate_hz', 10.0)
        self.declare_parameter('ema_alpha', 0.5)                 # 1.0 = sin suavizado
        self.declare_parameter('publish_debug_image', False)
        self.declare_parameter('pose_topic', '/hand_pose')

        p = self.get_parameter
        max_hands = int(p('max_hands').value)
        det, trk = float(p('min_detection_confidence').value), float(p('min_tracking_confidence').value)
        import mediapipe as mp
        backend = p('backend').value
        if backend == 'auto':  # mediapipe recientes ya no incluyen mp.solutions
            backend = 'legacy' if hasattr(mp, 'solutions') else 'tasks'
            self.get_logger().info(f"MediaPipe {mp.__version__}: backend '{backend}'")
        if backend == 'tasks':
            model = os.path.expanduser(p('tasks_model_path').value)
            if not os.path.isfile(model):
                raise RuntimeError("backend 'tasks' requiere hand_landmarker.task: descárgalo y pasa "
                                f"tasks_model_path (recibido: '{model}')")
            self.backend = _TasksBackend(model, max_hands, det, trk)
        else:
            self.backend = _LegacyBackend(max_hands, int(p('model_complexity').value), det, trk)
            
        self.select = p('select_hand').value
        self.base_frame = p('base_frame').value
        self.hand_z = float(p('hand_plane_z_m').value)
        self.alpha = float(p('ema_alpha').value)
        self._smoothed = None
        self._last_stamp = None

        self.pub = self.create_publisher(PoseStamped, p('pose_topic').value, 10)
        self.dbg_pub = (self.create_publisher(Image, '~/debug_image', 1)
                        if p('publish_debug_image').value else None)
        self._bridge = CvBridge()
        self.projector = PlaneProjector(self, self.base_frame)
        self.stream = ColorStream(self, p('color_topic').value, p('camera_info_topic').value,
                                  self._on_frame, max_rate_hz=float(p('max_rate_hz').value))

    def _on_frame(self, color, header, cam) -> None:
        h, w = color.shape[:2]
        rgb = cv2.cvtColor(color, cv2.COLOR_BGR2RGB)
        hands = self.backend.process(rgb)  # [(x_norm, y_norm, score), ...]
        project = self.projector.bind(cam, header.frame_id) if hands else None

        candidates = []  # (dist_a_la_base, score, u, v, punto_en_base)
        if project is not None:
            for xn, yn, score in hands:
                u, v = xn * w, yn * h
                pt = project(u, v, self.hand_z)
                if pt is not None:
                    candidates.append((math.hypot(pt[0], pt[1]), score, u, v, pt))

        if not candidates:
            self._smoothed = None  # al perder la mano no arrastramos una posición vieja
            return
        _, _, u, v, pt = (min(candidates, key=lambda c: c[0]) if self.select == 'closest'
                          else max(candidates, key=lambda c: c[1]))

        self._smoothed = ema(self._smoothed, (float(pt[0]), float(pt[1]), self.hand_z), self.alpha)

        msg = PoseStamped()
        msg.header.stamp = header.stamp
        msg.header.frame_id = self.base_frame              # ← la pose sale en link_base
        msg.pose.position.x, msg.pose.position.y, msg.pose.position.z = self._smoothed
        msg.pose.orientation.w = 1.0
        self.pub.publish(msg)

        if self.dbg_pub is not None:
            dbg = color.copy()
            cv2.circle(dbg, (int(u), int(v)), 8, (0, 0, 255), -1)
            cv2.putText(dbg, f'LM9 x={pt[0]:.2f} y={pt[1]:.2f} (z asumida)', (int(u) + 10, int(v)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            out = self._bridge.cv2_to_imgmsg(dbg, encoding='bgr8')
            out.header = header
            self.dbg_pub.publish(out)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = HandTrackingNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
