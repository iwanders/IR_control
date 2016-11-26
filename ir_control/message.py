#!/usr/bin/env python3

# The MIT License (MIT)
#
# Copyright (c) 2016 Ivor Wanders
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import ctypes
from collections import namedtuple

# packet length to be used for all communication.
PACKET_SIZE = 16

#############################################################################
# Message type enum
#############################################################################
# enum-like construction of msg_type_t
msg_type_t = namedtuple("msg_type", ["nop",
                                     "set_config",
                                     "get_config",
                                     "get_status",
                                     "action_IR_send",
                                     "action_IR_received"])
# can do msg_type.nop or msg_type.get_config now.
msg_type = msg_type_t(*range(0, len(msg_type_t._fields)))

# Depending on the message type, we interpret the payload as to be this field:
msg_type_field = {
          msg_type_t._fields.index("set_config"): "config",
          msg_type_t._fields.index("get_config"): "config",
          msg_type_t._fields.index("action_IR_send"): "ir_specification",
          msg_type_t._fields.index("action_IR_received"): "ir_specification",
          msg_type_t._fields.index("get_status"): "status",
        }

# Reverse lookup for msg type, that is id->name
msg_type_name = dict(enumerate(msg_type_t._fields))

# Reverse lookup for msg type, that is name->id
msg_type_id = dict((k, v) for v, k in enumerate(msg_type_t._fields))


#############################################################################
# IR specific data types
#############################################################################
# this is the enum from the library:
IR_type_t = namedtuple("IR_type", ["UNKNOWN",
                                   "UNUSED",
                                   "RC5",
                                   "RC6",
                                   "NEC",
                                   "SONY",
                                   "PANASONIC",
                                   "JVC",
                                   "SAMSUNG",
                                   "WHYNTER",
                                   "AIWA_RC_T501",
                                   "LG",
                                   "SANYO",
                                   "MITSUBISHI",
                                   "DISH",
                                   "SHARP",
                                   "DENON",
                                   "PRONTO"])
# can do IR_type.PANASONIC or IR_type.SAMSUNG now.
IR_type = IR_type_t(*([2**16-1] + list(range(0, len(IR_type_t._fields)-1))))
# Reverse lookup for IR type, that is id->name
IR_type_name = dict((v[1], v[0]) for v in IR_type._asdict().items())
# Reverse lookup for IR type, that is name->id
IR_type_id = dict((v[0], v[1]) for v in IR_type._asdict().items())

# create an IR type for easy definition of IR codes
IR = namedtuple("IR", ["type", "bits", "value"])


# add these methods for convenience.
def mapping_to_raw(self):
    return {"type": IR_type_id.get(self.type, self.type),  # get type as int.
            "bits": self.bits,
            "value": self.value}


def ir_print(self):
    return 'IR(type={}, bits={}, value=0x{:0>8X})'.format(
        repr(IR_type_name.get(self.type, self.type)), self.bits, self.value)


def config_print(self):
    return '{} {} 0x{:0>8X}'.format(IR_type_name.get(self.type, self.type),
                                    self.bits, self.value)


def to_tuple(self):
    return (IR_type_id.get(self.type, self.type), self.bits, self.value)

IR.raw = mapping_to_raw
IR.tuple = to_tuple
IR.config_print = config_print
IR.__str__ = ir_print
IR.IR_type = IR_type
IR.IR_type_name = IR_type_name
IR.IR_type_id = IR_type_id


#############################################################################
# Mixins & structures
#############################################################################
# Convenience mixin to allow construction of struct from a byte like object.
class Readable:
    @classmethod
    def read(cls, byte_object):
        a = cls()
        ctypes.memmove(ctypes.addressof(a), bytes(byte_object),
                       min(len(byte_object), ctypes.sizeof(cls)))
        return a


# Mixin to allow conversion of a ctypes structure to and from a dictionary.
class Dictionary:
    # Implement the iterator method such that dict(...) results in the correct
    # dictionary.
    def __iter__(self):
        for k, t in self._fields_:
            if (issubclass(t, ctypes.Structure)):
                yield (k, dict(getattr(self, k)))
            else:
                yield (k, getattr(self, k))

    # Implement the reverse method, with some special handling for dict's and
    # lists.
    def from_dict(self, dict_object):
        for k, t in self._fields_:
            set_value = dict_object[k]
            if (isinstance(set_value, dict)):
                v = t()
                v.from_dict(set_value)
                setattr(self, k, v)
            elif (isinstance(set_value, list)):
                v = getattr(self, k)
                for j in range(0, len(set_value)):
                    v[j] = set_value[j]
                setattr(self, k, v)
            else:
                setattr(self, k, set_value)

    def __str__(self):
        return str(dict(self))


#############################################################################
# Structs for the various parts in the firmware. These correspond to
# the structures as defined in the header files.
class MsgStatus(ctypes.LittleEndianStructure, Dictionary):
    _pack_ = 1
    _fields_ = [("uptime", ctypes.c_uint32)]


class MsgConfig(ctypes.LittleEndianStructure, Dictionary):
    _pack_ = 1
    _fields_ = [("serial_receive_timeout", ctypes.c_uint16)]


class MsgIRSpecification(ctypes.LittleEndianStructure, Dictionary):
    _pack_ = 1
    _fields_ = [("type", ctypes.c_uint8),
                ("bits", ctypes.c_uint8),
                ("value", ctypes.c_uint32)]

    def __str__(self):
        irtype = IR_type_name[self.type] if self.type in IR_type_name\
                    else self.type

        return 'dict(type="{}", bits={}, value=0x{:0>8X}) '.format(
                    irtype,
                    self.bits, self.value)


# create the composite message.
class _MsgBody(ctypes.Union):
    _fields_ = [("config", MsgConfig),
                ("status", MsgStatus),
                ("ir_specification", MsgIRSpecification),
                ("raw", ctypes.c_byte * (PACKET_SIZE-2))]

#############################################################################


# Class which represents all messages. That is; it holds all the structs.
class Msg(ctypes.LittleEndianStructure, Readable):
    type = msg_type
    _pack_ = 1
    _fields_ = [("msg_type", ctypes.c_uint16),
                ("_body", _MsgBody)]
    _anonymous_ = ["_body"]

    # Pretty print the message according to its type.
    def __str__(self):
        if (self.msg_type in msg_type_field):
            payload_text = str(getattr(self, msg_type_field[self.msg_type]))
            message_field = msg_type_name[self.msg_type]
        else:
            message_field = msg_type_name[self.msg_type]
            payload_text = "-"
        return "<Msg {}: {}>".format(message_field, payload_text)

    # We have to treat the mixin slightly different here, since we there is
    # special handling for the message type and thus the body.
    def __iter__(self):
        for k, t in self._fields_:
            if (k == "_body"):
                if (self.msg_type in msg_type_field):
                    message_field = msg_type_field[self.msg_type]
                    body = dict(getattr(self, msg_type_field[self.msg_type]))
                else:
                    message_field = "raw"
                    body = [a for a in getattr(self, message_field)]
                yield (message_field, body)
            elif (issubclass(t, ctypes.Structure)):
                yield (k, dict(getattr(self, k)))
            else:
                yield (k, getattr(self, k))

    def from_dict(self, dict_object):
        # Walk through the dictionary, as we do not know which elements from
        # the struct we would need.
        for k, set_value in dict_object.items():
            if (isinstance(set_value, dict)):
                v = getattr(self, k)
                v.from_dict(set_value)
                setattr(self, k, v)
            elif (isinstance(set_value, list)):
                v = getattr(self, k)
                for j in range(0, len(set_value)):
                    v[j] = set_value[j]
                setattr(self, k, v)
            else:
                setattr(self, k, set_value)

if __name__ == "__main__":
    print("Msg: {}".format(ctypes.sizeof(Msg)))
    print("MsgIRSpecification: {}".format(ctypes.sizeof(MsgIRSpecification)))

    msg = Msg()
    msg.msg_type = msg.type.action_IR_received
    msg.ir_specification.type = 0x1F
    msg.ir_specification.bits = 0x2F
    msg.ir_specification.value = 0x01020304
    print(bytes(msg))

    a = IR(type="SAMSUNG", bits=32, value=0xE0E040BF)
    print(a)
    print(str(a))
    print(a.raw())
    atuple = a.tuple()
    print(atuple)
    print(IR(*atuple))
