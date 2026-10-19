# Comando quirúrgico producido por voice_command_node (ASR + NLU).
std_msgs/Header header

# Intenciones: give_instrument | return_instrument | stop | home
string intent

# Nombre de clase del instrumento (debe coincidir con las clases del modelo YOLO-OBB).
# Vacío si la intención no requiere instrumento (stop, home).
string instrument_name

float32 confidence        # confianza del NLU [0..1]
float32 asr_confidence    # confianza media de la transcripción [0..1]
string raw_text           # transcripción tal cual salió de Whisper
float32 processing_time_s # latencia ASR + NLU (útil para métricas de la tesis)
