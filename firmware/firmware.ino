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

/*
  The IR LED used for transmission must be connected to pin 3.

  Be sure that the library IRremote is available (version 2.0.1 was used for
  development.)
*/

#include <IRremote.h>
#include "./messages.h"


// #define DEBUGPRINTS
#ifdef DEBUGPRINTS
  #define DBG(a) Serial.print(a);
  #define DBGln(a) Serial.println(a);
#else
  #define DBG(a)
  #define DBGln(a)
#endif

#define RECEIVE_PIN 4

// Setup the receive and send objects.
IRrecv irrecv(RECEIVE_PIN, LED_BUILTIN);
IRsend irsend;

// Allocate the decode result.
decode_results results_;

// Settings
uint16_t serial_receive_timeout_ = 1000;

void setup() {
  Serial.begin(9600);
  irrecv.blink13(1);  // enable led blink on receive.
  irrecv.enableIRIn();  // Start the receiver.
  Serial.setTimeout(serial_receive_timeout_);  // Set the readBytes timeout.
}


// Handle incomming commands from the serial port.
void processCommand(const msg_t* msg) {
  switch (msg->type) {
    case nop:
      DBGln("Got nop.");
      break;

    case set_config:
      DBGln("Got set_config.");
      serial_receive_timeout_ = msg->config.serial_receive_timeout;
      Serial.setTimeout(serial_receive_timeout_);
      break;

    case get_config: {
        DBGln("Got get_config.");
        char buffer[sizeof(msg_t)] = {0};
        msg_t* response = reinterpret_cast<msg_t*>(buffer);
        response->type = get_config;

        response->config.serial_receive_timeout = serial_receive_timeout_;
        Serial.write(buffer, sizeof(msg_t));
      }
      break;

    case action_IR_send: {
        DBGln("Got action_IR_send.");
        emitIRCode(msg->ir_specification.type,
                   msg->ir_specification.bits,
                   msg->ir_specification.value);
      }
      break;


    case get_status: {
        DBGln("Got get_status.");
        char buffer[sizeof(msg_t)] = {0};
        msg_t* response = reinterpret_cast<msg_t*>(buffer);
        response->type = get_status;
        response->status.uptime = millis();
        Serial.write(buffer, sizeof(msg_t));
      }
      break;

    default:
      DBGln("Got unknown command.");
  }
}

// This function takes care of sending a IR code, calling the appropriate
// function for each type.
void emitIRCode(uint8_t type, uint8_t nbits, uint32_t data) {
  DBG("type"); DBGln(type);
  DBG("nbits"); DBGln(nbits);
  DBG("data"); DBGln(data);
  switch (type) {
    #if SEND_RC5
      case RC5:
        irsend.sendRC5(data, nbits);
        break;
    #endif
    #if SEND_NEC
      case NEC:
        irsend.sendNEC(data, nbits);
        break;
    #endif
    #if SEND_SONY
      case SONY:  // Sony should be sent three times.
        irsend.sendSony(data, nbits);
        delay(40);
        irsend.sendSony(data, nbits);
        delay(40);
        irsend.sendSony(data, nbits);
        break;
    #endif
    #if SEND_SAMSUNG
      case SAMSUNG:
        irsend.sendSAMSUNG(data, nbits);
        break;
    #endif
    #if SEND_LG
      case LG:
        irsend.sendLG(data, nbits);
        break;
    #endif
      default:
        DBGln("Type unknown");
  }
  irrecv.enableIRIn();  // Re-enable the IR receiver.
}

// Send a received IR code over the serial port.
void sendReceivedIR(decode_results *results) {
  char buffer[sizeof(msg_t)] = {0};
  msg_t* response = reinterpret_cast<msg_t*>(buffer);
  response->type = action_IR_received;

  response->ir_specification.type = results->decode_type;
  response->ir_specification.bits = results->bits;
  response->ir_specification.value = results->value;

  Serial.write(buffer, sizeof(msg_t));
}

// loop; continuously read IR commands and read serial commands.
void loop() {
  // Check if we have decoded an IR code.
  if (irrecv.decode(&results_)) {
    sendReceivedIR(&results_);  // Sent it over the Serial port.
    irrecv.resume();  // Receive the next value.
  }

  // Check if we should read the serial port for commands.
  if (Serial.available()) {
    char buffer[sizeof(msg_t)] = {0};
    if (Serial.readBytes(buffer, sizeof(msg_t)) == sizeof(msg_t)) {
      // we have a command, process it.
      processCommand(reinterpret_cast<msg_t*>(buffer));
    }
  }
}
