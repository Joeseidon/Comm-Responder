#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  serialCommTester.py
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

from PyQt4 import QtGui, QtCore, uic
from collections import OrderedDict
#from enum import Enum
import json
import os
import sys
import serial
import time
import crc16

'''
	PI PIN  ::   FUNCTION
-----------------------------
	   6			GND
	   8			TX
	   10			RX
'''
'''
class Op_Mode(Enum):
	SENDING 	= 0
	RECEIVING	= 1
'''
ser = serial.Serial(
   port = '/dev/ttyAMA0',
   baudrate = 9600,
   parity = serial.PARITY_NONE,
   stopbits = serial.STOPBITS_ONE,
   bytesize = serial.EIGHTBITS,
   timeout = 1
)

class ResponseBox(QtGui.QComboBox):
	def __init__(self,index, data):
		super(ResponseBox, self).__init__()
		self.index = index
		self.data = data["data"]
		self.selected = data['selected']
		
	def getIndex(self):
		return self.index
		
	def setIndex(self,i):
		self.index = i
		
	def configure(self):
		#add data to box 
		self.addItems(self.data)
		for index in range(self.count()):
			if(self.itemText(index) == self.selected):
				self.setCurrentIndex(index)
				break

class MyWindow(QtGui.QMainWindow):  
	def __init__(self):
		super(MyWindow, self).__init__()
		uic.loadUi('serialResponseWindow.ui', self)
		self.show()
		qr = self.frameGeometry()
		cp = QtGui.QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

		self.loadLookupTable()
		
		#Local Variables for operation
		#self.Operation_Mode = Op_Mode.SENDING
		self.pSending = False
		self.pMsgFreq = 100
		self.defaultEncoding = "UTF8"
		
		self.pID = '1'
		self.pData = '234fac'
		
		self.pLogIndex = 0
		self.pDataPresent = False
		self.maxLogCount = 50
		
		self.cmdRespIndex = 0
		self.cmdRespMaxCount = 50
		self.cmdMonitor = False
		
		#Timer definitions
		self.timer = QtCore.QTimer()
		self.timer.setInterval(self.pMsgFreq)
		self.timer.timeout.connect(self.sendPmsg)
		
		self.pDataTimer = QtCore.QTimer()
		self.pDataTimer.setInterval(self.pMsgFreq/2)
		self.pDataTimer.timeout.connect(self.checkInput)
		
		self.cmdResponseTimer = QtCore.QTimer()
		self.cmdResponseTimer.setInterval(self.pMsgFreq/2)
		self.cmdResponseTimer.timeout.connect(self.cmdRespMonitor)

		#Register GUI connections
		self.tabWidget.currentChanged.connect(self.onTabChange)
			#Periodic Msg Testing
		self.startTimedSendbtn.clicked.connect(self.startPmsg)
		self.stopTimedSendbtn.clicked.connect(self.stopPmsg)
		self.stopTimedSendbtn.setEnabled(False)
		self.quickSendbtn.clicked.connect(self.sendPmsg)
		self.pMsgID.currentIndexChanged.connect(self.updateFrequentSendData)
		self.pMsgData.currentIndexChanged.connect(self.updateFrequentSendData)
		self.pMsgFreqspin.valueChanged.connect(self.updateFrequentSendData)

			#Command Response Testing
		self.cmdRespStartbtn.clicked.connect(self.startMonitor)
		self.cmdRespStopbtn.clicked.connect(self.stopMonitor)

			#Update Associations
		self.addAssociationbtn.clicked.connect(self.addNewAssoc)
		self.updateLookupTablebtn.clicked.connect(self.updateLookupTable)
		self.cmdRespStopbtn.setEnabled(False)
		
	def updateFrequentSendData(self):
		if(self.sender() == self.pMsgID):
			#update data choices
			self.pMsgData.clear()
			index = str(int(self.pMsgID.currentText(), base=16))
			for item in self.responseLookupTbl[index]['data']:
				self.pMsgData.addItem(item)
			
		#Update ID
		self.pID = self.pMsgID.currentText()
		#Update Data
		self.pData = self.pMsgData.currentText()
		#Update Freq
		self.pMsgFreq = self.pMsgFreqspin.value()
		#Update timer
		self.timer.setInterval(self.pMsgFreq)
		self.pDataTimer.setInterval(self.pMsgFreq/2)
	
	def addNewAssoc(self):
		index = str(int(self.newAssocID.currentText(),base=16))
		self.responseLookupTbl[index]['data'].append("0x"+self.newAssocData.text())
		self.boxlist[int(index)].addItem("0x"+self.newAssocData.text())
		
		#update pMsgData as well incase its being used 
		self.pMsgData.clear()
		index = str(int(self.pMsgID.currentText(), base=16))
		for item in self.responseLookupTbl[index]['data']:
			self.pMsgData.addItem(item)
		
	def createMsg(self, ID='01', data='234dfs'):
		#Conver id and data to bytes
		#remove 0x if present
		if(ID[0:2]=='0x'):
			ID = ID[2:]
		if(data[0:2]=='0x'):
			data = data[2:]
			
		#Determine CRC
		crc = crc16.crc16xmodem(bytes(data,self.defaultEncoding))
		print(crc)
		
		#Form MSG
		combination = ID + data + crc
		byteString = bytes(combination, self.defaultEncoding)
		
		#return byte string to be sent over serial connection 
		return byteString,crc
	
	def startMonitor(self):
		#confirm psending mode is off
		if self.pSending:
			self.stopPmsg()
		self.cmdMonitor = True
		self.cmdRespStartbtn.setEnabled(False)
		self.cmdRespStopbtn.setEnabled(True)
		
		#start buffer read timer
		self.cmdResponseTimer.start()
		
	def stopMonitor(self):
		self.cmdMonitor = False
		self.cmdRespStartbtn.setEnabled(True)
		self.cmdRespStopbtn.setEnabled(False)
		
		#start buffer read timer
		self.cmdResponseTimer.stop()
		
	def cmdRespMonitor(self):
		if(ser.inWaiting() > 0):
			#Reset log index to prevent overflow
			if(self.cmdRespIndex >= 50):
				self.cmdRespIndex = 0
			
			#read
			incomingData = ser.readline()
			
			#print("Data Found", pIncomingData)
			incomingData = incomingData.decode(encoding='UTF-8')
			
			#ID (first byte)
			self.IOLog.setItem(self.cmdRespIndex,0,QtGui.QTableWidgetItem("0x"+incomingData[:2]))
			#Data (can be None)
			self.IOLog.setItem(self.cmdRespIndex,1,QtGui.QTableWidgetItem("0x"+incomingData[2:-4]))
			#CRC (last two bytes
			self.IOLog.setItem(self.cmdRespIndex,2,QtGui.QTableWidgetItem("0x"+incomingData[-4:]))
			
			#Determine response 
			index = str(int(incomingData[:2],base=16))
			resp = self.responseLookupTbl[index]['selected']
			if(resp[:2]=='0x'):
				#remove
				resp=resp[2:]
			
			#send response
			byteStr,crc = self.createMsg(ID=incomingData[:2], data=resp)
			self.sendSerialMessage(byteStr)
			
			#Udpate Log
			crc=str(hex(crc))[2:] #remove leading '0x'
			self.IOLog.setItem(self.cmdRespIndex,3,QtGui.QTableWidgetItem("0x"+incomingData[:2]+resp+crc))
			
			self.cmdRespIndex+=1
			
	def startPmsg(self):
		#if monitor is running, stop it 
		if self.cmdMonitor:
			self.stopMonitor()
		#Verify all required data has been entered
		if self.verifyPdata():
			self.pSending = True
			self.startTimedSendbtn.setEnabled(False)
			self.stopTimedSendbtn.setEnabled(True)
			
			#reset serial buffers
			ser.flushInput()
			ser.flushOutput()
			
			#Start timer
			self.timer.start()
			self.pDataTimer.start()
		else:
			return 0
		
	def checkInput(self):
		#print("Checked")
		#bytesInwaiting = ser.inWaiting()
		if(ser.inWaiting() > 0):
			#Reset log index to prevent overflow
			if(self.pLogIndex >= 50):
				self.pLogIndex = 0
			
			#read
			pIncomingData = ser.readline()
			
			#print("Data Found", pIncomingData)
			pIncomingData = pIncomingData.decode(encoding='UTF-8')
			
			#ID
			self.pIncomingLog.setItem(self.pLogIndex,0,QtGui.QTableWidgetItem("0x"+pIncomingData[:2]))
			#Data
			self.pIncomingLog.setItem(self.pLogIndex,1,QtGui.QTableWidgetItem("0x"+pIncomingData[2:-2]))
			#CRC
			self.pIncomingLog.setItem(self.pLogIndex,2,QtGui.QTableWidgetItem("0x"+pIncomingData[-2:]))
			
			self.pLogIndex+=1
			
	def verifyPdata(self):
		if(not(self.pMsgID.currentText() == None) and not(self.pMsgData.currentText() == None) and (self.pMsgFreqspin.value() > 0)):
			return True
		else:
			return False
		
	def stopPmsg(self):
		self.pSending = False
		self.startTimedSendbtn.setEnabled(True)
		self.stopTimedSendbtn.setEnabled(False)
		self.timer.stop()

	def sendPmsg(self):
		if self.pSending or (self.sender() == self.quickSendbtn):
			#Get ID and Data. Convert to bytes
			msg,crc = self.createMsg(ID=self.pID, data=self.pData)
			
			#send out message
			self.sendSerialMessage(msg)
		
	def sendSerialMessage(self, msg=b'Testing'):
		try:
			ser.write(msg)
			time.sleep(1)
		except:
			#TODO
			pass
			
	def updateLookupTable(self):
		abs_path = os.path.join(os.path.dirname(__file__), 'responseLookup.json')
		#If new update local dictionary then write json to file
		with open('responseLookup.json', 'w') as f:
			json.dump(self.responseLookupTbl,f)
		
		#Reload
		with open(abs_path, 'r') as f:
			self.responseLookupTbl = json.load(f)
		
	def updateResponseData(self,i):
		x = 0
		sender = self.sender()
		for index in self.boxlist:
			if(index == sender):
				#print("Found source! at, ", x) 
				self.responseLookupTbl[str(x)]['selected']=sender.currentText()
			x+=1
			
		
	def loadLookupTable(self):
		#Read in look up table
		abs_path = os.path.join(os.path.dirname(__file__), 'responseLookup.json')
		with open(abs_path, 'r') as f:
			self.responseLookupTbl = json.load(f)
		
		#Sort input
		self.resposneLookupTbl = sorted(self.responseLookupTbl, key=self.toInt)
		
		#Create Table
		self.cmdRespAssocTbl.setRowCount(256)
		self.pIncomingLog.setRowCount(50)
		self.IOLog.setRowCount(50)
		
		self.boxlist=[]
		#Load data into GUI table
		for i in range(0,256):
			newBox = ResponseBox(i, self.responseLookupTbl[str(i)])
			#load data in to combobox
			newBox.configure()
			#add box to quick reference list
			self.boxlist.append(newBox)
			#connect box to update socket
			newBox.currentIndexChanged.connect(self.updateResponseData)
			#Add box to table
			self.cmdRespAssocTbl.setItem(i,0,QtGui.QTableWidgetItem(str(hex(i))))
			self.cmdRespAssocTbl.setCellWidget(i,1,newBox)
			
			#populate Id list
			self.newAssocID.addItem(str(hex(i)))
			self.pMsgID.addItem(str(hex(i)))
			
	def toInt(self,elem):
		#used for key in sort methods
		return int(elem)
	
	def onTabChange(self, event):
		
		pass
		
	def closeEvent(self,event):

		pass
		

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    app.setStyle("GTK+")
    window = MyWindow()
    sys.exit(app.exec_())
