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
import codecs
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
		ser.write(bytearray([4,54,77]))
		
def systemTest():
	tx = ['t','T']
	rx = ['r','R']
	while True:
		userinput = input("Transmit (t) or Recieve (r): ")
		if userinput in tx:
			commTesting(cmd='Tx')
		elif userinput in rx:
			commTesting(cmd='Rx')
			
def responseTest(cmd=0x00):
	dic = {'0x01':0x23477726}
	cmd_valid = False
	while not cmd_valid: 	#Tx msg not in cmd list
		'''nbChars = ser.inWaiting()
		if nbChars > 0:
			data = ser.readline()
			
			he = codecs.encode(data,'hex')
			print(he)
			if dic[he]:
				cmd_valid = True'''
		data = ser.readline()
		if data:
			print("Recieved: ", data)
			data = data.replace(b'\n',b'')
			data = data.replace(b'\r',b'')
			
			cmd_bytes = bytearray.fromhex(data.hex())
			print("Cmd Bytes: ", cmd_bytes)
			for byte in cmd_bytes:
				if byte in dic:
					cmd_valid = True
					cmd = byte_compile
	
	if dic[cmd]:
		b = bytes(str(dic[cmd]),'UTF-8')
		bary = bytearray(b)
		print(bary)
		ser.write(bary)
		time.sleep(1)
		print("Sent Response")
		
def main(args):
	responseTest(cmd=0x01)
	#systemTest()

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
