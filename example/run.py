#!/usr/bin/env python3

import sys
sys.path.insert(0, "..")  # add the ir_control module to the path.

from ir_control import start
from ir_control.config import Configurator
from ir_control.actions import shell, log, webhook, emit

conf = Configurator()

"""
    The IR code files map IR codes to names, when receiving, several codes can
    point to the same name. Sending to a name with multiple ir codes associated
    to it sends the last one set.

    IR code format is text based:
        Example:

            # These codes were recorded from a Samsung TV bought in 2016.
            @preset samsung_tv_
            SAMSUNG 32 0xE0E040BF standby
            ...

        Explanation:
            # Denotes a comment.
            @ Is a special key value entry, only preset is used and provides
              a default preset for the entire file. This default preset can be
              overruled when the file is loaded.

            The IR codes are written one per line, values separated by space:
                protocol bitcount value name

            Protocol MUST be present in the IR_type_t enum. The name may not be
            empty or whitespace character.

    The name is used to check if an action is to be performed.
"""

conf.load_codes('custom_codes.txt', preset="multi_")
conf.load_codes('samsung_tv')

# conf.print_codes()


"""
    Every action should be a callable, it is provided with two arguments, the
    first is the interactor (the IR_control subclass) and the second is the
    name of the action for which it was invoked.

    If you use your own functions, be sure that they catch any exceptions as
    these are not handled when the function is called.

    The following actions are available by default:

        - shell: calls subprocess.Popen(*args, **kwargs) in a separate thread.
                 By default shell is set to True in kwargs.
                    example: shell("mpc next")

        - webhook: requests.get(*args, **kwargs) in a separate thread.
                   This requires the requests module to be available!
                    example: webhook("http://127.0.0.1:8080/next")

        - emit: This sends the IR signal by the code or name specified.
                     example: emit("samsung_tv_standby"),

        - log: interactor.log.log(level, *args, **kwargs), prints via
               the logger. Examples:
                    log("Hi, I pressed a key!") # This prints at level INFO
                    log("Hi, I pressed a key!", level=logging.ERROR)
               logging.ERROR is also visible without the verbose flag.
"""

conf.action("multi_tv_blue", shell("/home/c35pp/.local/bin/wpc next"))
conf.action("multi_tv_yellow", shell("/home/c35pp/.local/bin/wpc prev"))
conf.action("multi_tv_red", shell("/home/c35pp/.local/bin/wpc downvote"))
conf.action("multi_tv_green", shell("/home/c35pp/.local/bin/wpc upvote"))

conf.action("multi_tv_standby", emit("samsung_tv_standby"))
conf.action("samsung_tv_volume_up", emit("multi_amp_volup"))
conf.action("samsung_tv_volume_down", emit("multi_amp_voldown"))
conf.action("multi_tv_volume_up", webhook("http://127.0.0.1:8080/next"))

# finally, start the ir control program with this configuration, this also
# handles the argument parsing etc.
start(conf)
