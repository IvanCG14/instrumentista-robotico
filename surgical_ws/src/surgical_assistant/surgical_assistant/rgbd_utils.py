"""Sincronización RGB-D y utilidades de profundidad compartidas por los nodos de visión."""
from __future__ import annotations

from typing import Callable, Optional

import numpy as np
import message_filters
from cv_bridge import CvBridge
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import CameraInfo, Image


def depth_to_meters(depth: np.ndarray, encoding: str) -> np.ndarray:
    """Convierte la imagen de profundidad a float32 en metros según su encoding ROS."""
    if encoding in ('16UC1', 'mono16'):
        return depth.astype(np.float32) * 0.001
    if encoding == '32FC1':
        return depth.astype(np.float32)
    raise ValueError(f'Encoding de profundidad no soportado: {encoding}')


def median_depth(depth_m: np.ndarray, u: float, v: float, win: int = 7,
                 min_d: float = 0.1, max_d: float = 3.0) -> Optional[float]:
    """Mediana de profundidades válidas en una ventana win×win centrada en (u, v) [px]."""
    h, w = depth_m.shape[:2]
    ui, vi = int(round(u)), int(round(v))
    if ui < 0 or vi < 0 or ui >= w or vi >= h:
        return None
    r = max(1, win // 2)
    patch = depth_m[max(0, vi - r):vi + r + 1, max(0, ui - r):ui + r + 1]
    valid = patch[np.isfinite(patch) & (patch > min_d) & (patch < max_d)]
    if valid.size == 0:
        return None
    return float(np.median(valid))


class RGBDSynchronizer:
    """Suscribe color + profundidad alineada (sincronización aproximada) y CameraInfo.

    Llama a `callback(color_bgr, depth_m, header, K)` con:
      color_bgr : np.ndarray HxWx3 uint8
      depth_m   : np.ndarray HxW float32 (metros), alineada al color
      header    : std_msgs/Header de la imagen de color (frame_id = marco óptico)
      K         : (fx, fy, cx, cy) intrínsecos de la imagen de color
    `max_rate_hz` limita el procesamiento (descarta fotogramas antes de convertirlos).
    """

    def __init__(self, node: Node, color_topic: str, depth_topic: str, info_topic: str,
                 callback: Callable, max_rate_hz: float = 0.0,
                 queue_size: int = 5, slop: float = 0.05):
        self._node = node
        self._cb = callback
        self._bridge = CvBridge()
        self._K = None
        self._min_period = 1.0 / max_rate_hz if max_rate_hz > 0 else 0.0
        self._last = 0.0

        node.create_subscription(CameraInfo, info_topic, self._on_info, 1)
        color_sub = message_filters.Subscriber(node, Image, color_topic,
                                               qos_profile=qos_profile_sensor_data)
        depth_sub = message_filters.Subscriber(node, Image, depth_topic,
                                               qos_profile=qos_profile_sensor_data)
        self._sync = message_filters.ApproximateTimeSynchronizer(
            [color_sub, depth_sub], queue_size=queue_size, slop=slop)
        self._sync.registerCallback(self._on_images)

    def _on_info(self, msg: CameraInfo) -> None:
        self._K = (msg.k[0], msg.k[4], msg.k[2], msg.k[5])

    def _on_images(self, color_msg: Image, depth_msg: Image) -> None:
        if self._K is None:
            self._node.get_logger().warn('Esperando CameraInfo...', throttle_duration_sec=5.0)
            return
        now = self._node.get_clock().now().nanoseconds * 1e-9
        if now - self._last < self._min_period:
            return
        self._last = now
        try:
            color = self._bridge.imgmsg_to_cv2(color_msg, desired_encoding='bgr8')
            depth = self._bridge.imgmsg_to_cv2(depth_msg, desired_encoding='passthrough')
            depth_m = depth_to_meters(depth, depth_msg.encoding)
        except Exception as exc:  # noqa: BLE001 - queremos loguear cualquier fallo de conversión
            self._node.get_logger().error(f'Error convirtiendo imágenes: {exc}')
            return
        # Si la profundidad no tiene la misma resolución que el color, se reescala el mapa de
        # coordenadas en los nodos (ver scale_uv). Aquí se entrega tal cual.
        self._cb(color, depth_m, color_msg.header, self._K)


def scale_uv(u: float, v: float, color_shape, depth_shape):
    """Convierte coordenadas de la imagen de color a la de profundidad si difieren en tamaño."""
    sh = depth_shape[0] / color_shape[0]
    sw = depth_shape[1] / color_shape[1]
    return u * sw, v * sh
