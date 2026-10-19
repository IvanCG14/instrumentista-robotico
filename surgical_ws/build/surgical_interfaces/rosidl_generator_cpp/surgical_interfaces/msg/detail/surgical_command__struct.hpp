// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from surgical_interfaces:msg/SurgicalCommand.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "surgical_interfaces/msg/surgical_command.hpp"


#ifndef SURGICAL_INTERFACES__MSG__DETAIL__SURGICAL_COMMAND__STRUCT_HPP_
#define SURGICAL_INTERFACES__MSG__DETAIL__SURGICAL_COMMAND__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__surgical_interfaces__msg__SurgicalCommand __attribute__((deprecated))
#else
# define DEPRECATED__surgical_interfaces__msg__SurgicalCommand __declspec(deprecated)
#endif

namespace surgical_interfaces
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct SurgicalCommand_
{
  using Type = SurgicalCommand_<ContainerAllocator>;

  explicit SurgicalCommand_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->intent = "";
      this->instrument_name = "";
      this->confidence = 0.0f;
      this->asr_confidence = 0.0f;
      this->raw_text = "";
      this->processing_time_s = 0.0f;
    }
  }

  explicit SurgicalCommand_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc, _init),
    intent(_alloc),
    instrument_name(_alloc),
    raw_text(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->intent = "";
      this->instrument_name = "";
      this->confidence = 0.0f;
      this->asr_confidence = 0.0f;
      this->raw_text = "";
      this->processing_time_s = 0.0f;
    }
  }

  // field types and members
  using _header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _header_type header;
  using _intent_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _intent_type intent;
  using _instrument_name_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _instrument_name_type instrument_name;
  using _confidence_type =
    float;
  _confidence_type confidence;
  using _asr_confidence_type =
    float;
  _asr_confidence_type asr_confidence;
  using _raw_text_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _raw_text_type raw_text;
  using _processing_time_s_type =
    float;
  _processing_time_s_type processing_time_s;

  // setters for named parameter idiom
  Type & set__header(
    const std_msgs::msg::Header_<ContainerAllocator> & _arg)
  {
    this->header = _arg;
    return *this;
  }
  Type & set__intent(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->intent = _arg;
    return *this;
  }
  Type & set__instrument_name(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->instrument_name = _arg;
    return *this;
  }
  Type & set__confidence(
    const float & _arg)
  {
    this->confidence = _arg;
    return *this;
  }
  Type & set__asr_confidence(
    const float & _arg)
  {
    this->asr_confidence = _arg;
    return *this;
  }
  Type & set__raw_text(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->raw_text = _arg;
    return *this;
  }
  Type & set__processing_time_s(
    const float & _arg)
  {
    this->processing_time_s = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    surgical_interfaces::msg::SurgicalCommand_<ContainerAllocator> *;
  using ConstRawPtr =
    const surgical_interfaces::msg::SurgicalCommand_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<surgical_interfaces::msg::SurgicalCommand_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<surgical_interfaces::msg::SurgicalCommand_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      surgical_interfaces::msg::SurgicalCommand_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<surgical_interfaces::msg::SurgicalCommand_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      surgical_interfaces::msg::SurgicalCommand_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<surgical_interfaces::msg::SurgicalCommand_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<surgical_interfaces::msg::SurgicalCommand_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<surgical_interfaces::msg::SurgicalCommand_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__surgical_interfaces__msg__SurgicalCommand
    std::shared_ptr<surgical_interfaces::msg::SurgicalCommand_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__surgical_interfaces__msg__SurgicalCommand
    std::shared_ptr<surgical_interfaces::msg::SurgicalCommand_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const SurgicalCommand_ & other) const
  {
    if (this->header != other.header) {
      return false;
    }
    if (this->intent != other.intent) {
      return false;
    }
    if (this->instrument_name != other.instrument_name) {
      return false;
    }
    if (this->confidence != other.confidence) {
      return false;
    }
    if (this->asr_confidence != other.asr_confidence) {
      return false;
    }
    if (this->raw_text != other.raw_text) {
      return false;
    }
    if (this->processing_time_s != other.processing_time_s) {
      return false;
    }
    return true;
  }
  bool operator!=(const SurgicalCommand_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct SurgicalCommand_

// alias to use template instance with default allocator
using SurgicalCommand =
  surgical_interfaces::msg::SurgicalCommand_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace surgical_interfaces

#endif  // SURGICAL_INTERFACES__MSG__DETAIL__SURGICAL_COMMAND__STRUCT_HPP_
