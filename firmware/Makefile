# Always use bash.
SHELL := /bin/bash

# The name of your project (the .ino file / folder name)
TARGET = firmware

# Path to your arduino installation
ARDUINOPATH ?= ../../arduino-1.6.9

# which board to target
# arduino:avr:uno for normal UNO.
# arduino:sam:arduino_due_x for Arduino DUE
BOARD = arduino:avr:uno

# Use PORT environment variable if it exists, otherwise use this.
PORT ?= /dev/ttyUSB0

# Additional flags to pass to the build & upload.
EXTRAFLAGS = --verbose-build

# Create path to the arduino executable.
ARDUINOEXEC = $(ARDUINOPATH)/arduino

all:
	$(ARDUINOEXEC) $(EXTRAFLAGS) --board $(BOARD) --port $(PORT) --upload $(TARGET).ino

clean:
	rm -f *.o *.d $(TARGET).elf $(TARGET).hex

libs:
	$(ARDUINOEXEC) --install-library IRremote:2.0.1
