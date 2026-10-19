#!/usr/bin/env python3
"""Comprobación de entorno y modelos del asistente quirúrgico. NO usa ROS ni mueve nada.

Carga de verdad cada modelo (YOLO-OBB ONNX, Faster-Whisper, MediaPipe, SetFit) y mide su latencia
en tu CPU, de modo que lo que aquí salga OK es lo que cargarán los nodos.

Uso (desde src/surgical_assistant, con el venv activo y `source install/setup.bash` hecho):
    python3 tools/check_setup.py --onnx ~/models/instrumental_obb.onnx
    python3 tools/check_setup.py --onnx modelo.onnx --setfit-dir ~/models/intent_setfit
    python3 tools/check_setup.py --skip-whisper --skip-onnx        # solo librerías, config y NLU
Código de salida: 0 si no hay [FAIL], 1 si hay alguno.
"""
import argparse
import importlib
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))

_levels = []


def report(level, name, detail=''):
    tag = {'ok': '[ OK ]', 'warn': '[WARN]', 'fail': '[FAIL]', 'info': '[INFO]'}[level]
    print(f'{tag} {name}' + (f' — {detail}' if detail else ''))
    _levels.append(level)


def try_import(mod, level_if_missing='fail', hint=''):
    try:
        m = importlib.import_module(mod)
        report('ok', f'import {mod}', getattr(m, '__version__', ''))
        return m
    except Exception as exc:  # noqa: BLE001 - queremos mostrar cualquier fallo de importación
        report(level_if_missing, f'import {mod}', f'{type(exc).__name__}: {exc}' + (f'  → {hint}' if hint else ''))
        return None


def check_libs():
    print('\n== Librerías ==')
    report('info', f'Python {sys.version.split()[0]}')
    np = try_import('numpy')
    if np is not None and int(np.__version__.split('.')[0]) >= 2:
        report('warn', 'NumPy >= 2', 'cv_bridge de los binarios de Jazzy suele exigir numpy<2')
    try_import('cv2')
    try_import('yaml')
    ort = try_import('onnxruntime')
    if ort is not None:
        report('info', 'Proveedores ONNX Runtime', ', '.join(ort.get_available_providers()))
    try_import('faster_whisper', hint='pip install faster-whisper')
    try_import('mediapipe', hint='pip install mediapipe')
    try_import('setfit', 'warn', 'opcional: sin SetFit se usan reglas por palabras clave')
    sd = try_import('sounddevice', hint='sudo apt install libportaudio2 && pip install sounddevice')
    if sd is not None:
        try:
            dev = sd.query_devices(kind='input')
            report('ok', 'Micrófono por defecto', f"{dev['name']} ({int(dev['default_samplerate'])} Hz)")
        except Exception as exc:  # noqa: BLE001
            report('fail', 'Micrófono por defecto', str(exc))
    hint_ros = 'haz `source /opt/ros/jazzy/setup.bash` y `source install/setup.bash`'
    try_import('rclpy', hint=hint_ros)
    try_import('cv_bridge', hint='con numpy>=2 falla; instala numpy<2')
    try_import('tf2_ros', hint=hint_ros)
    try_import('moveit_msgs', 'warn', 'sudo apt install ros-jazzy-moveit-msgs')
    try_import('xarm_msgs', 'warn', 'compila xarm_ros2 en tu workspace (aporta xarm_msgs)')
    m = try_import('surgical_interfaces.msg', hint='compila y haz source de install/setup.bash')
    if m is not None:
        fields = list(m.SurgicalCommand.get_fields_and_field_types())
        report('ok', 'SurgicalCommand', ', '.join(fields))


def load_config(path):
    print('\n== Configuración ==')
    if not os.path.isfile(path):
        report('fail', 'instruments.yaml', f'no existe: {path}')
        return None
    import yaml
    with open(path, 'r', encoding='utf-8') as f:
        cfg = yaml.safe_load(f) or {}
    insts = cfg.get('instruments', {})
    report('ok' if insts else 'fail', 'instruments.yaml', f'{len(insts)} instrumentos: {", ".join(insts)}')
    return cfg


def check_nlu(cfg):
    print('\n== NLU (reglas, sin SetFit) ==')
    from surgical_assistant.nlu import NLU
    nlu = NLU(cfg['instruments'])
    cases = [('pásame el bisturí', 'give_instrument', 'scalpel'), ('alto', 'stop', ''),
             ('toma las tijeras', 'return_instrument', 'scissors'), ('buenos días', 'unknown', '')]
    for text, intent, inst in cases:
        r = nlu.parse(text)
        ok = (r.intent, r.instrument) == (intent, inst)
        report('ok' if ok else 'fail', f'"{text}"', f'→ {r.intent}/{r.instrument or "-"} (esperado {intent}/{inst or "-"})')


def check_onnx(path, cfg, imgsz, conf, nc_arg=0):
    print('\n== YOLO-OBB (ONNX Runtime) ==')
    if not path:
        report('warn', 'Modelo .onnx', 'no indicado (--onnx). El nodo de detección exige `model_path`.')
        return
    path = os.path.expanduser(path)
    if not os.path.isfile(path):
        report('fail', 'Modelo .onnx', f'no existe: {path}')
        return
    import numpy as np
    from surgical_assistant.yolo_obb_onnx import YoloObbOnnx
    try:
        det = YoloObbOnnx(path, imgsz=imgsz, conf=conf)
    except Exception as exc:  # noqa: BLE001
        report('fail', 'Carga del modelo', f'{type(exc).__name__}: {exc}')
        return
    report('ok', 'Modelo cargado', f'entrada {det.in_w}x{det.in_h}, {os.path.getsize(path) / 1e6:.1f} MB')
    meta = det.session.get_modelmeta().custom_metadata_map or {}
    desc = det.session.get_modelmeta().description or meta.get('description', '')
    if desc:
        report('info', 'Descripción del modelo (metadata)', desc)
    task = meta.get('task', '')
    if task and task != 'obb':
        report('fail', 'Tipo de tarea', f"metadata task='{task}', se necesita 'obb'. Un modelo de detección "
               'normal (cajas sin ángulo) NO sirve: reentrena/exporta con una cabeza OBB.')
        return
    report('ok' if task == 'obb' else 'warn', 'Tipo de tarea',
           "task='obb'" if task else 'sin metadata `task` (no es un export de Ultralytics, o se perdió)')
    names = [det.names[i] for i in sorted(det.names)]
    report('ok' if names else 'warn', 'Clases en la metadata', ', '.join(names) or
           'ninguna: pasa class_names al nodo (parámetro `class_names`)')

    img = np.full((720, 1280, 3), 114, np.uint8)
    x, ratio, pad = det.preprocess(img)
    raw = det.session.run(None, {det.input_name: x})[0]
    nc_expected = len(names) or nc_arg
    if raw.ndim != 3 or raw.shape[0] != 1:
        report('fail', 'Formato de salida', f'{tuple(raw.shape)}: se esperaba (1, 4+nc+1, N)')
        return
    if nc_expected and raw.shape[1] != 4 + nc_expected + 1:
        report('fail', 'Formato de salida', f'{tuple(raw.shape)} no es (1, 4+nc+1, N) con nc={nc_expected}. '
               'Si es (1, 4+nc, N) el modelo es de detección sin ángulo; si no, revisa `decode`.')
        return
    if nc_expected:
        report('ok', 'Formato de salida', f'{tuple(raw.shape)} = (1, 4+nc+1, N), nc={nc_expected}')
    else:
        report('warn', 'Formato de salida', f'{tuple(raw.shape)}: sin nº de clases no puedo distinguir OBB '
               '(4+nc+1) de detección normal (4+nc). Repite con --nc <nº de clases>.')
    try:
        det.decode(raw, ratio, pad)
    except Exception as exc:  # noqa: BLE001
        report('fail', 'Post-proceso (decode + NMS rotado)', f'{type(exc).__name__}: {exc}')
        return
    t = []
    for _ in range(6):
        t0 = time.perf_counter()
        det.detect(img)
        t.append((time.perf_counter() - t0) * 1000)
    report('ok', 'Inferencia completa en CPU', f'{sum(t[1:]) / len(t[1:]):.0f} ms/imagen (media de 5, sin contar el calentamiento)')

    if cfg:
        yaml_keys = set(cfg.get('instruments', {}))
        if names:
            miss = [n for n in names if n not in yaml_keys]
            extra = sorted(yaml_keys - set(names))
            report('warn' if miss else 'ok', 'Clases del modelo ⊂ instruments.yaml',
                   f'sin entrada en el YAML: {miss}' if miss else 'todas tienen entrada (alpha_m, alias)')
            if extra:
                report('warn', 'Instrumentos del YAML que el modelo no detecta', str(extra))


def check_whisper(model_name, threads):
    print('\n== Faster-Whisper (CPU, int8) ==')
    try:
        import numpy as np
        from faster_whisper import WhisperModel
    except Exception as exc:  # noqa: BLE001
        report('fail', 'faster_whisper', str(exc))
        return
    report('info', f"Cargando '{model_name}' (la primera vez lo descarga de Hugging Face: necesita internet)...")
    try:
        t0 = time.perf_counter()
        model = WhisperModel(model_name, device='cpu', compute_type='int8', cpu_threads=threads)
        report('ok', 'Modelo cargado', f'{time.perf_counter() - t0:.1f} s')
        t0 = time.perf_counter()
        segs, _ = model.transcribe(np.zeros(16000, np.float32), language='es', beam_size=1)
        list(segs)
        report('ok', 'Transcripción de 1 s de silencio', f'{(time.perf_counter() - t0) * 1000:.0f} ms')
    except Exception as exc:  # noqa: BLE001
        report('fail', 'Whisper', f'{type(exc).__name__}: {exc}')


def check_mediapipe():
    print('\n== MediaPipe Hands ==')
    try:
        import numpy as np
        import mediapipe as mp
    except Exception as exc:  # noqa: BLE001
        report('fail', 'mediapipe', str(exc))
        return
    if not hasattr(mp, 'solutions'):
        report('warn', "backend 'legacy'", 'esta versión de mediapipe no tiene mp.solutions: el nodo usará el backend '
               "'tasks' (backend: auto) y necesita el archivo hand_landmarker.task (parámetro tasks_model_path)")
        return
    try:
        hands = mp.solutions.hands.Hands(static_image_mode=False, max_num_hands=2, model_complexity=0)
        res = hands.process(np.full((480, 640, 3), 127, np.uint8))
        report('ok', "backend 'legacy'", f'modelo incluido en el paquete; imagen gris → {"mano" if res.multi_hand_landmarks else "sin manos"} (lo esperado)')
    except Exception as exc:  # noqa: BLE001
        report('fail', 'MediaPipe Hands', f'{type(exc).__name__}: {exc}')


def check_setfit(path):
    print('\n== SetFit (intención) ==')
    if not path:
        report('info', 'Sin --setfit-dir', 'el nodo de voz usará reglas por palabras clave (válido para el MVP)')
        return
    try:
        from surgical_assistant.nlu import SetFitIntentClassifier
        clf = SetFitIntentClassifier(os.path.expanduser(path))
        for text in ('pasame el bisturi', 'alto'):
            intent, conf = clf.predict(text)
            report('ok', f'"{text}"', f'→ {intent} ({conf:.2f})')
    except Exception as exc:  # noqa: BLE001
        report('fail', 'SetFit', f'{type(exc).__name__}: {exc}')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--onnx', default='', help='Modelo YOLO-OBB exportado a .onnx')
    ap.add_argument('--instruments', default=os.path.join(HERE, '..', 'config', 'instruments.yaml'))
    ap.add_argument('--setfit-dir', default='')
    ap.add_argument('--whisper-model', default='small')
    ap.add_argument('--threads', type=int, default=4)
    ap.add_argument('--imgsz', type=int, default=640)
    ap.add_argument('--nc', type=int, default=0, help='Nº de clases del modelo (solo si el .onnx no trae metadata)')
    ap.add_argument('--conf', type=float, default=0.5)
    ap.add_argument('--skip-whisper', action='store_true')
    ap.add_argument('--skip-onnx', action='store_true')
    args = ap.parse_args()

    check_libs()
    cfg = load_config(args.instruments)
    if cfg:
        check_nlu(cfg)
    if not args.skip_onnx:
        check_onnx(args.onnx, cfg, args.imgsz, args.conf, args.nc)
    if not args.skip_whisper:
        check_whisper(args.whisper_model, args.threads)
    check_mediapipe()
    check_setfit(args.setfit_dir)

    n_fail, n_warn = _levels.count('fail'), _levels.count('warn')
    print(f'\nResumen: {_levels.count("ok")} OK, {n_warn} avisos, {n_fail} fallos')
    sys.exit(1 if n_fail else 0)


if __name__ == '__main__':
    main()
