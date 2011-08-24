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
# I found that the Telit's AT#WSCRIPT command  starts loosing bytes after
# about 7kb but a 10 second pause helps give the poor little bugger a chance
# to catch up.
#
# To save (a lot) of time I've added the ability to compile .pyo files
# before the script is transmited. Install TelitPy1.5.2+_v4.1.exe using
# Wine and provide the path as an argument, see usage notes for more details.
# (Also, apply telit862-python-crosscompile-fix.patch to
# Python\Lib\py-compile.py if you want the cross compiled files to be identical
# to unit compiled ones.)
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

TEMP_STORE = "/tmp/telit-send-python"
CHUNK_LIMIT = 7000
DEPLOY_PATH_RELATIVE = "../bin"

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

    # Stop UTF-8 messing up our characters
    run_cmd('unset LANG')

    # Deal with cross-compilation if we need to
    if telit_python_path:
        # Copy the script to the temporary store
        shutil.copyfile(script_path, TEMP_STORE + '/' + script_name)
        # Compile our .pyo
        cwd = os.getcwd()
        os.chdir(TEMP_STORE)
        run_cmd('wine ' + telit_python_path + '/python.exe ' +
                '-v -S -OO "' + telit_python_path + '/Lib/Dircompile.py" ' + script_name)
        compiled_script_path = TEMP_STORE + '/' + script_name + 'o'
        # Make sure it exists
        if os.path.exists(compiled_script_path):
            script_name = script_name + 'o'
            script_path = compiled_script_path
            # Copy the pyo to our deploy directory
            deploy_path = cwd + '/' + DEPLOY_PATH_RELATIVE + '/' + script_name
            if os.path.exists(deploy_path):
                shutil.copyfile(compiled_script_path, deploy_path)
        else:
            print("Failed to compile script :(")
            exit()

    # Split file name from extension
    script_base_name, script_type = os.path.splitext(script_name)

    with open(script_path, 'r') as f:
        data = f.read()

        if script_type == '.py':
            data = data.replace('\n', '\r\n').replace('\r\r', '\r')
    f.closed

    # Send the delete commands, clear existing files
    send_to_screen(screen_name, 'AT#DSCRIPT=' + script_base_name + '.py', 4)
    send_to_screen(screen_name, 'AT#DSCRIPT=' + script_base_name + '.pyo', 2)

    # Send the load code command
    send_to_screen(screen_name, 'AT#WSCRIPT="' + script_name + '",'
                  + str(len(data)))

    screen_send_raw_string(screen_name, data, CHUNK_LIMIT, 10)

    # Should we execute the code too?
    if bool(run):
        # Send the enable command
        send_to_screen(screen_name, 'AT#ESCRIPT="' + script_name + '"')
        # Finaly send the execute command
        send_to_screen(screen_name, 'AT#EXECSCR')

# Please forgive me for this function, I'll leave it as an excersise for the
# reader to fully grok the insanity here within..
def screen_send_raw_string(screen_name, string, chunk_size, delay):
    i = 0
    for c in string:
        run_cmd("screen -S " + screen_name + " -X digraph " + oct(ord(c)) + "\r")
        i += 1
        if i > chunk_size:
            i = 0
            time.sleep(delay)

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

def send_to_screen(screen_name, message, delay=0.5):
    message = message.replace("'", "\\'").replace('"', '\\"') + '\r'
    run_cmd("screen -S " + screen_name + " -X stuff $'" + message + "'")
    time.sleep(delay)

if len(sys.argv) in [3, 4, 5]:
    load_python(*sys.argv[1:])
else:
    print "Usage: telit-send-python.py screen_name script_name [execute? telit_python_path]"
    print "  - screen_name = GNU Screen target terminal."
    print "  - script_name = File name for Python to send."
    print "  - execute? = Optional boolean, true executes after write, false doesn't."
    print "    (Default is true)"
    print "  - telit_python_path = Path to Telit Python, no trailing slash."
    print "      If included the script will be compiled into a .pyo before it's"
    print "      sent."
    print ""
    print "Example usage:"
    print "  > unset LANG && screen -S telit -T vt100 /dev/tty.usbserial 115200,crtscts,-parity,-cstopb"
    print "  > telit-send-python.py telit example.py"
    print ""
    print "Notes:"
    print " - script name should be in current directory, paths are not handled"
    print " - make sure that the TEMP_STORE path set at top of the script looks OK"
    print " - compiling requires Telit Python, install with Wine and then provide path"
    print " - make sure that LANG environment variable is cleared with unset, otherwise some binary characters can get garbled."
