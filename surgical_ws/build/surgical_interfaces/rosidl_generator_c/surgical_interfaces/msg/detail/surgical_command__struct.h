// NOLINT: This file starts with a BOM since it contain non-ASCII characters
// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from surgical_interfaces:msg/SurgicalCommand.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "surgical_interfaces/msg/surgical_command.h"


#ifndef SURGICAL_INTERFACES__MSG__DETAIL__SURGICAL_COMMAND__STRUCT_H_
#define SURGICAL_INTERFACES__MSG__DETAIL__SURGICAL_COMMAND__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Constants defined in the message

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.h"
// Member 'intent'
// Member 'instrument_name'
// Member 'raw_text'
#include "rosidl_runtime_c/string.h"

/// Struct defined in msg/SurgicalCommand in the package surgical_interfaces.
/**
  * Comando quirúrgico producido por voice_command_node (ASR + NLU).
 */
typedef struct surgical_interfaces__msg__SurgicalCommand
{
  std_msgs__msg__Header header;
  /// Intenciones: give_instrument | return_instrument | stop | home
  rosidl_runtime_c__String intent;
  /// Nombre de clase del instrumento (debe coincidir con las clases del modelo YOLO-OBB).
  /// Vacío si la intención no requiere instrumento (stop, home).
  rosidl_runtime_c__String instrument_name;
  /// confianza del NLU
  float confidence;
  /// confianza media de la transcripción
  float asr_confidence;
  /// transcripción tal cual salió de Whisper
  rosidl_runtime_c__String raw_text;
  /// latencia ASR + NLU (útil para métricas de la tesis)
  float processing_time_s;
} surgical_interfaces__msg__SurgicalCommand;

// Struct for a sequence of surgical_interfaces__msg__SurgicalCommand.
typedef struct surgical_interfaces__msg__SurgicalCommand__Sequence
{
  surgical_interfaces__msg__SurgicalCommand * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} surgical_interfaces__msg__SurgicalCommand__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SURGICAL_INTERFACES__MSG__DETAIL__SURGICAL_COMMAND__STRUCT_H_
