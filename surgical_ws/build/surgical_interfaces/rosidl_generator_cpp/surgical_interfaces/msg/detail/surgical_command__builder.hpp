// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from surgical_interfaces:msg/SurgicalCommand.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "surgical_interfaces/msg/surgical_command.hpp"


#ifndef SURGICAL_INTERFACES__MSG__DETAIL__SURGICAL_COMMAND__BUILDER_HPP_
#define SURGICAL_INTERFACES__MSG__DETAIL__SURGICAL_COMMAND__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "surgical_interfaces/msg/detail/surgical_command__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace surgical_interfaces
{

namespace msg
{

namespace builder
{

class Init_SurgicalCommand_processing_time_s
{
public:
  explicit Init_SurgicalCommand_processing_time_s(::surgical_interfaces::msg::SurgicalCommand & msg)
  : msg_(msg)
  {}
  ::surgical_interfaces::msg::SurgicalCommand processing_time_s(::surgical_interfaces::msg::SurgicalCommand::_processing_time_s_type arg)
  {
    msg_.processing_time_s = std::move(arg);
    return std::move(msg_);
  }

private:
  ::surgical_interfaces::msg::SurgicalCommand msg_;
};

class Init_SurgicalCommand_raw_text
{
public:
  explicit Init_SurgicalCommand_raw_text(::surgical_interfaces::msg::SurgicalCommand & msg)
  : msg_(msg)
  {}
  Init_SurgicalCommand_processing_time_s raw_text(::surgical_interfaces::msg::SurgicalCommand::_raw_text_type arg)
  {
    msg_.raw_text = std::move(arg);
    return Init_SurgicalCommand_processing_time_s(msg_);
  }

private:
  ::surgical_interfaces::msg::SurgicalCommand msg_;
};

class Init_SurgicalCommand_asr_confidence
{
public:
  explicit Init_SurgicalCommand_asr_confidence(::surgical_interfaces::msg::SurgicalCommand & msg)
  : msg_(msg)
  {}
  Init_SurgicalCommand_raw_text asr_confidence(::surgical_interfaces::msg::SurgicalCommand::_asr_confidence_type arg)
  {
    msg_.asr_confidence = std::move(arg);
    return Init_SurgicalCommand_raw_text(msg_);
  }

private:
  ::surgical_interfaces::msg::SurgicalCommand msg_;
};

class Init_SurgicalCommand_confidence
{
public:
  explicit Init_SurgicalCommand_confidence(::surgical_interfaces::msg::SurgicalCommand & msg)
  : msg_(msg)
  {}
  Init_SurgicalCommand_asr_confidence confidence(::surgical_interfaces::msg::SurgicalCommand::_confidence_type arg)
  {
    msg_.confidence = std::move(arg);
    return Init_SurgicalCommand_asr_confidence(msg_);
  }

private:
  ::surgical_interfaces::msg::SurgicalCommand msg_;
};

class Init_SurgicalCommand_instrument_name
{
public:
  explicit Init_SurgicalCommand_instrument_name(::surgical_interfaces::msg::SurgicalCommand & msg)
  : msg_(msg)
  {}
  Init_SurgicalCommand_confidence instrument_name(::surgical_interfaces::msg::SurgicalCommand::_instrument_name_type arg)
  {
    msg_.instrument_name = std::move(arg);
    return Init_SurgicalCommand_confidence(msg_);
  }

private:
  ::surgical_interfaces::msg::SurgicalCommand msg_;
};

class Init_SurgicalCommand_intent
{
public:
  explicit Init_SurgicalCommand_intent(::surgical_interfaces::msg::SurgicalCommand & msg)
  : msg_(msg)
  {}
  Init_SurgicalCommand_instrument_name intent(::surgical_interfaces::msg::SurgicalCommand::_intent_type arg)
  {
    msg_.intent = std::move(arg);
    return Init_SurgicalCommand_instrument_name(msg_);
  }

private:
  ::surgical_interfaces::msg::SurgicalCommand msg_;
};

class Init_SurgicalCommand_header
{
public:
  Init_SurgicalCommand_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_SurgicalCommand_intent header(::surgical_interfaces::msg::SurgicalCommand::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_SurgicalCommand_intent(msg_);
  }

private:
  ::surgical_interfaces::msg::SurgicalCommand msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::surgical_interfaces::msg::SurgicalCommand>()
{
  return surgical_interfaces::msg::builder::Init_SurgicalCommand_header();
}

}  // namespace surgical_interfaces

#endif  // SURGICAL_INTERFACES__MSG__DETAIL__SURGICAL_COMMAND__BUILDER_HPP_
