# Instrumento detectado con su punto de agarre, expresado en el marco de la cámara.
#
# header.frame_id : marco óptico de la cámara (x derecha, y abajo, z hacia adelante).
# pose.position   : punto de agarre (centro OBB + offset lineal alpha a lo largo del eje largo).
# pose.orientation: rotación alrededor del eje Z de la cámara tal que el eje X de la pose
#                   apunta a lo largo del eje largo del instrumento.
std_msgs/Header header
string class_name
geometry_msgs/Pose pose
float32 confidence
float32 length_m          # longitud estimada del eje largo (m)
float32 grasp_offset_m    # alpha aplicado (m)
