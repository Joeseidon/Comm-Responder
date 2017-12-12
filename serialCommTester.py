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
from enum import Enum
import json
import os
import sys
import serial
import time

class Op_Mode(Enum):
	SENDING 	= 0
	RECEIVING	= 1
	
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
		for item in self.data:
			self.addItem(item)

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
		self.Operation_Mode = Op_Mode.SENDING
		self.pSending = False
		self.pMsgFreq = 100
		self.defaultEncoding = "UTF8"
		
		self.pID = '1'
		self.pData = '234fac'
		
		#Timer definitions
		self.timer = QtCore.QTimer()
		self.timer.setInterval(self.pMsgFreq)
		self.timer.timeout.connect(self.sendPmsg)

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
		#self.IOLog
		#self.cmdRespStartbtn
		#self.cmdRespStopbtn

			#Update Associations
		#self.newAssocID
		#self.newAssocData
		self.addAssociationbtn.clicked.connect(self.addNewAssoc)
		self.updateLookupTablebtn.clicked.connect(self.updateLookupTable)
		
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
	
	def addNewAssoc(self):
		index = str(int(self.newAssocID.currentText(),base=16))
		self.responseLookupTbl[index]['data'].append(self.newAssocData.text())
		self.boxlist[int(index)].addItem(self.newAssocData.text())
		
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
		combination = ID + data
		byteString = bytes(combination, self.defaultEncoding)
		#Calculate CRC and append to byte string
			#TODO
		#return byte string to be sent over serial connection 
		return byteString
		
	def startPmsg(self):
		#Verify all required data has been entered
		if self.verifyPdata():
			self.pSending = True
			self.startTimedSendbtn.setEnabled(False)
			self.stopTimedSendbtn.setEnabled(True)
			
			#Start timer
			self.timer.start()
		else:
			return 0
			
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
			msg = self.createMsg(ID=self.pID, data=self.pData)
			
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
	
	def onTabChange(self, i):


		pass
	
	def closeEvent(self,event):

		pass
		

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    app.setStyle("GTK+")
    window = MyWindow()
    sys.exit(app.exec_())
