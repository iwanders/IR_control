from .message import IR, IR_type_id
import os
import sys


def perror(a):
    sys.stderr.write(a + "\n")
    sys.stderr.flush()

"""
    Maps IR codes to names, when receiving, several codes can point to the same
    name. Sending to a name with multiple ir codes associated to it sends the
    last one set.

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

    Loading the configuration is done by:
        conf = Configurator()

        # Include a file in the current directory, prefix the names:
        conf.load_codes('custom_codes.txt', preset="multi_")

        # Or load with the default prefix from the file in the module folder:
        conf.load_codes('samsung_tv')

    Adding actions is straightforward:
        conf.action("multi_tv_blue", shell("/home/c35pp/.local/bin/wpc next"))

    Registers an action for the name "multi_tv_blue", the second argument is an
    callable that is called with:  function(interactor, action_name).
"""


class Configurator():
    def __init__(self):
        self.ir_codes = {}
        self.ir_actions = {}

    def load_codes(self, path, preset=None):
        # try in the current folder.
        if (os.path.isfile(path)):
            codes, special = self._load_code_file(path)
            self._add_codes(codes, special, preset)
            return

        # try in the 'codes' folder of the module.
        module_path = os.path.abspath(os.path.dirname(__file__))
        try_path = os.path.join(module_path, "codes", path)

        # these always end with .txt
        try_path = try_path if try_path.endswith(".txt") else try_path + ".txt"

        if (os.path.isfile(try_path)):
            codes, special = self._load_code_file(try_path)
            self._add_codes(codes, special, preset)
            return
        perror("Could not find code file: {}".format(path))

    def _load_code_file(self, path):
        codes = {}
        special = {}
        with open(path, 'r') as f:
            line_num = 0
            for line in f:
                line = line.strip()
                line_num += 1

                if line.startswith("#"):  # comment, ignore it.
                    continue
                if line.startswith("@"):  # special
                    try:
                        entries = line.split(" ")
                        special[entries[0][1:]] = entries[1]
                        continue
                    except IndexError as e:
                        perror("Could not split special entry"
                               " at line {} ({})".format(line_num, path))
                try:
                    entries = line.split(" ")

                    # empty lines are acceptable
                    if (len(entries) == 1) and (len(entries[0]) == 0):
                        continue

                    proto = entries[0].upper()
                    bits = int(entries[1])

                    if entries[2].lower().startswith("0x"):
                        value = int(entries[2][2:], 16)
                    else:
                        value = int(entries[2])

                    name = entries[3]

                    if not proto.upper() in IR_type_id:
                        perror("IR proto '{}' is not known, line {} in file {}"
                               " ({})".format(proto, line_num, path, line))
                        continue
                    code = IR(type=proto, bits=bits, value=value)
                    if (code in codes) and (name != codes[code]):
                        perror("Overwriting duplicate code entry with new name"
                               ", line {} in file {} ({})".format(line_num,
                                                                  path,
                                                                  line))
                        continue

                    codes[code] = name

                except IndexError as e:
                    perror("IR entry malformatted, line {} in file {}"
                           " ({})".format(line_num, path, line))
                    continue

        return codes, special

    def _add_codes(self, codes, special, preset):
        # determine the real preset
        if (preset is None) and ("preset" in special):
            preset = special["preset"]
        elif (preset is None):
            preset = ""
        for code in codes:
            name = codes[code]
            ir_name = preset + name
            if code in self.ir_codes:
                print("Duplicate IR code, now resolves to {}".format(ir_name))
            self.ir_codes[code] = ir_name

    def print_codes(self):
        for j in self.ir_codes:
            name = self.ir_codes[j]
            print("{: <50s} -> {:}".format(str(j), name))

    def action(self, name, callable):
        self.ir_actions[name] = callable

    def get_actions(self):
        return self.ir_actions

    def get_codes(self):
        return self.ir_codes
