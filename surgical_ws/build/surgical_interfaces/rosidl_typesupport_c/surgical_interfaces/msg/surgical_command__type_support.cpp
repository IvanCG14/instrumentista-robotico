// generated from rosidl_typesupport_c/resource/idl__type_support.cpp.em
// with input from surgical_interfaces:msg/SurgicalCommand.idl
// generated code does not contain a copyright notice

#include "cstddef"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "surgical_interfaces/msg/detail/surgical_command__struct.h"
#include "surgical_interfaces/msg/detail/surgical_command__type_support.h"
#include "surgical_interfaces/msg/detail/surgical_command__functions.h"
#include "rosidl_typesupport_c/identifier.h"
#include "rosidl_typesupport_c/message_type_support_dispatch.h"
#include "rosidl_typesupport_c/type_support_map.h"
#include "rosidl_typesupport_c/visibility_control.h"
#include "rosidl_typesupport_interface/macros.h"

namespace surgical_interfaces
{

namespace msg
{

namespace rosidl_typesupport_c
{

typedef struct _SurgicalCommand_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _SurgicalCommand_type_support_ids_t;

static const _SurgicalCommand_type_support_ids_t _SurgicalCommand_message_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_c",  // ::rosidl_typesupport_fastrtps_c::typesupport_identifier,
    "rosidl_typesupport_introspection_c",  // ::rosidl_typesupport_introspection_c::typesupport_identifier,
  }
};

typedef struct _SurgicalCommand_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _SurgicalCommand_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _SurgicalCommand_type_support_symbol_names_t _SurgicalCommand_message_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, surgical_interfaces, msg, SurgicalCommand)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, surgical_interfaces, msg, SurgicalCommand)),
  }
};

typedef struct _SurgicalCommand_type_support_data_t
{
  void * data[2];
} _SurgicalCommand_type_support_data_t;

static _SurgicalCommand_type_support_data_t _SurgicalCommand_message_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _SurgicalCommand_message_typesupport_map = {
  2,
  "surgical_interfaces",
  &_SurgicalCommand_message_typesupport_ids.typesupport_identifier[0],
  &_SurgicalCommand_message_typesupport_symbol_names.symbol_name[0],
  &_SurgicalCommand_message_typesupport_data.data[0],
};

static const rosidl_message_type_support_t SurgicalCommand_message_type_support_handle = {
  rosidl_typesupport_c__typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_SurgicalCommand_message_typesupport_map),
  rosidl_typesupport_c__get_message_typesupport_handle_function,
  &surgical_interfaces__msg__SurgicalCommand__get_type_hash,
  &surgical_interfaces__msg__SurgicalCommand__get_type_description,
  &surgical_interfaces__msg__SurgicalCommand__get_type_description_sources,
};

}  // namespace rosidl_typesupport_c

}  // namespace msg

}  // namespace surgical_interfaces

#ifdef __cplusplus
extern "C"
{
#endif

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_c, surgical_interfaces, msg, SurgicalCommand)() {
  return &::surgical_interfaces::msg::rosidl_typesupport_c::SurgicalCommand_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif
