# Asistente robótico quirúrgico — Paso 1: esqueleto MVP (ROS 2 + Lite 6)

```
src/
├── surgical_interfaces/      # msgs: SurgicalCommand, InstrumentPose
└── surgical_assistant/
    ├── surgical_assistant/
    │   ├── voice_command_node.py        # mic → Faster-Whisper → NLU → /surgical_command
    │   ├── instrument_detection_node.py # RGB-D → YOLO-OBB (ONNX) → /instrument_pose
    │   ├── hand_tracking_node.py        # RGB-D → MediaPipe LM9 → /hand_pose
    │   ├── task_coordinator_node.py     # orquesta y manda metas a MoveIt 2
    │   ├── robot_clients.py             # cliente MoveIt 2 + gripper Lite 6
    │   ├── nlu.py · geometry.py · yolo_obb_onnx.py · rgbd_utils.py   # lógica pura (con tests)
    ├── config/  (params.yaml, instruments.yaml)   ├── launch/   ├── test/   └── tools/train_intent_setfit.py
```

Flujo: `/surgical_command` + `/instrument_pose` (marco de cámara) + `/hand_pose` (marco de cámara)
→ el coordinador los lleva a `link_base` con **TF2** (la transformación `link_base → cámara` la
publica el Paso 2) → MoveIt 2.

## 1. Dependencias (Ubuntu 24.04 → ROS 2 **Jazzy**)

```bash
sudo apt install ros-jazzy-desktop ros-jazzy-moveit ros-jazzy-cv-bridge ros-jazzy-message-filters \
                 libportaudio2 python3-venv python3-colcon-common-extensions
# xarm_ros2 (rama de tu distro) en src/ o en otro workspace ya compilado: aporta xarm_msgs y xarm_moveit_config

python3 -m venv --system-site-packages ~/venvs/surgical && source ~/venvs/surgical/bin/activate
pip install faster-whisper sounddevice onnxruntime mediapipe "setfit>=1.0" "numpy<2"
```
* `numpy<2`: `cv_bridge` de los binarios de Jazzy está compilado contra NumPy 1.x; si `pip` instala NumPy 2 obtendrás errores al importar `cv_bridge`.
* Construye **con el venv activo** (`python3 -m colcon build`) para que los ejecutables usen ese Python.
* En Intel puedes probar `onnxruntime-openvino` y `onnx_providers: ["OpenVINOExecutionProvider", "CPUExecutionProvider"]`.

## 2. Compilar y probar la lógica pura

```bash
cd surgical_ws && source /opt/ros/jazzy/setup.bash && source ~/venvs/surgical/bin/activate
python3 -m colcon build --symlink-install && source install/setup.bash
python3 -m pytest src/surgical_assistant/test     # geometría, NLU y post-proceso YOLO (no requieren hardware)
```

## 3. Modelos

* **YOLO-OBB**: `yolo export model=best.pt format=onnx imgsz=640` (Ultralytics). Las claves de `config/instruments.yaml` deben coincidir con los nombres de clase del modelo.
* **SetFit** (opcional; sin él se usan reglas por palabras clave): `python3 src/surgical_assistant/tools/train_intent_setfit.py --out ~/models/intent_setfit`.
* **Whisper**: se descarga solo en el primer arranque (`small`, int8).

## 4. Ejecutar (siempre empieza en `dry_run:=true`)

```bash
# Cámara RGB-D (ejemplo RealSense) y, para el coordinador real, driver xarm_ros2 + MoveIt (ver su README)
ros2 launch surgical_assistant surgical_assistant.launch.py model_path:=$HOME/models/instrumental_obb.onnx
ros2 topic echo /task_state
```

Prueba del coordinador **sin cámara ni robot** (TF falso + poses falsas + comando falso):

```bash
ros2 run tf2_ros static_transform_publisher --x 0.5 --y 0 --z 0.6 --roll 3.14159 --pitch 0 --yaw 0 \
    --frame-id link_base --child-frame-id camera_color_optical_frame &
ros2 topic pub -r 5 /instrument_pose surgical_interfaces/msg/InstrumentPose \
 "{header: {frame_id: camera_color_optical_frame}, class_name: scalpel, pose: {position: {x: 0.0, y: 0.05, z: 0.58}, orientation: {w: 1.0}}, confidence: 0.9}" &
ros2 topic pub -r 5 /hand_pose geometry_msgs/msg/PoseStamped \
 "{header: {frame_id: camera_color_optical_frame}, pose: {position: {x: 0.0, y: -0.2, z: 0.5}, orientation: {w: 1.0}}}" &
ros2 topic pub --once /surgical_command surgical_interfaces/msg/SurgicalCommand \
 "{intent: give_instrument, instrument_name: scalpel, confidence: 0.9}"
```
En el log verás las coordenadas de agarre/entrega en `link_base` y la secuencia `[DRY-RUN] …`.

## 5. Antes de poner `dry_run:=false`

1. Valida en simulación: `ros2 launch xarm_moveit_config lite6_moveit_fake.launch.py` (confirma el nombre del launch en tu rama de xarm_ros2) y `gripper_required:=false`.
2. Confirma `move_group`, `ee_link`, `joint_names` y `home_joints_rad` con `ros2 topic echo /joint_states` y el SRDF. **Los valores por defecto son suposiciones.**
3. Ajusta `tcp_offset_m`, `grasp_z_offset_m`, `workspace_limits` y la velocidad (`velocity_scale`).
4. Ten el paro de emergencia físico al alcance: el comando de voz "alto" es un paro por software.

## Limitaciones conocidas del MVP

* `return_instrument` se reconoce en el NLU pero el coordinador aún no lo ejecuta.
* **Ambigüedad de 180°**: una OBB no distingue mango de punta; el signo de `alpha_m` se aplica sobre un eje con componente +x en la imagen. Para instrumentos con orientación libre hay que añadir una clase por extremo o un clasificador de sentido.
* La mano no es obstáculo en la escena de MoveIt; solo se guarda una distancia (`handover_standoff_m`).
* Nunca se ha ejecutado contra hardware ni contra ROS 2 en esta sesión (ver pruebas realizadas abajo).
* `all-MiniLM-L6-v2` es solo inglés: el script de entrenamiento usa `paraphrase-multilingual-MiniLM-L12-v2`.
