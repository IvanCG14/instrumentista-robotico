// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from surgical_interfaces:msg/SurgicalCommand.idl
// generated code does not contain a copyright notice
#include "surgical_interfaces/msg/detail/surgical_command__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/detail/header__functions.h"
// Member `intent`
// Member `instrument_name`
// Member `raw_text`
#include "rosidl_runtime_c/string_functions.h"

bool
surgical_interfaces__msg__SurgicalCommand__init(surgical_interfaces__msg__SurgicalCommand * msg)
{
  if (!msg) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__init(&msg->header)) {
    surgical_interfaces__msg__SurgicalCommand__fini(msg);
    return false;
  }
  // intent
  if (!rosidl_runtime_c__String__init(&msg->intent)) {
    surgical_interfaces__msg__SurgicalCommand__fini(msg);
    return false;
  }
  // instrument_name
  if (!rosidl_runtime_c__String__init(&msg->instrument_name)) {
    surgical_interfaces__msg__SurgicalCommand__fini(msg);
    return false;
  }
  // confidence
  // asr_confidence
  // raw_text
  if (!rosidl_runtime_c__String__init(&msg->raw_text)) {
    surgical_interfaces__msg__SurgicalCommand__fini(msg);
    return false;
  }
  // processing_time_s
  return true;
}

void
surgical_interfaces__msg__SurgicalCommand__fini(surgical_interfaces__msg__SurgicalCommand * msg)
{
  if (!msg) {
    return;
  }
  // header
  std_msgs__msg__Header__fini(&msg->header);
  // intent
  rosidl_runtime_c__String__fini(&msg->intent);
  // instrument_name
  rosidl_runtime_c__String__fini(&msg->instrument_name);
  // confidence
  // asr_confidence
  // raw_text
  rosidl_runtime_c__String__fini(&msg->raw_text);
  // processing_time_s
}

bool
surgical_interfaces__msg__SurgicalCommand__are_equal(const surgical_interfaces__msg__SurgicalCommand * lhs, const surgical_interfaces__msg__SurgicalCommand * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__are_equal(
      &(lhs->header), &(rhs->header)))
  {
    return false;
  }
  // intent
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->intent), &(rhs->intent)))
  {
    return false;
  }
  // instrument_name
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->instrument_name), &(rhs->instrument_name)))
  {
    return false;
  }
  // confidence
  if (lhs->confidence != rhs->confidence) {
    return false;
  }
  // asr_confidence
  if (lhs->asr_confidence != rhs->asr_confidence) {
    return false;
  }
  // raw_text
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->raw_text), &(rhs->raw_text)))
  {
    return false;
  }
  // processing_time_s
  if (lhs->processing_time_s != rhs->processing_time_s) {
    return false;
  }
  return true;
}

bool
surgical_interfaces__msg__SurgicalCommand__copy(
  const surgical_interfaces__msg__SurgicalCommand * input,
  surgical_interfaces__msg__SurgicalCommand * output)
{
  if (!input || !output) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__copy(
      &(input->header), &(output->header)))
  {
    return false;
  }
  // intent
  if (!rosidl_runtime_c__String__copy(
      &(input->intent), &(output->intent)))
  {
    return false;
  }
  // instrument_name
  if (!rosidl_runtime_c__String__copy(
      &(input->instrument_name), &(output->instrument_name)))
  {
    return false;
  }
  // confidence
  output->confidence = input->confidence;
  // asr_confidence
  output->asr_confidence = input->asr_confidence;
  // raw_text
  if (!rosidl_runtime_c__String__copy(
      &(input->raw_text), &(output->raw_text)))
  {
    return false;
  }
  // processing_time_s
  output->processing_time_s = input->processing_time_s;
  return true;
}

surgical_interfaces__msg__SurgicalCommand *
surgical_interfaces__msg__SurgicalCommand__create(void)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  surgical_interfaces__msg__SurgicalCommand * msg = (surgical_interfaces__msg__SurgicalCommand *)allocator.allocate(sizeof(surgical_interfaces__msg__SurgicalCommand), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(surgical_interfaces__msg__SurgicalCommand));
  bool success = surgical_interfaces__msg__SurgicalCommand__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
surgical_interfaces__msg__SurgicalCommand__destroy(surgical_interfaces__msg__SurgicalCommand * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    surgical_interfaces__msg__SurgicalCommand__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
surgical_interfaces__msg__SurgicalCommand__Sequence__init(surgical_interfaces__msg__SurgicalCommand__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  surgical_interfaces__msg__SurgicalCommand * data = NULL;

  if (size) {
    data = (surgical_interfaces__msg__SurgicalCommand *)allocator.zero_allocate(size, sizeof(surgical_interfaces__msg__SurgicalCommand), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = surgical_interfaces__msg__SurgicalCommand__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        surgical_interfaces__msg__SurgicalCommand__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
surgical_interfaces__msg__SurgicalCommand__Sequence__fini(surgical_interfaces__msg__SurgicalCommand__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      surgical_interfaces__msg__SurgicalCommand__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

surgical_interfaces__msg__SurgicalCommand__Sequence *
surgical_interfaces__msg__SurgicalCommand__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  surgical_interfaces__msg__SurgicalCommand__Sequence * array = (surgical_interfaces__msg__SurgicalCommand__Sequence *)allocator.allocate(sizeof(surgical_interfaces__msg__SurgicalCommand__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = surgical_interfaces__msg__SurgicalCommand__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
surgical_interfaces__msg__SurgicalCommand__Sequence__destroy(surgical_interfaces__msg__SurgicalCommand__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    surgical_interfaces__msg__SurgicalCommand__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
surgical_interfaces__msg__SurgicalCommand__Sequence__are_equal(const surgical_interfaces__msg__SurgicalCommand__Sequence * lhs, const surgical_interfaces__msg__SurgicalCommand__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!surgical_interfaces__msg__SurgicalCommand__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
surgical_interfaces__msg__SurgicalCommand__Sequence__copy(
  const surgical_interfaces__msg__SurgicalCommand__Sequence * input,
  surgical_interfaces__msg__SurgicalCommand__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(surgical_interfaces__msg__SurgicalCommand);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    surgical_interfaces__msg__SurgicalCommand * data =
      (surgical_interfaces__msg__SurgicalCommand *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!surgical_interfaces__msg__SurgicalCommand__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          surgical_interfaces__msg__SurgicalCommand__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!surgical_interfaces__msg__SurgicalCommand__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
