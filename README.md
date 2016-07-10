# IR_Control
This project is meant as a replacement for [lirc][lirc]. Its goal is to provide
a less cumbersome way to add IR codes and actions. It does so by using a
microcontroller to decode the IR signals, a Python process is running on the
computer to act on the received signals.

## Outline
The IR transmission and receipt is done with external hardware and a
microcontroller, such as an Arduino.

If an IR code is received, this is relayed to the PC over the serial port and it
is resolved to an `ir_name`. If it is unknown, and the program runs in verbose
mode any code that is unknown is printed in the output for easy copy-pasting
into the IR code files. Multiple different IR codes can resolve to the same
`ir_name`. If an `ir_name` is to be transmitted, the last IR code associated to
that name is sent.

Actions can be associated to an `ir_name`, actions should be a callable
[Python][python] function. The IR code files use a straightforward text-based
format which allows for easy additions.

The program itself is intended to be run from the commandline and is tested on
Debian 7.9 (Wheezy) and Ubuntu Mate 14.04 (Trusty). Please see the
[example/run.py][example] file as a starting point, this script can be modified
to suit your liking and then run it, or call it with `--help` to see the
available options.


## Hardware
As said, an external microcontroller (MCU) is used to decode the received
infra-red signals. The [IRRemote][IRRemote] library is used, this library has
support for plenty of protocols and is capable of both receiving and
transmitting the signals. I used an Arduino UNO-like board and will refer to the
pinout of that throughout this paragraph, it uses an [Atmega328p][atmega328p].

To be able to receive IR signals a receiver needs to be connected to the MCU. I
used the TSOP1238 for this, the Vs and GND pins are connected to the 5V and GND
respectively. The OUT pin should be connected to any digital pin, I used pin 4.

For transmitting IR signals, a IR LED should be attached from pin 3 to the GND.
Using a current limiting resistor is recommended, but you could also use a
transistor to toggle the LED.

There are plenty of guides available that explan how to connect an IR receiver
and LED in case you run into trouble. One tip, if you use the ICSP header on the
right side of the board for the GND and 5V pins you can create a nice, compact
PCB 'shield' to connect the components to the Arduino.

## Firmware
In the `firmware` folder the Arduino sketch / code can be found. The behaviour
of the MCU is quite simple; at boot it configures the [IRRemote][IRRemote]
library with the right pins. Then it it enters a loop which continuously checks
if an IR signal was received, or data was received over the serial port.

If an IR signal was received, this signal is sent to the PC via the serial port.
Three parameters define the signal, the `type` (protocol), `bits` and `value`.
The `bits` field determines how many bits of the `value` should be taken into
account. These three values are all placed in a message and sent to the PC.

In case communication from the PC is received, the MCU processes the message
and acts according to which command was received. The most relevant command is
`action_IR_send`, which interprets the `type`, `bits` and `value` fields from
the message and emits an IR signal to that specification.

## Software
At the PC side, a [Python 3][python] process is used to communicate to the MCU
over the serial port and perform actions. The code is composed of several parts,
which will be detailed in the next paragraphs.

The communication with the serial port is performed by the
[`SerialInterface`][interfacepy] class, it uses two queues and a separate thread
to ensure that only one thread communicates with the serial port.

The communication over the serial port itself is interpreted according to the
messages defined in the [`message.py`][messagepy] file, this is the counterpart
of the `messages.h` file from the firmware, but also holds some convenience
functions for defining and IR signal.

The [`IR_Control`][initpy] class provides the most basic functionality to deal
with the messages received from the `SerialInterface`, it is subclassed by the
[`Interactor`][initpy] which actually performs the main functionality, such as
checking if we should act on a received IR signal.

The [`Configurator`][configpy] class deals with the parsing of the IR code files
and resolving the paths to these, as it looks in both the current directory as
well as the `ir_control` module itself.

Any action should be a callable, default actions are defined in
[`actions.py`][actionspy], if you create your own, be sure to remember that they
should be non-blocking and catch any errors they can produce themselves.

The following actions are available by default:

- shell: calls `subprocess.Popen(*args, **kwargs)` in a separate thread. By
            default shell is set to True in kwargs.
            Example: `shell("mpc next")`.

- webhook: requests.get(*args, **kwargs) in a separate thread. This requires the
            requests module to be available! Example:
            `webhook("http://127.0.0.1:8080/next")`.

- emit: This sends the IR signal by the code or name specified. Example:
        `emit("samsung_tv_standby")`.

- log: `interactor.log.log(level, *args, **kwargs)`, prints via the logger.
        Examples:
            `log("Hi, I pressed a key!")`, this prints at level INFO,
            `log("Hi, I pressed a key!", level=logging.ERROR)` logging.ERROR is
            also visible without the verbose flag.

## IR Codes

The IR code file format is text based and basically requires just four fields
per IR code. Theses are "`type` `bits` `value` `ir_name`", every line should
hold one IR code. The `ir_name` fields can be prefixed by a prefix, this string
will be added in front of every in this file to form the final `ir_name`.

An example:

    # These codes were recorded from a remote for a Samsung TV bought in 2016.
    @prefix samsung_tv_
    SAMSUNG 32 0xE0E040BF standby
    SAMSUNG 32 0xE0E0807F source
    SAMSUNG 32 0xE0E020DF key_1
    SAMSUNG 32 0xE0E0A05F key_2
            ...

- \# Denotes a comment.
- @ Is a special key value entry, only preset is used and provides a default
    prefix for the entire file. This default prefix can be overruled when the
    file is loaded.

The type must be present in the IR_type_t enum. The name may not be empty or
whitespace character.

The `load_codes` method of the `Configurator` looks in the current path as well
as in the module's [directory][ircodesdir] for IR code files.

## License

MIT License, see [LICENSE.md](LICENSE.md).

Copyright (c) 2016 Ivor Wanders

[lirc]: http://www.lirc.org/
[IRRemote]: https://github.com/z3t0/Arduino-IRremote/
[atmega328p]: http://www.atmel.com/devices/atmega328p.aspx
[python]: https://www.python.org/
[actionspy]: ir_control/actions.py
[messagepy]: ir_control/message.py
[configpy]: ir_control/config.py
[interfacepy]: ir_control/interface.py
[initpy]: ir_control/__init__.py
[example]: example/run.py
[ircodesdir]: ir_control/codes/