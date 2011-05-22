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
# For more details view my blog post:
#   http://kzar.co.uk/blog/view/embedded-development-setup-with-macbook
#
# I've had to add another layer of complexity as the Telit unit can't handle
# files over about 7 or 8k with the AT#WSCRIPT command. To work around this
# the script chunks the file and adds a delay after each part is sent.
# (What's more I noticed that using DSCRIPT without quotes is more reliable and
#  AT+FLO=0 helps when sending larger files!)
#
# To save (a lot) of time I've added the ability to compile .pyo files
# before the script is transmited. Install TelitPy1.5.2+_v4.1.exe using
# Wine and provide the path as an argument. (See usage notes.)
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

import os, time, sys, subprocess, shutil

TEMP_STORE = "/tmp/rs-send-python"
CHUNK_LIMIT = 7000

def load_python(screen_name, script_name, run=True, telit_python_path=False):
    # Check the extension of our file
    if not script_name.endswith('.py'):
        print("Script filename should end with .py")
        exit()

    # Check the details for our file
    if os.path.exists(script_name):
        script_path = os.path.abspath(script_name)
    else:
        print("Unable to find file: '" + script_name + "'")
        exit()

    # Set our temp storage directory up
    tidy_up()

    # Deal with cross-compilation if we need to
    if telit_python_path and not bool(run):
        # Make sure we open as binary later!
        open_as = 'rb'
        # Copy the script to the temporary store
        shutil.copyfile(script_path, TEMP_STORE + '/' + script_name)
        # Compile our .pyo
        os.chdir(TEMP_STORE)
        run_cmd('wine ' + telit_python_path + '/python.exe ' +
                '-v -S -OO "' + telit_python_path + '/Lib/Dircompile.py" ' + script_name)
        compiled_script_path = TEMP_STORE + '/' + script_name + 'o'
        # Make sure it exists
        print compiled_script_path
        if os.path.exists(compiled_script_path):
            script_name = script_name + 'o'
            script_path = compiled_script_path
        else:
            print("Failed to compile script :(")
            exit()
    else:
        # If it's just a .py we should open as ascii
        open_as = 'r'

    # Number of chunks we're splitting the script into
    temporary_files = 0
    # Total number of bytes for the script
    script_length = 0
    # Split file name from extension
    script_base_name, script_type = os.path.splitext(script_name)

    # Load our script
    with open(script_path, open_as) as f:
        while 1:
            data = f.read(CHUNK_LIMIT)
            if not data:
                break
            # Increase our file count
            temporary_files += 1
            # Fix the line terminators
            if script_type == '.py':
                data = data.replace('\n', '\r\n').replace('\r\r', '\r')
            # Increase our script_length
            script_length += len(data)
            # Write our chunk
            with open(TEMP_STORE + "/" + str(temporary_files), 'w') as f_out:
                f_out.write(data)
            f_out.closed
    f.closed

    # Send the delete commands, clear existing files
    send_to_screen(screen_name, 'AT#DSCRIPT=' + script_base_name + '.py', 4)
    send_to_screen(screen_name, 'AT#DSCRIPT=' + script_base_name + '.pyo', 2)

    # Send the load code command
    send_to_screen(screen_name, 'AT#WSCRIPT="' + script_name + '",'
                   + str(script_length))
    # Have the file sent over
    for i in range(1, temporary_files + 1):
        screen_read_file(screen_name, TEMP_STORE + "/" + str(i), 10)
    # Should we execute the code too?
    if bool(run):
        # Send the enable command
        send_to_screen(screen_name, 'AT#ESCRIPT="' + script_name + '"')
        # Finaly send the execute command
        send_to_screen(screen_name, 'AT#EXECSCR')

def tidy_up():
    # Clear all the temp files
    if os.path.exists(TEMP_STORE):
        shutil.rmtree(TEMP_STORE)
    # Re-create our temp directory
    os.makedirs(TEMP_STORE)

def bool(string):
    if isinstance(string, str):
        return string.lower() in ["true", "yes", "on", "t" "1"]
    else:
        return string

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

if len(sys.argv) in [3, 4, 5]:
    load_python(*sys.argv[1:])
else:
    print "Usage: rs-send-python.py screen_name script_name [execute? telit_python_path]"
    print "  - screen_name = GNU Screen target terminal."
    print "  - script_name = File name for Python to send."
    print "  - execute? = Optional boolean, true executes after write, false doesn't."
    print "    (Default is true)"
    print "  - telit_python_path = Path to Telit Python, no trailing slash."
    print "      If included the script will be compiled into a .pyo before it's"
    print "      sent."
    print ""
    print "Example usage:"
    print "  > screen -S rs -T vt100 /dev/tty.usbserial 115200,crtscts,-parity,-cstopb"
    print "  > rs-send-python.py rs example.py"
    print ""
    print "Notes:"
    print " - script name should be in current directory, paths are not handled"
    print " - make sure that the TEMP_STORE path set at top of the script looks OK"
    print " - compiling requires Telit Python, install with Wine and then provide path"

