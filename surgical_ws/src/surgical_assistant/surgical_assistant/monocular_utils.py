"""Cámara monocular (sin profundidad): suscripción RGB + CameraInfo y proyección píxel → plano.

Sustituye a rgbd_utils.RGBDSynchronizer en los nodos de visión. Con una sola cámara fija
(eye-to-hand) la posición 3D se obtiene intersectando el rayo del píxel con un plano horizontal
de altura conocida expresado en el marco base del robot (p. ej. la mesa de instrumental).
"""
from __future__ import annotations

from typing import Callable, Optional

import numpy as np
from cv_bridge import CvBridge
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from rclpy.time import Time
from sensor_msgs.msg import CameraInfo, Image
from tf2_ros import Buffer, TransformException, TransformListener

from surgical_assistant.geometry import pixel_ray, quat_to_matrix, ray_plane_z


class CameraModel:
    """Intrínsecos y distorsión tomados de un sensor_msgs/CameraInfo."""

    def __init__(self, msg: CameraInfo):
        self.K = np.array(msg.k, dtype=np.float64).reshape(3, 3)
        self.D = np.array(msg.d, dtype=np.float64).reshape(-1)
        self.width, self.height = int(msg.width), int(msg.height)

    @property
    def valid(self) -> bool:
        return self.K[0, 0] > 1.0 and self.K[1, 1] > 1.0  # un driver sin calibrar publica ceros


class ColorStream:
    """Suscribe imagen de color + CameraInfo. Llama a callback(color_bgr, header, cam: CameraModel).

    Se usa QoS de sensor (best-effort) en AMBOS tópicos: es compatible con publicadores reliable
    y best-effort, así que funciona con cualquier driver UVC.
    """

    def __init__(self, node: Node, color_topic: str, info_topic: str, callback: Callable,
                 max_rate_hz: float = 0.0):
        self._node = node
        self._cb = callback
        self._bridge = CvBridge()
        self._cam: Optional[CameraModel] = None
        self._min_period = 1.0 / max_rate_hz if max_rate_hz > 0 else 0.0
        self._last = 0.0
        node.create_subscription(CameraInfo, info_topic, self._on_info, qos_profile_sensor_data)
        node.create_subscription(Image, color_topic, self._on_image, qos_profile_sensor_data)

    def _on_info(self, msg: CameraInfo) -> None:
        cam = CameraModel(msg)
        if not cam.valid:
            self._node.get_logger().warn(
                'CameraInfo sin intrínsecos: ¿cámara sin calibrar? (ver camera_info_url del driver)',
                throttle_duration_sec=5.0)
            return
        self._cam = cam

    def _on_image(self, msg: Image) -> None:
        if self._cam is None:
            self._node.get_logger().warn('Esperando CameraInfo calibrada...', throttle_duration_sec=5.0)
            return
        now = self._node.get_clock().now().nanoseconds * 1e-9
        if now - self._last < self._min_period:
            return
        self._last = now
        try:
            color = self._bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as exc:  # noqa: BLE001
            self._node.get_logger().error(f'Error convirtiendo imagen: {exc}')
            return
        h, w = color.shape[:2]
        if self._cam.width and (self._cam.width, self._cam.height) != (w, h):
            self._node.get_logger().error(
                f'La imagen es {w}x{h} pero la calibración es {self._cam.width}x{self._cam.height}: '
                'recalibra a la resolución de trabajo.', throttle_duration_sec=5.0)
            return
        self._cb(color, msg.header, self._cam)


class PlaneProjector:
    """Convierte píxeles en puntos del marco base apoyados en un plano z = cte (usa TF2)."""

    def __init__(self, node: Node, base_frame: str = 'link_base'):
        self.node = node
        self.base_frame = base_frame
        self._buf = Buffer()
        self._listener = TransformListener(self._buf, node)

    def bind(self, cam: CameraModel, cam_frame: str):
        """Hace UNA consulta TF y devuelve project(u, v, plane_z) → np.ndarray(3) | None.

        Devuelve None si aún no existe la transformación base ← cámara (publicada por el Paso 2).
        """
        try:
            tf = self._buf.lookup_transform(self.base_frame, cam_frame, Time())
        except TransformException as exc:
            self.node.get_logger().warn(
                f'TF {self.base_frame} ← {cam_frame} no disponible: {exc}', throttle_duration_sec=5.0)
            return None
        t, r = tf.transform.translation, tf.transform.rotation
        rot = quat_to_matrix((r.x, r.y, r.z, r.w))
        origin = (t.x, t.y, t.z)

        def project(u: float, v: float, plane_z: float):
            ray_cam = np.array(pixel_ray(u, v, cam.K, cam.D))
            p = ray_plane_z(origin, rot @ ray_cam, plane_z)
            return None if p is None else np.array(p)

        return project
