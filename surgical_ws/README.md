# Asistente robótico quirúrgico — ROS 2 Jazzy + UFACTORY Lite 6

Estado: **Paso 1 (esqueleto MVP)**. Cámara: **Logitech MX Brio, monocular (sin profundidad)**.
Sistema: Ubuntu 24.04, ROS 2 Jazzy, Python 3.12, CPU sin GPU.

```
asist_rbt_instrument/             # carpeta del proyecto
├── venv/                         # entorno virtual (ver §2); vive junto al workspace
└── surgical_ws/
    ├── requirements.txt          # dependencias de Python (ver §2)
    ├── README.md
    └── src/
        ├── surgical_interfaces/  # msgs: SurgicalCommand, InstrumentPose
        └── surgical_assistant/
            ├── surgical_assistant/
            │   ├── voice_command_node.py        # mic → Faster-Whisper → NLU → /surgical_command
            │   ├── instrument_detection_node.py # imagen → YOLO-OBB (ONNX) → /instrument_pose
            │   ├── hand_tracking_node.py        # imagen → MediaPipe LM9 → /hand_pose
            │   ├── task_coordinator_node.py     # orquesta y manda metas a MoveIt 2
            │   ├── monocular_utils.py           # suscripción RGB + proyección píxel → plano (TF2)
            │   ├── robot_clients.py             # cliente MoveIt 2 + gripper Lite 6
            │   └── nlu.py · geometry.py · yolo_obb_onnx.py   # lógica pura (con tests)
            ├── config/   (params.yaml, instruments.yaml)
            ├── launch/   test/   tools/ (check_setup.py, train_intent_setfit.py)
```

Flujo: `/surgical_command` + `/instrument_pose` + `/hand_pose` → el coordinador →
MoveIt 2. Los nodos de visión publican sus poses **ya en `link_base`**: intersectan el rayo de cada
píxel con un plano de altura conocida usando la TF `link_base ← cámara` (la publica el Paso 2).

## 1. Requisitos del sistema

```bash
sudo apt install ros-jazzy-desktop ros-jazzy-moveit ros-jazzy-cv-bridge ros-jazzy-message-filters \
                 libportaudio2 python3-venv python3-colcon-common-extensions
# + xarm_ros2 (rama compatible con Jazzy) compilado en un workspace: aporta xarm_msgs y xarm_moveit_config
# + driver UVC para la cámara (usb_cam o v4l2_camera): verifica el nombre del paquete con apt-cache
```

## 2. Entorno virtual con `requirements.txt`

El venv debe usar **el mismo Python que ROS (3.12)** y ver los paquetes de ROS, por eso se crea con
`--system-site-packages`. Desde la carpeta del proyecto:

```bash
cd ~/Documents/asist_rbt_instrument
python3 -m venv --system-site-packages venv
source /opt/ros/jazzy/setup.bash
source venv/bin/activate
which python3 pip          # AMBOS deben apuntar a .../asist_rbt_instrument/venv/bin/
pip install -r surgical_ws/requirements.txt
```

> El prefijo `(venv)` del prompt **no prueba** que el venv esté activo; lo que cuenta es `which python3`.
> Si apunta a `/usr/bin/python3`, el venv está roto o movido (ver §9). Ajusta la ruta del
> `requirements.txt` si lo guardaste en otro lugar.

| Paquete | Para qué | Nota |
|---|---|---|
| `numpy==1.26.4` | todo | **Debe ser < 2**: `cv_bridge` de los binarios de Jazzy está compilado contra NumPy 1.x. |
| `opencv-contrib-python==4.11.0.86` | imágenes | `mediapipe` ya depende de esta distribución. **No instales también `opencv-python`**: ambos publican `cv2` y se pisan. |
| `PyYAML`, `onnxruntime` | configuración, inferencia YOLO-OBB | CPU (`CPUExecutionProvider`). |
| `faster-whisper` | ASR | modelo `small`, CPU int8; se descarga solo la 1.ª vez (internet). |
| `mediapipe` | mano (Landmark 9) | la versión 1.1.1 **no trae `mp.solutions`**: usa el backend `tasks` (ver §4). |
| `sounddevice` | micrófono | necesita `libportaudio2` (apt, §1). |
| `setfit` *(opcional)* | NLU con SetFit | arrastra PyTorch (varios GB); sin él se usan reglas. Descomentar en el `requirements.txt`. |

Reglas de oro:
* Orden de activación en **cada terminal**: ROS → venv → `install/setup.bash`.
* **Compila con el venv activo** (§3), o los nodos usarán el Python del sistema y no verán estas librerías.
* **Un venv no se puede mover ni renombrar** (guarda rutas absolutas): si cambia de sitio, créalo de nuevo.
* Comprobación de que todo convive (debe imprimir `1.26.4 4.11.0` y luego `(4, 4, 3)`):

```bash
python3 -c "import numpy, cv2, cv_bridge; print(numpy.__version__, cv2.__version__)"
python3 -c "import numpy as np; from cv_bridge import CvBridge; b=CvBridge(); m=b.cv2_to_imgmsg(np.zeros((4,4,3),np.uint8),'bgr8'); print(b.imgmsg_to_cv2(m,'bgr8').shape)"
```

## 3. Compilar

```bash
cd ~/Documents/asist_rbt_instrument/surgical_ws          # con ROS + venv activos
python3 -m colcon build --symlink-install
source install/setup.bash
head -1 install/surgical_assistant/lib/surgical_assistant/voice_command_node   # debe apuntar al Python del venv
```
Si apunta a `/usr/bin/python3`: `rm -rf build/surgical_assistant install/surgical_assistant` y recompila.

## 4. Modelos (no vienen incluidos en el workspace)

| Componente | De dónde sale |
|---|---|
| Faster-Whisper | Se descarga solo la primera vez (Hugging Face; el aviso de `HF_TOKEN` es inofensivo). |
| YOLO-OBB | **Lo aportas tú** como `.onnx` (parámetro `model_path`); llega con el Paso 3. Export de Ultralytics: `yolo export model=best.pt format=onnx imgsz=640`. Debe ser **OBB** (`task=obb`). |
| MediaPipe Hands | Con `backend: auto` el nodo usa `tasks` y necesita `hand_landmarker.task` (página de modelos de MediaPipe Hand Landmarker). Guárdalo y apunta `tasks_model_path` en `config/params.yaml`, p. ej. `~/models/hand_landmarker.task`. |
| SetFit | Opcional: `python3 tools/train_intent_setfit.py --out ~/models/intent_setfit` y `setfit_model_dir`. |

## 5. Comprobar el entorno y los modelos

```bash
cd ~/Documents/asist_rbt_instrument/surgical_ws/src/surgical_assistant
python3 tools/check_setup.py --skip-onnx                       # sin modelo YOLO todavía
python3 tools/check_setup.py --onnx ~/models/instrumental_obb.onnx   # cuando lo tengas
python3 -m pytest test        # lógica pura (NLU, geometría, YOLO, monocular); pytest viene del sistema (ROS)
```
`check_setup.py` carga de verdad cada modelo y mide la latencia en tu CPU. `[FAIL]` = hay que arreglarlo;
`[WARN]` suele ser opcional (SetFit, `xarm_msgs` hasta compilar xarm_ros2). `--skip-whisper` evita la descarga.

## 6. Cámara monocular (MX Brio)

Sin profundidad, la posición 3D es **rayo del píxel ∩ plano horizontal** en `link_base`:
* **Instrumentos:** plano de la mesa, `instrument_plane_z_m` (altura de la cara superior del instrumento).
* **Mano:** altura **asumida** (`hand_plane_z_m`); es la principal limitación de precisión.
* Un error Δh en la altura del plano da un error lateral ≈ Δh·tan(θ), con θ el ángulo respecto a la
  vertical: monta la cámara lo más cenital posible.
* Hacen falta: **intrínsecos calibrados a la resolución de trabajo** (trabaja en 1920×1080 o 1280×720, no
  en 4K), **enfoque fijo** (cualquier cambio de enfoque, zoom o resolución invalida la calibración) y la
  **TF `link_base ← marco óptico de la cámara`** (Paso 2). El `frame_id` del driver debe coincidir.

## 7. Ejecutar (siempre empieza en `dry_run:=true`)

```bash
ros2 launch surgical_assistant surgical_assistant.launch.py model_path:=$HOME/models/instrumental_obb.onnx
ros2 node list ; ros2 topic echo /task_state
```
Solo el nodo de voz (no necesita cámara): `ros2 run surgical_assistant voice_command_node --ros-args --params-file install/surgical_assistant/share/surgical_assistant/config/params.yaml`.

**Coordinador sin cámara ni robot** (poses ya en `link_base`, no hace falta TF; una terminal por comando):

```bash
ros2 run surgical_assistant task_coordinator_node --ros-args \
  --params-file install/surgical_assistant/share/surgical_assistant/config/params.yaml

ros2 topic pub -r 5 /instrument_pose surgical_interfaces/msg/InstrumentPose \
 "{header: {frame_id: link_base}, class_name: scalpel, pose: {position: {x: 0.30, y: 0.05, z: 0.03}, orientation: {w: 1.0}}, confidence: 0.9}"
ros2 topic pub -r 5 /hand_pose geometry_msgs/msg/PoseStamped \
 "{header: {frame_id: link_base}, pose: {position: {x: 0.35, y: -0.20, z: 0.25}, orientation: {w: 1.0}}}"
ros2 topic pub --once /surgical_command surgical_interfaces/msg/SurgicalCommand \
 "{intent: give_instrument, instrument_name: scalpel, confidence: 0.9}"
```
Con los parámetros por defecto: pre-agarre z=0.125 m, agarre z=0.025 m, entrega en (0.22, −0.126, 0.30) y la
secuencia `[DRY-RUN] OPEN_GRIPPER … RETURN_HOME` → `Tarea completada.` (el agarre debe quedar dentro de
`workspace_limits`; con `tcp_offset_m` real sube y el límite deja de ser problema).

## 8. Antes de poner `dry_run:=false`

1. Valida en simulación: `ros2 launch xarm_moveit_config lite6_moveit_fake.launch.py` (confirma el nombre del launch en tu rama de xarm_ros2) y `gripper_required:=false`.
2. Confirma `move_group`, `ee_link`, `joint_names` y `home_joints_rad` con `ros2 topic echo /joint_states` y el SRDF. **Los valores por defecto son suposiciones.**
3. Ajusta `tcp_offset_m`, `grasp_z_offset_m`, `workspace_limits` y `velocity_scale`.
4. Ten el paro de emergencia físico al alcance: el comando de voz "alto" es solo un paro por software.

## 9. Solución de problemas

| Síntoma | Causa y arreglo |
|---|---|
| Prompt con `(venv)` pero `which python3` = `/usr/bin/python3` | El venv se movió o se rompió. Bórralo y recréalo (§2). |
| `externally-managed-environment` al usar `pip` | No hay venv activo; `pip` es el del sistema. Actívalo (§2). |
| `No matching distribution found for opencv-python==4.11.0` | Esa versión no existe; usa `opencv-contrib-python==4.11.0.86` (ya está en el `requirements.txt`). |
| Dos paquetes OpenCV instalados (`pip list \| grep -i opencv`) | `pip uninstall -y opencv-python opencv-contrib-python` y `pip install opencv-contrib-python==4.11.0.86`. |
| `import cv_bridge` falla o menciona NumPy | NumPy ≥ 2. `pip install "numpy==1.26.4"`. |
| `PortAudio library not found` | `sudo apt install libportaudio2`. |
| `AttributeError … solutions` (MediaPipe) | Usa `backend: auto` y el archivo `hand_landmarker.task` (§4). |
| Los nodos no ven las librerías del venv | Compilaron con el Python del sistema: recompila con el venv activo (§3). |
| `FileNotFoundError: instruments.yaml` | `config/` no se instaló: recompila (`setup.py` copia `config/*.yaml`). |
| `PortAudioError: Invalid sample rate` (nodo de voz) | El micrófono no admite 16 kHz: hay que capturar a su tasa y remuestrear. |
| `fuera de workspace_limits` en el coordinador | Punto de agarre o entrega fuera de la caja; revisa `workspace_limits` y `tcp_offset_m`. |

## Limitaciones conocidas del MVP

* `return_instrument` se reconoce en el NLU pero el coordinador aún no lo ejecuta.
* **Ambigüedad de 180°:** una OBB no distingue mango de punta; el signo de `alpha_m` se aplica hacia el extremo con mayor `u` en la imagen.
* La altura de la mano es asumida; la mano no es obstáculo en la escena de MoveIt (solo hay distancia de seguridad, `handover_standoff_m`).
* Los nodos no se han ejecutado contra el robot real ni contra el modelo YOLO entrenado.
* `all-MiniLM-L6-v2` es solo inglés: el script de entrenamiento usa `paraphrase-multilingual-MiniLM-L12-v2`.
