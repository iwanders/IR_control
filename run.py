#!/usr/bin/env python3

from ir_control import start

from ir_control.actions import shell, log, webhook, emit

"""
    Action to perform when a IR code is received. Type defines what to do.

    Every action should be a callable, it is provided with two arguments, the
    first is the interactor (the IR_control subclass) and the second is the
    name of the action for which it was invoked.

    If you use your own functions, be sure that they catch any exceptions as
    these are not handled when the function is called.

    The following actions are available by default:

        - shell: calls subprocess.Popen(*args, **kwargs) in a separate
                        thread. By default shell is set to True in kwargs.
                        example: action_shell("mpc next")

        - webhook: requests.get(*args, **kwargs) in a separate thread.
                          This requires the requests module to be available!
                          example: action_get("http://127.0.0.1:8080/next")

        - emit: This sends the IR signal by the code or name specified.
                     example: action_ir("samsung_tv_standby"),

        - log: interactor.log.log(level, *args, **kwargs), prints via
                      the logger. Examples:
                      action_log("Hi, I pressed a key!") # This prints at level
                        logging.INFO
                      action_log("Hi, I pressed a key!", level=logging.ERROR)
                        # This prints at logging.ERROR, so also visible without
                        # verbose mode.
"""
ir_actions = {
    "multi_tv_blue": shell("/home/c35pp/.local/bin/wpc next"),
    "multi_tv_yellow": shell("/home/c35pp/.local/bin/wpc prev"),
    "multi_tv_red": shell("/home/c35pp/.local/bin/wpc downvote"),
    "multi_tv_green": shell("/home/c35pp/.local/bin/wpc upvote"),

    "multi_tv_standby": emit("samsung_tv_standby"),
    "samsung_tv_volup": emit("multi_amp_volup"),
    "samsung_tv_voldown": emit("multi_amp_voldown"),

    "multi_tv_volup": webhook("http://127.0.0.1:8080/next"),
}

start()