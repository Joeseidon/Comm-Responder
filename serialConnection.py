#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  serialConnection.py
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
import serial.tools.list_ports
import time
'''Found with terminal command:
	python -m serial.tools.list_ports

port = "/dev/ttyAMA0" #Raspberry pi 2
#port = "/dev/ttyS0" #Raspberry pi 3
'''
from enum import Enum
class Op_Mode(Enum):
	SENDING 	= 0
	RECEIVING	= 1
	
class SerialComm():
	def __init__(self, baudRate = 115200,
					   parity 	= serial.PARITY_NONE,
					   stopbits = serial.STOPBITS_ONE,
					   bytesize	= serial.EIGHTBITS):
					   
		self.baud = baudRate
		self.parity = parity
		self.stopbits = stopbits
		self.bytesize = serial.EIGHTBITS
		
		self.identify_ports()
		if(len(self.ports) >= 1):
			self.port = self.ports[0]
		else:
			self.port = None
			print("Invalid Use")
		self.port = "/dev/serial0"
			
		#create serial module
		self.ser = serial.Serial(self.port,
								 baudrate 	= self.baud,
								 parity		= self.parity,
								 stopbits	= self.stopbits,
								 bytesize	= self.bytesize,
								 timeout	= 1)
		if not self.ser.isOpen():
			self.ser.open()
		self.ser.flush()
		self.ser.reset_input_buffer()
		self.ser.reset_output_buffer()
		
								 
		#set operation mode
		self.setOpMode(Op_Mode.RECEIVING)
		
		#operation settings
		self.sendFreq = 1 
		self.response = b'7'
		self.msg	  = b'F'
		
		self.operate = False
		
	
	def cancelOperation(self):
		self.operate = False
		
	def startOperation(self):
		self.operate = True
		print("Operation Started in Mode: ", self.op_mode, "Operation = ",self.operate)
		if(self.op_mode == Op_Mode.SENDING):
			while(self.operate):
				#print("Sending: ", self.msg)
				self.ser.write(self.msg)
				time.sleep(1)
				
		else:
			while(self.operate):
				time.sleep(1)
				nbChars = self.ser.inWaiting()
				if nbChars > 0:
					data = self.ser.readln()
					print("Recieved: ", data)
					
	def send(self,msg):
		self.ser.write(msg)
		time.sleep(1)
		print("Sent: ", msg)
		
	def recieve(self):
		time.sleep(1)
		nbChars = 0 
		while True:
			try:
				nbChars = self.ser.inWaiting()
				if nbChars > 0:
					data = self.ser.read(nbChars)
					print("Recieved: ", data)
					time.sleep(10)
			except KeyboardInterrupt:
				return 0
		
	def getSerialComm(self):
		return self.ser
		
	def setOpMode(self,op_mode):
		self.op_mode = op_mode
		
	def identify_ports(self):
		self.port_choices = []
		self.ports = []
		for n, (portname,desc, hwid) in enumerate(sorted(serial.tools.list_ports.comports())):
			self.port_choices.append(u'{} - {}'.format(portname,desc))
			self.ports.append(portname)
		print(self.port_choices)

def main(args):
	comm = SerialComm()
	while True:
		cmd = input()
		if cmd == 's':
			comm.send(b'Testing')
			time.sleep(10)
		if cmd == 'r':			
			comm.recieve()
			time.sleep(10)
			
	'''identify_ports()
	ser = serial.Serial(port, baudrate = 9600,
							parity=serial.PARITY_NONE,
							stopbits=serial.STOPBITS_ONE,
							bytesize=serial.EIGHTBITS)
	time.sleep(1)
	while True:
		time.sleep(1)
		nbChars = ser.inWaiting()
		if nbChars > 0:
			data = ser.read(nbChars)
			if(b'A'in data):
				ser.write(b'R')
				
			print("Recieved: ", data)
			
		while True:
			for byte in range(0,6):
				ser.write(bytes(str(byte),'utf8'))
				time.sleep(1000)
				while(nbChars <= 0):
					pass
				data = ser.read(nbChars)
				print("Data Recieved: ", data)'''

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
