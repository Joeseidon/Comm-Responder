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
import json
import os
import sys
from collections import OrderedDict

from enum import Enum
class Op_Mode(Enum):
	SENDING 	= 0
	RECEIVING	= 1

class ResponseBox(QtGui.QComboBox):
	def __init__(self,index, data, handler, parent):
		super(ResponseBox, self).__init__()
		self.index = index
		self.data = data["data"]
		self.selected = data['selected']
		self.handler = handler
		self.parent = parent
		
	def getIndex(self):
		return self.index
		
	def setIndex(self,i):
		self.index = i
		
	def selectionHandler(self):
		print('selected new response')
		self.selected = self.currentText()
		self.parent.handler(index = self.index, selected = self.selected)
		
	def configure(self):
		#add data to box 
		for item in self.data:
			self.addItem(str(hex(item)))
		#add selection change handler
		self.currentIndexChanged.connect(lambda:self.selectionHandler)
		print("configured")

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
		self.pSendfreq = 100
		
		#Timer definitions
		self.timer = QtCore.QTimer()
		self.timer.setInterval(self.pSendfreq)
		self.timer.timeout.connect(self.sendPmsg)

		#Register GUI connections
		self.tabWidget.currentChanged.connect(self.onTabChange)
			#Periodic Msg Testing
		self.startTimedSendbtn.clicked.connect(self.startPmsg)
		self.stopTimedSendbtn.clicked.connect(self.stopPmsg)
		self.quickSendbtn.clicked.connect(self.sendQuickMsg)
		#self.pMsgID
		#self.pMsgData
		#self.pMsgFreqspin

			#Command Response Testing
		#self.IOLog
		#self.cmdRespStartbtn
		#self.cmdRespStopbtn

			#Update Associations
		#self.newAssocID
		#self.newAssocData
		self.addAssociationbtn.clicked.connect(self.addNewAssoc)
		self.updateLookupTablebtn.clicked.connect(self.updateLookupTable)
	
	def addNewAssoc(self):
		index = str(self.newAssocID.currentText())
		print(index)
		self.responseLookupTbl[index]['data'].append(int(hex(self.newAssocData.text())))
		self.boxlist[int(index)].addItem(self.newAssocData.text())
		#temp.addItem('Test')
		#self.cmdRespAssocTbl.setItem(1,1,temp)

	def startPmsg(self):
		
		pass
		
	def stopPmsg(self):
		
		pass
		
	def sendQuickMsg(self):
		
		
		pass

	def sendPmsg(self):
		#Get code 
		
		#Get Data
		
		#Combine into 1 message
		
		#send out message
		
		pass
		
	def updateIndexData(self, index, selected):
		self.responseLookupTbl[index]['selected'] = selected
		
	def updateLookupTable(self):
		#If new update local dictionary then write json to file
		
		pass
	
	def responseUpdated(self, boxIndex):
		
		pass
		
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
			print(i,str(hex(i)))
			newBox = ResponseBox(i, self.responseLookupTbl[str(i)], handler = self.updateIndexData, parent=self)
			newBox.configure()
			self.boxlist.append(newBox)
			#Add box to table
			self.cmdRespAssocTbl.setItem(i,0,QtGui.QTableWidgetItem(str(hex(i))))
			self.cmdRespAssocTbl.setCellWidget(i,1,newBox)
			
		for i in range(0,256):
			self.newAssocID.addItem(str(i))
			
	def toInt(self,elem):
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
