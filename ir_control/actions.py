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


import logging
import subprocess  # for shell action


# factory function to perform subprocess.popen in a separate thread.
def shell(*args, **kwargs):
    kwarguments = {'shell':True}
    kwarguments.update(kwargs)
    def tmp(interactor, action_name):
        def quietly_call():
            try:
                subprocess.Popen(*args, **kwarguments)
            except (OSError, ValueError) as e:
                interactor.log.warn("Error: {}".format(str(e)))
        threading.Timer(0, quietly_call).start()
    return tmp


# factory function to output text via the logger.
def log(*args, level=logging.INFO, **kwargs):
    def tmp(interactor, action_name):
        interactor.log.log(level, *args, **kwargs)
    return tmp


# factory function to use the requests module's get method.
def webhook(*args, **kwargs):
    try:
        import requests  # for geturl action
    except ImportError as e:
        return action_log("Could not perform GET, requests module is missing. "
                          "Ensure that it is available before using the get "
                          "action. (Request {} not performed.)".format(args),
                          level=logging.ERROR)

    def tmp(interactor, action_name):
        def quietly_get():
            try:
                res = requests.get(*args, **kwargs)
            except requests.exceptions.RequestException as e:
                interactor.log.warn("Error: {}".format(str(e)))
        # call it in a non-blocking manner...
        threading.Timer(0, quietly_get).start()
    return tmp


# factory function to send out another IR code.
def emit(name_or_code):
    def tmp(interactor, action_name):
        if (type(name_or_code) == str):
            interactor.send_ir_by_name(name_or_code)
        else:
            interactor.send_ir(name_or_code)
    return tmp

