"""Utilidades geométricas puras (sin dependencias de ROS) para el asistente quirúrgico.

Convenciones:
  * Cuaterniones en orden (x, y, z, w), igual que geometry_msgs.
  * Marco óptico de cámara: x derecha, y abajo, z hacia adelante.
  * Marco base del robot (link_base): z hacia arriba.
"""
from __future__ import annotations

import math
from typing import Iterable, Optional, Sequence, Tuple

import numpy as np

Quat = Tuple[float, float, float, float]
Vec3 = Tuple[float, float, float]


# ----------------------------------------------------------------------------
# Cuaterniones
# ----------------------------------------------------------------------------
def quat_multiply(q1: Sequence[float], q2: Sequence[float]) -> Quat:
    """Producto de Hamilton q1 ⊗ q2 (aplica q2 y luego q1)."""
    x1, y1, z1, w1 = q1
    x2, y2, z2, w2 = q2
    return (
        w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
        w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
        w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2,
        w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
    )


def quat_normalize(q: Sequence[float]) -> Quat:
    n = math.sqrt(sum(c * c for c in q))
    if n < 1e-12:
        return (0.0, 0.0, 0.0, 1.0)
    return (q[0] / n, q[1] / n, q[2] / n, q[3] / n)


def quat_from_yaw(yaw: float) -> Quat:
    """Rotación pura alrededor de +Z."""
    return (0.0, 0.0, math.sin(yaw / 2.0), math.cos(yaw / 2.0))


def quat_from_rpy(roll: float, pitch: float, yaw: float) -> Quat:
    """RPY extrínseco (R = Rz(yaw) · Ry(pitch) · Rx(roll)), igual que tf/URDF."""
    cr, sr = math.cos(roll / 2.0), math.sin(roll / 2.0)
    cp, sp = math.cos(pitch / 2.0), math.sin(pitch / 2.0)
    cy, sy = math.cos(yaw / 2.0), math.sin(yaw / 2.0)
    return (
        sr * cp * cy - cr * sp * sy,
        cr * sp * cy + sr * cp * sy,
        cr * cp * sy - sr * sp * cy,
        cr * cp * cy + sr * sp * sy,
    )


def quat_to_matrix(q: Sequence[float]) -> np.ndarray:
    x, y, z, w = quat_normalize(q)
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
    ])


def tool_down_quat(yaw: float) -> Quat:
    """Orientación con el eje Z de la herramienta apuntando hacia -Z base (agarre vertical)
    y el eje X de la herramienta a `yaw` rad respecto al eje X de la base.

    Equivale a RPY = (π, 0, yaw).
    """
    return quat_from_rpy(math.pi, 0.0, yaw)


# ----------------------------------------------------------------------------
# Transformaciones rígidas
# ----------------------------------------------------------------------------
def apply_transform(
    t_xyz: Sequence[float],
    t_quat: Sequence[float],
    p_xyz: Sequence[float],
    p_quat: Sequence[float] = (0.0, 0.0, 0.0, 1.0),
) -> Tuple[Vec3, Quat]:
    """Expresa una pose (p_xyz, p_quat) —dada en el marco hijo— en el marco padre.

    (t_xyz, t_quat) es la transformación padre←hijo (lo que devuelve
    tf2 lookup_transform(target=padre, source=hijo)).
    """
    r = quat_to_matrix(t_quat)
    p = r @ np.asarray(p_xyz, dtype=float) + np.asarray(t_xyz, dtype=float)
    q = quat_normalize(quat_multiply(t_quat, p_quat))
    return (float(p[0]), float(p[1]), float(p[2])), q


# ----------------------------------------------------------------------------
# Cámara
# ----------------------------------------------------------------------------
def deproject(u: float, v: float, z: float, fx: float, fy: float, cx: float, cy: float) -> Vec3:
    """Pixel (u, v) con profundidad z (m) → punto 3D en el marco óptico."""
    return ((u - cx) * z / fx, (v - cy) * z / fy, z)


def obb_long_axis(w: float, h: float, angle: float) -> Tuple[float, float]:
    """Devuelve (longitud_eje_largo_px, ángulo_eje_largo_rad) de una OBB.

    El ángulo sigue la convención de imagen (x→derecha, y→abajo) y se normaliza a
    (-π/2, π/2] para que la dirección sea única (la OBB no distingue 0° de 180°).
    """
    if w >= h:
        long_len, ang = w, angle
    else:
        long_len, ang = h, angle + math.pi / 2.0
    ang = math.atan2(math.sin(ang), math.cos(ang))  # → (-π, π]
    if ang > math.pi / 2.0:
        ang -= math.pi
    elif ang <= -math.pi / 2.0:
        ang += math.pi
    return long_len, ang


def wrap_half_pi(a: float) -> float:
    """Envuelve un ángulo a [-π/2, π/2) (simetría de una pinza paralela)."""
    return (a + math.pi / 2.0) % math.pi - math.pi / 2.0


def grasp_yaw_from_quat(q_long_axis_in_base: Sequence[float], yaw_offset: float) -> float:
    """Yaw de la herramienta (en base) para agarrar un instrumento.

    El eje X de la pose del instrumento apunta a lo largo de su eje largo. Se proyecta al
    plano XY de la base y se suma `yaw_offset` (π/2 → mordazas perpendiculares al instrumento).
    """
    x_axis = quat_to_matrix(q_long_axis_in_base)[:, 0]
    yaw = math.atan2(x_axis[1], x_axis[0]) + yaw_offset
    return wrap_half_pi(yaw)


# ----------------------------------------------------------------------------
# Espacio de trabajo y entrega
# ----------------------------------------------------------------------------
def in_box(p: Sequence[float], box: Sequence[float]) -> bool:
    """box = [xmin, xmax, ymin, ymax, zmin, zmax]."""
    return (box[0] <= p[0] <= box[1]
            and box[2] <= p[1] <= box[3]
            and box[4] <= p[2] <= box[5])


def flange_from_tip(tip_xyz: Sequence[float], q: Sequence[float], tcp_offset: float) -> Vec3:
    """Posición de `ee_link` dada la posición deseada de la punta de las mordazas.

    `tcp_offset` = distancia (m) desde ee_link hasta el centro de las mordazas a lo largo del
    eje Z de la herramienta. Con la herramienta apuntando hacia abajo, ee_link queda
    `tcp_offset` por encima de la punta.
    """
    z_axis = quat_to_matrix(q)[:, 2]
    p = np.asarray(tip_xyz, dtype=float) - tcp_offset * z_axis
    return (float(p[0]), float(p[1]), float(p[2]))


def handover_target(hand_xyz: Sequence[float], standoff: float, dz: float,
                    robot_xy: Tuple[float, float] = (0.0, 0.0)) -> Vec3:
    """Punto de entrega: desde la mano, `standoff` m hacia el robot (en el plano XY) y `dz` m arriba."""
    dx = robot_xy[0] - hand_xyz[0]
    dy = robot_xy[1] - hand_xyz[1]
    n = math.hypot(dx, dy)
    if n < 1e-3:
        dx, dy, n = -1.0, 0.0, 1.0
    return (hand_xyz[0] + standoff * dx / n,
            hand_xyz[1] + standoff * dy / n,
            hand_xyz[2] + dz)


def ema(prev: Iterable[float] | None, new: Iterable[float], alpha: float) -> Tuple[float, ...]:
    """Media móvil exponencial vectorial; alpha=1 → sin suavizado."""
    new_t = tuple(float(c) for c in new)
    if prev is None:
        return new_t
    return tuple(alpha * n + (1.0 - alpha) * float(p) for p, n in zip(prev, new_t))


# ----------------------------------------------------------------------------
# Cámara monocular (sin profundidad): rayo de un pixel + intersección con un plano z = cte
# ----------------------------------------------------------------------------
def pixel_ray(u: float, v: float, K, D=None) -> Vec3:
    """Pixel (u, v) → dirección (xn, yn, 1) en el marco óptico, corrigiendo la distorsión.

    K: matriz 3x3 (array-like). D: coeficientes (plumb_bob) o None/[] si no hay distorsión.
    """
    import cv2
    k = np.asarray(K, dtype=np.float64).reshape(3, 3)
    d = None if D is None or len(D) == 0 else np.asarray(D, dtype=np.float64).reshape(-1)
    xn, yn = cv2.undistortPoints(np.array([[[u, v]]], dtype=np.float64), k, d)[0, 0]
    return (float(xn), float(yn), 1.0)


def ray_plane_z(origin: Sequence[float], direction: Sequence[float], plane_z: float,
                eps: float = 1e-6) -> Optional[Vec3]:
    """Corte del rayo origin + s·direction (s > 0) con el plano horizontal z = plane_z."""
    dz = float(direction[2])
    if abs(dz) < eps:
        return None
    s = (plane_z - float(origin[2])) / dz
    if s <= 0.0:
        return None
    return (float(origin[0]) + s * float(direction[0]),
            float(origin[1]) + s * float(direction[1]),
            float(plane_z))


def grasp_on_plane(project, cx: float, cy: float, long_len_px: float, axis: float,
                   alpha: float, plane_z: float) -> Optional[Tuple[float, float, float, float]]:
    """Punto de agarre de una OBB apoyada en el plano z = plane_z (marco base).

    project(u, v, z) → np.ndarray (x, y, z) en base, o None. `axis` es el ángulo del eje largo en
    la imagen, en (-π/2, π/2] (ver obb_long_axis): el sentido +alpha es el del extremo con mayor u.
    Devuelve (x, y, yaw, longitud_m) o None si algún rayo no corta el plano.
    """
    ux, uy = math.cos(axis), math.sin(axis)
    hl = long_len_px / 2.0
    centre = project(cx, cy, plane_z)
    end_a = project(cx - ux * hl, cy - uy * hl, plane_z)
    end_b = project(cx + ux * hl, cy + uy * hl, plane_z)
    if centre is None or end_a is None or end_b is None:
        return None
    vx, vy = float(end_b[0] - end_a[0]), float(end_b[1] - end_a[1])
    length = math.hypot(vx, vy)
    if length < 1e-4:
        return None
    dx, dy = vx / length, vy / length
    return (float(centre[0]) + alpha * dx, float(centre[1]) + alpha * dy,
            math.atan2(dy, dx), length)
