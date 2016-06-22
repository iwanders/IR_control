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

import socketserver
import argparse
import threading
import time
import logging

import subprocess  # for shell action
import requests  # for geturl action
import config  # loads the configuration from the config file.


class IR_Control:
    def __init__(self, interface, serial_port, baudrate):
        self.i = interface
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.log = logging.getLogger("IR_Control")

    # blocks reading from serial port and acting appropriately.
    def loop(self):
        while(True):
            if (not self.i.is_serial_connected()):
                self.log.error("No serial port!")
                self.i.connect(self.serial_port, self.baudrate)
                time.sleep(1)
            a = self.i.get_message()
            if (a):
                self.received_serial(a)
            else:
                time.sleep(0.001)

    # processes received messages from serial
    def received_serial(self, msg):
        # receives messages from the interface.
        if (msg.msg_type == msg.type.action_IR_received):
            # convert it into a ir_message
            ir_code = message.IR(**dict(msg.ir_specification))
            self.ir_received(ir_code)

    # sends a message over the serial port
    def send_serial(self, msg):
        self.i.put_message(msg)

    # send an IR code with the hardware.
    def send_ir(self, ir_code):
        self.log.debug("sending ir {}".format(ir_code))
        # create the message
        msg = message.Msg()
        msg.msg_type = msg.type.action_IR_send
        try:
            msg.ir_specification.from_dict(ir_code.raw())
        except TypeError as e:
            self.log.error("Conversion failed: {} ".format(str(e)))
        self.send_serial(msg)

    # This method is called when an IR code is received from the serial port.
    def ir_received(self, ir_code):
        raise NotImplementedError("Subclass should implement this.")


# This object actually deals with the interaction and configuration file
# it is up to you to change this to suit your needs... or use this and modify
# the configuration file.
class Interactor(IR_Control):
    def __init__(self, *args, **kwargs):
        super(Interactor, self).__init__(*args, **kwargs)
        self.load_config()
        self.log = logging.getLogger("Interactor")

    # load the config, and convert it into the code and name lookup lists.
    def load_config(self):
        by_name = {}
        by_code = {}

        # recursive function to walk over the configuration and flatten it.
        def R(d, *args):
            for j in d:
                if (type(j) != str):
                    by_name["_".join(list(args[::-1]) + [d[j]])] = j
                    by_code[j.tuple()] = "_".join(list(args[::-1]) + [d[j]])
                else:
                    R(d[j], j, *args)
        R(config.ir_codes)

        # store lookup for name -> ir_code and ir_code -> name.
        self.ir_by_name = by_name
        self.ir_by_code = by_code

        # store actions per name.
        self.ir_actions = config.ir_actions

    # called when an ir code is received from the serial port.
    def ir_received(self, ir_code):
        if (ir_code.tuple() in self.ir_by_code):
            # if it is in the list, convert to ir_name
            ir_name = self.ir_by_code[ir_code.tuple()]
            self.log.debug("IR name known: {}".format(ir_name))
            # try to perform the action:
            self.perform_action(ir_name)
        else:
            self.log.debug("IR code not known: {}".format(
                           ir_code))

    # When an IR code is received and we have a name for this, this performs
    # the action associated to that name.
    def perform_action(self, action_name):
        if (action_name not in self.ir_actions):
            return
        action = self.ir_actions[action_name]

        self.log.info("Action {}".format(action))

        # the shell action; call it non blocking catch all errors
        if (action["type"] == "shell"):
            def quietly_call(*arg):
                try:
                    subprocess.Popen(*arg, shell=True)
                except (OSError, ValueError) as e:
                    self.log.warn("Error: {}".format(str(e)))
            threading.Timer(0, quietly_call, [action["call"]]).start()

        # GET method on an url.
        if (action["type"] == "get_url"):
            def quietly_get(args):
                try:
                    res = requests.get(*args)
                except requests.exceptions.RequestException as e:
                    self.log.warn("Error: {}".format(str(e)))
            # call it in a non-blocking manner...
            threading.Timer(0, quietly_get, [action["arguments"]]).start()

        # send another IR command.
        if (action["type"] == "ir_send"):
            self.send_ir_by_name(action["ir_name"])

    # send an IR code by name.
    def send_ir_by_name(self, name):
        if name in self.ir_by_name:
            self.send_ir(self.ir_by_name[name])
        else:
            self.log.warn("Tried to send unknown {} ir code".format(name))

    # this method is called when something is passed via the TCP socket.
    def incoming_external_command(self, cmd):
        cmd = str(cmd, 'ascii')
        self.log.debug("Incoming command: {}".format(cmd))
        self.send_ir_by_name(cmd)


class TCPCommandHandler(socketserver.StreamRequestHandler):
    def handle(self):
        data = self.request.recv(1024).strip()
        self.server.mcu_manager_.incoming_external_command(data)
        self.finish()


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    def setManager(self, manager):
        self.mcu_manager_ = manager


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Control MCU at serial port.")
    parser.add_argument('--serial', '-s', help="The serial port to use.",
                        default="/dev/ttyUSB0")
    parser.add_argument('--baudrate', '-r', help="The badurate for the port.",
                        default=9600, type=int)
    parser.add_argument('--verbose', '-v', help="Print all communication.",
                        action="store_true", default=False)

    parser.add_argument('--tcpport', '-p', help="The port used for the tcp"
                        " socket.",
                        default=9999)
    parser.add_argument('--tcphost', '-b', help="The host/ip on which to bind"
                        " the tcp socket receiving the IR commands.",
                        default="127.0.0.1")

    # parse the arguments.
    args = parser.parse_args()

    # start the serial interface
    a = SerialInterface(packet_size=message.PACKET_SIZE)
    a.connect(serial_port=args.serial, baudrate=args.baudrate)
    a.start()  # start the interface

    # pretty elaborate logging...
    logger_interface = logging.getLogger("interface")
    logger_IR_control = logging.getLogger("IR_control")
    logger_interactor = logging.getLogger("Interactor")
    if (args.verbose):
        logger_interface.setLevel(logging.DEBUG)
        logger_IR_control.setLevel(logging.DEBUG)
        logger_interactor.setLevel(logging.DEBUG)
    else:
        logger_interactor.setLevel(logging.WARN)
        logger_interface.setLevel(logging.WARN)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(name)s - %(asctime)s - %(levelname)s'
                                  ' - %(message)s')
    ch.setFormatter(formatter)
    logger_interface.addHandler(ch)
    logger_IR_control.addHandler(ch)
    logger_interactor.addHandler(ch)

    # start the Interactor 'glue' object.
    m = Interactor(a, serial_port=args.serial, baudrate=args.baudrate)

    # This is only for the TCP server to facilitate sending IR codes from the
    # terminal easily.
    server = ThreadedTCPServer((args.tcphost, args.tcpport), TCPCommandHandler)
    server.setManager(m)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    # loop the IR_Control object such that the correct actions are performed
    m.loop()
