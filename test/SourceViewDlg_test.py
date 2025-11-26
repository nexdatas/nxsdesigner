#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2017 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
# \package test nexdatas
# \file SourceViewDlgTest.py
# unittests for sourceview Tags running Tango Server
#
import unittest
import os
import sys
import random
import struct
import binascii
import time

from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import (QApplication, QMessageBox,
                             QTableWidgetItem, QPushButton)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtXml import QDomDocument

from nxsconfigtool.SourceViewDlg import SourceViewDlg
from nxsconfigtool.ComponentModel import ComponentModel
from nxsconfigtool.AttributeDlg import AttributeDlg
from nxsconfigtool.NodeDlg import NodeDlg
from nxsconfigtool.DimensionsDlg import DimensionsDlg

# from nxsconfigtool.ui.ui_sourceviewdlg import Ui_SourceViewDlg
from nxsconfigtool.DomTools import DomTools

#  Qt-application
app = None

if sys.version_info > (3,):
    unicode = str
    long = int

# if 64-bit machione
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


# test fixture
class SourceViewDlgTest(unittest.TestCase):

    # constructor
    # \param methodName name of the test method
    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"
        # MessageBox text
        self.text = None
        # MessageBox title
        self.title = None

        # attribute name
        self.aname = "myname"
        # attribute value
        self.avalue = "myentry"

        self.dimensions = [1, 2, 3, 4]

        # action status
        self.performed = False

        try:
            self.__seed = long(binascii.hexlify(os.urandom(16)), 16)
        except NotImplementedError:
            self.__seed = long(time.time() * 256)

        self.__rnd = random.Random(self.__seed)

    # test starter
    # \brief Common set up
    def setUp(self):
        print("\nsetting up...")
        print("SEED = %s" % self.__seed)

    # test closer
    # \brief Common tear down
    def tearDown(self):
        print("tearing down ...")

    def checkMessageBox(self):
        # self.assertEqual(QApplication.activeWindow(), None)
        mb = QApplication.activeModalWidget()
        self.assertTrue(isinstance(mb, QMessageBox))
#        print mb.text()
        self.text = mb.text()
        self.title = mb.windowTitle()
        mb.close()

    def rmAttributeWidget(self):
        # aw =
        QApplication.activeWindow()
        mb = QApplication.activeModalWidget()
        self.assertTrue(isinstance(mb, QMessageBox))
        self.text = mb.text()
        self.title = mb.windowTitle()

        QTest.mouseClick(mb.button(QMessageBox.Yes), Qt.LeftButton)

    def rmAttributeWidgetClose(self):
        # aw =
        QApplication.activeWindow()
        mb = QApplication.activeModalWidget()
        self.assertTrue(isinstance(mb, QMessageBox))
        self.text = mb.text()
        self.title = mb.windowTitle()

        QTest.mouseClick(mb.button(QMessageBox.No), Qt.LeftButton)

    def attributeWidget(self):
        # aw =
        QApplication.activeWindow()
        mb = QApplication.activeModalWidget()
        self.assertTrue(isinstance(mb, AttributeDlg))

        QTest.keyClicks(mb.ui.nameLineEdit, self.aname)
        self.assertEqual(mb.ui.nameLineEdit.text(), self.aname)
        QTest.keyClicks(mb.ui.valueLineEdit, self.avalue)
        self.assertEqual(mb.ui.valueLineEdit.text(), self.avalue)

        mb.accept()

    def dimensionsWidget(self):
        # aw =
        QApplication.activeWindow()
        mb = QApplication.activeModalWidget()
        self.assertTrue(isinstance(mb, DimensionsDlg))
        self.assertTrue(hasattr(mb, "ui"))

        mb.ui.rankSpinBox.setValue(len(self.dimensions))

        for r in range(len(self.dimensions)):
            mb.ui.dimTableWidget.setCurrentCell(r, 0)
            it = QTableWidgetItem(unicode(self.dimensions[r]))
            mb.ui.dimTableWidget.setItem(r, 0, it)

#        QTest.keyClicks(mb.ui.nameLineEdit, self.aname)
#        self.assertEqual(mb.ui.nameLineEdit.text(), self.aname)
#        QTest.keyClicks(mb.ui.valueLineEdit, self.avalue)
#        self.assertEqual(mb.ui.valueLineEdit.text(), self.avalue)

        mb.accept()

    def attributeWidgetClose(self):
        # aw =
        QApplication.activeWindow()
        mb = QApplication.activeModalWidget()
        self.assertTrue(isinstance(mb, AttributeDlg))

        QTest.keyClicks(mb.ui.nameLineEdit, self.aname)
        self.assertEqual(mb.ui.nameLineEdit.text(), self.aname)
        QTest.keyClicks(mb.ui.valueLineEdit, self.avalue)
        self.assertEqual(mb.ui.valueLineEdit.text(), self.avalue)

#        mb.close()
        mb.reject()

#        mb.accept()

    # constructor test
    # \brief It tests default settings
    def test_constructor(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        form = SourceViewDlg()
        form.show()
        self.assertEqual(form.doc, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.selection, [])
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(
            form.subItems,
            ['datasource', 'doc', 'dimensions',
             'selection', 'enumeration', 'strategy'])
        self.assertEqual(form.ui.__class__.__name__, "Ui_SourceViewDlg")
        self.assertTrue(isinstance(form, NodeDlg))
        self.assertEqual(form.externalApply, None)
        self.assertEqual(form.externalDSLink, None)

        self.assertEqual(form.replaceText,
                         super(SourceViewDlg, form).replaceText)
        self.assertEqual(form.removeElement,
                         super(SourceViewDlg, form).removeElement)
        self.assertEqual(form.replaceElement,
                         super(SourceViewDlg, form).replaceElement)
        self.assertTrue(form.appendElement is not
                        super(SourceViewDlg, form).appendElement)
        self.assertEqual(form.reset, super(SourceViewDlg, form).reset)

    # constructor test
    # \brief It tests default settings
    def test_constructor_accept(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        form = SourceViewDlg()
        form.show()
        self.assertEqual(form.doc, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.selection, [])
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(
            form.subItems,
            ['datasource', 'doc', 'dimensions',
             'selection', 'enumeration', 'strategy'])
        self.assertEqual(form.ui.__class__.__name__, "Ui_SourceViewDlg")

        form.createGUI()

        self.assertTrue(form.ui.applyPushButton.isEnabled())
        self.assertTrue(form.ui.resetPushButton.isEnabled())

        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)

#        form.apply()
#        self.assertEqual(form.name, name)

        self.assertEqual(form.result(), 0)

    # constructor test
    # \brief It tests default settings
    def test_constructor_accept_long(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        form = SourceViewDlg()
        form.show()
        self.assertEqual(form.doc, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.selection, [])
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(
            form.subItems,
            ['datasource', 'doc', 'dimensions',
             'selection', 'enumeration', 'strategy'])
        self.assertEqual(form.ui.__class__.__name__, "Ui_SourceViewDlg")

        form.createGUI()

        self.assertTrue(not form.ui.docTextEdit.toPlainText())
        self.assertEqual(form.ui.dimLabel.text(), '[]')

        self.assertTrue(form.ui.applyPushButton.isEnabled())
        self.assertTrue(form.ui.resetPushButton.isEnabled())

        self.assertTrue(not form.ui.docTextEdit.toPlainText())
        self.assertEqual(form.ui.dimLabel.text(), '[]')

        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)

#        form.apply()
#        self.assertEqual(form.name, name)

        self.assertEqual(form.result(), 0)

    # constructor test
    # \brief It tests default settings
    def test_updateForm(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        form = SourceViewDlg()
        form.show()
        self.assertEqual(form.doc, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.selection, [])
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(
            form.subItems,
            ['datasource', 'doc', 'dimensions',
             'selection', 'enumeration', 'strategy'])
        self.assertEqual(form.ui.__class__.__name__, "Ui_SourceViewDlg")

        form.createGUI()

        self.assertTrue(not form.ui.docTextEdit.toPlainText())
        self.assertEqual(form.ui.dimLabel.text(), '[]')
        self.assertEqual(form.ui.selLabel.text(), '[]')

        doc = "My documentation: \n ble ble ble "
        nn = self.__rnd.randint(1, 9)

        dimensions = [str(self.__rnd.randint(1, 40)) for n in range(nn)]

        self.assertEqual(form.updateForm(), None)

        self.assertTrue(not form.ui.docTextEdit.toPlainText())
        self.assertEqual(form.ui.dimLabel.text(), '[]')

        self.assertTrue(not form.ui.docTextEdit.toPlainText())
        self.assertEqual(form.ui.dimLabel.text(), '[]')

        self.assertEqual(form.updateForm(), None)

        self.assertTrue(not form.ui.docTextEdit.toPlainText())
        self.assertEqual(form.ui.dimLabel.text(), '[]')

        self.assertTrue(not form.ui.docTextEdit.toPlainText())
        self.assertEqual(form.ui.dimLabel.text(), '[]')

        self.assertEqual(form.updateForm(), None)

        self.assertTrue(not form.ui.docTextEdit.toPlainText())
        self.assertEqual(form.ui.dimLabel.text(), '[]')

        self.assertTrue(not form.ui.docTextEdit.toPlainText())
        self.assertEqual(form.ui.dimLabel.text(), '[]')

        self.assertEqual(form.updateForm(), None)

        self.assertTrue(not form.ui.docTextEdit.toPlainText())
        self.assertEqual(form.ui.dimLabel.text(), '[]')

        form.dimensions = dimensions

        self.assertTrue(not form.ui.docTextEdit.toPlainText())
        self.assertEqual(form.ui.dimLabel.text(), '[]')

        self.assertEqual(form.updateForm(), None)

        self.assertTrue(not form.ui.docTextEdit.toPlainText())
        self.assertEqual(form.ui.dimLabel.text(), str(dimensions))
        self.assertEqual(form.rank, len(dimensions))

        form.ui.dimLabel.setText("[]")
        form.dimensions = []

        self.assertTrue(not form.ui.docTextEdit.toPlainText())
        self.assertEqual(form.ui.dimLabel.text(), '[]')
        self.assertEqual(form.rank, len(dimensions))

        self.assertEqual(form.updateForm(), None)

        self.assertTrue(not form.ui.docTextEdit.toPlainText())
        self.assertEqual(
            form.ui.dimLabel.text(),
            str([0]*len(dimensions)).replace('0', '*'))
        self.assertEqual(form.rank, len(dimensions))

        form.ui.dimLabel.setText("[]")
        form.dimensions = []
        form.rank = 0

        form.doc = doc

        self.assertTrue(not form.ui.docTextEdit.toPlainText())
        self.assertEqual(form.ui.dimLabel.text(), '[]')

        self.assertEqual(form.updateForm(), None)

        self.assertEqual(form.ui.docTextEdit.toPlainText(), doc)
        self.assertEqual(form.ui.dimLabel.text(), '[]')

        form.ui.docTextEdit.setText("")

        form.doc = doc

        self.assertTrue(not form.ui.docTextEdit.toPlainText())

        self.assertEqual(form.updateForm(), None)

        self.assertEqual(form.ui.docTextEdit.toPlainText(), doc)

        self.assertEqual(form.ui.docTextEdit.toPlainText(), doc)

        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)

        self.assertEqual(form.result(), 0)

    # constructor test
    # \brief It tests default settings
    def test_getState(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        form = SourceViewDlg()
        form.show()

        self.assertEqual(form.doc, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.selection, [])
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(
            form.subItems,
            ['datasource', 'doc', 'dimensions',
             'selection', 'enumeration', 'strategy'])
        self.assertEqual(form.ui.__class__.__name__, "Ui_SourceViewDlg")

        form.createGUI()

        doc = "My documentation: \n ble ble ble "
        rank = 3
        dimensions = [1, 2, 3, 4]
        selection = [[1, 3, None], [None, 4, None], [2, 10, 2]]
        self.assertEqual(form.getState(), ('', 0,  [], []))

        form.doc = doc
        self.assertEqual(form.getState(), (doc, 0,  [], []))
        self.assertTrue(not form.ui.docTextEdit.toPlainText())
        self.assertEqual(form.ui.dimLabel.text(), '[]')
        form.doc = ""

        form.rank = rank
        self.assertEqual(form.getState(), ('', rank, [], []))
        self.assertTrue(not form.ui.docTextEdit.toPlainText())
        self.assertEqual(form.ui.dimLabel.text(), '[]')
        self.assertEqual(form.ui.selLabel.text(), '[]')
        form.rank = 0

        form.dimensions = dimensions
        state = form.getState()

        self.assertEqual(state[0], '')
        self.assertEqual(state[1], 0)
        self.assertEqual(state[3], [])
        self.assertEqual(len(state), 4)
        self.assertEqual(len(state[2]), len(dimensions))
        for i in range(len(dimensions)):
            self.assertEqual(dimensions[i], state[2][i])
        self.assertTrue(not form.ui.docTextEdit.toPlainText())
        self.assertEqual(form.ui.dimLabel.text(), '[]')

        form.dimensions = []

        form.selection = selection
        state = form.getState()

        self.assertEqual(state[0], '')
        self.assertEqual(state[1], 0)
        self.assertEqual(state[2], [])
        self.assertEqual(len(state), 4)
        self.assertEqual(len(state[3]), len(selection))
        for i in range(len(selection)):
            self.assertEqual(selection[i], state[3][i])

        self.assertTrue(not form.ui.docTextEdit.toPlainText())
        self.assertEqual(form.ui.dimLabel.text(), '[]')

        form.selection = []

        form.doc = doc
        form.rank = rank
        form.dimensions = dimensions
        form.selection = selection

        state = form.getState()

        self.assertEqual(state[0], doc)
        self.assertEqual(state[1], rank)
        self.assertEqual(len(state), 4)
        self.assertEqual(len(state[2]), len(dimensions))
        for i in range(len(dimensions)):
            self.assertEqual(dimensions[i], state[2][i])
        self.assertEqual(len(state[3]), len(selection))
        for i in range(len(selection)):
            self.assertEqual(selection[i], state[3][i])

        self.assertTrue(not form.ui.docTextEdit.toPlainText())
        self.assertEqual(form.ui.dimLabel.text(), '[]')

        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)

        self.assertEqual(form.result(), 0)

    # constructor test
    # \brief It tests default settings
    def test_setState(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        form = SourceViewDlg()
        form.show()

        self.assertEqual(form.doc, '')
        self.assertEqual(form.rank, 0)
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.selection, [])
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(
            form.subItems,
            ['datasource', 'doc', 'dimensions',
             'selection', 'enumeration', 'strategy'])
        self.assertEqual(form.ui.__class__.__name__, "Ui_SourceViewDlg")

        form.createGUI()

        doc = "My documentation: \n ble ble ble "
        rank = 3
        dimensions = [1, 2, 3, 4]
        selection = [[1, 3, None], [None, 4, None], [2, 10, 2]]

        self.assertEqual(form.setState(['',  0, [], []]), None)

        self.assertTrue(not form.ui.docTextEdit.toPlainText())
        self.assertEqual(form.ui.dimLabel.text(), '[]')
        self.assertEqual(form.ui.selLabel.text(), '[]')

        self.assertEqual(form.doc, '')
        self.assertEqual(form.rank, 0)
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.selection, [])

        self.assertEqual(form.setState([doc, 0, [], []]), None)

        self.assertEqual(form.ui.dimLabel.text(), '[]')
        self.assertEqual(form.ui.selLabel.text(), '[]')

        self.assertEqual(form.doc, doc)
        self.assertEqual(form.rank, 0)
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.selection, [])

        form.doc = ''

        self.assertEqual(
            form.setState(['', rank, [], []]), None)

        self.assertTrue(not form.ui.docTextEdit.toPlainText())
        self.assertEqual(form.ui.dimLabel.text(), '[]')

        self.assertEqual(form.doc, '')
        self.assertEqual(form.rank, rank)
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.selection, [])

        form.rank = 0

        self.assertEqual(
            form.setState(['', 0, dimensions, []]), None)

        self.assertTrue(not form.ui.docTextEdit.toPlainText())
        self.assertEqual(form.ui.dimLabel.text(), '[]')
        self.assertEqual(form.ui.selLabel.text(), '[]')

        self.assertEqual(form.doc, '')
        self.assertEqual(form.rank, 0)
        self.assertEqual(form.dimensions, dimensions)
        self.assertEqual(form.selection, [])

        form.dimensions = []

        self.assertEqual(
            form.setState(['', 0, [], selection]), None)

        self.assertTrue(not form.ui.docTextEdit.toPlainText())
        self.assertEqual(form.ui.dimLabel.text(), '[]')

        self.assertEqual(form.doc, '')
        self.assertEqual(form.rank, 0)
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.selection, selection)

        form.selection = {}

        self.assertEqual(
            form.setState([doc, rank, dimensions, selection]), None)

        self.assertTrue(not form.ui.docTextEdit.toPlainText())
        self.assertEqual(form.ui.dimLabel.text(), '[]')
        self.assertEqual(form.ui.selLabel.text(), '[]')

        self.assertEqual(form.doc, doc)
        self.assertEqual(form.rank, rank)
        self.assertEqual(form.dimensions, dimensions)
        self.assertEqual(form.selection, selection)

        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)

        self.assertEqual(form.result(), 0)

    # constructor test
    # \brief It tests default settings
    def test_createGUI(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        form = SourceViewDlg()
        form.show()
        self.assertEqual(form.doc, '')
        self.assertEqual(form.rank, 0)
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.selection, [])
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(
            form.subItems,
            ['datasource', 'doc', 'dimensions',
             'selection', 'enumeration', 'strategy'])
        self.assertEqual(form.ui.__class__.__name__, "Ui_SourceViewDlg")

        form = SourceViewDlg()
        form.show()
        self.assertEqual(form.createGUI(), None)

        self.assertTrue(not form.ui.docTextEdit.toPlainText())
        self.assertEqual(form.ui.dimLabel.text(), '[]')
        self.assertEqual(form.ui.selLabel.text(), '[]')

        doc = "My documentation: \n ble ble ble "
        nn = self.__rnd.randint(1, 9)

        dimensions = [self.__rnd.randint(1, 40) for n in range(nn)]

        self.assertEqual(form.updateForm(), None)

        form = SourceViewDlg()
        form.show()

        form = SourceViewDlg()
        form.show()

        self.assertEqual(form.createGUI(), None)

        self.assertTrue(not form.ui.docTextEdit.toPlainText())
        self.assertEqual(form.rank, 0)
        self.assertEqual(form.ui.dimLabel.text(), '[]')
        self.assertEqual(form.ui.selLabel.text(), '[]')

        form = SourceViewDlg()
        form.show()

        self.assertEqual(form.createGUI(), None)

        self.assertTrue(not form.ui.docTextEdit.toPlainText())
        self.assertEqual(form.rank, 0)
        self.assertEqual(form.ui.dimLabel.text(), '[]')
        self.assertEqual(form.ui.selLabel.text(), '[]')

        form = SourceViewDlg()
        form.show()
        form.dimensions = dimensions

        self.assertEqual(form.createGUI(), None)

        self.assertTrue(not form.ui.docTextEdit.toPlainText())
        self.assertEqual(form.ui.dimLabel.text(), str(dimensions))
        self.assertEqual(form.rank, len(dimensions))
        form.ui.dimLabel.setText("[]")
        form.dimensions = []

        form = SourceViewDlg()
        form.show()

        form.rank = nn
        self.assertEqual(form.createGUI(), None)

        self.assertTrue(not form.ui.docTextEdit.toPlainText())
        self.assertEqual(
            form.ui.dimLabel.text(),
            str([0]*len(dimensions)).replace('0', '*'))
        self.assertEqual(form.rank, len(dimensions))

        form.ui.dimLabel.setText("[]")
        form.dimensions = []
        form.rank = 0

        form = SourceViewDlg()
        form.show()
        form.doc = doc

        self.assertEqual(form.createGUI(), None)

        self.assertEqual(form.ui.docTextEdit.toPlainText(), doc)
        self.assertEqual(form.ui.dimLabel.text(), '[]')

        form.ui.docTextEdit.setText("")

        form = SourceViewDlg()
        form.show()
        form.doc = doc

        self.assertEqual(form.createGUI(), None)

        self.assertEqual(form.ui.docTextEdit.toPlainText(), doc)

        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)

        self.assertEqual(form.result(), 0)

    # constructor test
    # \brief It tests default settings
    def test_setFromNode(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        dks = []
        doc = QDomDocument()
        nname = "sourceview"
        qdn = doc.createElement(nname)
        doc.appendChild(qdn)
        dname = "doc"

        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc)
        ndcs = self.__rnd.randint(0, 10)
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" % n))
            mdoc.appendChild(dks[-1])

        rn = self.__rnd.randint(1, 9)
        dimensions = [str(self.__rnd.randint(1, 40)) for n in range(rn)]

        mdim = doc.createElement('dimensions')
        mdim.setAttribute("rank", str(unicode(rn)))

        for i in range(rn):
            dim = doc.createElement(str("dim"))
            dim.setAttribute(str("index"), str(unicode(i + 1)))
            dim.setAttribute(str("value"), str(unicode(dimensions[i])))
            mdim.appendChild(dim)

        qdn.appendChild(mdim)

        form = SourceViewDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.doc, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.selection, [])
        self.assertEqual(
            form.subItems,
            ['datasource', 'doc', 'dimensions',
             'selection', 'enumeration', 'strategy'])
        self.assertEqual(form.ui.__class__.__name__, "Ui_SourceViewDlg")

        form.createGUI()

        self.assertEqual(form.doc, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.selection, [])
        self.assertEqual(
            form.subItems,
            ['datasource', 'doc', 'dimensions',
             'selection', 'enumeration', 'strategy'])

        form.setFromNode()

        self.assertEqual(
            form.doc,
            "".join(["\nText\n %s\n" % n for n in range(ndcs)]).strip())
        self.assertEqual(
            form.subItems,
            ['datasource', 'doc', 'dimensions',
             'selection', 'enumeration', 'strategy'])

        self.assertEqual(form.dimensions, dimensions)
        self.assertTrue(not form.ui.docTextEdit.toPlainText())

    # constructor test
    # \brief It tests default settings
    def test_setFromNode_parameter(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        dks = []
        doc = QDomDocument()
        nname = "sourceview"
        qdn = doc.createElement(nname)
        doc.appendChild(qdn)
        dname = "doc"

        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc)
        ndcs = self.__rnd.randint(0, 10)
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" % n))
            mdoc.appendChild(dks[-1])

        dval = []
        nval = self.__rnd.randint(0, 10)
        for n in range(nval):
            dval.append(doc.createTextNode("\nVAL\n %s\n" % n))
            qdn.appendChild(dval[-1])

        rn = self.__rnd.randint(1, 9)
        dimensions = [str(self.__rnd.randint(1, 40)) for n in range(rn)]

        mdim = doc.createElement('dimensions')
        mdim.setAttribute("rank", str(unicode(rn)))

        for i in range(rn):
            dim = doc.createElement(str("dim"))
            dim.setAttribute(str("index"), str(unicode(i + 1)))
            dim.setAttribute(str("value"), str(unicode(dimensions[i])))
            mdim.appendChild(dim)

        qdn.appendChild(mdim)

        form = SourceViewDlg()
        form.show()
        form.node = None
        self.assertEqual(form.doc, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.selection, [])
        self.assertEqual(
            form.subItems,
            ['datasource', 'doc', 'dimensions',
             'selection', 'enumeration', 'strategy'])
        self.assertEqual(form.ui.__class__.__name__, "Ui_SourceViewDlg")

        form.createGUI()

        self.assertEqual(form.doc, '')
        self.assertEqual(form.selection, [])
        self.assertEqual(form.dimensions, [])
        self.assertEqual(
            form.subItems,
            ['datasource', 'doc', 'dimensions',
             'selection', 'enumeration', 'strategy'])

        form.setFromNode(qdn)

        self.assertEqual(
            form.doc,
            "".join(["\nText\n %s\n" % n for n in range(ndcs)]).strip())
        self.assertEqual(
            form.subItems,
            ['datasource', 'doc', 'dimensions',
             'selection', 'enumeration', 'strategy'])

        self.assertEqual(form.dimensions, dimensions)

        self.assertTrue(not form.ui.docTextEdit.toPlainText())
        self.assertEqual(form.ui.dimLabel.text(), '[]')

    # constructor test
    # \brief It tests default settings
    def test_setFromNode_parameter_nodim(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        dks = []
        doc = QDomDocument()
        nname = "sourceview"
        qdn = doc.createElement(nname)
        doc.appendChild(qdn)
        dname = "doc"

        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc)
        ndcs = self.__rnd.randint(0, 10)
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" % n))
            mdoc.appendChild(dks[-1])

        dval = []
        nval = self.__rnd.randint(0, 10)
        for n in range(nval):
            dval.append(doc.createTextNode("\nVAL\n %s\n" % n))
            qdn.appendChild(dval[-1])

        rn = self.__rnd.randint(1, 9)
        dimensions = [self.__rnd.randint(1, 40) for n in range(rn)]

        mdim = doc.createElement('dimensions')
        mdim.setAttribute("rank", str(unicode(rn)))

        qdn.appendChild(mdim)

        form = SourceViewDlg()
        form.show()
        form.node = None
        self.assertEqual(form.doc, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.selection, [])
        self.assertEqual(
            form.subItems,
            ['datasource', 'doc', 'dimensions',
             'selection', 'enumeration', 'strategy'])
        self.assertEqual(form.ui.__class__.__name__, "Ui_SourceViewDlg")

        form.createGUI()

        self.assertEqual(form.doc, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.selection, [])
        self.assertEqual(
            form.subItems,
            ['datasource', 'doc', 'dimensions',
             'selection', 'enumeration', 'strategy'])

        form.setFromNode(qdn)

        self.assertEqual(
            form.doc,
            "".join(["\nText\n %s\n" % n for n in range(ndcs)]).strip())
        self.assertEqual(
            form.subItems,
            ['datasource', 'doc', 'dimensions',
             'selection', 'enumeration', 'strategy'])

        self.assertEqual(form.dimensions, [None]*len(dimensions))

        self.assertTrue(not form.ui.docTextEdit.toPlainText())
        self.assertEqual(form.ui.dimLabel.text(), '[]')

    # constructor test
    # \brief It tests default settings
    def test_setFromNode_nonode(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        dks = []
        doc = QDomDocument()
        nname = "sourceview"
        qdn = doc.createElement(nname)
        doc.appendChild(qdn)
        dname = "doc"

        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc)
        ndcs = self.__rnd.randint(0, 10)
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" % n))
            mdoc.appendChild(dks[-1])

        rn = self.__rnd.randint(1, 9)
        dimensions = [self.__rnd.randint(1, 40) for n in range(rn)]

        mdim = doc.createElement('dimensions')
        mdim.setAttribute("rank", str(unicode(rn)))

        for i in range(rn):
            dim = doc.createElement(str("dim"))
            dim.setAttribute(str("index"), str(unicode(i + 1)))
            dim.setAttribute(str("value"), str(unicode(dimensions[i])))
            mdim.appendChild(dim)

        qdn.appendChild(mdim)

        form = SourceViewDlg()
        form.show()
        form.node = None
        self.assertEqual(form.doc, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.selection, [])
        self.assertEqual(
            form.subItems,
            ['datasource', 'doc', 'dimensions',
             'selection', 'enumeration', 'strategy'])
        self.assertEqual(form.ui.__class__.__name__, "Ui_SourceViewDlg")

        form.createGUI()

        self.assertEqual(form.doc, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.selection, [])
        self.assertEqual(
            form.subItems,
            ['datasource', 'doc', 'dimensions',
             'selection', 'enumeration', 'strategy'])

        form.setFromNode()

        self.assertEqual(form.doc, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.selection, [])
        self.assertEqual(
            form.subItems,
            ['datasource', 'doc', 'dimensions',
             'selection', 'enumeration', 'strategy'])

        self.assertTrue(not form.ui.docTextEdit.toPlainText())

    # constructor test
    # \brief It tests default settings
    def test_setFromNode_clean(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        # dks = []
        doc = QDomDocument()
        nname = "sourceview"
        qdn = doc.createElement(nname)
        doc.appendChild(qdn)

        form = SourceViewDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.doc, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.selection, [])
        self.assertEqual(
            form.subItems,
            ['datasource', 'doc', 'dimensions',
             'selection', 'enumeration', 'strategy'])
        self.assertEqual(form.ui.__class__.__name__, "Ui_SourceViewDlg")

        form.createGUI()

        self.assertEqual(form.doc, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.selection, [])
        self.assertEqual(
            form.subItems,
            ['datasource', 'doc', 'dimensions',
             'selection', 'enumeration', 'strategy'])

        form.setFromNode()

        self.assertEqual(form.doc, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.selection, [])
        self.assertEqual(
            form.subItems,
            ['datasource', 'doc', 'dimensions',
             'selection', 'enumeration', 'strategy'])

        self.assertTrue(not form.ui.docTextEdit.toPlainText())

    # constructor test
    # \brief It tests default settings
    def test_updateNode(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        dks = []
        doc = QDomDocument()
        nname = "sourceview"
        qdn = doc.createElement(nname)
        doc.appendChild(qdn)
        dname = "doc"

        dval = []
        nval = self.__rnd.randint(0, 10)
        for n in range(nval):
            dval.append(doc.createTextNode("\nVAL\n %s\n" % n))
            qdn.appendChild(dval[-1])

        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc)
        ndcs = self.__rnd.randint(0, 10)
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" % n))
            mdoc.appendChild(dks[-1])

        rn = self.__rnd.randint(1, 9)

        dimensions = [self.__rnd.randint(1, 40) for n in range(rn)]

        mdim = doc.createElement('dimensions')
        mdim.setAttribute("rank", str(unicode(rn)))

        for i in range(rn):
            dim = doc.createElement(str("dim"))
            dim.setAttribute(str("index"), str(unicode(i + 1)))
            dim.setAttribute(str("value"), str(unicode(dimensions[i])))
            mdim.appendChild(dim)

        qdn.appendChild(mdim)

        form = SourceViewDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.doc, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.selection, [])
        self.assertEqual(
            form.subItems,
            ['datasource', 'doc', 'dimensions',
             'selection', 'enumeration', 'strategy'])
        self.assertEqual(form.ui.__class__.__name__, "Ui_SourceViewDlg")

        form.setFromNode()
        form.createGUI()

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        ri = cm.rootIndex
        di = cm.index(0, 0, ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        mdoc = "New text \nNew text"

        vtext = DomTools.getText(qdn)
        oldval = unicode(vtext).strip() if vtext else ""
        self.assertEqual(oldval, form.value)

        mydoc = form.node.firstChildElement(str("doc"))
        text = DomTools.getText(mydoc)
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc, form.doc)

        mrnk = self.__rnd.randint(0, 5)
        mdimensions = [str(self.__rnd.randint(1, 40)) for n in range(mrnk)]
        form.rank = mrnk
        form.dimensions = mdimensions
        form.doc = mdoc

        form.root = doc

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        ri = cm.rootIndex
        di = cm.index(0, 0, ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        form.updateNode()

        mydm = form.node.firstChildElement(str("dimensions"))

        atdim = mydm.attributes()

        trank = atdim.namedItem("rank").nodeValue()
        self.assertEqual(mrnk, int(trank) if trank else 0)
        child = mydm.firstChild()
        while not child.isNull():
            if child.nodeName() == unicode("dim"):
                at = child.attributes()
                ind = int(at.namedItem("index").nodeValue())
                vl = int(at.namedItem("value").nodeValue())
                self.assertTrue(ind > 0)
                self.assertTrue(ind <= mrnk)
                self.assertEqual(mdimensions[ind - 1], str(vl))
            child = child.nextSibling()

        vtext = DomTools.getText(qdn)
        oldval = unicode(vtext).strip() if vtext else ""
        self.assertEqual(oldval, form.value)

        mydoc = form.node.firstChildElement(str("doc"))
        text = DomTools.getText(mydoc)
        olddoc = unicode(text).strip() if text else ""

        self.assertEqual(olddoc, mdoc)

    # constructor test
    # \brief It tests default settings
    def test_updateNode_withindex(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        dks = []
        doc = QDomDocument()
        nname = "sourceview"
        qdn = doc.createElement(nname)
        doc.appendChild(qdn)
        dname = "doc"

        dval = []
        nval = self.__rnd.randint(0, 10)
        for n in range(nval):
            dval.append(doc.createTextNode("\nVAL\n %s\n" % n))
            qdn.appendChild(dval[-1])

        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc)
        ndcs = self.__rnd.randint(0, 10)
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" % n))
            mdoc.appendChild(dks[-1])

        rn = self.__rnd.randint(1, 9)

        dimensions = [self.__rnd.randint(1, 40) for n in range(rn)]

        mdim = doc.createElement('dimensions')
        mdim.setAttribute("rank", str(unicode(rn)))

        for i in range(rn):
            dim = doc.createElement(str("dim"))
            dim.setAttribute(str("index"), str(unicode(i + 1)))
            dim.setAttribute(str("value"), str(unicode(dimensions[i])))
            mdim.appendChild(dim)

        qdn.appendChild(mdim)

        form = SourceViewDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.doc, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.selection, [])
        self.assertEqual(
            form.subItems,
            ['datasource', 'doc', 'dimensions',
             'selection', 'enumeration', 'strategy'])
        self.assertEqual(form.ui.__class__.__name__, "Ui_SourceViewDlg")

        form.setFromNode()
        form.createGUI()

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        ri = cm.rootIndex
        di = cm.index(0, 0, ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        mdoc = "New text \nNew text"

        vtext = DomTools.getText(qdn)
        oldval = unicode(vtext).strip() if vtext else ""
        self.assertEqual(oldval, form.value)

        mydoc = form.node.firstChildElement(str("doc"))
        text = DomTools.getText(mydoc)
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc, form.doc)

        mrnk = self.__rnd.randint(0, 5)
        mdimensions = [self.__rnd.randint(1, 40) for n in range(mrnk)]
        form.rank = mrnk
        form.dimensions = mdimensions
        form.doc = mdoc

        form.root = doc

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        ri = cm.rootIndex
        di = cm.index(0, 0, ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        form.updateNode(di)

        mydm = form.node.firstChildElement(str("dimensions"))

        atdim = mydm.attributes()

        trank = atdim.namedItem("rank").nodeValue()
        self.assertEqual(mrnk, int(trank) if trank else 0)
        child = mydm.firstChild()
        while not child.isNull():
            if child.nodeName() == unicode("dim"):
                at = child.attributes()
                ind = int(at.namedItem("index").nodeValue())
                vl = int(at.namedItem("value").nodeValue())
                self.assertTrue(ind > 0)
                self.assertTrue(ind <= mrnk)
                self.assertEqual(mdimensions[ind - 1], vl)
            child = child.nextSibling()

        vtext = DomTools.getText(qdn)
        oldval = unicode(vtext).strip() if vtext else ""
        self.assertEqual(oldval, form.value)

        mydoc = form.node.firstChildElement(str("doc"))
        text = DomTools.getText(mydoc)
        olddoc = unicode(text).strip() if text else ""

        self.assertEqual(olddoc, mdoc)

    # constructor test
    # \brief It tests default settings
    def test_apply(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        dks = []
        doc = QDomDocument()
        nname = "sourceview"
        qdn = doc.createElement(nname)
        doc.appendChild(qdn)
        dname = "doc"

        dval = []
        nval = self.__rnd.randint(0, 10)
        for n in range(nval):
            dval.append(doc.createTextNode("\nVAL\n %s\n" % n))
            qdn.appendChild(dval[-1])

        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc)
        ndcs = self.__rnd.randint(0, 10)
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" % n))
            mdoc.appendChild(dks[-1])

        rn = self.__rnd.randint(1, 9)

        dimensions = [self.__rnd.randint(1, 40) for n in range(rn)]

        mdim = doc.createElement('dimensions')
        mdim.setAttribute("rank", str(unicode(rn)))

        for i in range(rn):
            dim = doc.createElement(str("dim"))
            dim.setAttribute(str("index"), str(unicode(i + 1)))
            dim.setAttribute(str("value"), str(unicode(dimensions[i])))
            mdim.appendChild(dim)

        qdn.appendChild(mdim)

        form = SourceViewDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.doc, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.selection, [])
        self.assertEqual(
            form.subItems,
            ['datasource', 'doc', 'dimensions',
             'selection', 'enumeration', 'strategy'])
        self.assertEqual(form.ui.__class__.__name__, "Ui_SourceViewDlg")

        form.setFromNode()
        form.createGUI()

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        ri = cm.rootIndex
        di = cm.index(0, 0, ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        mdoc = "New text \nNew text"

        vtext = DomTools.getText(qdn)
        oldval = unicode(vtext).strip() if vtext else ""
        self.assertEqual(oldval, form.value)

        mydoc = form.node.firstChildElement(str("doc"))
        text = DomTools.getText(mydoc)
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc, form.doc)

        form.doc = mdoc

        form.root = doc

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        ri = cm.rootIndex
        di = cm.index(0, 0, ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        form.ui.docTextEdit.setText(str(mdoc))

        mrnk = self.__rnd.randint(0, 5)
        self.dimensions = [str(self.__rnd.randint(1, 40)) for n in range(mrnk)]
        idimensions = [int(dm) for dm in self.dimensions]

        QTimer.singleShot(10, self.dimensionsWidget)
        QTest.mouseClick(form.ui.dimPushButton, Qt.LeftButton)

        form.apply()

        self.assertEqual(form.doc, str(mdoc))
        self.assertEqual(form.rank, len(self.dimensions))
        self.assertEqual(form.dimensions, idimensions)

        mydoc = form.node.firstChildElement(str("doc"))
        text = DomTools.getText(mydoc)
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc, mdoc)

        mydm = form.node.firstChildElement(str("dimensions"))

        atdim = mydm.attributes()
        trank = atdim.namedItem("rank").nodeValue()
        self.assertEqual(mrnk, int(trank) if trank else 0)
        child = mydm.firstChild()
        while not child.isNull():
            if child.nodeName() == unicode("dim"):
                at = child.attributes()
                ind = int(at.namedItem("index").nodeValue())
                vl = int(at.namedItem("value").nodeValue())
                self.assertTrue(ind > 0)
                self.assertTrue(ind <= mrnk)
                self.assertEqual(self.dimensions[ind - 1], str(vl))
            child = child.nextSibling()

        mydoc = form.node.firstChildElement(str("doc"))
        text = DomTools.getText(mydoc)
        olddoc = unicode(text).strip() if text else ""

        self.assertEqual(olddoc, mdoc)

    # constructor test
    # \brief It tests default settings
    def test_reset(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        dks = []
        doc = QDomDocument()
        nname = "sourceview"
        qdn = doc.createElement(nname)
        doc.appendChild(qdn)
        dname = "doc"

        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc)
        ndcs = self.__rnd.randint(0, 10)
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" % n))
            mdoc.appendChild(dks[-1])

        rn = self.__rnd.randint(1, 9)

        dimensions = [str(self.__rnd.randint(1, 40)) for n in range(rn)]

        mdim = doc.createElement('dimensions')
        mdim.setAttribute("rank", str(unicode(rn)))

        for i in range(rn):
            dim = doc.createElement(str("dim"))
            dim.setAttribute(str("index"), str(unicode(i + 1)))
            dim.setAttribute(str("value"), str(unicode(dimensions[i])))
            mdim.appendChild(dim)

        qdn.appendChild(mdim)

        form = SourceViewDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.doc, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.selection, [])
        self.assertEqual(
            form.subItems,
            ['datasource', 'doc', 'dimensions',
             'selection', 'enumeration', 'strategy'])
        self.assertEqual(form.ui.__class__.__name__, "Ui_SourceViewDlg")

        form.setFromNode()
        form.createGUI()

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        ri = cm.rootIndex
        di = cm.index(0, 0, ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        mdoc = "New text \nNew text"

        mydoc = form.node.firstChildElement(str("doc"))
        text = DomTools.getText(mydoc)
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc, form.doc)

        form.doc = mdoc

        form.root = doc

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        ri = cm.rootIndex
        di = cm.index(0, 0, ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        form.ui.docTextEdit.setText(str(mdoc))

        mrnk = self.__rnd.randint(0, 5)
        self.dimensions = [str(self.__rnd.randint(1, 40)) for n in range(mrnk)]

        QTimer.singleShot(10, self.dimensionsWidget)
        QTest.mouseClick(form.ui.dimPushButton, Qt.LeftButton)

        form.reset()
        self.assertEqual(
            form.doc,
            "".join(["\nText\n %s\n" % n for n in range(ndcs)]).strip())
        self.assertEqual(
            form.subItems,
            ['datasource', 'doc', 'dimensions',
             'selection', 'enumeration', 'strategy'])

        self.assertEqual(form.dimensions, dimensions)

        mydoc = form.node.firstChildElement(str("doc"))
        text = DomTools.getText(mydoc)
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(
            olddoc,
            "".join(["\nText\n %s\n" % n for n in range(ndcs)]).strip())

        mydm = form.node.firstChildElement(str("dimensions"))

        atdim = mydm.attributes()
        self.assertEqual(rn, int(atdim.namedItem("rank").nodeValue()))
        child = mydm.firstChild()
        while not child.isNull():
            if child.nodeName() == unicode("dim"):
                at = child.attributes()
                ind = int(at.namedItem("index").nodeValue())
                vl = int(at.namedItem("value").nodeValue())
                self.assertTrue(ind > 0)
                self.assertTrue(ind <= rn)
                self.assertEqual(dimensions[ind - 1], str(vl))
            child = child.nextSibling()

    # constructor test
    # \brief It tests default settings
    def test_reset_button(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        dks = []
        doc = QDomDocument()
        nname = "sourceview"
        qdn = doc.createElement(nname)
        doc.appendChild(qdn)
        dname = "doc"

        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc)
        ndcs = self.__rnd.randint(0, 10)
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" % n))
            mdoc.appendChild(dks[-1])

        rn = self.__rnd.randint(1, 9)

        dimensions = [str(self.__rnd.randint(1, 40)) for n in range(rn)]

        mdim = doc.createElement('dimensions')
        mdim.setAttribute("rank", str(unicode(rn)))

        for i in range(rn):
            dim = doc.createElement(str("dim"))
            dim.setAttribute(str("index"), str(unicode(i + 1)))
            dim.setAttribute(str("value"), str(unicode(dimensions[i])))
            mdim.appendChild(dim)

        qdn.appendChild(mdim)

        form = SourceViewDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.doc, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.selection, [])
        self.assertEqual(
            form.subItems,
            ['datasource', 'doc', 'dimensions',
             'selection', 'enumeration', 'strategy'])
        self.assertEqual(form.ui.__class__.__name__, "Ui_SourceViewDlg")

        form.setFromNode()
        form.createGUI()

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        ri = cm.rootIndex
        di = cm.index(0, 0, ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        mdoc = "New text \nNew text"

        mydoc = form.node.firstChildElement(str("doc"))
        text = DomTools.getText(mydoc)
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc, form.doc)

        form.doc = mdoc

        form.root = doc

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        ri = cm.rootIndex
        di = cm.index(0, 0, ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        form.ui.docTextEdit.setText(str(mdoc))

        mrnk = self.__rnd.randint(0, 5)
        self.dimensions = [str(self.__rnd.randint(1, 40)) for n in range(mrnk)]

        QTimer.singleShot(10, self.dimensionsWidget)
        QTest.mouseClick(form.ui.dimPushButton, Qt.LeftButton)

        QTest.mouseClick(form.ui.resetPushButton, Qt.LeftButton)

        self.assertEqual(
            form.doc,
            "".join(["\nText\n %s\n" % n for n in range(ndcs)]).strip())
        self.assertEqual(
            form.subItems,
            ['datasource', 'doc', 'dimensions',
             'selection', 'enumeration', 'strategy'])

        self.assertEqual(form.dimensions, dimensions)

        mydoc = form.node.firstChildElement(str("doc"))
        text = DomTools.getText(mydoc)
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(
            olddoc,
            "".join(["\nText\n %s\n" % n for n in range(ndcs)]).strip())

        mydm = form.node.firstChildElement(str("dimensions"))

        atdim = mydm.attributes()
        self.assertEqual(rn, int(atdim.namedItem("rank").nodeValue()))
        child = mydm.firstChild()
        while not child.isNull():
            if child.nodeName() == unicode("dim"):
                at = child.attributes()
                ind = int(at.namedItem("index").nodeValue())
                vl = int(at.namedItem("value").nodeValue())
                self.assertTrue(ind > 0)
                self.assertTrue(ind <= rn)
                self.assertEqual(dimensions[ind - 1], str(vl))
            child = child.nextSibling()

    def myAction(self):
        self.performed = True

    # constructor test

    # constructor test
    # \brief It tests default settings
    def test_connect_actions(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        form = SourceViewDlg()
        form.show()
        self.assertEqual(form.connectExternalActions(), None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.ui.__class__.__name__, "Ui_SourceViewDlg")
        self.assertEqual(form.externalApply, None)
        self.assertEqual(form.externalDSLink, None)
#        self.assertTrue(isinstance(DomTools, DomTools))

        self.assertEqual(form.result(), 0)

    # constructor test
    # \brief It tests default settings
    def test_connect_actions_with_action(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        form = SourceViewDlg()
        form.show()
        self.assertEqual(form.connectExternalActions(self.myAction), None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.ui.__class__.__name__, "Ui_SourceViewDlg")
        self.assertEqual(form.externalApply, None)

        self.assertEqual(form.result(), 0)

    # constructor test
    # \brief It tests default settings
    def test_connect_actions_with_button(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        form = SourceViewDlg()
        # form.ui = Ui_SourceViewDlg()
        form.ui.applyPushButton = QPushButton(form)
        form.ui.linkDSPushButton = QPushButton(form)
        form.show()
        self.assertEqual(form.connectExternalActions(), None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.ui.__class__.__name__, "Ui_SourceViewDlg")
        self.assertEqual(form.externalApply, None)
        self.assertEqual(form.externalDSLink, None)

        self.assertEqual(form.result(), 0)

    # constructor test
    # \brief It tests default settings
    def test_connect_actions_with_action_button(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        form = SourceViewDlg()
        # form.ui = Ui_SourceViewDlg()
        form.ui.applyPushButton = QPushButton(form)
        form.ui.linkDSPushButton = QPushButton(form)
        form.show()
        self.assertEqual(form.connectExternalActions(self.myAction), None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.ui.__class__.__name__, "Ui_SourceViewDlg")
        self.assertEqual(form.externalApply, self.myAction)
        self.performed = False

        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)
        self.assertEqual(self.performed, True)

        self.assertEqual(form.result(), 0)

    # constructor test
    # \brief It tests default settings
    def test_connect_actions_with_action_button_2(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        form = SourceViewDlg()
        # form.ui = Ui_SourceViewDlg()
        form.ui.applyPushButton = QPushButton(form)
        form.ui.linkDSPushButton = QPushButton(form)
        form.show()
        self.assertEqual(form.connectExternalActions(self.myAction), None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.ui.__class__.__name__, "Ui_SourceViewDlg")
        self.assertEqual(form.externalApply, self.myAction)
        self.performed = False

        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)
        self.assertEqual(self.performed, True)

        self.assertEqual(form.result(), 0)

    # constructor test
    # \brief It tests default settings
    def test_connect_actions_with_action_link_button(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        form = SourceViewDlg()
        form.createGUI()
        form.ui.applyPushButton = QPushButton(form)
        form.ui.linkDSPushButton = QPushButton(form)
        form.show()
        self.assertEqual(
            form.connectExternalActions(externalDSLink=self.myAction), None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.ui.__class__.__name__, "Ui_SourceViewDlg")
        self.assertEqual(form.externalDSLink, self.myAction)
        self.performed = False

        self.assertEqual(form.result(), 0)

    # constructor test
    # \brief It tests default settings
    def ttest_connect_actions_with_action_and_apply_button(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        form = SourceViewDlg()
        # form.ui = Ui_SourceViewDlg()
        form.ui.applyPushButton = QPushButton(form)
        form.createGUI()
        form.show()
        self.assertEqual(
            form.connectExternalActions(self.myAction, None), None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.ui.__class__.__name__, "Ui_SourceViewDlg")
        self.assertEqual(form.externalApply, self.myAction)
        self.assertEqual(form.externalDSLink, None)
        self.performed = False

        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)
        self.assertEqual(self.performed, True)

        self.assertEqual(form.result(), 0)

    # constructor test
    # \brief It tests default settings
    def test_connect_actions_with_action_and_sapply_button(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        form = SourceViewDlg()
        # form.ui = Ui_SourceViewDlg()
        form.ui.applyPushButton = QPushButton(form)
        form.ui.linkDSPushButton = QPushButton(form)
        form.createGUI()

        form.show()
        self.assertEqual(
            form.connectExternalActions(self.myAction, None), None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.ui.__class__.__name__, "Ui_SourceViewDlg")
        self.assertEqual(form.externalApply, self.myAction)
        self.performed = False

        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)
        self.assertEqual(self.performed, True)

        self.assertEqual(form.result(), 0)

    # constructor test
    # \brief It tests default settings
    def test_connect_actions_with_action_and_apply_button_noname(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        form = SourceViewDlg()
        # form.ui = Ui_SourceViewDlg()
        form.ui.applyPushButton = QPushButton(form)
        form.createGUI()

        form.show()
        self.assertEqual(
            form.connectExternalActions(self.myAction, None), None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.ui.__class__.__name__, "Ui_SourceViewDlg")
        self.assertEqual(form.externalApply, self.myAction)
        self.assertEqual(form.externalDSLink, None)
        self.performed = False

        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)
        self.assertEqual(self.performed, True)

        self.assertEqual(form.result(), 0)

    # constructor test
    # \brief It tests default settings
    def test_connect_actions_with_action_link_and_apply_button_noname(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        form = SourceViewDlg()
        # form.ui = Ui_SourceViewDlg()
        form.ui.applyPushButton = QPushButton(form)
        form.createGUI()

        form.show()
        self.assertEqual(
            form.connectExternalActions(self.myAction, None), None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.ui.__class__.__name__, "Ui_SourceViewDlg")
        self.assertEqual(form.externalApply, self.myAction)
        self.assertEqual(form.externalDSLink, None)
        self.performed = False

        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)
        self.assertEqual(self.performed, True)

        self.assertEqual(form.result(), 0)

    # constructor test
    # \brief It tests default settings
    def test_appendElement(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        dks = []
        doc = QDomDocument()
        nname = "sourceview"
        qdn = doc.createElement(nname)
        doc.appendChild(qdn)
        dname = "doc"

        dval = []
        nval = self.__rnd.randint(0, 10)
        for n in range(nval):
            dval.append(doc.createTextNode("\nVAL\n %s\n" % n))
            qdn.appendChild(dval[-1])

        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc)
        ndcs = self.__rnd.randint(0, 10)
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" % n))
            mdoc.appendChild(dks[-1])

        rn = self.__rnd.randint(1, 9)

        dimensions = [str(self.__rnd.randint(1, 40)) for n in range(rn)]

        mdim = doc.createElement('dimensions')
        mdim.setAttribute("rank", str(unicode(rn)))

        for i in range(rn):
            dim = doc.createElement(str("dim"))
            dim.setAttribute(str("index"), str(unicode(i + 1)))
            dim.setAttribute(str("value"), str(unicode(dimensions[i])))
            mdim.appendChild(dim)

        qdn.appendChild(mdim)

        form = SourceViewDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.doc, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.selection, [])
        self.assertEqual(
            form.subItems,
            ['datasource', 'doc', 'dimensions',
             'selection', 'enumeration', 'strategy'])
        self.assertEqual(form.ui.__class__.__name__, "Ui_SourceViewDlg")

        form.setFromNode()
        form.createGUI()

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        ri = cm.rootIndex
        di = cm.index(0, 0, ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        self.assertEqual(
            form.doc,
            "".join(["\nText\n %s\n" % n for n in range(ndcs)]).strip())
        self.assertEqual(
            form.subItems,
            ['datasource', 'doc', 'dimensions',
             'selection', 'enumeration', 'strategy'])

        self.assertEqual(form.dimensions, dimensions)

        mydoc = form.node.firstChildElement(str("doc"))
        text = DomTools.getText(mydoc)
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(
            olddoc,
            "".join(["\nText\n %s\n" % n for n in range(ndcs)]).strip())

        mydm = form.node.firstChildElement(str("dimensions"))

        atdim = mydm.attributes()
        self.assertEqual(rn, int(atdim.namedItem("rank").nodeValue()))
        child = mydm.firstChild()
        while not child.isNull():
            if child.nodeName() == unicode("dim"):
                at = child.attributes()
                ind = int(at.namedItem("index").nodeValue())
                vl = int(at.namedItem("value").nodeValue())
                self.assertTrue(ind > 0)
                self.assertTrue(ind <= rn)
                self.assertEqual(dimensions[ind - 1], str(vl))
            child = child.nextSibling()

        doc2 = QDomDocument()
        nname2 = "datasource"
        qdn2 = doc2.createElement(nname2)
        doc2.appendChild(qdn2)

        form.appendElement(qdn2, di)

        mydoc = form.node.firstChildElement(str("doc"))
        text = DomTools.getText(mydoc)
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(
            olddoc,
            "".join(["\nText\n %s\n" % n for n in range(ndcs)]).strip())

        vtext = DomTools.getText(qdn)
        oldval = unicode(vtext).strip() if vtext else ""
        self.assertEqual(
            oldval,
            "".join(["\nVAL\n %s\n" % n for n in range(nval)]).strip())

        mydm = form.node.firstChildElement(str("dimensions"))

        atdim = mydm.attributes()
        self.assertEqual(rn, int(atdim.namedItem("rank").nodeValue()))
        child = mydm.firstChild()
        while not child.isNull():
            if child.nodeName() == unicode("dim"):
                at = child.attributes()
                ind = int(at.namedItem("index").nodeValue())
                vl = int(at.namedItem("value").nodeValue())
                self.assertTrue(ind > 0)
                self.assertTrue(ind <= rn)
                self.assertEqual(dimensions[ind - 1], str(vl))
            child = child.nextSibling()

    # constructor test
    # \brief It tests default settings
    def test_appendElement_error(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        dks = []
        doc = QDomDocument()
        nname = "sourceview"
        qdn = doc.createElement(nname)
        nn = self.__rnd.randint(0, 9)
        doc.appendChild(qdn)
        dname = "doc"

        dval = []
        nval = self.__rnd.randint(0, 10)
        for n in range(nval):
            dval.append(doc.createTextNode("\nVAL\n %s\n" % n))
            qdn.appendChild(dval[-1])

        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc)
        ndcs = self.__rnd.randint(0, 10)
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" % n))
            mdoc.appendChild(dks[-1])

        rn = self.__rnd.randint(1, 9)

        dimensions = [str(self.__rnd.randint(1, 40)) for n in range(rn)]

        mdim = doc.createElement('dimensions')
        mdim.setAttribute("rank", str(unicode(rn)))

        for i in range(rn):
            dim = doc.createElement(str("dim"))
            dim.setAttribute(str("index"), str(unicode(i + 1)))
            dim.setAttribute(str("value"), str(unicode(dimensions[i])))
            mdim.appendChild(dim)

        qdn.appendChild(mdim)

        form = SourceViewDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.doc, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.selection, [])
        self.assertEqual(
            form.subItems,
            ['datasource', 'doc', 'dimensions',
             'selection', 'enumeration', 'strategy'])
        self.assertEqual(form.ui.__class__.__name__, "Ui_SourceViewDlg")

        form.setFromNode()
        form.createGUI()

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        ri = cm.rootIndex
        di = cm.index(0, 0, ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        self.assertEqual(
            form.doc,
            "".join(["\nText\n %s\n" % n for n in range(ndcs)]).strip())
        self.assertEqual(
            form.subItems,
            ['datasource', 'doc', 'dimensions',
             'selection', 'enumeration', 'strategy'])

        self.assertEqual(form.dimensions, dimensions)

        mydoc = form.node.firstChildElement(str("doc"))
        text = DomTools.getText(mydoc)
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(
            olddoc,
            "".join(["\nText\n %s\n" % n for n in range(ndcs)]).strip())

        vtext = DomTools.getText(qdn)
        oldval = unicode(vtext).strip() if vtext else ""
        self.assertEqual(
            oldval,
            "".join(["\nVAL\n %s\n" % n for n in range(nval)]).strip())

        mydm = form.node.firstChildElement(str("dimensions"))

        atdim = mydm.attributes()
        self.assertEqual(rn, int(atdim.namedItem("rank").nodeValue()))
        child = mydm.firstChild()
        while not child.isNull():
            if child.nodeName() == unicode("dim"):
                at = child.attributes()
                ind = int(at.namedItem("index").nodeValue())
                vl = int(at.namedItem("value").nodeValue())
                self.assertTrue(ind > 0)
                self.assertTrue(ind <= rn)
                self.assertEqual(dimensions[ind - 1], str(vl))
            child = child.nextSibling()

        tags = ["datasource", "strategy"]
        wtext = "To add a new %s please remove the old one"
        for tg in tags:

            doc2 = QDomDocument()
            nname2 = tg
            qdn2 = doc2.createElement(nname2)
            qdn2.setAttribute("name", "my2name%s" % nn)
            qdn2.setAttribute("type", "my2type%s" % nn)
            qdn2.setAttribute("target2", "my2target%s" % nn)
            qdn2.setAttribute("target", "my2target%s" % nn)
            qdn2.setAttribute("shortname2", "my2nshort%s" % nn)
            doc2.appendChild(qdn2)

            form.appendElement(qdn2, di)

            QTimer.singleShot(10, self.checkMessageBox)
            form.appendElement(qdn2, di)
            self.assertEqual(self.text, wtext % nname2)

        tags = ["mydatasource", "mystrategy", "random"]
        wtext = "To add a new %s please remove the old one"
        for tg in tags:

            doc2 = QDomDocument()
            nname2 = tg
            qdn2 = doc2.createElement(nname2)
            qdn2.setAttribute("name", "my2name%s" % nn)
            qdn2.setAttribute("type", "my2type%s" % nn)
            qdn2.setAttribute("target2", "my2target%s" % nn)
            qdn2.setAttribute("target", "my2target%s" % nn)
            qdn2.setAttribute("shortname2", "my2nshort%s" % nn)
            doc2.appendChild(qdn2)

            form.appendElement(qdn2, di)

            form.appendElement(qdn2, di)


if __name__ == '__main__':
    if not app:
        app = QApplication([])
    unittest.main()
