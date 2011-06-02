# Python REPL for Telit 862!
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

import SER, MOD, MDM, GPS, sys

class SerWriter:
  def write(self, s):
    SER.send('%d %s\r' %(MOD.secCounter(), s))
SER.set_speed('115200', '8N1')
sys.stdout = sys.stderr = SerWriter()

def check_serial(f, buffer):
  # Wait for serial input
  data = SER.receive(1)
  if data:
    # Echo it
    SER.send(data)
    # Add it to the buffer
    buffer = buffer + data
    # If the message's done send it
    end_index = buffer.find('\r')
    if end_index > -1:
      message = buffer[:end_index + 1]
      buffer = buffer[end_index + 1:]
      f(message)
  return buffer

def try_eval(code):
  try:
    return str(eval(code))
  except:
    return "Exception: %s" % str(sys.exc_info()[0])

def repl():
  buffer = ''
  while 1:
    buffer = check_serial(lambda s: SER.send(s + '\r\n' +
                                             try_eval(s.strip()) +
                                             '\r\n > '),
                          buffer)
    if buffer.find('+++') > -1:
      break

print('Telit REPL, +++ to escape.\r\n > ')
repl()
