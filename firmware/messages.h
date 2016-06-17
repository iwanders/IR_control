/*
  The MIT License (MIT)

  Copyright (c) 2016 Ivor Wanders

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  SOFTWARE.
*/

#include <stdint.h>

#define MSG_LENGTH 16

enum msg_type {
  nop = 0,
  set_config = 1,
  get_config = 2,
  get_status = 3,
  action_IR_send = 4,
  action_IR_received = 5,
};

// typedef struct {
  // uint8_t unstaged;
  // uint8_t staged;
  // uint8_t hash[13];
// } msg_version_t;

typedef struct {
  uint32_t uptime;
} msg_status_t;

typedef struct {
  uint16_t serial_receive_timeout;
} msg_config_t;

typedef struct {
  uint8_t type;
  uint8_t bits;
  uint32_t value;
} msg_ir_t;

// A struct which represents a message.
typedef struct {
  msg_type type;
  union {
    msg_ir_t ir_specification;
    msg_status_t status;
    msg_config_t config;
    // msg_version_t version;
    uint8_t raw[MSG_LENGTH - sizeof(msg_type)];
  };
} msg_t;
