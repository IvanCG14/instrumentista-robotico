// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from surgical_interfaces:msg/InstrumentPose.idl
// generated code does not contain a copyright notice
#include "surgical_interfaces/msg/detail/instrument_pose__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/detail/header__functions.h"
// Member `class_name`
#include "rosidl_runtime_c/string_functions.h"
// Member `pose`
#include "geometry_msgs/msg/detail/pose__functions.h"

bool
surgical_interfaces__msg__InstrumentPose__init(surgical_interfaces__msg__InstrumentPose * msg)
{
  if (!msg) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__init(&msg->header)) {
    surgical_interfaces__msg__InstrumentPose__fini(msg);
    return false;
  }
  // class_name
  if (!rosidl_runtime_c__String__init(&msg->class_name)) {
    surgical_interfaces__msg__InstrumentPose__fini(msg);
    return false;
  }
  // pose
  if (!geometry_msgs__msg__Pose__init(&msg->pose)) {
    surgical_interfaces__msg__InstrumentPose__fini(msg);
    return false;
  }
  // confidence
  // length_m
  // grasp_offset_m
  return true;
}

void
surgical_interfaces__msg__InstrumentPose__fini(surgical_interfaces__msg__InstrumentPose * msg)
{
  if (!msg) {
    return;
  }
  // header
  std_msgs__msg__Header__fini(&msg->header);
  // class_name
  rosidl_runtime_c__String__fini(&msg->class_name);
  // pose
  geometry_msgs__msg__Pose__fini(&msg->pose);
  // confidence
  // length_m
  // grasp_offset_m
}

bool
surgical_interfaces__msg__InstrumentPose__are_equal(const surgical_interfaces__msg__InstrumentPose * lhs, const surgical_interfaces__msg__InstrumentPose * rhs)
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
  // class_name
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->class_name), &(rhs->class_name)))
  {
    return false;
  }
  // pose
  if (!geometry_msgs__msg__Pose__are_equal(
      &(lhs->pose), &(rhs->pose)))
  {
    return false;
  }
  // confidence
  if (lhs->confidence != rhs->confidence) {
    return false;
  }
  // length_m
  if (lhs->length_m != rhs->length_m) {
    return false;
  }
  // grasp_offset_m
  if (lhs->grasp_offset_m != rhs->grasp_offset_m) {
    return false;
  }
  return true;
}

bool
surgical_interfaces__msg__InstrumentPose__copy(
  const surgical_interfaces__msg__InstrumentPose * input,
  surgical_interfaces__msg__InstrumentPose * output)
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
  // class_name
  if (!rosidl_runtime_c__String__copy(
      &(input->class_name), &(output->class_name)))
  {
    return false;
  }
  // pose
  if (!geometry_msgs__msg__Pose__copy(
      &(input->pose), &(output->pose)))
  {
    return false;
  }
  // confidence
  output->confidence = input->confidence;
  // length_m
  output->length_m = input->length_m;
  // grasp_offset_m
  output->grasp_offset_m = input->grasp_offset_m;
  return true;
}

surgical_interfaces__msg__InstrumentPose *
surgical_interfaces__msg__InstrumentPose__create(void)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  surgical_interfaces__msg__InstrumentPose * msg = (surgical_interfaces__msg__InstrumentPose *)allocator.allocate(sizeof(surgical_interfaces__msg__InstrumentPose), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(surgical_interfaces__msg__InstrumentPose));
  bool success = surgical_interfaces__msg__InstrumentPose__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
surgical_interfaces__msg__InstrumentPose__destroy(surgical_interfaces__msg__InstrumentPose * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    surgical_interfaces__msg__InstrumentPose__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
surgical_interfaces__msg__InstrumentPose__Sequence__init(surgical_interfaces__msg__InstrumentPose__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  surgical_interfaces__msg__InstrumentPose * data = NULL;

  if (size) {
    data = (surgical_interfaces__msg__InstrumentPose *)allocator.zero_allocate(size, sizeof(surgical_interfaces__msg__InstrumentPose), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = surgical_interfaces__msg__InstrumentPose__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        surgical_interfaces__msg__InstrumentPose__fini(&data[i - 1]);
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
surgical_interfaces__msg__InstrumentPose__Sequence__fini(surgical_interfaces__msg__InstrumentPose__Sequence * array)
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
      surgical_interfaces__msg__InstrumentPose__fini(&array->data[i]);
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

surgical_interfaces__msg__InstrumentPose__Sequence *
surgical_interfaces__msg__InstrumentPose__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  surgical_interfaces__msg__InstrumentPose__Sequence * array = (surgical_interfaces__msg__InstrumentPose__Sequence *)allocator.allocate(sizeof(surgical_interfaces__msg__InstrumentPose__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = surgical_interfaces__msg__InstrumentPose__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
surgical_interfaces__msg__InstrumentPose__Sequence__destroy(surgical_interfaces__msg__InstrumentPose__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    surgical_interfaces__msg__InstrumentPose__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
surgical_interfaces__msg__InstrumentPose__Sequence__are_equal(const surgical_interfaces__msg__InstrumentPose__Sequence * lhs, const surgical_interfaces__msg__InstrumentPose__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!surgical_interfaces__msg__InstrumentPose__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
surgical_interfaces__msg__InstrumentPose__Sequence__copy(
  const surgical_interfaces__msg__InstrumentPose__Sequence * input,
  surgical_interfaces__msg__InstrumentPose__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(surgical_interfaces__msg__InstrumentPose);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    surgical_interfaces__msg__InstrumentPose * data =
      (surgical_interfaces__msg__InstrumentPose *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!surgical_interfaces__msg__InstrumentPose__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          surgical_interfaces__msg__InstrumentPose__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!surgical_interfaces__msg__InstrumentPose__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
