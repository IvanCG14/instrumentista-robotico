import math

import numpy as np

from surgical_assistant import geometry as g


def close(a, b, tol=1e-6):
    return np.allclose(np.asarray(a, float), np.asarray(b, float), atol=tol)


def test_tool_down_quat_points_down():
    yaw = 0.7
    q = g.tool_down_quat(yaw)
    assert close(q, (math.cos(yaw / 2), math.sin(yaw / 2), 0.0, 0.0))
    r = g.quat_to_matrix(q)
    assert close(r[:, 2], (0, 0, -1))
    assert close(r[:, 0], (math.cos(yaw), math.sin(yaw), 0))


def test_rpy_yaw_rotates_x_to_y():
    r = g.quat_to_matrix(g.quat_from_rpy(0, 0, math.pi / 2))
    assert close(r @ np.array([1, 0, 0]), (0, 1, 0))


def test_apply_transform():
    t_q = g.quat_from_yaw(math.pi / 2)
    p, q = g.apply_transform((1, 2, 3), t_q, (1, 0, 0), g.quat_from_yaw(0.0))
    assert close(p, (1, 3, 3))
    assert close(q, t_q)


def test_apply_transform_composes_rotations():
    _, q = g.apply_transform((0, 0, 0), g.quat_from_yaw(0.3), (0, 0, 0), g.quat_from_yaw(0.4))
    assert close(q, g.quat_from_yaw(0.7))


def test_obb_long_axis():
    assert close(g.obb_long_axis(100, 20, 0.0), (100, 0.0))
    ln, ang = g.obb_long_axis(20, 100, 0.0)
    assert ln == 100 and close(ang, math.pi / 2)
    ln, ang = g.obb_long_axis(20, 100, math.pi / 4)  # 3π/4 → -π/4
    assert close(ang, -math.pi / 4)
    # El eje largo siempre cae en (-π/2, π/2]
    for a in np.linspace(-3, 3, 25):
        _, ang = g.obb_long_axis(50, 10, float(a))
        assert -math.pi / 2 < ang <= math.pi / 2 + 1e-9


def test_grasp_yaw_is_perpendicular_to_instrument():
    # Instrumento a lo largo de +Y de la base → mordazas (eje X herramienta) a lo largo de +X.
    yaw = g.grasp_yaw_from_quat(g.quat_from_yaw(math.pi / 2), math.pi / 2)
    assert close(yaw, 0.0)
    # Instrumento a lo largo de +X → mordazas a lo largo de ±Y (yaw = -π/2 tras envolver).
    yaw = g.grasp_yaw_from_quat(g.quat_from_yaw(0.0), math.pi / 2)
    assert close(abs(yaw), math.pi / 2)


def test_wrap_half_pi_range():
    for a in np.linspace(-10, 10, 101):
        w = g.wrap_half_pi(float(a))
        assert -math.pi / 2 - 1e-9 <= w < math.pi / 2 + 1e-9
        assert close(math.tan(w), math.tan(a), 1e-6) or abs(math.cos(a)) < 1e-6


def test_flange_from_tip_tool_down():
    p = g.flange_from_tip((0.3, 0.0, 0.05), g.tool_down_quat(0.4), 0.1)
    assert close(p, (0.3, 0.0, 0.15))


def test_handover_target():
    hand = (0.4, 0.2, 0.2)
    t = g.handover_target(hand, 0.15, 0.05)
    assert close(math.hypot(t[0] - hand[0], t[1] - hand[1]), 0.15)
    assert close(t[2], 0.25)
    # Se acerca al robot (origen)
    assert math.hypot(t[0], t[1]) < math.hypot(hand[0], hand[1])


def test_in_box():
    box = [0.1, 0.5, -0.3, 0.3, 0.0, 0.4]
    assert g.in_box((0.3, 0.0, 0.2), box)
    assert not g.in_box((0.6, 0.0, 0.2), box)
    assert not g.in_box((0.3, 0.0, -0.01), box)


def test_deproject_and_ema():
    assert close(g.deproject(320, 240, 1.0, 600, 600, 320, 240), (0, 0, 1))
    assert close(g.deproject(920, 240, 2.0, 600, 600, 320, 240), (2.0, 0, 2.0))
    assert g.ema(None, (1, 2, 3), 0.5) == (1.0, 2.0, 3.0)
    assert close(g.ema((0, 0, 0), (2, 4, 6), 0.5), (1, 2, 3))
