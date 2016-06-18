"""
    Maps IR code names to the actual values.

    ir_mapping = {
        "tv":{
            "standby":dict(type="SAMSUNG", bits=32, value=0xAA),
            "standby_true":dict(type="SAMSUNG", bits=32, value=0xBB)
        },
        "foobar":dict(type="SAMSUNG", bits=32, value=0xEE),
    }
    Additional depth created by more dicationaries is separated by underscores:
        sending ir_name "tv_standby" will result in 0xAA.
        sending ir_name "tv_standby_true" will result in 0xBB.
        sending ir_name "foobar" will result in 0xEE.
"""
ir_mapping = {
    "samsung":{
        "tv":{
            "standby":dict(type="SAMSUNG", bits=32, value=0xE0E040BF),
            "source":dict(type="SAMSUNG", bits=32, value=0xE0E0807F),
            "key_1":dict(type="SAMSUNG", bits=32, value=0xE0E020DF),
            "key_2":dict(type="SAMSUNG", bits=32, value=0xE0E0A05F),
            "key_3":dict(type="SAMSUNG", bits=32, value=0xE0E0609F),
            "key_4":dict(type="SAMSUNG", bits=32, value=0xE0E010EF),
            "key_5":dict(type="SAMSUNG", bits=32, value=0xE0E0906F),
            "key_6":dict(type="SAMSUNG", bits=32, value=0xE0E050AF),
            "key_7":dict(type="SAMSUNG", bits=32, value=0xE0E030CF),
            "key_8":dict(type="SAMSUNG", bits=32, value=0xE0E0B04F),
            "key_9":dict(type="SAMSUNG", bits=32, value=0xE0E0708F),
            "key_0":dict(type="SAMSUNG", bits=32, value=0xE0E08877),
            "ttx":dict(type="SAMSUNG", bits=32, value=0xE0E034CB),
            "mute":dict(type="SAMSUNG", bits=32, value=0xE0E0F00F),
            "prech":dict(type="SAMSUNG", bits=32, value=0xE0E0C837),
            "chlist":dict(type="SAMSUNG", bits=32, value=0xE0E0D629),
            "red":dict(type="SAMSUNG", bits=32, value=0xE0E036C9),
            "green":dict(type="SAMSUNG", bits=32, value=0xE0E028D7),
            "yellow":dict(type="SAMSUNG", bits=32, value=0xE0E0A857),
            "blue":dict(type="SAMSUNG", bits=32, value=0xE0E06897),
            "volup":dict(type="SAMSUNG", bits=32, value=0xE0E0E01F),
            "voldown":dict(type="SAMSUNG", bits=32, value=0xE0E0D02F),
            "chanup":dict(type="SAMSUNG", bits=32, value=0xE0E048B7),
            "chandown":dict(type="SAMSUNG", bits=32, value=0xE0E008F7),
            "menu":dict(type="SAMSUNG", bits=32, value=0xE0E058A7),
            "media":dict(type="SAMSUNG", bits=32, value=0xE0E031CE),
            "guide":dict(type="SAMSUNG", bits=32, value=0xE0E0F20D),
            "tools":dict(type="SAMSUNG", bits=32, value=0xE0E0D22D),
            "info":dict(type="SAMSUNG", bits=32, value=0xE0E0F807),
            "up":dict(type="SAMSUNG", bits=32, value=0xE0E006F9),
            "right":dict(type="SAMSUNG", bits=32, value=0xE0E046B9),
            "left":dict(type="SAMSUNG", bits=32, value=0xE0E0A659),
            "down":dict(type="SAMSUNG", bits=32, value=0xE0E08679),
            "enter":dict(type="SAMSUNG", bits=32, value=0xE0E016E9),
            "return":dict(type="SAMSUNG", bits=32, value=0xE0E01AE5),
            "exit":dict(type="SAMSUNG", bits=32, value=0xE0E0B44B),
            "emanual":dict(type="SAMSUNG", bits=32, value=0xE0E0FC03),
            "picsize":dict(type="SAMSUNG", bits=32, value=0xE0E07C83),
            "subt":dict(type="SAMSUNG", bits=32, value=0xE0E0A45B),
            "stop":dict(type="SAMSUNG", bits=32, value=0xE0E0629D),
            "forward":dict(type="SAMSUNG", bits=32, value=0xE0E012ED),
            "backward":dict(type="SAMSUNG", bits=32, value=0xE0E0A25D),
            "play":dict(type="SAMSUNG", bits=32, value=0xE0E0E21D),
            "pause":dict(type="SAMSUNG", bits=32, value=0xE0E052AD),
        },
    },
    "foobar":dict(type="SAMSUNG", bits=32, value=0xE0E04F),
    "multi":{
        "tv":{
        
               "green":dict(type="NEC", bits=32, value=0x20DF8E71),
               "red":dict(type="NEC", bits=32, value=0x20DF4EB1),
               "blue":dict(type="NEC", bits=32, value=0x20DF8679),
               "yellow":dict(type="NEC", bits=32, value=0x20DFC639),
               "standby":dict(type="NEC", bits=32, value=0x20DF10EF),
            },
        "amp":{
               "volup":dict(type="SONY", bits=12, value=0x00000481),
               "voldown":dict(type="SONY", bits=12, value=0x00000C81)
        }
    }
}

"""
    Action to perform when a IR code is received. Type defines what to do.

    - type="shell":
        "ir_name":dict(type="shell", call="date > /tmp/lala")
        Results in a shell call via the following:
            subprocess.Popen(action["call"], shell=True)
    - type="geturl":
        "ir_name":dict(type="geturl", arguments=["http://127.0.0.1:3333/foo"])
        Results in:
            requests.get(*action["arguments"])
        All errors are quietly catched.

    No input verification is done; if you break it you get to keep both parts.
"""
ir_actions = {
    "multi_tv_blue":dict(type="shell", call=["/home/c35pp/.local/bin/wpc next"]),
    "multi_tv_yellow":dict(type="shell", call=["/home/c35pp/.local/bin/wpc prev"]),
    "multi_tv_red":dict(type="shell", call=["/home/c35pp/.local/bin/wpc downvote"]),
    "multi_tv_standby":dict(type="ir_send", ir_name="samsung_tv_standby"),
    "multi_tv_green":dict(type="shell", call=["/home/c35pp/.local/bin/wpc upvote"]),
    "samsung_tv_volup": dict(type="ir_send", ir_name="multi_amp_volup"),
    "samsung_tv_voldown": dict(type="ir_send", ir_name="multi_amp_voldown"),
}
