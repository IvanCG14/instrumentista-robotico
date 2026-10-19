// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from surgical_interfaces:msg/SurgicalCommand.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "surgical_interfaces/msg/surgical_command.hpp"


#ifndef SURGICAL_INTERFACES__MSG__DETAIL__SURGICAL_COMMAND__TRAITS_HPP_
#define SURGICAL_INTERFACES__MSG__DETAIL__SURGICAL_COMMAND__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "surgical_interfaces/msg/detail/surgical_command__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"

namespace surgical_interfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const SurgicalCommand & msg,
  std::ostream & out)
{
  out << "{";
  // member: header
  {
    out << "header: ";
    to_flow_style_yaml(msg.header, out);
    out << ", ";
  }

  // member: intent
  {
    out << "intent: ";
    rosidl_generator_traits::value_to_yaml(msg.intent, out);
    out << ", ";
  }

  // member: instrument_name
  {
    out << "instrument_name: ";
    rosidl_generator_traits::value_to_yaml(msg.instrument_name, out);
    out << ", ";
  }

  // member: confidence
  {
    out << "confidence: ";
    rosidl_generator_traits::value_to_yaml(msg.confidence, out);
    out << ", ";
  }

  // member: asr_confidence
  {
    out << "asr_confidence: ";
    rosidl_generator_traits::value_to_yaml(msg.asr_confidence, out);
    out << ", ";
  }

  // member: raw_text
  {
    out << "raw_text: ";
    rosidl_generator_traits::value_to_yaml(msg.raw_text, out);
    out << ", ";
  }

  // member: processing_time_s
  {
    out << "processing_time_s: ";
    rosidl_generator_traits::value_to_yaml(msg.processing_time_s, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const SurgicalCommand & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: header
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "header:\n";
    to_block_style_yaml(msg.header, out, indentation + 2);
  }

  // member: intent
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "intent: ";
    rosidl_generator_traits::value_to_yaml(msg.intent, out);
    out << "\n";
  }

  // member: instrument_name
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "instrument_name: ";
    rosidl_generator_traits::value_to_yaml(msg.instrument_name, out);
    out << "\n";
  }

  // member: confidence
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "confidence: ";
    rosidl_generator_traits::value_to_yaml(msg.confidence, out);
    out << "\n";
  }

  // member: asr_confidence
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "asr_confidence: ";
    rosidl_generator_traits::value_to_yaml(msg.asr_confidence, out);
    out << "\n";
  }

  // member: raw_text
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "raw_text: ";
    rosidl_generator_traits::value_to_yaml(msg.raw_text, out);
    out << "\n";
  }

  // member: processing_time_s
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "processing_time_s: ";
    rosidl_generator_traits::value_to_yaml(msg.processing_time_s, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const SurgicalCommand & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace msg

}  // namespace surgical_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use surgical_interfaces::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const surgical_interfaces::msg::SurgicalCommand & msg,
  std::ostream & out, size_t indentation = 0)
{
  surgical_interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use surgical_interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const surgical_interfaces::msg::SurgicalCommand & msg)
{
  return surgical_interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<surgical_interfaces::msg::SurgicalCommand>()
{
  return "surgical_interfaces::msg::SurgicalCommand";
}

template<>
inline const char * name<surgical_interfaces::msg::SurgicalCommand>()
{
  return "surgical_interfaces/msg/SurgicalCommand";
}

template<>
struct has_fixed_size<surgical_interfaces::msg::SurgicalCommand>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<surgical_interfaces::msg::SurgicalCommand>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<surgical_interfaces::msg::SurgicalCommand>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // SURGICAL_INTERFACES__MSG__DETAIL__SURGICAL_COMMAND__TRAITS_HPP_
