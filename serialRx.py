#! /usr/bin/env python3
import serial
import time
ser = serial.Serial(
   port = '/dev/ttyAMA0',
   baudrate = 9600,
   parity = serial.PARITY_NONE,
   stopbits = serial.STOPBITS_ONE,
   bytesize = serial.EIGHTBITS,
   timeout = 10
)
while True:
   print (('SERIAL PORT:'), ser.readline())
