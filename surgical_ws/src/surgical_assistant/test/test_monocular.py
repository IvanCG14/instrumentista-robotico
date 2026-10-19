import math

import cv2
import numpy as np

from surgical_assistant import geometry as g

K = np.array([[1400.0, 0, 960.0], [0, 1400.0, 540.0], [0, 0, 1]])
D = np.array([-0.12, 0.05, 0.0005, -0.0003, 0.0])        # distorsión realista de gran angular
PLANE_Z = 0.01


def make_camera(roll=math.pi, pitch=0.25, yaw=0.15, pos=(0.30, 0.0, 0.75)):
    """Cámara cenital inclinada. Devuelve (R_base_cam, origen, project, to_pixel)."""
    rot = g.quat_to_matrix(g.quat_from_rpy(roll, pitch, yaw))
    origin = np.array(pos)

    def to_pixel(p_base):  # verdad de terreno: proyección con distorsión (cv2.projectPoints)
        r_cb = rot.T
        rvec, _ = cv2.Rodrigues(r_cb)
        tvec = -r_cb @ origin
        px, _ = cv2.projectPoints(np.array([p_base], float), rvec, tvec, K, D)
        return px[0, 0]

    def project(u, v, z):
        ray = rot @ np.array(g.pixel_ray(u, v, K, D))
        p = g.ray_plane_z(origin, ray, z)
        return None if p is None else np.array(p)

    return rot, origin, project, to_pixel


def test_pixel_to_plane_roundtrip_with_distortion():
    _, _, project, to_pixel = make_camera()
    for x, y in [(0.30, 0.0), (0.2, 0.15), (0.45, -0.2), (0.15, -0.3), (0.5, 0.3)]:
        u, v = to_pixel((x, y, PLANE_Z))
        p = project(u, v, PLANE_Z)
        assert np.allclose(p, (x, y, PLANE_Z), atol=2e-4), (x, y, p)


def test_no_distortion_and_none_cases():
    ray = g.pixel_ray(960.0, 540.0, K, None)
    assert np.allclose(ray, (0, 0, 1))
    assert g.pixel_ray(960.0, 540.0, K, [])[2] == 1.0
    assert g.ray_plane_z((0, 0, 0.5), (0, 0, 1), 0.0) is None        # el plano queda detrás
    assert g.ray_plane_z((0, 0, 0.5), (1, 0, 0), 0.0) is None        # rayo paralelo al plano
    assert np.allclose(g.ray_plane_z((0, 0, 1), (1, 0, -1), 0.0), (1, 0, 0))


def _obb_from_world(to_pixel, centre_xy, yaw, length):
    c = np.array([*centre_xy, PLANE_Z])
    d = np.array([math.cos(yaw), math.sin(yaw), 0.0])
    pa, pb = to_pixel(c - d * length / 2), to_pixel(c + d * length / 2)
    cx, cy = to_pixel(c)
    vec = pb - pa
    _, axis = g.obb_long_axis(float(np.hypot(*vec)), 5.0, math.atan2(vec[1], vec[0]))
    return float(cx), float(cy), float(np.hypot(*vec)), axis


def test_grasp_on_plane_recovers_position_axis_and_alpha():
    _, _, project, to_pixel = make_camera()
    alpha = 0.02
    for centre, yaw in [((0.30, 0.05), 0.6), ((0.22, -0.12), -1.1), ((0.40, 0.2), 2.4), ((0.30, 0.0), 0.0)]:
        cx, cy, lpx, axis = _obb_from_world(to_pixel, centre, yaw, 0.15)
        x, y, yaw_est, length = g.grasp_on_plane(project, cx, cy, lpx, axis, alpha, PLANE_Z)
        # Dirección: la misma recta (ambigüedad de 180° resuelta hacia el extremo con mayor u)
        d_est = np.array([math.cos(yaw_est), math.sin(yaw_est)])
        d_true = np.array([math.cos(yaw), math.sin(yaw)])
        assert abs(abs(d_est @ d_true) - 1.0) < 2e-3
        assert abs(length - 0.15) < 2e-3
        # Posición: centro + alpha·d_est
        assert np.allclose((x, y), np.array(centre) + alpha * d_est, atol=2e-3)
        # El sentido +alpha apunta al extremo con mayor coordenada u en la imagen
        eps = 1e-3
        u_plus = to_pixel(np.array([*centre, PLANE_Z]) + eps * np.array([*d_est, 0]))[0]
        u_minus = to_pixel(np.array([*centre, PLANE_Z]) - eps * np.array([*d_est, 0]))[0]
        assert u_plus >= u_minus


def test_grasp_on_plane_none_when_tf_missing():
    assert g.grasp_on_plane(lambda u, v, z: None, 10, 10, 50, 0.0, 0.0, PLANE_Z) is None


def test_plane_height_error_sensitivity_matches_theory():
    """Error en altura del plano Δh → error lateral ≈ Δh·tan(θ), θ = ángulo respecto a la vertical."""
    _, origin, project, to_pixel = make_camera(pitch=0.0, yaw=0.0)
    target = np.array([0.30 + 0.3, 0.0, PLANE_Z])           # 0.3 m de desplazamiento horizontal
    u, v = to_pixel(target)
    dh = 0.05
    wrong = project(u, v, PLANE_Z + dh)
    theta = math.atan2(0.3, origin[2] - PLANE_Z)
    assert abs(np.hypot(*(wrong[:2] - target[:2])) - dh * math.tan(theta)) < 1e-3
