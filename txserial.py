#!/usr/bin/python3
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
while True:
   message = str(input('>> '))
   ser.write(bytes(message, 'UTF-8')) 
   time.sleep(1)
