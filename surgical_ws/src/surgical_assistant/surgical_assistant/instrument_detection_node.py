#!/usr/bin/env python3
"""instrument_detection_node: RGB-D → YOLO-OBB (ONNX/CPU) → punto de agarre 3D → /instrument_pose.

El punto de agarre se calcula así:
    1. Eje largo de la OBB (dirección u, con ambigüedad de 180° resuelta por convención).
    2. Pixel de agarre = centro + u · (α · fx / Z)       (α fijo en metros, por clase, en instruments.yaml)
    3. Profundidad mediana en ese pixel → deproyección con los intrínsecos de la cámara.
Se publica UN mensaje por clase (la detección con mayor confianza) en el marco óptico de la cámara;
el coordinador lo lleva al marco base con TF2 (Paso 2: calibración mano-ojo).
"""
from __future__ import annotations

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

from surgical_interfaces.msg import InstrumentPose
from surgical_assistant.config_loader import load_instruments_config
from surgical_assistant.geometry import grasp_on_plane, obb_long_axis, quat_from_yaw
from surgical_assistant.monocular_utils import ColorStream, PlaneProjector
from surgical_assistant.yolo_obb_onnx import YoloObbOnnx, draw_detection


class InstrumentDetectionNode(Node):
    def __init__(self) -> None:
        super().__init__('instrument_detection_node')

        self.declare_parameter('color_topic', '/image_raw')
        self.declare_parameter('camera_info_topic', '/camera_info')
        self.declare_parameter('base_frame', 'link_base')
        self.declare_parameter('instrument_plane_z_m', 0.01)   # altura (en link_base) de la cara superior del instrumento
        self.declare_parameter('model_path', '')
        self.declare_parameter('imgsz', 640)
        self.declare_parameter('conf_threshold', 0.5)
        self.declare_parameter('iou_threshold', 0.45)
        self.declare_parameter('class_names', [''])             # [''] = leer de la metadata del ONNX
        self.declare_parameter('onnx_providers', ['CPUExecutionProvider'])
        self.declare_parameter('intra_threads', 4)
        self.declare_parameter('max_rate_hz', 5.0)
        self.declare_parameter('instruments_config', '')
        self.declare_parameter('publish_debug_image', False)
        self.declare_parameter('pose_topic', '/instrument_pose')

        p = self.get_parameter
        model_path = p('model_path').value
        if not model_path:
            raise RuntimeError("Parámetro 'model_path' (modelo .onnx YOLO-OBB) es obligatorio.")
        names = [n for n in p('class_names').value if n] or None

        self.detector = YoloObbOnnx(model_path, int(p('imgsz').value),
                                    float(p('conf_threshold').value), float(p('iou_threshold').value),
                                    names, list(p('onnx_providers').value), int(p('intra_threads').value))
        self.get_logger().info(
            f'Modelo cargado ({self.detector.in_w}x{self.detector.in_h}); clases: {self.detector.names}')

        cfg = load_instruments_config(p('instruments_config').value)
        self.alpha = {k: float(v.get('alpha_m', cfg['default_alpha_m']))
                      for k, v in cfg['instruments'].items()}
        self.default_alpha = float(cfg['default_alpha_m'])
        missing = [n for n in self.detector.names.values() if n not in self.alpha]
        if missing:
            self.get_logger().warn(f'Clases del modelo sin entrada en instruments.yaml: {missing} '
                                   f'(se usa alpha={self.default_alpha} m).')

        self.base_frame = p('base_frame').value
        self.plane_z = float(p('instrument_plane_z_m').value)
        self.pub_debug_enabled = bool(p('publish_debug_image').value)

        self.pub = self.create_publisher(InstrumentPose, p('pose_topic').value, 10)
        self.dbg_pub = self.create_publisher(Image, '~/debug_image', 1) if self.pub_debug_enabled else None
        self._bridge = CvBridge()

        self.projector = PlaneProjector(self, self.base_frame)
        self.stream = ColorStream(self, p('color_topic').value, p('camera_info_topic').value,
                                  self._on_frame, max_rate_hz=float(p('max_rate_hz').value))

    def _on_frame(self, color, header, cam) -> None:
        project = self.projector.bind(cam, header.frame_id)   # None si falta la TF base ← cámara
        if project is None:
            return
        dets = self.detector.detect(color)
        best_per_class = {}
        for d in dets:  # `dets` viene ordenada por score descendente
            best_per_class.setdefault(d.class_name, d)

        debug = color.copy() if self.dbg_pub is not None else None
        for name, d in best_per_class.items():
            long_len_px, axis = obb_long_axis(d.w, d.h, d.angle)
            alpha = self.alpha.get(name, self.default_alpha)
            res = grasp_on_plane(project, d.cx, d.cy, long_len_px, axis, alpha, self.plane_z)
            if res is None:
                self.get_logger().warn(f'{name}: el rayo no corta el plano z={self.plane_z} m '
                                       '(revisa la TF del Paso 2 y instrument_plane_z_m).',
                                       throttle_duration_sec=2.0)
                continue
            gx, gy, yaw, length = res
            q = quat_from_yaw(yaw)

            msg = InstrumentPose()
            msg.header.stamp = header.stamp
            msg.header.frame_id = self.base_frame          # ← ahora la pose ya sale en link_base
            msg.class_name = name
            msg.pose.position.x, msg.pose.position.y, msg.pose.position.z = gx, gy, self.plane_z
            msg.pose.orientation.x, msg.pose.orientation.y = q[0], q[1]
            msg.pose.orientation.z, msg.pose.orientation.w = q[2], q[3]
            msg.confidence = float(d.score)
            msg.length_m = float(length)
            msg.grasp_offset_m = float(alpha)
            self.pub.publish(msg)

            if debug is not None:
                draw_detection(debug, d)

        if debug is not None:
            out = self._bridge.cv2_to_imgmsg(debug, encoding='bgr8')
            out.header = header
            self.dbg_pub.publish(out)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = InstrumentDetectionNode()
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
