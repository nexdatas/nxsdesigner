#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2013 DESY, Jan Kotanski <jkotan@mail.desy.de>
#
#    nexdatas is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    nexdatas is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with nexdatas.  If not, see <http://www.gnu.org/licenses/>.
## \package test nexdatas
## \file FieldDlgTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import subprocess
import random
import struct
import binascii
import time

from PyQt4.QtTest import QTest
from PyQt4.QtGui import (QApplication, QMessageBox, QTableWidgetItem, QPushButton)
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt, QTimer, SIGNAL, QObject, QVariant, QString
from PyQt4.QtXml import QDomNode, QDomDocument, QDomElement


from ndtsconfigtool.FieldDlg import FieldDlg
from ndtsconfigtool.ComponentModel import ComponentModel
from ndtsconfigtool.AttributeDlg import AttributeDlg
from ndtsconfigtool.NodeDlg import NodeDlg

from ndtsconfigtool.ui.ui_fielddlg import Ui_FieldDlg


##  Qt-application
app = None


## if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)

class TestView(object):
    def __init__(self, model):
        self.testIndex = None
        self.testModel = model
        self.stack = []

    def currentIndex(self):
        return self.testIndex 

    def model(self):
        return self.testModel

    def expand(self, index):
        self.stack.append("expand")
        self.stack.append(index)

## test fixture
class FieldDlgTest(unittest.TestCase):

    ## constructor
    # \param methodName name of the test method
    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)



        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"
        ## MessageBox text
        self.text = None
        ## MessageBox title
        self.title = None

        ## attribute name
        self.aname = "myname"
        ## attribute value
        self.avalue = "myentry"

        ## action status
        self.performed = False

        try:
            self.__seed  = long(binascii.hexlify(os.urandom(16)), 16)
        except NotImplementedError:
            self.__seed  = long(time.time() * 256) 
        self.__rnd = random.Random(self.__seed)


    ## test starter
    # \brief Common set up
    def setUp(self):
        print "\nsetting up..."        
        print "SEED =", self.__seed 
        

    ## test closer
    # \brief Common tear down
    def tearDown(self):
        print "tearing down ..."

    def checkMessageBox(self):
#        self.assertEqual(QApplication.activeWindow(),None)
        mb = QApplication.activeModalWidget()
        self.assertTrue(isinstance(mb, QMessageBox))
#        print mb.text()
        self.text = mb.text()
        self.title = mb.windowTitle()
        mb.close()


    def rmAttributeWidget(self):
        aw = QApplication.activeWindow()
        mb = QApplication.activeModalWidget()
        self.assertTrue(isinstance(mb, QMessageBox))
        self.text = mb.text()
        self.title = mb.windowTitle()

        QTest.mouseClick(mb.button(QMessageBox.Yes), Qt.LeftButton)


    def rmAttributeWidgetClose(self):
        aw = QApplication.activeWindow()
        mb = QApplication.activeModalWidget()
        self.assertTrue(isinstance(mb, QMessageBox))
        self.text = mb.text()
        self.title = mb.windowTitle()

        QTest.mouseClick(mb.button(QMessageBox.No), Qt.LeftButton)


    def attributeWidget(self):
        aw = QApplication.activeWindow()
        mb = QApplication.activeModalWidget()
        self.assertTrue(isinstance(mb, AttributeDlg))

        QTest.keyClicks(mb.ui.nameLineEdit, self.aname)
        self.assertEqual(mb.ui.nameLineEdit.text(),self.aname)
        QTest.keyClicks(mb.ui.valueLineEdit, self.avalue)
        self.assertEqual(mb.ui.valueLineEdit.text(),self.avalue)

        mb.accept()

    def attributeWidgetClose(self):
        aw = QApplication.activeWindow()
        mb = QApplication.activeModalWidget()
        self.assertTrue(isinstance(mb, AttributeDlg))

        QTest.keyClicks(mb.ui.nameLineEdit, self.aname)
        self.assertEqual(mb.ui.nameLineEdit.text(),self.aname)
        QTest.keyClicks(mb.ui.valueLineEdit, self.avalue)
        self.assertEqual(mb.ui.valueLineEdit.text(),self.avalue)

#        mb.close()
        mb.reject()

#        mb.accept()



    ## constructor test
    # \brief It tests default settings
    def test_constructor(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = FieldDlg()
        form.show()
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.units, '')
        self.assertEqual(form.dimDoc, '')
        self.assertEqual(form.rank, 0) 
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_FieldDlg))
        self.assertTrue(isinstance(form, NodeDlg))
        self.assertEqual(form.externalApply, None)
        self.assertEqual(form.externalDSLink, None)
        
        self.assertEqual(form.replaceText,super(FieldDlg,form).replaceText )
        self.assertEqual(form.removeElement,super(FieldDlg,form).removeElement )
        self.assertEqual(form.replaceElement,super(FieldDlg,form).replaceElement )
        self.assertTrue(form.appendElement is not super(FieldDlg,form).appendElement )
        self.assertEqual(form.reset,super(FieldDlg,form).reset )


    ## constructor test
    # \brief It tests default settings
    def test_constructor_accept(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = FieldDlg()
        form.show()
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.dimDoc, '')
        self.assertEqual(form.units, '')
        self.assertEqual(form.rank, 0) 
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_FieldDlg))

        form.createGUI()

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        
        self.assertTrue(not form.ui.applyPushButton.isEnabled())
        self.assertTrue(form.ui.resetPushButton.isEnabled())

        name = "myname"
        nType = "NXEntry"
        QTest.keyClicks(form.ui.nameLineEdit, name)
        self.assertEqual(form.ui.nameLineEdit.text(),name)
        QTest.keyClicks(form.ui.typeLineEdit, nType)
        self.assertEqual(form.ui.typeLineEdit.text(), nType)

        self.assertTrue(not form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(not form.ui.typeLineEdit.text().isEmpty())


        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)

#        form.apply()
#        self.assertEqual(form.name, name)
#        self.assertEqual(form.nexusType, nType)

        self.assertEqual(form.result(),0)





    ## constructor test
    # \brief It tests default settings
    def test_constructor_accept_long(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = FieldDlg()
        form.show()
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.units, '')
        self.assertEqual(form.dimDoc, '')
        self.assertEqual(form.rank, 0) 
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_FieldDlg))

        form.createGUI()

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))
        
        self.assertTrue(not form.ui.applyPushButton.isEnabled())
        self.assertTrue(form.ui.resetPushButton.isEnabled())

        name = "myfield"
        nType = "NX_DATE_TIME"
        units = "seconds"
        value = "14:45"
        QTest.keyClicks(form.ui.nameLineEdit, name)
        self.assertEqual(form.ui.nameLineEdit.text(),name)
        QTest.keyClicks(form.ui.typeLineEdit, nType)
        self.assertEqual(form.ui.typeLineEdit.text(), nType)

        QTest.keyClicks(form.ui.unitsLineEdit, units)
        self.assertEqual(form.ui.unitsLineEdit.text(), units)
        QTest.keyClicks(form.ui.valueLineEdit, value)
        self.assertEqual(form.ui.valueLineEdit.text(), value)


        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

     
        self.assertTrue(not form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(not form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(not form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(not form.ui.valueLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))
        


        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)

#        form.apply()
#        self.assertEqual(form.name, name)
#        self.assertEqual(form.nexusType, nType)

        self.assertEqual(form.result(),0)




    ## constructor test
    # \brief It tests default settings
    def test_updateForm(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = FieldDlg()
        form.show()
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.units, '')
        self.assertEqual(form.dimDoc, '')
        self.assertEqual(form.rank, 0) 
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_FieldDlg))

        form.createGUI()

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))


        name = "myname"
        nType = "NXEntry"
        units = "seconds"
        value = "14:45"
        doc = "My documentation: \n ble ble ble "
        attributes = {"myattr":"myvalue","myattr2":"myvalue2","myattr3":"myvalue3" }
        nn =  self.__rnd.randint(1, 9) 

        dimensions = [self.__rnd.randint(0, 40)  for n in range(nn)]
        
        self.assertEqual(form.updateForm(),None)
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.rank,0)
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        form.name = name

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        self.assertEqual(form.updateForm(),None)
    
        self.assertEqual(form.ui.nameLineEdit.text(),name)
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertEqual(form.rank,0)
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        form.ui.nameLineEdit.setText("")

        form.name = ""
        form.nexusType = nType

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertEqual(form.rank,0)
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        self.assertEqual(form.updateForm(),None)
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.typeLineEdit.text(), nType)
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertEqual(form.rank,0)
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))





        form.ui.typeLineEdit.setText("")

        form.nexusType = ""

        form.units = units

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertEqual(form.rank,0)
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        self.assertEqual(form.updateForm(),None)
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertEqual(form.rank,0)
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertEqual(form.ui.unitsLineEdit.text(), units)
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))


        form.ui.unitsLineEdit.setText("")
        form.units = ""


        form.dimensions = dimensions

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.rank,0)
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        self.assertEqual(form.updateForm(),None)
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty)
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),str(dimensions))
        self.assertEqual(form.rank,len(dimensions))
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))


        form.ui.dimLabel.setText("[]")
        form.dimensions = []

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.rank,len(dimensions))
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        self.assertEqual(form.updateForm(),None)
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty)
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),str([0]*len(dimensions)).replace('0','*'))
        self.assertEqual(form.rank,len(dimensions))
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))


        form.ui.dimLabel.setText("[]")
        form.dimensions = []
        form.rank = 0

        form.value = value

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.rank,0)
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        self.assertEqual(form.updateForm(),None)
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertEqual(form.ui.valueLineEdit.text(), value)
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))


        form.ui.valueLineEdit.setText("")
        form.value = ""


        form.doc = doc

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        self.assertEqual(form.updateForm(),None)
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertEqual(form.ui.docTextEdit.toPlainText(), doc)
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))



        form.ui.docTextEdit.setText("")

        form.name = name
        form.doc = doc
        form.nexusType = nType
        form.attributes = attributes

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertEqual(form.updateForm(),None)
    
        self.assertEqual(form.ui.typeLineEdit.text(), nType)
        self.assertEqual(form.ui.nameLineEdit.text(),name)
        self.assertEqual(form.ui.docTextEdit.toPlainText(), doc)



        self.assertEqual(form.ui.attributeTableWidget.columnCount(),2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(),len(attributes))
        for i in range(len(attributes)):
            it = form.ui.attributeTableWidget.item(i, 0) 
            k = str(it.text())
            self.assertTrue(k in attributes.keys())
            it2 = form.ui.attributeTableWidget.item(i, 1) 
            self.assertEqual(it2.text(), attributes[k])

        self.assertEqual(form.ui.docTextEdit.toPlainText(), doc)


        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)


        self.assertEqual(form.result(),0)




    ## constructor test
    # \brief It tests default settings
    def test_getState(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = FieldDlg()
        form.show()

        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.dimDoc, '')
        self.assertEqual(form.rank, 0) 
        self.assertEqual(form.units, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_FieldDlg))

        form.createGUI()

        name = "myname"
        nType = "NXEntry"
        units = "Tmm"
        value = "asd1234"
        doc = "My documentation: \n ble ble ble "
        dimdoc = "My Dim documentation: \n ble ble ble "
        rank = 3
        attributes = {"myattr":"myvalue","myattr2":"myvalue2","myattr3":"myvalue3" }
        dimensions = [1, 2, 3, 4]

        
        self.assertEqual(form.getState(),('','','','','','',0,{},[]))
    

        form.name = name

        self.assertEqual(form.getState(),(name,'','','','','',0,{},[]))
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))


        form.name = ""

        form.nexusType = nType
        self.assertEqual(form.getState(),('',nType,'','','','',0,{},[]))

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))
        form.nexusType = ""


        form.units = units
        self.assertEqual(form.getState(),('','',units,'','','',0,{},[]))
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))
        form.units = ""

        form.value = value
        self.assertEqual(form.getState(),('','','',value,'','',0,{},[]))
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))
        form.value = ""



        form.doc = doc
        self.assertEqual(form.getState(),('','','','',doc,'',0,{},[]))
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))
        form.doc = ""


        form.dimDoc = dimdoc
        self.assertEqual(form.getState(),('','','','','',dimdoc,0,{},[]))
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))
        form.dimDoc = ""



        form.rank = rank
        self.assertEqual(form.getState(),('','','','','','',rank,{},[]))
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))
        form.rank = 0


        
        form.attributes = attributes
        state = form.getState()

        self.assertEqual(state[0],'')
        self.assertEqual(state[1],'')
        self.assertEqual(state[2],'')
        self.assertEqual(state[3],'')
        self.assertEqual(state[4],'')
        self.assertEqual(state[5],'')
        self.assertEqual(state[6],0)
        self.assertEqual(state[8],[])
        self.assertEqual(len(state),9)
        self.assertEqual(len(state[7]),len(attributes))
        for at in attributes:
            self.assertEqual(attributes[at], state[7][at])

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        form.attributes = {}


        form.dimensions = dimensions
        state = form.getState()

        self.assertEqual(state[0],'')
        self.assertEqual(state[1],'')
        self.assertEqual(state[2],'')
        self.assertEqual(state[3],'')
        self.assertEqual(state[4],'')
        self.assertEqual(state[5],'')
        self.assertEqual(state[6],0)
        self.assertEqual(state[7],{})
        self.assertEqual(len(state),9)
        self.assertEqual(len(state[8]),len(dimensions))
        for i in range(len(dimensions)):
            self.assertEqual(dimensions[i], state[8][i])

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        form.dimensions = []


        form.name = name
        form.nexusType = nType
        form.units = units
        form.value = value
        form.doc = doc
        form.dimDoc = dimdoc
        form.rank = rank
        form.dimensions = dimensions
        form.attributes = attributes

        state = form.getState()

        self.assertEqual(state[0],name)
        self.assertEqual(state[1],nType)
        self.assertEqual(state[2],units)
        self.assertEqual(state[3],value)
        self.assertEqual(state[4],doc)
        self.assertEqual(state[5],dimdoc)
        self.assertEqual(state[6],rank)
        self.assertEqual(len(state),9)
        self.assertTrue(state[7] is not attributes)
        self.assertEqual(len(state[7]),len(attributes))
        for at in attributes:
            self.assertEqual(attributes[at], state[7][at])
        self.assertEqual(len(state[8]),len(dimensions))
        for i in range(len(dimensions)):
            self.assertEqual(dimensions[i], state[8][i])

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))


        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)


        self.assertEqual(form.result(),0)







    ## constructor test
    # \brief It tests default settings
    def test_setState(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = FieldDlg()
        form.show()


        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.units, '')
        self.assertEqual(form.dimDoc, '')
        self.assertEqual(form.rank, 0) 
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_FieldDlg))

        form.createGUI()


        name = "myname"
        nType = "NXEntry"
        units = "Tmm"
        value = "asd1234"
        doc = "My documentation: \n ble ble ble "
        dimdoc = "My Dim documentation: \n ble ble ble "
        rank = 3
        attributes = {"myattr":"myvalue","myattr2":"myvalue2","myattr3":"myvalue3" }
        dimensions = [1, 2, 3, 4]

        
        self.assertEqual(form.setState(['','','','','','',0,{},[]]), None)
    

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.units, '')
        self.assertEqual(form.dimDoc, '')
        self.assertEqual(form.rank, 0) 
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.attributes, {})


        self.assertEqual(form.setState([name,'','','','','',0,{},[]]), None)
    

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        self.assertEqual(form.name, name)
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.units, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.dimDoc, '')
        self.assertEqual(form.rank, 0) 
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.attributes, {})

        form.name = ""



        self.assertEqual(form.setState(['',nType,'','','','',0,{},[]]), None)
    

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, nType)
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.units, '')
        self.assertEqual(form.dimDoc, '')
        self.assertEqual(form.rank, 0) 
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.attributes, {})

        form.nexusType = ''




        self.assertEqual(form.setState(['','',units,'','','',0,{},[]]), None)
    

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.units, units)
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.dimDoc, '')
        self.assertEqual(form.rank, 0) 
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.attributes, {})

        form.units = ''




        self.assertEqual(form.setState(['','','',value,'','',0,{},[]]), None)
    

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, value)
        self.assertEqual(form.dimDoc, '')
        self.assertEqual(form.rank, 0) 
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.attributes, {})

        form.value = ''





        self.assertEqual(form.setState(['','','','',doc,'',0,{},[]]), None)
    

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, doc)
        self.assertEqual(form.value, '')
        self.assertEqual(form.dimDoc, '')
        self.assertEqual(form.rank, 0) 
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.units, '')

        form.doc = ''



        self.assertEqual(form.setState(['','','','','',dimdoc,0,{},[]]), None)
    

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.dimDoc, dimdoc)
        self.assertEqual(form.rank, 0) 
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.attributes, {})

        form.dimdoc = ''




        self.assertEqual(form.setState(['','','','','','',rank,{},[]]), None)
    

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.units, '')
        self.assertEqual(form.dimDoc, '')
        self.assertEqual(form.rank, rank) 
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.attributes, {})

        form.rank = 0




        self.assertEqual(form.setState(['','','','','','',0,attributes,[]]), None)
    

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.dimDoc, '')
        self.assertEqual(form.rank, 0) 
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.attributes, attributes)

        form.attributes = {}



        self.assertEqual(form.setState(['','','','','','',0,{},dimensions]), None)
    

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.dimDoc, '')
        self.assertEqual(form.units, '')
        self.assertEqual(form.rank, 0) 
        self.assertEqual(form.dimensions, dimensions)
        self.assertEqual(form.attributes, {})

        form.dimensions = {}

        self.assertEqual(form.setState([name,nType,units,value,doc,dimdoc,rank,attributes,dimensions]), None)
    

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        self.assertEqual(form.name, name)
        self.assertEqual(form.nexusType, nType)
        self.assertEqual(form.doc, doc)
        self.assertEqual(form.value, value)
        self.assertEqual(form.units, units)
        self.assertEqual(form.dimDoc, dimdoc)
        self.assertEqual(form.rank, rank) 
        self.assertEqual(form.dimensions, dimensions)
        self.assertEqual(form.attributes, attributes)



        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)


        self.assertEqual(form.result(),0)

##################
############ TODO

    ## constructor test
    # \brief It tests default settings
    def test_createGUI(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = FieldDlg()
        form.show()
        form.createGUI()

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())


        name = "myname"
        nType = "NXEntry"
        doc = "My documentation: \n ble ble ble "
        attributes = {"myattr":"myvalue","myattr2":"myvalue2","myattr3":"myvalue3" }
        
        form = FieldDlg()
        form.show()
        form.createGUI()
 
        self.assertEqual(form.ui.nameLineEdit.text(), '') 
        self.assertEqual(form.ui.typeLineEdit.text(), '')
        self.assertEqual(form.ui.docTextEdit.toPlainText(), '')

        form = FieldDlg()
        form.show()
        form.name = name


        form.createGUI()
    
        self.assertEqual(form.ui.nameLineEdit.text(),name)
        self.assertEqual(form.ui.typeLineEdit.text(), '')
        self.assertEqual(form.ui.docTextEdit.toPlainText(), '')
        self.assertEqual(form.ui.attributeTableWidget.columnCount(),2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(),0)


        form = FieldDlg()
        form.show()
        form.nexusType = nType


        form.createGUI()
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.typeLineEdit.text(), nType)
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())





        form = FieldDlg()
        form.show()
        form.doc = doc

        form.createGUI()
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertEqual(form.ui.docTextEdit.toPlainText(), doc)




        form = FieldDlg()
        form.show()
        form.name = name
        form.doc = doc
        form.nexusType = nType
        form.attributes = attributes

        form.createGUI()
    
        self.assertEqual(form.ui.typeLineEdit.text(), nType)
        self.assertEqual(form.ui.nameLineEdit.text(),name)
        self.assertEqual(form.ui.docTextEdit.toPlainText(), doc)

        self.assertEqual(form.ui.attributeTableWidget.columnCount(),2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(),len(attributes))
        for i in range(len(attributes)):
            it = form.ui.attributeTableWidget.item(i, 0) 
            k = str(it.text())
            self.assertTrue(k in attributes.keys())
            it2 = form.ui.attributeTableWidget.item(i, 1) 
            self.assertEqual(it2.text(), attributes[k])

        self.assertEqual(form.ui.docTextEdit.toPlainText(), doc)



        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)

#        form.apply()
#        self.assertEqual(form.name, name)
#        self.assertEqual(form.nexusType, nType)

        self.assertEqual(form.result(),0)






    ## constructor test
    # \brief It tests default settings
    def test_setFromNode(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        dks = []
        doc = QDomDocument()
        nname = "field"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
        qdn.setAttribute("type","mytype%s" %  nn)
        qdn.setAttribute("unit","myunits%s" %  nn)
        qdn.setAttribute("shortname","mynshort%s" %  nn)
        doc.appendChild(qdn) 
        dname = "doc"
        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 



        form = FieldDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_FieldDlg))

        form.createGUI()
        
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        
        form.setFromNode()


        self.assertEqual(form.name, "myname%s" %  nn)
        self.assertEqual(form.nexusType, "mytype%s" %  nn)
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        self.assertEqual(form.attributes, {u'shortname': u'mynshort%s' % nn, u'unit': u'myunits%s' % nn})
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])


        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertEqual(form.ui.attributeTableWidget.columnCount(),2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(),0)





    ## constructor test
    # \brief It tests default settings
    def test_setFromNode_parameter(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        dks = []
        doc = QDomDocument()
        nname = "field"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
        qdn.setAttribute("type","mytype%s" %  nn)
        qdn.setAttribute("unit","myunits%s" %  nn)
        qdn.setAttribute("shortname","mynshort%s" %  nn)
        doc.appendChild(qdn) 
        dname = "doc"
        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 



        form = FieldDlg()
        form.show()
#        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_FieldDlg))

        form.createGUI()
        
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        
        form.setFromNode(qdn)
        self.assertEqual(form.node, qdn)


        self.assertEqual(form.name, "myname%s" %  nn)
        self.assertEqual(form.nexusType, "mytype%s" %  nn)
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        self.assertEqual(form.attributes, {u'shortname': u'mynshort%s' % nn, u'unit': u'myunits%s' % nn})
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])


        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertEqual(form.ui.attributeTableWidget.columnCount(),2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(),0)


    ## constructor test
    # \brief It tests default settings
    def ttest_setFromNode_noNode(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        dks = []
        doc = QDomDocument()
        nname = "field"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
        qdn.setAttribute("type","mytype%s" %  nn)
        qdn.setAttribute("unit","myunits%s" %  nn)
        qdn.setAttribute("shortname","mynshort%s" %  nn)
        doc.appendChild(qdn) 
        dname = "doc"
        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 



        form = FieldDlg()
        form.show()
#        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_FieldDlg))

        form.createGUI()
        
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        
        form.setFromNode()

        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])


        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertEqual(form.ui.attributeTableWidget.columnCount(),2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(),0)



    ## constructor test
    # \brief It tests default settings
    def test_setFromNode_clean(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        dks = []
        doc = QDomDocument()
        nname = "field"
        qdn = doc.createElement(nname)
        doc.appendChild(qdn) 


        form = FieldDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_FieldDlg))

        form.createGUI()
        
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        
        form.setFromNode()

        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])



        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertEqual(form.ui.attributeTableWidget.columnCount(),2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(),0)



    ## constructor test
    # \brief It tests default settings
    def test_populateAttribute_setFromNode(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        dks = []
        doc = QDomDocument()
        nname = "field"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
        qdn.setAttribute("type","mytype%s" %  nn)
        qdn.setAttribute("unit","myunits%s" %  nn)
        qdn.setAttribute("shortname","mynshort%s" %  nn)
        doc.appendChild(qdn) 
        dname = "doc"
        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 



        form = FieldDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_FieldDlg))

        form.createGUI()
        
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        
        form.setFromNode()

        attributes = {u'shortname': u'mynshort%s' % nn, u'unit': u'myunits%s' % nn}

        self.assertEqual(form.name, "myname%s" %  nn)
        self.assertEqual(form.nexusType, "mytype%s" %  nn)
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        self.assertEqual(form.attributes, attributes)
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])


        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertEqual(form.ui.attributeTableWidget.columnCount(),2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(),0)

        form.populateAttributes()




        self.assertEqual(form.ui.attributeTableWidget.columnCount(),2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(),len(attributes))
        for i in range(len(attributes)):
            it = form.ui.attributeTableWidget.item(i, 0) 
            k = str(it.text())
            self.assertTrue(k in attributes.keys())
            it2 = form.ui.attributeTableWidget.item(i, 1) 
            self.assertEqual(it2.text(), attributes[k])


        item = form.ui.attributeTableWidget.item(form.ui.attributeTableWidget.currentRow(), 0)
        self.assertEqual(item,None)
        



    ## constructor test
    # \brief It tests default settings
    def test_populateAttribute_setFromNode_selected_wrong(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        dks = []
        doc = QDomDocument()
        nname = "field"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
        qdn.setAttribute("type","mytype%s" %  nn)
        qdn.setAttribute("unit","myunits%s" %  nn)
        qdn.setAttribute("shortname","mynshort%s" %  nn)
        doc.appendChild(qdn) 
        dname = "doc"
        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 



        form = FieldDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_FieldDlg))

        form.createGUI()
        
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        
        form.setFromNode()

        attributes = {u'shortname': u'mynshort%s' % nn, u'unit': u'myunits%s' % nn}

        self.assertEqual(form.name, "myname%s" %  nn)
        self.assertEqual(form.nexusType, "mytype%s" %  nn)
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        self.assertEqual(form.attributes, attributes)
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])


        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertEqual(form.ui.attributeTableWidget.columnCount(),2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(),0)

        form.populateAttributes("ble")




        self.assertEqual(form.ui.attributeTableWidget.columnCount(),2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(),len(attributes))
        for i in range(len(attributes)):
            it = form.ui.attributeTableWidget.item(i, 0) 
            k = str(it.text())
            self.assertTrue(k in attributes.keys())
            it2 = form.ui.attributeTableWidget.item(i, 1) 
            self.assertEqual(it2.text(), attributes[k])


        item = form.ui.attributeTableWidget.item(form.ui.attributeTableWidget.currentRow(), 0)
        self.assertEqual(item,None)
        





    ## constructor test
    # \brief It tests default settings
    def test_populateAttribute_setFromNode_selected(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        dks = []
        doc = QDomDocument()
        nname = "field"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
        qdn.setAttribute("type","mytype%s" %  nn)
        qdn.setAttribute("unit","myunits%s" %  nn)
        qdn.setAttribute("shortname","mynshort%s" %  nn)
        doc.appendChild(qdn) 
        dname = "doc"
        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 



        form = FieldDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_FieldDlg))

        form.createGUI()
        
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        
        form.setFromNode()

        attributes = {u'shortname': u'mynshort%s' % nn, u'unit': u'myunits%s' % nn}

        self.assertEqual(form.name, "myname%s" %  nn)
        self.assertEqual(form.nexusType, "mytype%s" %  nn)
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        self.assertEqual(form.attributes, attributes)
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])


        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertEqual(form.ui.attributeTableWidget.columnCount(),2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(),0)

        
        na =  self.__rnd.randint(0, len(attributes)-1) 
        sel = attributes.keys()[na]
        form.populateAttributes(sel)




        self.assertEqual(form.ui.attributeTableWidget.columnCount(),2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(),len(attributes))
        for i in range(len(attributes)):
            it = form.ui.attributeTableWidget.item(i, 0) 
            k = str(it.text())
            self.assertTrue(k in attributes.keys())
            it2 = form.ui.attributeTableWidget.item(i, 1) 
            self.assertEqual(it2.text(), attributes[k])


        item = form.ui.attributeTableWidget.item(form.ui.attributeTableWidget.currentRow(), 0)
        
        self.assertEqual(item.data(Qt.UserRole).toString(),sel)




    ## constructor test
    # \brief It tests default settings
    def test_populateAttribute_setFromNode_selected_addAttribute(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        dks = []
        doc = QDomDocument()
        nname = "field"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
        qdn.setAttribute("type","mytype%s" %  nn)
        qdn.setAttribute("unit","myunits%s" %  nn)
        qdn.setAttribute("shortname","mynshort%s" %  nn)
        doc.appendChild(qdn) 
        dname = "doc"
        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 



        form = FieldDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_FieldDlg))

        form.createGUI()
        
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        
        form.setFromNode()

        attributes = {u'shortname': u'mynshort%s' % nn, u'unit': u'myunits%s' % nn}

        self.assertEqual(form.name, "myname%s" %  nn)
        self.assertEqual(form.nexusType, "mytype%s" %  nn)
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        self.assertEqual(form.attributes, attributes)
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])


        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertEqual(form.ui.attributeTableWidget.columnCount(),2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(),0)

        
        na =  self.__rnd.randint(0, len(attributes)-1) 
        sel = attributes.keys()[na]
        form.populateAttributes(sel)




        self.assertEqual(form.ui.attributeTableWidget.columnCount(),2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(),len(attributes))
        for i in range(len(attributes)):
            it = form.ui.attributeTableWidget.item(i, 0) 
            k = str(it.text())
            self.assertTrue(k in attributes.keys())
            it2 = form.ui.attributeTableWidget.item(i, 1) 
            self.assertEqual(it2.text(), attributes[k])


        item = form.ui.attributeTableWidget.item(form.ui.attributeTableWidget.currentRow(), 0)
        
        self.assertEqual(item.data(Qt.UserRole).toString(),sel)

        self.aname = "addedAttribute"
        self.avalue = "addedAttributeValue"


        QTimer.singleShot(10, self.attributeWidgetClose)
        QTest.mouseClick(form.ui.addPushButton, Qt.LeftButton)
        



        self.assertEqual(form.ui.attributeTableWidget.columnCount(),2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(),len(attributes))
        for i in range(len(attributes)):
            it = form.ui.attributeTableWidget.item(i, 0) 
            k = str(it.text())
            self.assertTrue(k in attributes.keys())
            it2 = form.ui.attributeTableWidget.item(i, 1) 
            self.assertEqual(it2.text(), attributes[k])


        item = form.ui.attributeTableWidget.item(form.ui.attributeTableWidget.currentRow(), 0)
        
        self.assertEqual(item.data(Qt.UserRole).toString(),sel)

        self.aname = "addedAttribute"
        self.avalue = "addedAttributeValue"

        QTimer.singleShot(10, self.attributeWidget)
        QTest.mouseClick(form.ui.addPushButton, Qt.LeftButton)
        



        self.assertEqual(form.ui.attributeTableWidget.columnCount(),2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(),len(attributes)+1)
        for i in range(len(attributes)+1):
            it = form.ui.attributeTableWidget.item(i, 0) 
            k = str(it.text())
            it2 = form.ui.attributeTableWidget.item(i, 1) 
            if k in attributes.keys():
                self.assertEqual(it2.text(), attributes[k])
            else:
                self.assertEqual(it2.text(), self.avalue)
                
        item = form.ui.attributeTableWidget.item(form.ui.attributeTableWidget.currentRow(), 0)        
        self.assertEqual(item.data(Qt.UserRole).toString(),self.aname)






    ## constructor test
    # \brief It tests default settings
    def test_populateAttribute_setFromNode_selected_removeAttribute(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        dks = []
        doc = QDomDocument()
        nname = "field"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
        qdn.setAttribute("type","mytype%s" %  nn)
        qdn.setAttribute("unit","myunits%s" %  nn)
        qdn.setAttribute("shortname","mynshort%s" %  nn)
        qdn.setAttribute("logname","mynlong%s" %  nn)
        doc.appendChild(qdn) 
        dname = "doc"
        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 



        form = FieldDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_FieldDlg))

        form.createGUI()
        
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        
        form.setFromNode()

        attributes = {u'shortname': u'mynshort%s' % nn, u'logname': u'mynlong%s' %nn, u'unit': u'myunits%s' % nn}

        self.assertEqual(form.name, "myname%s" %  nn)
        self.assertEqual(form.nexusType, "mytype%s" %  nn)
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        self.assertEqual(form.attributes, attributes)
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])


        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertEqual(form.ui.attributeTableWidget.columnCount(),2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(),0)

        
        na =  self.__rnd.randint(0, len(attributes)-1) 
        sel = attributes.keys()[na]
        form.populateAttributes(sel)




        self.assertEqual(form.ui.attributeTableWidget.columnCount(),2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(),len(attributes))
        for i in range(len(attributes)):
            it = form.ui.attributeTableWidget.item(i, 0) 
            k = str(it.text())
            self.assertTrue(k in attributes.keys())
            it2 = form.ui.attributeTableWidget.item(i, 1) 
            self.assertEqual(it2.text(), attributes[k])


        item = form.ui.attributeTableWidget.item(form.ui.attributeTableWidget.currentRow(), 0)
        
        self.assertEqual(item.data(Qt.UserRole).toString(),sel)

        aname = self.__rnd.choice(attributes.keys())
        avalue = attributes[aname]
        
        
        form.populateAttributes(aname)


        QTimer.singleShot(10, self.rmAttributeWidgetClose)
        QTest.mouseClick(form.ui.removePushButton, Qt.LeftButton)
        
        self.assertEqual(self.text,"Remove attribute: %s = '%s'" % (aname,avalue))


        self.assertEqual(form.ui.attributeTableWidget.columnCount(),2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(),len(attributes))
        for i in range(len(attributes)):
            it = form.ui.attributeTableWidget.item(i, 0) 
            k = str(it.text())
            self.assertTrue(k in attributes.keys())
            it2 = form.ui.attributeTableWidget.item(i, 1) 
            self.assertEqual(it2.text(), attributes[k])


        item = form.ui.attributeTableWidget.item(form.ui.attributeTableWidget.currentRow(), 0)




        aname = self.__rnd.choice(attributes.keys())
        avalue = attributes[aname]
        
        
        form.populateAttributes(aname)

        

        QTimer.singleShot(10, self.rmAttributeWidget)
        QTest.mouseClick(form.ui.removePushButton, Qt.LeftButton)
        
        self.assertEqual(self.text,"Remove attribute: %s = '%s'" % (aname,avalue))


        self.assertEqual(form.ui.attributeTableWidget.columnCount(),2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(), len(attributes)-1)
        for i in range(len(attributes)-1):
            it = form.ui.attributeTableWidget.item(i, 0) 
            k = str(it.text())
            self.assertTrue(k in attributes.keys())
            it2 = form.ui.attributeTableWidget.item(i, 1) 
            self.assertEqual(it2.text(), attributes[k])


        item = form.ui.attributeTableWidget.item(form.ui.attributeTableWidget.currentRow(), 0)
        self.assertEqual(item, None)





    ## constructor test
    # \brief It tests default settings
    def test_populateAttribute_setFromNode_selected_tableItemChanged(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        dks = []
        doc = QDomDocument()
        nname = "field"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
        qdn.setAttribute("type","mytype%s" %  nn)
        qdn.setAttribute("unit","myunits%s" %  nn)
        qdn.setAttribute("shortname","mynshort%s" %  nn)
        qdn.setAttribute("logname","mynlong%s" %  nn)
        doc.appendChild(qdn) 
        dname = "doc"
        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 



        form = FieldDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_FieldDlg))

        form.createGUI()

        atw = form.ui.attributeTableWidget        
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        
        form.setFromNode()

        attributes = {u'shortname': u'mynshort%s' % nn, u'logname': u'mynlong%s' %nn, u'unit': u'myunits%s' % nn}

        self.assertEqual(form.name, "myname%s" %  nn)
        self.assertEqual(form.nexusType, "mytype%s" %  nn)
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        self.assertEqual(form.attributes, attributes)
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])


        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertEqual(atw.columnCount(),2)
        self.assertEqual(atw.rowCount(),0)

        
        na =  self.__rnd.randint(0, len(attributes)-1) 
        sel = attributes.keys()[na]
        form.populateAttributes(sel)


        self.assertEqual(atw.columnCount(),2)
        self.assertEqual(atw.rowCount(),len(attributes))
        for i in range(len(attributes)):
            it = atw.item(i, 0) 
            k = str(it.text())
            self.assertTrue(k in attributes.keys())
            it2 = atw.item(i, 1) 
            self.assertEqual(it2.text(), attributes[k])


        item = atw.item(atw.currentRow(), 0)
        self.assertEqual(item.data(Qt.UserRole).toString(), sel)

        ch = self.__rnd.randint(0, len(attributes)-1)
        atw.setCurrentCell(ch,0)
        item = atw.item(atw.currentRow(), 0)
        aname = str(item.data(Qt.UserRole).toString())

        it = QTableWidgetItem(unicode(aname))
        it.setData(Qt.DisplayRole, QVariant(aname+"_"+attributes[aname]))
        it.setData(Qt.UserRole, QVariant(aname))

        atw.setCurrentCell(ch,0)

        QTimer.singleShot(10, self.checkMessageBox)
        atw.setItem(ch,0,it)
        self.assertEqual(self.text, 
                         "To change the attribute name, please remove the attribute and add the new one")
        

        avalue = attributes[str(aname)]
                

        self.assertEqual(atw.columnCount(),2)
        self.assertEqual(atw.rowCount(),len(attributes))
        for i in range(len(attributes)):
            it = atw.item(i, 0) 
            k = str(it.text())
            self.assertTrue(k in attributes.keys())
            it2 = atw.item(i, 1) 
            self.assertEqual(it2.text(), attributes[k])




        it = QTableWidgetItem(unicode(aname))
        it.setData(Qt.DisplayRole, QVariant(aname+"_"+attributes[aname]))
        it.setData(Qt.UserRole, QVariant(aname))

        atw.setCurrentCell(ch,1)

        atw.setItem(ch,1,it)
        

        avalue = attributes[str(aname)]
                

        self.assertEqual(atw.columnCount(),2)
        self.assertEqual(atw.rowCount(),len(attributes))
        for i in range(len(attributes)):
            it = atw.item(i, 0)
            k = str(it.text())
            if k != aname:
                self.assertTrue(k in attributes.keys())
                it2 = atw.item(i, 1) 
                self.assertEqual(it2.text(), attributes[k])
            else:
                it2 = atw.item(i, 1) 
                self.assertEqual(it2.text(), QVariant(aname+"_"+attributes[aname]))




    ## constructor test
    # \brief It tests default settings
    def ttest_updateNode(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        dks = []
        doc = QDomDocument()
        nname = "field"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
        qdn.setAttribute("type","mytype%s" %  nn)
        qdn.setAttribute("unit","myunits%s" %  nn)
        qdn.setAttribute("shortname","mynshort%s" %  nn)
        doc.appendChild(qdn) 
        dname = "doc"
        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 



        form = FieldDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_FieldDlg))

        form.setFromNode()
        form.createGUI()

        allAttr = True
        cm = ComponentModel(doc,allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        nname = "newname"
        ntype = "newtype"
        attrs = {"unit":"newunit","longname":"newlogname"}
        mdoc = "New text \nNew text"

        attributeMap = form.node.attributes()
        
        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "name":
                self.assertEqual(vl,form.name)
                cnt += 1 
            elif nm == "type":
                self.assertEqual(vl,form.nexusType)
                cnt += 1 
            else:
                self.assertEqual(vl,form.attributes[str(nm)])
        self.assertEqual(len(form.attributes),attributeMap.count() - cnt)


        mydoc = form.node.firstChildElement(QString("doc"))           
        text = form.dts.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""

        self.assertEqual(olddoc,form.doc)



        form.name = nname
        form.nexusType = ntype
        form.attributes.clear()
        for at in attrs.keys() :
            form.attributes[at] =  attrs[at]
        form.doc = mdoc

        form.root = doc

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        form.updateNode()

        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "name":
                self.assertEqual(vl, nname)
                cnt += 1 
            elif nm == "type":
                self.assertEqual(vl, ntype)
                cnt += 1 
            else:
                self.assertEqual(vl,attrs[str(nm)])
        self.assertEqual(len(attrs),attributeMap.count() - cnt)


        mydoc = form.node.firstChildElement(QString("doc"))           
        text = form.dts.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""

        self.assertEqual(olddoc,mdoc)



    ## constructor test
    # \brief It tests default settings
    def test_updateNode_withindex(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        dks = []
        doc = QDomDocument()
        nname = "group"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
        qdn.setAttribute("type","mytype%s" %  nn)
        qdn.setAttribute("unit","myunits%s" %  nn)
        qdn.setAttribute("shortname","mynshort%s" %  nn)
        doc.appendChild(qdn) 
        dname = "doc"
        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 



        form = FieldDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_FieldDlg))

        form.setFromNode()
        form.createGUI()

        allAttr = True
        cm = ComponentModel(doc,allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        nname = "newname"
        ntype = "newtype"
        attrs = {"unit":"newunit","longname":"newlogname"}
        mdoc = "New text \nNew text"

        attributeMap = form.node.attributes()
        
        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "name":
                self.assertEqual(vl,form.name)
                cnt += 1 
            elif nm == "type":
                self.assertEqual(vl,form.nexusType)
                cnt += 1 
            else:
                self.assertEqual(vl,form.attributes[str(nm)])
        self.assertEqual(len(form.attributes),attributeMap.count() - cnt)


        mydoc = form.node.firstChildElement(QString("doc"))           
        text = form.dts.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""

        self.assertEqual(olddoc,form.doc)



        form.name = nname
        form.nexusType = ntype
        form.attributes.clear()
        for at in attrs.keys() :
            form.attributes[at] =  attrs[at]
        form.doc = mdoc

        form.root = doc

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        form.updateNode(di)

        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "name":
                self.assertEqual(vl, nname)
                cnt += 1 
            elif nm == "type":
                self.assertEqual(vl, ntype)
                cnt += 1 
            else:
                self.assertEqual(vl,attrs[str(nm)])
        self.assertEqual(len(attrs),attributeMap.count() - cnt)


        mydoc = form.node.firstChildElement(QString("doc"))           
        text = form.dts.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""

        self.assertEqual(olddoc,mdoc)




    ## constructor test
    # \brief It tests default settings
    def test_apply(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        dks = []
        doc = QDomDocument()
        nname = "field"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
        qdn.setAttribute("type","mytype%s" %  nn)
        qdn.setAttribute("unit","myunits%s" %  nn)
        qdn.setAttribute("shortname","mynshort%s" %  nn)
        doc.appendChild(qdn) 
        dname = "doc"
        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 



        form = FieldDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_FieldDlg))

        form.setFromNode()
        form.createGUI()

        allAttr = True
        cm = ComponentModel(doc,allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di


        attributeMap = form.node.attributes()
        
        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "name":
                self.assertEqual(vl,form.name)
                cnt += 1 
            elif nm == "type":
                self.assertEqual(vl,form.nexusType)
                cnt += 1 
            else:
                self.assertEqual(vl,form.attributes[str(nm)])
        self.assertEqual(len(form.attributes),attributeMap.count() - cnt)


        mydoc = form.node.firstChildElement(QString("doc"))           
        text = form.dts.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""

        self.assertEqual(olddoc,form.doc)


        nname = "newname"
        ntype = "newtype"
        attrs = {"unit":"newunit","longname":"newlogname", "mynew":"newvalue"}
        mdoc = "New text New text"



        form.root = doc

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di


        form.ui.nameLineEdit.setText(nname)
        form.ui.typeLineEdit.setText(ntype)

        form.ui.docTextEdit.setText(str(mdoc))
        form.ui.docTextEdit.setText(str(mdoc))
        
        
        
        for r in form.attributes:
            form.ui.attributeTableWidget.setCurrentCell(0,1)
            item = form.ui.attributeTableWidget.item(form.ui.attributeTableWidget.currentRow(), 0) 
            print item.text()


            QTimer.singleShot(10, self.rmAttributeWidget)
            QTest.mouseClick(form.ui.removePushButton, Qt.LeftButton)



        i = 0
        for r in attrs:
            form.ui.attributeTableWidget.setCurrentCell(i,1)
            self.aname = r
            self.avalue = attrs[r]
            QTimer.singleShot(10, self.attributeWidget)
            QTest.mouseClick(form.ui.addPushButton, Qt.LeftButton)
            i += 1

        form.apply()


        self.assertEqual(form.name, nname)
        self.assertEqual(form.nexusType, ntype)
        self.assertEqual(form.doc, mdoc)
        self.assertEqual(form.attributes, attrs)


        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "name":
                self.assertEqual(vl, nname)
                cnt += 1 
            elif nm == "type":
                self.assertEqual(vl, ntype)
                cnt += 1 
            else:
                self.assertEqual(vl,attrs[str(nm)])
        self.assertEqual(len(attrs),attributeMap.count() - cnt)


        mydoc = form.node.firstChildElement(QString("doc"))           
        text = form.dts.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""

        self.assertEqual(olddoc,mdoc)





    ## constructor test
    # \brief It tests default settings
    def test_reset(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        dks = []
        doc = QDomDocument()
        nname = "group"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
        qdn.setAttribute("type","mytype%s" %  nn)
        qdn.setAttribute("unit","myunits%s" %  nn)
        qdn.setAttribute("shortname","mynshort%s" %  nn)
        doc.appendChild(qdn) 
        dname = "doc"
        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 



        form = FieldDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_FieldDlg))

        form.setFromNode()
        form.createGUI()

        allAttr = True
        cm = ComponentModel(doc,allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di


        attributeMap = form.node.attributes()
        
        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "name":
                self.assertEqual(vl,form.name)
                cnt += 1 
            elif nm == "type":
                self.assertEqual(vl,form.nexusType)
                cnt += 1 
            else:
                self.assertEqual(vl,form.attributes[str(nm)])
        self.assertEqual(len(form.attributes),attributeMap.count() - cnt)


        mydoc = form.node.firstChildElement(QString("doc"))           
        text = form.dts.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""

        self.assertEqual(olddoc,form.doc)


        nname = "newname"
        ntype = "newtype"
        attrs = {"unit":"newunit","longname":"newlogname", "mynew":"newvalue"}
        mdoc = "New text New text"



        form.root = doc

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di


        form.ui.nameLineEdit.setText(nname)
        form.ui.typeLineEdit.setText(ntype)

        form.ui.docTextEdit.setText(str(mdoc))
        form.ui.docTextEdit.setText(str(mdoc))
        
        
        
        for r in form.attributes:
            form.ui.attributeTableWidget.setCurrentCell(0,1)
            item = form.ui.attributeTableWidget.item(form.ui.attributeTableWidget.currentRow(), 0) 
            print item.text()


            QTimer.singleShot(10, self.rmAttributeWidget)
            QTest.mouseClick(form.ui.removePushButton, Qt.LeftButton)



        i = 0
        for r in attrs:
            form.ui.attributeTableWidget.setCurrentCell(i,1)
            self.aname = r
            self.avalue = attrs[r]
            QTimer.singleShot(10, self.attributeWidget)
            QTest.mouseClick(form.ui.addPushButton, Qt.LeftButton)
            i += 1

        form.reset()

        ats= {u'shortname': u'mynshort%s' % nn, u'unit': u'myunits%s' % nn}
        self.assertEqual(form.name, "myname%s" %  nn)
        self.assertEqual(form.nexusType, "mytype%s" %  nn)
        self.assertEqual(form.doc, ("".join(["\nText\n %s\n" %  i  for i in range(ndcs)])).strip()) 
        self.assertEqual(form.attributes,  ats )


        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "name":
                self.assertEqual(vl, "myname%s" % nn)
                cnt += 1 
            elif nm == "type":
                self.assertEqual(vl, "mytype%s" % nn)
                cnt += 1 
            else:
                self.assertEqual(vl,ats[str(nm)])
        self.assertEqual(len(ats),attributeMap.count() - cnt)


        mydoc = form.node.firstChildElement(QString("doc"))           
        text = form.dts.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc, ("".join(["\nText\n %s\n" %  i  for i in range(ndcs)])).strip())




    ## constructor test
    # \brief It tests default settings
    def test_reset_button(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        dks = []
        doc = QDomDocument()
        nname = "field"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
        qdn.setAttribute("type","mytype%s" %  nn)
        qdn.setAttribute("unit","myunits%s" %  nn)
        qdn.setAttribute("shortname","mynshort%s" %  nn)
        doc.appendChild(qdn) 
        dname = "doc"
        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 



        form = FieldDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_FieldDlg))

        form.setFromNode()
        form.createGUI()

        allAttr = True
        cm = ComponentModel(doc,allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di


        attributeMap = form.node.attributes()
        
        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "name":
                self.assertEqual(vl,form.name)
                cnt += 1 
            elif nm == "type":
                self.assertEqual(vl,form.nexusType)
                cnt += 1 
            else:
                self.assertEqual(vl,form.attributes[str(nm)])
        self.assertEqual(len(form.attributes),attributeMap.count() - cnt)


        mydoc = form.node.firstChildElement(QString("doc"))           
        text = form.dts.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""

        self.assertEqual(olddoc,form.doc)


        nname = "newname"
        ntype = "newtype"
        attrs = {"unit":"newunit","longname":"newlogname", "mynew":"newvalue"}
        mdoc = "New text New text"



        form.root = doc

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di


        form.ui.nameLineEdit.setText(nname)
        form.ui.typeLineEdit.setText(ntype)

        form.ui.docTextEdit.setText(str(mdoc))
        form.ui.docTextEdit.setText(str(mdoc))
        
        
        
        for r in form.attributes:
            form.ui.attributeTableWidget.setCurrentCell(0,1)
            item = form.ui.attributeTableWidget.item(form.ui.attributeTableWidget.currentRow(), 0) 
            print item.text()


            QTimer.singleShot(10, self.rmAttributeWidget)
            QTest.mouseClick(form.ui.removePushButton, Qt.LeftButton)



        i = 0
        for r in attrs:
            form.ui.attributeTableWidget.setCurrentCell(i,1)
            self.aname = r
            self.avalue = attrs[r]
            QTimer.singleShot(10, self.attributeWidget)
            QTest.mouseClick(form.ui.addPushButton, Qt.LeftButton)
            i += 1

        QTest.mouseClick(form.ui.resetPushButton, Qt.LeftButton)

        ats= {u'shortname': u'mynshort%s' % nn, u'unit': u'myunits%s' % nn}
        self.assertEqual(form.name, "myname%s" %  nn)
        self.assertEqual(form.nexusType, "mytype%s" %  nn)
        self.assertEqual(form.doc, ("".join(["\nText\n %s\n" %  i  for i in range(ndcs)])).strip()) 
        self.assertEqual(form.attributes,  ats )


        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "name":
                self.assertEqual(vl, "myname%s" % nn)
                cnt += 1 
            elif nm == "type":
                self.assertEqual(vl, "mytype%s" % nn)
                cnt += 1 
            else:
                self.assertEqual(vl,ats[str(nm)])
        self.assertEqual(len(ats),attributeMap.count() - cnt)


        mydoc = form.node.firstChildElement(QString("doc"))           
        text = form.dts.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc, ("".join(["\nText\n %s\n" %  i  for i in range(ndcs)])).strip())





    def myAction(self):
        self.performed = True


    ## constructor test


    ## constructor test
    # \brief It tests default settings
    def test_connect_actions(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = FieldDlg()
        form.show()
        self.assertEqual(form.connectExternalActions(),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui, Ui_FieldDlg))
        self.assertEqual(form.externalApply, None)
        self.assertEqual(form.externalDSLink, None)
#        self.assertTrue(isinstance(form.dts, DomTools))

        self.assertEqual(form.result(),0)

    ## constructor test
    # \brief It tests default settings
    def test_connect_actions_with_action(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = FieldDlg()
        form.show()
        self.assertEqual(form.connectExternalActions(self.myAction),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui, Ui_FieldDlg))
        self.assertEqual(form.externalApply, None)


        self.assertEqual(form.result(),0)




    ## constructor test
    # \brief It tests default settings
    def test_connect_actions_with_button(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = FieldDlg()
        form.ui = Ui_FieldDlg() 
        form.ui.applyPushButton = QPushButton(form)
        form.ui.linkDSPushButton = QPushButton(form)
        form.show()
        self.assertEqual(form.connectExternalActions(),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui,Ui_FieldDlg))
        self.assertEqual(form.externalApply, None)
        self.assertEqual(form.externalDSLink, None)


        self.assertEqual(form.result(),0)



    ## constructor test
    # \brief It tests default settings
    def test_connect_actions_with_action_button(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = FieldDlg()
        form.ui = Ui_FieldDlg() 
        form.ui.applyPushButton = QPushButton(form)
        form.show()
        self.assertEqual(form.connectExternalActions(self.myAction),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui,Ui_FieldDlg))
        self.assertEqual(form.externalApply, self.myAction)
        self.performed = False

        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)
        self.assertEqual(self.performed, True)


        self.assertEqual(form.result(),0)




    ## constructor test
    # \brief It tests default settings
    def test_connect_actions_with_action_button(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = FieldDlg()
        form.ui = Ui_FieldDlg() 
        form.ui.applyPushButton = QPushButton(form)
        form.show()
        self.assertEqual(form.connectExternalActions(self.myAction),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui,Ui_FieldDlg))
        self.assertEqual(form.externalApply, self.myAction)
        self.performed = False

        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)
        self.assertEqual(self.performed, True)


        self.assertEqual(form.result(),0)




    ## constructor test
    # \brief It tests default settings
    def ttest_connect_actions_with_action_link_button(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = FieldDlg()
        form.createGUI()
        form.show()
        self.assertEqual(form.connectExternalActions(None,self.myAction),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui,Ui_FieldDlg))
        self.assertEqual(form.externalDSLink, None)
        self.performed = False



        self.assertEqual(form.result(),0)




    ## constructor test
    # \brief It tests default settings
    def ttest_connect_actions_with_action_link_and_apply_button(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = FieldDlg()
        form.ui = Ui_FieldDlg() 
        form.ui.applyPushButton = QPushButton(form)
        form.createGUI()
        form.show()
        self.assertEqual(form.connectExternalActions(self.myAction,None),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui,Ui_FieldDlg))
        self.assertEqual(form.externalApply, self.myAction)
        self.assertEqual(form.externalDSLink, None)
        self.performed = False

        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)
        self.assertEqual(self.performed, False)


        self.assertEqual(form.result(),0)




    ## constructor test
    # \brief It tests default settings
    def ttest_connect_actions_with_action_link_and_apply_button(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = FieldDlg()
        form.ui = Ui_FieldDlg() 
        form.ui.applyPushButton = QPushButton(form)
        form.createGUI()
        QTest.keyClicks(form.ui.typeLineEdit, "namename")

        form.show()
        self.assertEqual(form.connectExternalActions(self.myAction,None),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui,Ui_FieldDlg))
        self.assertEqual(form.externalApply, self.myAction)
        self.assertEqual(form.externalDSLink, None)
        self.performed = False

        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)
        self.assertEqual(self.performed, True)


        self.assertEqual(form.result(),0)








if __name__ == '__main__':
    if not app:
        app = QApplication([])
    unittest.main()
