// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from surgical_interfaces:msg/SurgicalCommand.idl
// generated code does not contain a copyright notice

#include "surgical_interfaces/msg/detail/surgical_command__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_surgical_interfaces
const rosidl_type_hash_t *
surgical_interfaces__msg__SurgicalCommand__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x99, 0x44, 0x30, 0xd4, 0xb3, 0xa9, 0x8e, 0x5c,
      0xa0, 0x32, 0x4b, 0xea, 0x4a, 0xc1, 0xfe, 0x13,
      0x8a, 0xef, 0x74, 0x05, 0x48, 0x6d, 0xa2, 0x8b,
      0x91, 0xd5, 0x3c, 0x19, 0x52, 0xc2, 0xc9, 0x48,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types
#include "builtin_interfaces/msg/detail/time__functions.h"
#include "std_msgs/msg/detail/header__functions.h"

// Hashes for external referenced types
#ifndef NDEBUG
static const rosidl_type_hash_t builtin_interfaces__msg__Time__EXPECTED_HASH = {1, {
    0xb1, 0x06, 0x23, 0x5e, 0x25, 0xa4, 0xc5, 0xed,
    0x35, 0x09, 0x8a, 0xa0, 0xa6, 0x1a, 0x3e, 0xe9,
    0xc9, 0xb1, 0x8d, 0x19, 0x7f, 0x39, 0x8b, 0x0e,
    0x42, 0x06, 0xce, 0xa9, 0xac, 0xf9, 0xc1, 0x97,
  }};
static const rosidl_type_hash_t std_msgs__msg__Header__EXPECTED_HASH = {1, {
    0xf4, 0x9f, 0xb3, 0xae, 0x2c, 0xf0, 0x70, 0xf7,
    0x93, 0x64, 0x5f, 0xf7, 0x49, 0x68, 0x3a, 0xc6,
    0xb0, 0x62, 0x03, 0xe4, 0x1c, 0x89, 0x1e, 0x17,
    0x70, 0x1b, 0x1c, 0xb5, 0x97, 0xce, 0x6a, 0x01,
  }};
#endif

static char surgical_interfaces__msg__SurgicalCommand__TYPE_NAME[] = "surgical_interfaces/msg/SurgicalCommand";
static char builtin_interfaces__msg__Time__TYPE_NAME[] = "builtin_interfaces/msg/Time";
static char std_msgs__msg__Header__TYPE_NAME[] = "std_msgs/msg/Header";

// Define type names, field names, and default values
static char surgical_interfaces__msg__SurgicalCommand__FIELD_NAME__header[] = "header";
static char surgical_interfaces__msg__SurgicalCommand__FIELD_NAME__intent[] = "intent";
static char surgical_interfaces__msg__SurgicalCommand__FIELD_NAME__instrument_name[] = "instrument_name";
static char surgical_interfaces__msg__SurgicalCommand__FIELD_NAME__confidence[] = "confidence";
static char surgical_interfaces__msg__SurgicalCommand__FIELD_NAME__asr_confidence[] = "asr_confidence";
static char surgical_interfaces__msg__SurgicalCommand__FIELD_NAME__raw_text[] = "raw_text";
static char surgical_interfaces__msg__SurgicalCommand__FIELD_NAME__processing_time_s[] = "processing_time_s";

static rosidl_runtime_c__type_description__Field surgical_interfaces__msg__SurgicalCommand__FIELDS[] = {
  {
    {surgical_interfaces__msg__SurgicalCommand__FIELD_NAME__header, 6, 6},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {std_msgs__msg__Header__TYPE_NAME, 19, 19},
    },
    {NULL, 0, 0},
  },
  {
    {surgical_interfaces__msg__SurgicalCommand__FIELD_NAME__intent, 6, 6},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {surgical_interfaces__msg__SurgicalCommand__FIELD_NAME__instrument_name, 15, 15},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {surgical_interfaces__msg__SurgicalCommand__FIELD_NAME__confidence, 10, 10},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {surgical_interfaces__msg__SurgicalCommand__FIELD_NAME__asr_confidence, 14, 14},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {surgical_interfaces__msg__SurgicalCommand__FIELD_NAME__raw_text, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {surgical_interfaces__msg__SurgicalCommand__FIELD_NAME__processing_time_s, 17, 17},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

static rosidl_runtime_c__type_description__IndividualTypeDescription surgical_interfaces__msg__SurgicalCommand__REFERENCED_TYPE_DESCRIPTIONS[] = {
  {
    {builtin_interfaces__msg__Time__TYPE_NAME, 27, 27},
    {NULL, 0, 0},
  },
  {
    {std_msgs__msg__Header__TYPE_NAME, 19, 19},
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
surgical_interfaces__msg__SurgicalCommand__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {surgical_interfaces__msg__SurgicalCommand__TYPE_NAME, 39, 39},
      {surgical_interfaces__msg__SurgicalCommand__FIELDS, 7, 7},
    },
    {surgical_interfaces__msg__SurgicalCommand__REFERENCED_TYPE_DESCRIPTIONS, 2, 2},
  };
  if (!constructed) {
    assert(0 == memcmp(&builtin_interfaces__msg__Time__EXPECTED_HASH, builtin_interfaces__msg__Time__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[0].fields = builtin_interfaces__msg__Time__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&std_msgs__msg__Header__EXPECTED_HASH, std_msgs__msg__Header__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[1].fields = std_msgs__msg__Header__get_type_description(NULL)->type_description.fields;
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "# Comando quir\\xc3\\xbargico producido por voice_command_node (ASR + NLU).\n"
  "std_msgs/Header header\n"
  "\n"
  "# Intenciones: give_instrument | return_instrument | stop | home\n"
  "string intent\n"
  "\n"
  "# Nombre de clase del instrumento (debe coincidir con las clases del modelo YOLO-OBB).\n"
  "# Vac\\xc3\\xado si la intenci\\xc3\\xb3n no requiere instrumento (stop, home).\n"
  "string instrument_name\n"
  "\n"
  "float32 confidence        # confianza del NLU [0..1]\n"
  "float32 asr_confidence    # confianza media de la transcripci\\xc3\\xb3n [0..1]\n"
  "string raw_text           # transcripci\\xc3\\xb3n tal cual sali\\xc3\\xb3 de Whisper\n"
  "float32 processing_time_s # latencia ASR + NLU (\\xc3\\xbatil para m\\xc3\\xa9tricas de la tesis)";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
surgical_interfaces__msg__SurgicalCommand__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {surgical_interfaces__msg__SurgicalCommand__TYPE_NAME, 39, 39},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 616, 616},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
surgical_interfaces__msg__SurgicalCommand__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[3];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 3, 3};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *surgical_interfaces__msg__SurgicalCommand__get_individual_type_description_source(NULL),
    sources[1] = *builtin_interfaces__msg__Time__get_individual_type_description_source(NULL);
    sources[2] = *std_msgs__msg__Header__get_individual_type_description_source(NULL);
    constructed = true;
  }
  return &source_sequence;
}
