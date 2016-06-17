SHELL := /bin/bash

# The name of your project (used to name the compiled .hex file)
TARGET = firmware

# Path to your arduino installation
ARDUINOPATH ?= ../../arduino-1.6.9
ARDUINOEXEC ?= $(ARDUINOPATH)/arduino

BOARD = arduino:avr:uno
# BOARD = arduino:sam:arduino_due_x # for DUE

PORT = /dev/ttyUSB0

EXTRAFLAGS = --verbose-build

all:
	$(ARDUINOEXEC) $(EXTRAFLAGS) --board $(BOARD) --port $(PORT) --upload $(TARGET).ino

clean:
	rm -f *.o *.d $(TARGET).elf $(TARGET).hex

libs:
	$(ARDUINOEXEC) --install-library IRremote:2.0.1
