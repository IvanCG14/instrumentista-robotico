// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from surgical_interfaces:msg/InstrumentPose.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "surgical_interfaces/msg/instrument_pose.hpp"


#ifndef SURGICAL_INTERFACES__MSG__DETAIL__INSTRUMENT_POSE__BUILDER_HPP_
#define SURGICAL_INTERFACES__MSG__DETAIL__INSTRUMENT_POSE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "surgical_interfaces/msg/detail/instrument_pose__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace surgical_interfaces
{

namespace msg
{

namespace builder
{

class Init_InstrumentPose_grasp_offset_m
{
public:
  explicit Init_InstrumentPose_grasp_offset_m(::surgical_interfaces::msg::InstrumentPose & msg)
  : msg_(msg)
  {}
  ::surgical_interfaces::msg::InstrumentPose grasp_offset_m(::surgical_interfaces::msg::InstrumentPose::_grasp_offset_m_type arg)
  {
    msg_.grasp_offset_m = std::move(arg);
    return std::move(msg_);
  }

private:
  ::surgical_interfaces::msg::InstrumentPose msg_;
};

class Init_InstrumentPose_length_m
{
public:
  explicit Init_InstrumentPose_length_m(::surgical_interfaces::msg::InstrumentPose & msg)
  : msg_(msg)
  {}
  Init_InstrumentPose_grasp_offset_m length_m(::surgical_interfaces::msg::InstrumentPose::_length_m_type arg)
  {
    msg_.length_m = std::move(arg);
    return Init_InstrumentPose_grasp_offset_m(msg_);
  }

private:
  ::surgical_interfaces::msg::InstrumentPose msg_;
};

class Init_InstrumentPose_confidence
{
public:
  explicit Init_InstrumentPose_confidence(::surgical_interfaces::msg::InstrumentPose & msg)
  : msg_(msg)
  {}
  Init_InstrumentPose_length_m confidence(::surgical_interfaces::msg::InstrumentPose::_confidence_type arg)
  {
    msg_.confidence = std::move(arg);
    return Init_InstrumentPose_length_m(msg_);
  }

private:
  ::surgical_interfaces::msg::InstrumentPose msg_;
};

class Init_InstrumentPose_pose
{
public:
  explicit Init_InstrumentPose_pose(::surgical_interfaces::msg::InstrumentPose & msg)
  : msg_(msg)
  {}
  Init_InstrumentPose_confidence pose(::surgical_interfaces::msg::InstrumentPose::_pose_type arg)
  {
    msg_.pose = std::move(arg);
    return Init_InstrumentPose_confidence(msg_);
  }

private:
  ::surgical_interfaces::msg::InstrumentPose msg_;
};

class Init_InstrumentPose_class_name
{
public:
  explicit Init_InstrumentPose_class_name(::surgical_interfaces::msg::InstrumentPose & msg)
  : msg_(msg)
  {}
  Init_InstrumentPose_pose class_name(::surgical_interfaces::msg::InstrumentPose::_class_name_type arg)
  {
    msg_.class_name = std::move(arg);
    return Init_InstrumentPose_pose(msg_);
  }

private:
  ::surgical_interfaces::msg::InstrumentPose msg_;
};

class Init_InstrumentPose_header
{
public:
  Init_InstrumentPose_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_InstrumentPose_class_name header(::surgical_interfaces::msg::InstrumentPose::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_InstrumentPose_class_name(msg_);
  }

private:
  ::surgical_interfaces::msg::InstrumentPose msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::surgical_interfaces::msg::InstrumentPose>()
{
  return surgical_interfaces::msg::builder::Init_InstrumentPose_header();
}

}  // namespace surgical_interfaces

#endif  // SURGICAL_INTERFACES__MSG__DETAIL__INSTRUMENT_POSE__BUILDER_HPP_
