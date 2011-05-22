#
# Script to dump all pyo's on a Telit 862GPS over the serial port as hex.
# (Useful as the unit takes SO long to compile .pyo's.)
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
import SER, MDM, sys

# Set the baud rate
SER.set_speed('115200', '8N1')

# Send stout and stderr over serial
# http://forum.sparkfun.com/viewtopic.php?t=6289
class SerWriter:
  def write(self, s):
    SER.send(s + '\r')
sys.stdout = sys.stderr = SerWriter()

# http://bit.ly/k5W55l
def hexlify(b):
  return "%02x"*len(b) % tuple(map(ord, b))

# Setup Booleans!
True, False = 1, 0

# Fairly robust AT command function
def at_command(command, win="OK", fail="ERROR", delay=10):
  # Send the command
  MDM.send(command + '\r', 5)
  # Wait for the response
  for i in range(delay):
    # Listen to serial port for click
    res = MDM.receive(1)
    # See what happened
    if res.find(win) > -1:
      return False, res
    if res.find(fail) > -1:
      return True, res
  # Timed out :(
  return True, "Timed out"

# Noddy, ugly function to list files on device
# Format returned: [["filename.pyo", size]]
def list_files(extension):
  # Run the AT command and make sure it worked
  error, response = at_command('AT#LSCRIPT')
  if error:
    return []
  # Munge the response it to something more useful
  # (No regexp on the Telit remember!)
  junk = response.replace('\n', '').replace('\r', '').replace('#LSCRIPT: ', '').split('"')[1:-1]
  files = []
  # Return a list of files
  for i in range(0, len(junk) - 1, 2):
    if junk[i].endswith(extension):
      files.append([junk[i], int(junk[i + 1][1:])])
  return files

for filename, size in list_files('.pyo'):
  f = open(filename, 'r')
  print(str(size) + ', ' + filename + '\n')
  while 1:
    data = f.read(512)
    if not data:
      print '\n\n'
      break
    SER.send(hexlify(data))
