// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from surgical_interfaces:msg/InstrumentPose.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "surgical_interfaces/msg/instrument_pose.hpp"


#ifndef SURGICAL_INTERFACES__MSG__DETAIL__INSTRUMENT_POSE__STRUCT_HPP_
#define SURGICAL_INTERFACES__MSG__DETAIL__INSTRUMENT_POSE__STRUCT_HPP_

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
// Member 'pose'
#include "geometry_msgs/msg/detail/pose__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__surgical_interfaces__msg__InstrumentPose __attribute__((deprecated))
#else
# define DEPRECATED__surgical_interfaces__msg__InstrumentPose __declspec(deprecated)
#endif

namespace surgical_interfaces
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct InstrumentPose_
{
  using Type = InstrumentPose_<ContainerAllocator>;

  explicit InstrumentPose_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_init),
    pose(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->class_name = "";
      this->confidence = 0.0f;
      this->length_m = 0.0f;
      this->grasp_offset_m = 0.0f;
    }
  }

  explicit InstrumentPose_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc, _init),
    class_name(_alloc),
    pose(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->class_name = "";
      this->confidence = 0.0f;
      this->length_m = 0.0f;
      this->grasp_offset_m = 0.0f;
    }
  }

  // field types and members
  using _header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _header_type header;
  using _class_name_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _class_name_type class_name;
  using _pose_type =
    geometry_msgs::msg::Pose_<ContainerAllocator>;
  _pose_type pose;
  using _confidence_type =
    float;
  _confidence_type confidence;
  using _length_m_type =
    float;
  _length_m_type length_m;
  using _grasp_offset_m_type =
    float;
  _grasp_offset_m_type grasp_offset_m;

  // setters for named parameter idiom
  Type & set__header(
    const std_msgs::msg::Header_<ContainerAllocator> & _arg)
  {
    this->header = _arg;
    return *this;
  }
  Type & set__class_name(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->class_name = _arg;
    return *this;
  }
  Type & set__pose(
    const geometry_msgs::msg::Pose_<ContainerAllocator> & _arg)
  {
    this->pose = _arg;
    return *this;
  }
  Type & set__confidence(
    const float & _arg)
  {
    this->confidence = _arg;
    return *this;
  }
  Type & set__length_m(
    const float & _arg)
  {
    this->length_m = _arg;
    return *this;
  }
  Type & set__grasp_offset_m(
    const float & _arg)
  {
    this->grasp_offset_m = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    surgical_interfaces::msg::InstrumentPose_<ContainerAllocator> *;
  using ConstRawPtr =
    const surgical_interfaces::msg::InstrumentPose_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<surgical_interfaces::msg::InstrumentPose_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<surgical_interfaces::msg::InstrumentPose_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      surgical_interfaces::msg::InstrumentPose_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<surgical_interfaces::msg::InstrumentPose_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      surgical_interfaces::msg::InstrumentPose_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<surgical_interfaces::msg::InstrumentPose_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<surgical_interfaces::msg::InstrumentPose_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<surgical_interfaces::msg::InstrumentPose_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__surgical_interfaces__msg__InstrumentPose
    std::shared_ptr<surgical_interfaces::msg::InstrumentPose_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__surgical_interfaces__msg__InstrumentPose
    std::shared_ptr<surgical_interfaces::msg::InstrumentPose_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const InstrumentPose_ & other) const
  {
    if (this->header != other.header) {
      return false;
    }
    if (this->class_name != other.class_name) {
      return false;
    }
    if (this->pose != other.pose) {
      return false;
    }
    if (this->confidence != other.confidence) {
      return false;
    }
    if (this->length_m != other.length_m) {
      return false;
    }
    if (this->grasp_offset_m != other.grasp_offset_m) {
      return false;
    }
    return true;
  }
  bool operator!=(const InstrumentPose_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct InstrumentPose_

// alias to use template instance with default allocator
using InstrumentPose =
  surgical_interfaces::msg::InstrumentPose_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace surgical_interfaces

#endif  // SURGICAL_INTERFACES__MSG__DETAIL__INSTRUMENT_POSE__STRUCT_HPP_
