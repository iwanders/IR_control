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

from interface import SerialInterface
import message
import config

import socketserver
import argparse
import threading
import time
import logging
import subprocess  # for shell action
import requests  # for geturl action


logger = logging.getLogger("IR_Control")

class IR_Control:
    def __init__(self, interface, serial_port, baudrate):
        self.i = interface
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.process_config()

    # tries to send a IR code for the name provided
    def sendIR(self, ir_name):
        # check if it is available:
        if (ir_name in self.ir_entries):
            ir_code = self.ir_entries[ir_name]
            logger.debug("sending {}: {}".format(ir_name, ir_code))
            # create the message
            msg = message.Msg()
            msg.msg_type = msg.type.action_IR_send
            try:
                msg.ir_specification.from_dict(ir_code.raw())
            except TypeError as e:
                logger.error("Conversion went wrong: {} ".format(str(e)))
            # put the message on the queue
            self.i.put_message(msg)
        else:
            logger.error("Could not find {} to send.".format(ir_name))

    # blocks reading from serial port and acting appropriately.
    def loop(self):
        while(True):
            if (not self.i.is_serial_connected()):
                logger.error("No serial port!")
                self.i.connect(self.serial_port, self.baudrate)
                time.sleep(1)
            a = self.i.get_message()
            if (a):
                self.received_serial(a)
            else:
                time.sleep(0.001)

    # handles incomming commands from TCP or somethign else:
    def incoming_cmd(self, cmd):
        cmd = str(cmd, 'ascii')
        # at the moment we just pass this along to the sendIR command
        self.sendIR(cmd)

    def received_serial(self, msg):
        # receives messages from the interface.
        if (msg.msg_type == msg.type.action_IR_received):
            # convert it into a ir_message
            ir_msg = message.IR(**dict(msg.ir_specification))
            if (ir_msg.tuple() in self.ir_reverse):
                # if it is in the list, convert to ir_name
                ir_name = self.ir_reverse[ir_msg.tuple()]
                logger.debug("IR name known: {}".format(ir_name))
                # try to perform the action:
                self.perform_action(ir_name)
            else:
                logger.debug("IR code not known: {}".format(msg.ir_specification))

    def process_config(self):
        entries = {}

        # recursive function to walk over the configuration.
        def R(d, *args):
            for j in d:
                if (type(d[j]) == dict and ("value" in d[j])):
                    entries["_".join(list(args[::-1]) + [j])] = message.IR(**d[j])
                else:
                    R(d[j], j, *args)
        R(config.ir_mapping)

        self.ir_entries = entries
        self.ir_reverse = dict((k.tuple(), v) for v, k in
                               self.ir_entries.items())

        self.ir_actions = config.ir_actions

    def perform_action(self, action_name):
        if (action_name not in self.ir_actions):
            return
        action = self.ir_actions[action_name]

        logger.info("Action {}".format(action))

        # perform the shell action
        if (action["type"] == "shell"):
            try:
                subprocess.Popen(action["call"], shell=True)
            except Exception as e:
                logger.debug("Error: {}".format(str(e)))

        if (action["type"] == "get_url"):
            def quietly_get(args):
                try:
                    res = requests.get(*args)
                except Exception as e:
                    logger.debug("Error: {}".format(str(e)))
            # call it in a non-blocking manner...
            threading.Timer(0, quietly_get, [action["arguments"]]).start()
        if (action["type"] == "ir_send"):
             self.sendIR(action["ir_name"])

class TCPCommandHandler(socketserver.StreamRequestHandler):
    def handle(self):
        data = self.request.recv(1024).strip()
        self.server.mcu_manager_.incoming_cmd(data)
        self.finish()


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    def setManager(self, manager):
        self.mcu_manager_ = manager


if __name__ == "__main__":
    # Create a simple commandline interface.

    parser = argparse.ArgumentParser(description="Control MCU at serial port.")
    parser.add_argument('--serial', '-s', help="The serial port to use.",
                        default="/dev/ttyUSB0")
    parser.add_argument('--baudrate', '-r', help="The badurate for the port.",
                        default=9600, type=int)
    parser.add_argument('--tcpport', '-p', help="The port used for the tcp"
                        " socket.",
                        default=9999)
    parser.add_argument('--tcphost', '-b', help="The host/ip on which to bind"
                        " the tcp socket receiving the IR commands.",
                        default="127.0.0.1")
    parser.add_argument('--verbose', '-v', help="Print all communication.",
                        action="store_true", default=False)
    # parse the arguments.
    args = parser.parse_args()

    # start the serial interface
    a = SerialInterface(packet_size=message.PACKET_SIZE)
    # a.connect(serial_port=args.serial, baudrate=args.baudrate)
    a.start()  # start the interface

    interface_logger = logging.getLogger("interface")
    interface_logger.setLevel(logging.DEBUG)

    if (args.verbose):
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(name)s - %(asctime)s - %(levelname)s'
                                  ' - %(message)s')
    ch.setFormatter(formatter)
    interface_logger.addHandler(ch)
    logger.addHandler(ch)

    # start the IR_Control 'glue' object.
    m = IR_Control(a, serial_port=args.serial, baudrate=args.baudrate)

    # start the TCP server to listen for instructions.
    server = ThreadedTCPServer((args.tcphost, args.tcpport), TCPCommandHandler)
    server.setManager(m)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    # loop the IR_Control object such that the correct actions are performed
    m.loop()
