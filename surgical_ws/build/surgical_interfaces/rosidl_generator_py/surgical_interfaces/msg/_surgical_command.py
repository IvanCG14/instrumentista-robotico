# generated from rosidl_generator_py/resource/_idl.py.em
# with input from surgical_interfaces:msg/SurgicalCommand.idl
# generated code does not contain a copyright notice

# This is being done at the module level and not on the instance level to avoid looking
# for the same variable multiple times on each instance. This variable is not supposed to
# change during runtime so it makes sense to only look for it once.
from os import getenv

ros_python_check_fields = getenv('ROS_PYTHON_CHECK_FIELDS', default='')


# Import statements for member types

import builtins  # noqa: E402, I100

import math  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_SurgicalCommand(type):
    """Metaclass of message 'SurgicalCommand'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
    }

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('surgical_interfaces')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'surgical_interfaces.msg.SurgicalCommand')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__surgical_command
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__surgical_command
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__surgical_command
            cls._TYPE_SUPPORT = module.type_support_msg__msg__surgical_command
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__surgical_command

            from std_msgs.msg import Header
            if Header.__class__._TYPE_SUPPORT is None:
                Header.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class SurgicalCommand(metaclass=Metaclass_SurgicalCommand):
    """Message class 'SurgicalCommand'."""

    __slots__ = [
        '_header',
        '_intent',
        '_instrument_name',
        '_confidence',
        '_asr_confidence',
        '_raw_text',
        '_processing_time_s',
        '_check_fields',
    ]

    _fields_and_field_types = {
        'header': 'std_msgs/Header',
        'intent': 'string',
        'instrument_name': 'string',
        'confidence': 'float',
        'asr_confidence': 'float',
        'raw_text': 'string',
        'processing_time_s': 'float',
    }

    # This attribute is used to store an rosidl_parser.definition variable
    # related to the data type of each of the components the message.
    SLOT_TYPES = (
        rosidl_parser.definition.NamespacedType(['std_msgs', 'msg'], 'Header'),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        if 'check_fields' in kwargs:
            self._check_fields = kwargs['check_fields']
        else:
            self._check_fields = ros_python_check_fields == '1'
        if self._check_fields:
            assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
                'Invalid arguments passed to constructor: %s' % \
                ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        from std_msgs.msg import Header
        self.header = kwargs.get('header', Header())
        self.intent = kwargs.get('intent', str())
        self.instrument_name = kwargs.get('instrument_name', str())
        self.confidence = kwargs.get('confidence', float())
        self.asr_confidence = kwargs.get('asr_confidence', float())
        self.raw_text = kwargs.get('raw_text', str())
        self.processing_time_s = kwargs.get('processing_time_s', float())

    def __repr__(self):
        typename = self.__class__.__module__.split('.')
        typename.pop()
        typename.append(self.__class__.__name__)
        args = []
        for s, t in zip(self.get_fields_and_field_types().keys(), self.SLOT_TYPES):
            field = getattr(self, s)
            fieldstr = repr(field)
            # We use Python array type for fields that can be directly stored
            # in them, and "normal" sequences for everything else.  If it is
            # a type that we store in an array, strip off the 'array' portion.
            if (
                isinstance(t, rosidl_parser.definition.AbstractSequence) and
                isinstance(t.value_type, rosidl_parser.definition.BasicType) and
                t.value_type.typename in ['float', 'double', 'int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'int64', 'uint64']
            ):
                if len(field) == 0:
                    fieldstr = '[]'
                else:
                    if self._check_fields:
                        assert fieldstr.startswith('array(')
                    prefix = "array('X', "
                    suffix = ')'
                    fieldstr = fieldstr[len(prefix):-len(suffix)]
            args.append(s + '=' + fieldstr)
        return '%s(%s)' % ('.'.join(typename), ', '.join(args))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.header != other.header:
            return False
        if self.intent != other.intent:
            return False
        if self.instrument_name != other.instrument_name:
            return False
        if self.confidence != other.confidence:
            return False
        if self.asr_confidence != other.asr_confidence:
            return False
        if self.raw_text != other.raw_text:
            return False
        if self.processing_time_s != other.processing_time_s:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def header(self):
        """Message field 'header'."""
        return self._header

    @header.setter
    def header(self, value):
        if self._check_fields:
            from std_msgs.msg import Header
            assert \
                isinstance(value, Header), \
                "The 'header' field must be a sub message of type 'Header'"
        self._header = value

    @builtins.property
    def intent(self):
        """Message field 'intent'."""
        return self._intent

    @intent.setter
    def intent(self, value):
        if self._check_fields:
            assert \
                isinstance(value, str), \
                "The 'intent' field must be of type 'str'"
        self._intent = value

    @builtins.property
    def instrument_name(self):
        """Message field 'instrument_name'."""
        return self._instrument_name

    @instrument_name.setter
    def instrument_name(self, value):
        if self._check_fields:
            assert \
                isinstance(value, str), \
                "The 'instrument_name' field must be of type 'str'"
        self._instrument_name = value

    @builtins.property
    def confidence(self):
        """Message field 'confidence'."""
        return self._confidence

    @confidence.setter
    def confidence(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'confidence' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'confidence' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._confidence = value

    @builtins.property
    def asr_confidence(self):
        """Message field 'asr_confidence'."""
        return self._asr_confidence

    @asr_confidence.setter
    def asr_confidence(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'asr_confidence' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'asr_confidence' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._asr_confidence = value

    @builtins.property
    def raw_text(self):
        """Message field 'raw_text'."""
        return self._raw_text

    @raw_text.setter
    def raw_text(self, value):
        if self._check_fields:
            assert \
                isinstance(value, str), \
                "The 'raw_text' field must be of type 'str'"
        self._raw_text = value

    @builtins.property
    def processing_time_s(self):
        """Message field 'processing_time_s'."""
        return self._processing_time_s

    @processing_time_s.setter
    def processing_time_s(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'processing_time_s' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'processing_time_s' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._processing_time_s = value
