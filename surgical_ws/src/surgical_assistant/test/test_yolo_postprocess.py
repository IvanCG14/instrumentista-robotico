import numpy as np

from surgical_assistant.yolo_obb_onnx import YoloObbOnnx


def make_detector():
    d = object.__new__(YoloObbOnnx)  # sin cargar un modelo .onnx real
    d.in_h = d.in_w = 640
    d.conf, d.iou = 0.5, 0.45
    d.names = {0: 'scalpel', 1: 'forceps'}
    return d


def row(cx, cy, w, h, s0, s1, ang):
    return [cx, cy, w, h, s0, s1, ang]


def test_preprocess_shapes_and_letterbox():
    d = make_detector()
    img = np.zeros((960, 1280, 3), np.uint8)  # alto 960, ancho 1280
    x, r, pad = d.preprocess(img)
    assert x.shape == (1, 3, 640, 640) and x.dtype == np.float32
    assert abs(r - 0.5) < 1e-9 and abs(pad[0]) < 1e-9 and abs(pad[1] - 80) < 1e-9


def test_decode_maps_back_and_applies_nms():
    d = make_detector()
    rows = [
        row(320, 320, 200, 40, 0.90, 0.05, 0.3),   # scalpel (la mejor)
        row(322, 321, 198, 41, 0.80, 0.05, 0.3),   # duplicado → NMS lo elimina
        row(100, 200, 120, 30, 0.10, 0.70, -0.2),  # forceps
        row(500, 500, 100, 30, 0.10, 0.10, 0.0),   # bajo umbral → filtrado
    ]
    raw = np.array(rows, np.float32).T[None]  # (1, 7, 4)
    dets = d.decode(raw, 0.5, (0.0, 80.0))
    assert [x.class_name for x in dets] == ['scalpel', 'forceps']
    s = dets[0]
    assert abs(s.cx - 640) < 1e-3 and abs(s.cy - 480) < 1e-3
    assert abs(s.w - 400) < 1e-3 and abs(s.h - 80) < 1e-3
    assert abs(s.angle - 0.3) < 1e-6 and abs(s.score - 0.9) < 1e-6


def test_decode_no_detections():
    d = make_detector()
    raw = np.zeros((1, 7, 10), np.float32)
    assert d.decode(raw, 1.0, (0.0, 0.0)) == []
