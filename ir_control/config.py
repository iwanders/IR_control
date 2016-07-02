from .message import IR
# from .__init__ import action_shell, action_get, action_ir, action_log
"""
    Maps IR codes to names, when receiving, several codes can point to the same
    name. Sending to a name with multiple ir codes associated to it sends one
    ir code only, which one is not really defined.


    ir_codes = {
        "tv":{
            IR(type="SAMSUNG", bits=32, value=0xAA): "standby"
            IR(type="SAMSUNG", bits=32, value=0xDD): "standby"
            IR(type="SAMSUNG", bits=32, value=0xBB): "standby_true"
        },
        IR(type="SAMSUNG", bits=32, value=0xEE): "foobar",
    }
    Additional depth created by more dicationaries is separated by underscores:
        sending ir_name "tv_standby" is not defined.
        sending ir_name "tv_standby_true" will result in 0xBB.
        sending ir_name "foobar" will result in 0xEE.
    Both IR(type="SAMSUNG", bits=32, value=0xAA) and
         IR(type="SAMSUNG", bits=32, value=0xDD) will result in "tv_standby".
"""
ir_codes = {
    "samsung": {
        "tv": {
            IR(type="SAMSUNG", bits=32, value=0xE0E040BF): "standby",
            IR(type="SAMSUNG", bits=32, value=0xE0E0807F): "source",
            IR(type="SAMSUNG", bits=32, value=0xE0E020DF): "key_1",
            IR(type="SAMSUNG", bits=32, value=0xE0E0A05F): "key_2",
            IR(type="SAMSUNG", bits=32, value=0xE0E0609F): "key_3",
            IR(type="SAMSUNG", bits=32, value=0xE0E010EF): "key_4",
            IR(type="SAMSUNG", bits=32, value=0xE0E0906F): "key_5",
            IR(type="SAMSUNG", bits=32, value=0xE0E050AF): "key_6",
            IR(type="SAMSUNG", bits=32, value=0xE0E030CF): "key_7",
            IR(type="SAMSUNG", bits=32, value=0xE0E0B04F): "key_8",
            IR(type="SAMSUNG", bits=32, value=0xE0E0708F): "key_9",
            IR(type="SAMSUNG", bits=32, value=0xE0E08877): "key_0",
            IR(type="SAMSUNG", bits=32, value=0xE0E034CB): "ttx",
            IR(type="SAMSUNG", bits=32, value=0xE0E0F00F): "mute",
            IR(type="SAMSUNG", bits=32, value=0xE0E0C837): "prech",
            IR(type="SAMSUNG", bits=32, value=0xE0E0D629): "chlist",
            IR(type="SAMSUNG", bits=32, value=0xE0E036C9): "red",
            IR(type="SAMSUNG", bits=32, value=0xE0E028D7): "green",
            IR(type="SAMSUNG", bits=32, value=0xE0E0A857): "yellow",
            IR(type="SAMSUNG", bits=32, value=0xE0E06897): "blue",
            IR(type="SAMSUNG", bits=32, value=0xE0E0E01F): "volup",
            IR(type="SAMSUNG", bits=32, value=0xE0E0D02F): "voldown",
            IR(type="SAMSUNG", bits=32, value=0xE0E048B7): "chanup",
            IR(type="SAMSUNG", bits=32, value=0xE0E008F7): "chandown",
            IR(type="SAMSUNG", bits=32, value=0xE0E058A7): "menu",
            IR(type="SAMSUNG", bits=32, value=0xE0E031CE): "media",
            IR(type="SAMSUNG", bits=32, value=0xE0E0F20D): "guide",
            IR(type="SAMSUNG", bits=32, value=0xE0E0D22D): "tools",
            IR(type="SAMSUNG", bits=32, value=0xE0E0F807): "info",
            IR(type="SAMSUNG", bits=32, value=0xE0E006F9): "up",
            IR(type="SAMSUNG", bits=32, value=0xE0E046B9): "right",
            IR(type="SAMSUNG", bits=32, value=0xE0E0A659): "left",
            IR(type="SAMSUNG", bits=32, value=0xE0E08679): "down",
            IR(type="SAMSUNG", bits=32, value=0xE0E016E9): "enter",
            IR(type="SAMSUNG", bits=32, value=0xE0E01AE5): "return",
            IR(type="SAMSUNG", bits=32, value=0xE0E0B44B): "exit",
            IR(type="SAMSUNG", bits=32, value=0xE0E0FC03): "emanual",
            IR(type="SAMSUNG", bits=32, value=0xE0E07C83): "picsize",
            IR(type="SAMSUNG", bits=32, value=0xE0E0A45B): "subt",
            IR(type="SAMSUNG", bits=32, value=0xE0E0629D): "stop",
            IR(type="SAMSUNG", bits=32, value=0xE0E012ED): "forward",
            IR(type="SAMSUNG", bits=32, value=0xE0E0A25D): "backward",
            IR(type="SAMSUNG", bits=32, value=0xE0E0E21D): "play",
            IR(type="SAMSUNG", bits=32, value=0xE0E052AD): "pause",
        },
    },
    IR(type="SAMSUNG", bits=32, value=0xE0E04F): "foobar",
    "multi": {
        "tv": {
               IR(type="NEC", bits=32, value=0x20DF8E71): "green",
               IR(type="NEC", bits=32, value=0x20DF4EB1): "red",
               IR(type="NEC", bits=32, value=0x20DF8679): "blue",
               IR(type="NEC", bits=32, value=0x20DFC639): "yellow",
               IR(type="NEC", bits=32, value=0x20DF10EF): "standby",
               IR(type='NEC', bits=32, value=0x20DF40BF): "volup",
            },
        "amp": {
               IR(type="SONY", bits=12, value=0x00000481): "volup",
               IR(type="SONY", bits=12, value=0x00000C81): "voldown"
        }
    }
}

