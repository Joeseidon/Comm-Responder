#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  serialCT.py
#  
#  Copyright 2017  <pi@raspberrypi>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

import serial
import time
ser = serial.Serial(
   port = '/dev/ttyAMA0',
   baudrate = 9600,
   parity = serial.PARITY_NONE,
   stopbits = serial.STOPBITS_ONE,
   bytesize = serial.EIGHTBITS,
   timeout = 1
)

def commTesting(cmd):
	while True and cmd=='Rx':
		print (('SERIAL PORT:'), ser.readline())
	while True and cmd=='Tx':
		message = str(input('>> ')+'\n')
		if('quit tx' in message): return 0
		ser.write(bytes(message, 'UTF-8')) 
		time.sleep(1)
		
def systemTest():
	tx = ['t','T']
	rx = ['r','R']
	while True:
		userinput = input("Transmit (t) or Recieve (r): ")
		if userinput in tx:
			commTesting(cmd='Tx')
		elif userinput in rx:
			commTesting(cmd='Rx')
def main(args):
	systemTest()

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
