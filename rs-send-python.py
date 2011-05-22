#!/usr/bin/python

# Script to send Python scripts to the Round solutions development board
# (Designed for use with the GSM862-GPS and RS-EB-S3 Rev 3)
#
# Idea is that you connect to the Unit through the serial port provided
# using the screen command. You then use this script to have the commands
# and your code sent to screen automatically.
# (For help with screen read this:
#     http://www.tigoe.net/pcomp/resources/archives/avr/000749.shtml )
#
#
# Copyright 2011 Dave Barker
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os, time, sys, subprocess

def load_python(screen_name, script_name):
    # Check the details for our file
    if os.path.exists(script_name):
        script_path = os.path.abspath(script_name)
        script_size = os.path.getsize(script_name)
    else:
        print("Unable to find file: '" + script_name + "'")
        exit()

    # Send the load code command
    send_to_screen(screen_name, 'AT#WSCRIPT="' + script_name + '",'
                   + str(script_size))
    # Have the file sent over
    screen_read_file(screen_name, script_path)
    # Send the enable command
    send_to_screen(screen_name, 'AT#ESCRIPT="' + script_name + '"')
    # Finaly send the reboot command
    send_to_screen(screen_name, 'AT#REBOOT')

def run_cmd(command):
    proc = subprocess.Popen(command, shell = True, executable = "/bin/bash",
                            stdout=subprocess.PIPE)
    proc.wait()

def screen_read_file(screen_name, file_path, delay=1):
    # Tell screen to read file into paste buffer
    run_cmd("screen -S " + screen_name + " -X readbuf " + file_path)
    # Have screen paste the contents
    run_cmd("screen -S " + screen_name + " -X paste .")
    # Wait for a moment (default 1 second)
    time.sleep(delay)

def send_to_screen(screen_name, message, delay=0.5):
    message = message.replace("'", "\\'") + '\r'
    run_cmd("screen -S " + screen_name + " -X stuff $'" + message + "'")
    time.sleep(delay)

if len(sys.argv) != 3:
    print sys.argv
    print "Usage: rs-send-python.py screen_name script_name"
    print "(E.G 'rs-send-python.py rs example.py')"
    print "But first start a screen connection to the device, EG: 'screen -S rs /dev/tty.usbserial 115200'."
    print "(Note script name should be in current directory, paths are not handled)"
else:
    _, screen_name, script_name = sys.argv
    load_python(screen_name, script_name)
