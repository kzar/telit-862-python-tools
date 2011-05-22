#!/usr/bin/python
#
# Script to write pyo files from dump provided by telit-pyo.py script
#  - Expects format provided by telit-pyo.py
#      https://gist.github.com/985401
#  - Prepends 'telit-' to file names
#  - Verifies sizes match what the unit reported before writing
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
#
import string, sys

# http://bit.ly/k5W55l
def unhexlify(s):
  acc = []
  append = acc.append
  # In Python 2.0, we can use the int() built-in
  int16 = string.atoi
  for i in range(0, len(s), 2):
    append(chr(int16(s[i:i+2], 16)))
  return string.join(acc, '')

# http://bit.ly/cOCSsn
def chunks(l, n):
  """ Yield successive n-sized chunks from l.
  """
  for i in xrange(0, len(l), n):
    yield l[i:i+n]

if len(sys.argv) < 2:
  sys.exit('Usage: hex-to-binary.py filename')

with open(sys.argv[1]) as f:
  contents = f.read()
f.closed

for size, name, hex_data in chunks(contents.split(), 3):
  size = int(size[:-1])
  binary_data = unhexlify(hex_data)
  if len(binary_data) != size:
    print("ERROR - " + name + " was wrong size, " + str(len(binary_data)) +
          " instead of " + str(size) + "!")
  else:
    print("OK - " + name + " sizes match, writing file")
    f_out = open('telit-' + name, 'w')
    f_out.write(binary_data)
    f_out.close()
