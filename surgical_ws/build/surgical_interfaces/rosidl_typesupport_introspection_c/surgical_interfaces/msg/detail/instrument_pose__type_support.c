// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from surgical_interfaces:msg/InstrumentPose.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "surgical_interfaces/msg/detail/instrument_pose__rosidl_typesupport_introspection_c.h"
#include "surgical_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "surgical_interfaces/msg/detail/instrument_pose__functions.h"
#include "surgical_interfaces/msg/detail/instrument_pose__struct.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/header.h"
// Member `header`
#include "std_msgs/msg/detail/header__rosidl_typesupport_introspection_c.h"
// Member `class_name`
#include "rosidl_runtime_c/string_functions.h"
// Member `pose`
#include "geometry_msgs/msg/pose.h"
// Member `pose`
#include "geometry_msgs/msg/detail/pose__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void surgical_interfaces__msg__InstrumentPose__rosidl_typesupport_introspection_c__InstrumentPose_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  surgical_interfaces__msg__InstrumentPose__init(message_memory);
}

void surgical_interfaces__msg__InstrumentPose__rosidl_typesupport_introspection_c__InstrumentPose_fini_function(void * message_memory)
{
  surgical_interfaces__msg__InstrumentPose__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember surgical_interfaces__msg__InstrumentPose__rosidl_typesupport_introspection_c__InstrumentPose_message_member_array[6] = {
  {
    "header",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(surgical_interfaces__msg__InstrumentPose, header),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "class_name",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(surgical_interfaces__msg__InstrumentPose, class_name),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "pose",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(surgical_interfaces__msg__InstrumentPose, pose),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "confidence",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(surgical_interfaces__msg__InstrumentPose, confidence),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "length_m",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(surgical_interfaces__msg__InstrumentPose, length_m),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "grasp_offset_m",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(surgical_interfaces__msg__InstrumentPose, grasp_offset_m),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers surgical_interfaces__msg__InstrumentPose__rosidl_typesupport_introspection_c__InstrumentPose_message_members = {
  "surgical_interfaces__msg",  // message namespace
  "InstrumentPose",  // message name
  6,  // number of fields
  sizeof(surgical_interfaces__msg__InstrumentPose),
  false,  // has_any_key_member_
  surgical_interfaces__msg__InstrumentPose__rosidl_typesupport_introspection_c__InstrumentPose_message_member_array,  // message members
  surgical_interfaces__msg__InstrumentPose__rosidl_typesupport_introspection_c__InstrumentPose_init_function,  // function to initialize message memory (memory has to be allocated)
  surgical_interfaces__msg__InstrumentPose__rosidl_typesupport_introspection_c__InstrumentPose_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t surgical_interfaces__msg__InstrumentPose__rosidl_typesupport_introspection_c__InstrumentPose_message_type_support_handle = {
  0,
  &surgical_interfaces__msg__InstrumentPose__rosidl_typesupport_introspection_c__InstrumentPose_message_members,
  get_message_typesupport_handle_function,
  &surgical_interfaces__msg__InstrumentPose__get_type_hash,
  &surgical_interfaces__msg__InstrumentPose__get_type_description,
  &surgical_interfaces__msg__InstrumentPose__get_type_description_sources,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_surgical_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, surgical_interfaces, msg, InstrumentPose)() {
  surgical_interfaces__msg__InstrumentPose__rosidl_typesupport_introspection_c__InstrumentPose_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, std_msgs, msg, Header)();
  surgical_interfaces__msg__InstrumentPose__rosidl_typesupport_introspection_c__InstrumentPose_message_member_array[2].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, geometry_msgs, msg, Pose)();
  if (!surgical_interfaces__msg__InstrumentPose__rosidl_typesupport_introspection_c__InstrumentPose_message_type_support_handle.typesupport_identifier) {
    surgical_interfaces__msg__InstrumentPose__rosidl_typesupport_introspection_c__InstrumentPose_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &surgical_interfaces__msg__InstrumentPose__rosidl_typesupport_introspection_c__InstrumentPose_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
