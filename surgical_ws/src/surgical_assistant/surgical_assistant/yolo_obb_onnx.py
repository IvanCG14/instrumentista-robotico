"""Inferencia YOLO-OBB con ONNX Runtime (CPU) — sin dependencia de ROS ni de ultralytics.

Formato de salida esperado (export de Ultralytics: `yolo export model=best.pt format=onnx`):
    output0: (1, 4 + nc + 1, N)  →  [cx, cy, w, h, score_0..score_nc-1, ángulo(rad)]
con coordenadas en píxeles del tensor de entrada (letterbox). Probado contra ese layout
(YOLOv8-OBB / YOLO11-OBB). Si tu modelo viene de otro repositorio (p. ej. un YOLOv9 con
cabeza OBB propia) el layout puede variar: ajusta `_decode`.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import cv2
import numpy as np


@dataclass
class ObbDetection:
    class_id: int
    class_name: str
    score: float
    cx: float
    cy: float
    w: float
    h: float
    angle: float  # rad, convención de imagen (y hacia abajo), w a lo largo de (cos a, sin a)


class YoloObbOnnx:
    def __init__(self, model_path: str, imgsz: int = 640, conf: float = 0.5, iou: float = 0.45,
                 class_names: Optional[Sequence[str]] = None,
                 providers: Optional[Sequence[str]] = None, intra_threads: int = 0):
        import onnxruntime as ort

        so = ort.SessionOptions()
        if intra_threads > 0:
            so.intra_op_num_threads = intra_threads
        so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        self.session = ort.InferenceSession(model_path, sess_options=so,
                                            providers=list(providers or ['CPUExecutionProvider']))
        inp = self.session.get_inputs()[0]
        self.input_name = inp.name
        shape = inp.shape  # [1, 3, H, W] (puede traer strings si es dinámico)
        self.in_h = shape[2] if isinstance(shape[2], int) else imgsz
        self.in_w = shape[3] if isinstance(shape[3], int) else imgsz
        self.conf = conf
        self.iou = iou
        self.names = self._resolve_names(class_names)

    # ------------------------------------------------------------------ nombres
    def _resolve_names(self, override: Optional[Sequence[str]]) -> Dict[int, str]:
        if override:
            return {i: n for i, n in enumerate(override)}
        meta = self.session.get_modelmeta().custom_metadata_map or {}
        if 'names' in meta:
            try:
                parsed = ast.literal_eval(meta['names'])
                return {int(k): str(v) for k, v in parsed.items()}
            except (ValueError, SyntaxError):
                pass
        return {}

    # --------------------------------------------------------------- preprocesado
    def _letterbox(self, img: np.ndarray) -> Tuple[np.ndarray, float, Tuple[float, float]]:
        h, w = img.shape[:2]
        r = min(self.in_h / h, self.in_w / w)
        nh, nw = int(round(h * r)), int(round(w * r))
        resized = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_LINEAR)
        dh, dw = (self.in_h - nh) / 2.0, (self.in_w - nw) / 2.0
        top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
        left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
        out = cv2.copyMakeBorder(resized, top, bottom, left, right, cv2.BORDER_CONSTANT,
                                 value=(114, 114, 114))
        return out, r, (dw, dh)

    def preprocess(self, bgr: np.ndarray):
        lb, r, pad = self._letterbox(bgr)
        x = cv2.cvtColor(lb, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
        x = np.transpose(x, (2, 0, 1))[None]
        return np.ascontiguousarray(x), r, pad

    # ------------------------------------------------------------- postprocesado
    def decode(self, raw: np.ndarray, ratio: float, pad: Tuple[float, float]) -> List[ObbDetection]:
        """raw: salida cruda (1, 4+nc+1, N) del export de Ultralytics. Devuelve detecciones tras NMS rotado."""
        if raw.ndim != 3 or raw.shape[0] != 1:
            raise ValueError(f'Salida inesperada {raw.shape}: se esperaba (1, 4+nc+1, N).')
        pred = raw[0].T  # (C, N) → (N, C)
        nc = pred.shape[1] - 5
        if nc < 1:
            raise ValueError(f'Salida inesperada {raw.shape}: no parece un modelo OBB.')
        scores_all = pred[:, 4:4 + nc]
        cls_ids = scores_all.argmax(axis=1)
        scores = scores_all[np.arange(len(pred)), cls_ids]
        keep = scores >= self.conf
        if not np.any(keep):
            return []
        pred, cls_ids, scores = pred[keep], cls_ids[keep], scores[keep]

        cx = (pred[:, 0] - pad[0]) / ratio
        cy = (pred[:, 1] - pad[1]) / ratio
        w = pred[:, 2] / ratio
        h = pred[:, 3] / ratio
        ang = pred[:, 4 + nc]

        dets: List[ObbDetection] = []
        for c in np.unique(cls_ids):  # NMS rotado por clase
            idx = np.where(cls_ids == c)[0]
            rects = [((float(cx[i]), float(cy[i])), (float(w[i]), float(h[i])),
                      float(np.degrees(ang[i]))) for i in idx]
            sel = cv2.dnn.NMSBoxesRotated(rects, [float(scores[i]) for i in idx], self.conf, self.iou)
            for k in np.array(sel).reshape(-1):
                i = idx[int(k)]
                dets.append(ObbDetection(int(c), self.names.get(int(c), str(int(c))), float(scores[i]),
                                         float(cx[i]), float(cy[i]), float(w[i]), float(h[i]),
                                         float(ang[i])))
        dets.sort(key=lambda d: d.score, reverse=True)
        return dets

    def detect(self, bgr: np.ndarray) -> List[ObbDetection]:
        x, ratio, pad = self.preprocess(bgr)
        raw = self.session.run(None, {self.input_name: x})[0]
        return self.decode(raw, ratio, pad)


def draw_detection(img: np.ndarray, d: ObbDetection, grasp_uv: Optional[Tuple[float, float]] = None) -> None:
    """Dibuja la OBB (y el punto de agarre) sobre `img` in-place."""
    box = cv2.boxPoints(((d.cx, d.cy), (d.w, d.h), float(np.degrees(d.angle))))
    cv2.polylines(img, [box.astype(np.int32)], True, (0, 255, 0), 2)
    cv2.putText(img, f'{d.class_name} {d.score:.2f}', (int(d.cx), int(d.cy) - 8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    if grasp_uv is not None:
        cv2.circle(img, (int(grasp_uv[0]), int(grasp_uv[1])), 5, (0, 0, 255), -1)
