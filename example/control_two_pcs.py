#!/usr/bin/env python3

"""
    This example shows how to use the system in a more complex manner. It
    allows toggling between controlling two devices. It also shows how to add
    codes to the configurator without an external file.

    This uses an aluminum Apple IR remote, the menu button toggles between
    controlling the PC and the RPi. When the PC is controlled alsamixer is
    used to change the volume and xdotool to control mplayer. Toggling is done
    with the menu button, after which an instance of mpd is controlled with mpc.
"""


import sys
sys.path.insert(0, "..")  # add the ir_control module to the path.

from ir_control import start
from ir_control.config import Configurator, IR
from ir_control.actions import shell, log, webhook, emit

# Create our manager class to toggle between controlling the pc and mpd.
class manager():
    actions = {
        "pc":{"up":shell("amixer -D pulse sset Master 2%+"),
            "down": shell("amixer -D pulse sset Master 2%-"),
            "left": shell("xdotool key Left"),
            "right": shell("xdotool key Right"),
            "pauseplay": shell("xdotool key space"),
            "center": shell("xdotool key o"),
            "repeat":log("No repeat action yet")
        },
        "mpd":{"repeat":log("No repeat action yet"),
            "up": shell("mpc volume +2"),
            "down": shell("mpc volume -2"),
            "center": shell("mpc volume 70"),
            "pauseplay": shell("mpc toggle"),
            "left": shell("mpc prev"),
            "right": shell("mpc next"),
        }
    }

    def __init__(self):
        self.state = "pc"

    def perform(self, action, interactor, action_name):
        # Set the repeat action to this action
        self.actions[self.state]["repeat"] = action
        # Call it.
        action(interactor, action_name)

    def toggle(self, interactor, action_name):
        print("Toggling between devices.")
        self.state = "mpd" if (self.state == "pc") else "pc"
        self.actions[self.state]["repeat"] = log("No repeat action yet")
        # just use shell("...")(None, None) to send a notification.
        shell("notify-send -t 500 {}".format(self.state))(None, None)

    def code(self, interactor, action_name):
        # Check if we know the action, if so act on it.
        if (action_name in self.actions[self.state]):
            action = self.actions[self.state][action_name]
            self.perform(action, interactor, action_name)
        else:
            print("no action to perform")


conf = Configurator()

# Register the necessary keys to the configurator.
proto = IR.IR_type_id["NEC"]
conf.add_code("center", IR(type=proto, bits=32, value=0x77E1BA14))
conf.add_code("left", IR(type=proto, bits=32, value=0x77E11014))
conf.add_code("right", IR(type=proto, bits=32, value=0x77E1E014))
conf.add_code("up", IR(type=proto, bits=32, value=0x77E1D014))
conf.add_code("down", IR(type=proto, bits=32, value=0x77E1B014))
conf.add_code("menu", IR(type=proto, bits=32, value=0x77E14014))
conf.add_code("pauseplay", IR(type=proto, bits=32, value=0x77E17A14))
conf.add_code("repeat", IR(type=proto, bits=0, value=0xFFFFFFFF))

# Create the manager instance.
m = manager()
# Provide a function to call the handling method of the manager.
f = lambda interactor, action_name: m.code(interactor, action_name)

# add actions for all events.
conf.action("up", f)
conf.action("down", f)
conf.action("left", f)
conf.action("pauseplay", f)
conf.action("right", f)
conf.action("center", f)
conf.action("repeat", f)
conf.action("menu", m.toggle)

start(conf)
