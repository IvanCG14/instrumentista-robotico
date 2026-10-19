// NOLINT: This file starts with a BOM since it contain non-ASCII characters
// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from surgical_interfaces:msg/InstrumentPose.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "surgical_interfaces/msg/instrument_pose.h"


#ifndef SURGICAL_INTERFACES__MSG__DETAIL__INSTRUMENT_POSE__STRUCT_H_
#define SURGICAL_INTERFACES__MSG__DETAIL__INSTRUMENT_POSE__STRUCT_H_

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
// Member 'class_name'
#include "rosidl_runtime_c/string.h"
// Member 'pose'
#include "geometry_msgs/msg/detail/pose__struct.h"

/// Struct defined in msg/InstrumentPose in the package surgical_interfaces.
/**
  * Instrumento detectado con su punto de agarre, expresado en el marco de la cámara.
  *
  * header.frame_id : marco óptico de la cámara (x derecha, y abajo, z hacia adelante).
  * pose.position   : punto de agarre (centro OBB + offset lineal alpha a lo largo del eje largo).
  * pose.orientation: rotación alrededor del eje Z de la cámara tal que el eje X de la pose
  *                   apunta a lo largo del eje largo del instrumento.
 */
typedef struct surgical_interfaces__msg__InstrumentPose
{
  std_msgs__msg__Header header;
  rosidl_runtime_c__String class_name;
  geometry_msgs__msg__Pose pose;
  float confidence;
  /// longitud estimada del eje largo (m)
  float length_m;
  /// alpha aplicado (m)
  float grasp_offset_m;
} surgical_interfaces__msg__InstrumentPose;

// Struct for a sequence of surgical_interfaces__msg__InstrumentPose.
typedef struct surgical_interfaces__msg__InstrumentPose__Sequence
{
  surgical_interfaces__msg__InstrumentPose * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} surgical_interfaces__msg__InstrumentPose__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SURGICAL_INTERFACES__MSG__DETAIL__INSTRUMENT_POSE__STRUCT_H_
