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
# \file SelectionDlgTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import random
import struct
import binascii
import time
from PyQt5.QtWidgets import (QApplication, QMessageBox)

from nxsconfigtool.SelectionDlg import SelectionDlg
# from nxsconfigtool.ui.ui_selectiondlg import Ui_SelectionDlg

#  Qt-application
app = None

# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)

if sys.version_info > (3,):
    unicode = str
    long = int


# test fixture
class SelectionDlgTest(unittest.TestCase):

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

    # constructor test
    # \brief It tests default settings
    def test_constructor(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        form = SelectionDlg()
        self.assertEqual(form.rank, 0)
        self.assertEqual(form.offsets, [])
        self.assertEqual(form.blocks, [])
        self.assertEqual(form.counts, [])
        self.assertEqual(form.strides, [])
        self.assertEqual(form.starts, [])
        self.assertEqual(form.stops, [])
        self.assertEqual(form.steps, [])
        self.assertEqual(form.keytype, "slices")
        self.assertEqual(form.subItems, ["slice", "slab"])
        self.assertEqual(form.ui.__class__.__name__, "Ui_SelectionDlg")

        self.assertEqual(form.result(), 0)

    def checkMessageBox(self):
        # aw = QApplication.activeWindow()
        mb = QApplication.activeModalWidget()
        self.assertTrue(isinstance(mb, QMessageBox))
#        print mb.text()
#        print "AW", aw
#        print "mb", mb
        self.text = mb.text()
        self.title = mb.windowTitle()
        mb.accept()
        mb.close()

    # create GUI test
    # \brief It tests default settings
    def test_createGUI(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        form = SelectionDlg()
        self.assertEqual(form.rank, 0)
        self.assertEqual(form.keytype, "slices")
        self.assertEqual(form.starts, [])
        self.assertEqual(form.stops, [])
        self.assertEqual(form.steps, [])
        self.assertEqual(form.offsets, [])
        self.assertEqual(form.blocks, [])
        self.assertEqual(form.counts, [])
        self.assertEqual(form.strides, [])
        self.assertEqual(form.subItems, ["slice", "slab"])
        self.assertEqual(form.ui.__class__.__name__, "Ui_SelectionDlg")

        self.assertEqual(form.createGUI(), None)
        form.show()

        self.assertEqual(form.result(), 0)

        self.assertEqual(form.rank, 0)
        self.assertEqual(form.starts, [])
        self.assertEqual(form.stops, [])
        self.assertEqual(form.steps, [])
        self.assertEqual(form.offsets, [])
        self.assertEqual(form.blocks, [])
        self.assertEqual(form.counts, [])
        self.assertEqual(form.strides, [])
        self.assertEqual(form.ui.rankSpinBox.value(), 0)
        self.assertEqual(form.ui.selTableWidget.columnCount(), 3)
        self.assertEqual(form.ui.selTableWidget.rowCount(), 0)

    # create GUI test
    # \brief It tests default settings
    def test_createGUI_rank(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        rank = self.__rnd.randint(1, 6)

        form = SelectionDlg()
        form.rank = rank
        self.assertEqual(form.rank, rank)
        self.assertEqual(form.keytype, "slices")
        self.assertEqual(form.starts, [])
        self.assertEqual(form.stops, [])
        self.assertEqual(form.steps, [])
        self.assertEqual(form.offsets, [])
        self.assertEqual(form.blocks, [])
        self.assertEqual(form.counts, [])
        self.assertEqual(form.strides, [])
        self.assertEqual(form.subItems, ["slice", "slab"])
        self.assertEqual(form.ui.__class__.__name__, "Ui_SelectionDlg")

        self.assertEqual(form.createGUI(), None)
        form.show()

        self.assertEqual(form.result(), 0)

        self.assertEqual(form.rank, rank)
        self.assertEqual(form.starts, [None] * rank)
        self.assertEqual(form.stops, [None] * rank)
        self.assertEqual(form.steps, [None] * rank)
        self.assertEqual(form.offsets, [])
        self.assertEqual(form.blocks, [])
        self.assertEqual(form.counts, [])
        self.assertEqual(form.strides, [])
        self.assertEqual(form.ui.rankSpinBox.value(), rank)
        self.assertEqual(form.ui.selTableWidget.columnCount(), 3)
        self.assertEqual(form.ui.selTableWidget.rowCount(), rank)
        for r in range(rank):
            for cl in range(3):
                it = form.ui.selTableWidget.item(r, cl)
                self.assertEqual(it.text(), "")

    # create GUI test
    # \brief It tests default settings
    def test_createGUI_rank_slides(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        rank = self.__rnd.randint(1, 6)
        starts = [str(self.__rnd.randint(1, 100)) for r in range(rank)]
        stops = [str(self.__rnd.randint(1, 100)) for r in range(rank)]
        steps = [str(self.__rnd.randint(1, 100)) for r in range(rank)]
        form = SelectionDlg()
        form.rank = rank
        form.starts = starts
        form.stops = stops
        form.steps = steps
        self.assertEqual(form.rank, rank)
        self.assertEqual(form.subItems, ["slice", "slab"])
        self.assertEqual(form.ui.__class__.__name__, "Ui_SelectionDlg")

        self.assertEqual(form.createGUI(), None)
        form.show()

        self.assertEqual(form.result(), 0)

        self.assertEqual(form.rank, rank)
        self.assertEqual(form.starts, starts)
        self.assertEqual(form.stops, stops)
        self.assertEqual(form.steps, steps)
        self.assertEqual(form.offsets, [])
        self.assertEqual(form.blocks, [])
        self.assertEqual(form.counts, [])
        self.assertEqual(form.strides, [])
        self.assertEqual(form.ui.rankSpinBox.value(), rank)
        self.assertEqual(form.ui.selTableWidget.columnCount(), 3)
        self.assertEqual(form.ui.selTableWidget.rowCount(), rank)
        elem = [starts, stops, steps]
        for r in range(rank):
            for cl in range(3):
                it = form.ui.selTableWidget.item(r, cl)
                self.assertEqual(it.text(), str(elem[cl][r]))

    # create GUI test
    # \brief It tests default settings
    def test_createGUI_rank_slabs(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        rank = self.__rnd.randint(1, 6)
        offsets = [str(self.__rnd.randint(1, 100)) for r in range(rank)]
        blocks = [str(self.__rnd.randint(1, 100)) for r in range(rank)]
        counts = [str(self.__rnd.randint(1, 100)) for r in range(rank)]
        strides = [str(self.__rnd.randint(1, 100)) for r in range(rank)]
        form = SelectionDlg()
        form.rank = rank
        form.offsets = offsets
        form.blocks = blocks
        form.counts = counts
        form.strides = strides
        form.keytype = 'slabs'
        self.assertEqual(form.rank, rank)
        self.assertEqual(form.subItems, ["slice", "slab"])
        self.assertEqual(form.ui.__class__.__name__, "Ui_SelectionDlg")

        self.assertEqual(form.createGUI(), None)
        form.show()

        self.assertEqual(form.result(), 0)

        self.assertEqual(form.rank, rank)
        self.assertEqual(form.starts, [])
        self.assertEqual(form.stops, [])
        self.assertEqual(form.steps, [])
        self.assertEqual(form.offsets, offsets)
        self.assertEqual(form.blocks, blocks)
        self.assertEqual(form.counts, counts)
        self.assertEqual(form.strides, strides)
        self.assertEqual(form.ui.rankSpinBox.value(), rank)
        self.assertEqual(form.ui.selTableWidget.columnCount(), 4)
        self.assertEqual(form.ui.selTableWidget.rowCount(), rank)
        elem = [offsets, blocks, counts, strides]
        for r in range(rank):
            for cl in range(len(elem)):
                it = form.ui.selTableWidget.item(r, cl)
                self.assertEqual(it.text(), str(elem[cl][r]))

    # create GUI test
    # \brief It tests default settings
    def test_createGUI_rank_str_slides(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        rank = str(self.__rnd.randint(1, 6))
        irank = int(rank)
        starts = [str(self.__rnd.randint(1, 100)) for r in range(irank)]
        stops = [str(self.__rnd.randint(1, 100)) for r in range(irank)]
        steps = [str(self.__rnd.randint(1, 100)) for r in range(irank)]
        form = SelectionDlg()
        form.rank = rank
        form.starts = starts
        form.stops = stops
        form.steps = steps
        self.assertEqual(form.rank, rank)
        self.assertEqual(form.subItems, ["slice", "slab"])
        self.assertEqual(form.ui.__class__.__name__, "Ui_SelectionDlg")

        self.assertEqual(form.createGUI(), None)
        form.show()

        self.assertEqual(form.result(), 0)

        self.assertEqual(form.rank, irank)
        self.assertEqual(form.starts, starts)
        self.assertEqual(form.stops, stops)
        self.assertEqual(form.steps, steps)
        self.assertEqual(form.offsets, [])
        self.assertEqual(form.blocks, [])
        self.assertEqual(form.counts, [])
        self.assertEqual(form.strides, [])
        self.assertEqual(form.ui.rankSpinBox.value(), irank)
        self.assertEqual(form.ui.selTableWidget.columnCount(), 3)
        self.assertEqual(form.ui.selTableWidget.rowCount(), irank)
        elem = [starts, stops, steps]
        for r in range(irank):
            for cl in range(3):
                it = form.ui.selTableWidget.item(r, cl)
                self.assertEqual(it.text(), str(elem[cl][r]))

    # create GUI test
    # \brief It tests default settings
    def test_createGUI_rank_str_slabs_accept(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        rank = str(self.__rnd.randint(1, 6))
        irank = int(rank)
        offsets = [str(self.__rnd.randint(1, 100)) for r in range(irank)]
        blocks = [str(self.__rnd.randint(1, 100)) for r in range(irank)]
        counts = [str(self.__rnd.randint(1, 100)) for r in range(irank)]
        strides = [str(self.__rnd.randint(1, 100)) for r in range(irank)]
        form = SelectionDlg()
        form.rank = rank
        form.offsets = offsets
        form.blocks = blocks
        form.counts = counts
        form.strides = strides
        form.keytype = 'slabs'
        self.assertEqual(form.rank, rank)
        self.assertEqual(form.subItems, ["slice", "slab"])
        self.assertEqual(form.ui.__class__.__name__, "Ui_SelectionDlg")

        self.assertEqual(form.createGUI(), None)
        form.show()

        form.accept()
        self.assertEqual(form.result(), 1)

        self.assertEqual(form.rank, irank)
        self.assertEqual(form.starts, [])
        self.assertEqual(form.stops, [])
        self.assertEqual(form.steps, [])
        self.assertEqual(form.offsets, offsets)
        self.assertEqual(form.blocks, blocks)
        self.assertEqual(form.counts, counts)
        self.assertEqual(form.strides, strides)
        self.assertEqual(form.ui.rankSpinBox.value(), irank)
        self.assertEqual(form.ui.selTableWidget.columnCount(), 4)
        self.assertEqual(form.ui.selTableWidget.rowCount(), irank)
        elem = [offsets, blocks, counts, strides]
        for r in range(irank):
            for cl in range(len(elem)):
                it = form.ui.selTableWidget.item(r, cl)
                self.assertEqual(it.text(), str(elem[cl][r]))

    # create GUI test
    # \brief It tests default settings
    def test_createGUI_rank_slides_accept(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        rank = self.__rnd.randint(1, 6)
        starts = [str(self.__rnd.randint(1, 100)) for r in range(rank)]
        stops = [str(self.__rnd.randint(1, 100)) for r in range(rank)]
        steps = [str(self.__rnd.randint(1, 100)) for r in range(rank)]
        form = SelectionDlg()
        form.rank = rank
        form.starts = starts
        form.stops = stops
        form.steps = steps
        self.assertEqual(form.rank, rank)
        self.assertEqual(form.subItems, ["slice", "slab"])
        self.assertEqual(form.ui.__class__.__name__, "Ui_SelectionDlg")

        self.assertEqual(form.createGUI(), None)
        form.show()

        form.accept()
        self.assertEqual(form.result(), 1)

        self.assertEqual(form.rank, rank)
        self.assertEqual(form.starts, starts)
        self.assertEqual(form.stops, stops)
        self.assertEqual(form.steps, steps)
        self.assertEqual(form.offsets, [])
        self.assertEqual(form.blocks, [])
        self.assertEqual(form.counts, [])
        self.assertEqual(form.strides, [])
        self.assertEqual(form.ui.rankSpinBox.value(), rank)
        self.assertEqual(form.ui.selTableWidget.columnCount(), 3)
        self.assertEqual(form.ui.selTableWidget.rowCount(), rank)
        elem = [starts, stops, steps]
        for r in range(rank):
            for cl in range(3):
                it = form.ui.selTableWidget.item(r, cl)
                self.assertEqual(it.text(), str(elem[cl][r]))

    # create GUI test
    # \brief It tests default settings
    def test_createGUI_rank_ui_slabs_accept(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        rank = str(self.__rnd.randint(1, 6))
        irank = int(rank)
        offsets = [str(self.__rnd.randint(1, 100)) for r in range(irank)]
        blocks = [str(self.__rnd.randint(1, 100)) for r in range(irank)]
        counts = [str(self.__rnd.randint(1, 100)) for r in range(irank)]
        strides = [str(self.__rnd.randint(1, 100)) for r in range(irank)]
        form = SelectionDlg()
        # form.rank = rank
        form.offsets = offsets
        form.blocks = blocks
        form.counts = counts
        form.strides = strides
        form.keytype = 'slabs'
        self.assertEqual(form.subItems, ["slice", "slab"])
        self.assertEqual(form.ui.__class__.__name__, "Ui_SelectionDlg")

        self.assertEqual(form.createGUI(), None)
        form.show()

        form.ui.rankSpinBox.setValue(int(rank))
        self.assertEqual(form.ui.rankSpinBox.value(), irank)
        form.accept()
        self.assertEqual(form.result(), 1)

        self.assertEqual(form.rank, irank)
        self.assertEqual(form.starts, [])
        self.assertEqual(form.stops, [])
        self.assertEqual(form.steps, [])
        self.assertEqual(form.offsets, offsets)
        self.assertEqual(form.blocks, blocks)
        self.assertEqual(form.counts, counts)
        self.assertEqual(form.strides, strides)
        self.assertEqual(form.ui.rankSpinBox.value(), irank)
        self.assertEqual(form.ui.selTableWidget.columnCount(), 4)
        self.assertEqual(form.ui.selTableWidget.rowCount(), irank)
        elem = [offsets, blocks, counts, strides]
        for r in range(irank):
            for cl in range(len(elem)):
                it = form.ui.selTableWidget.item(r, cl)
                self.assertEqual(it.text(), str(elem[cl][r]))

    # create GUI test
    # \brief It tests default settings
    def test_createGUI_rank_ui_slides_accept(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        rank = self.__rnd.randint(1, 6)
        starts = [str(self.__rnd.randint(1, 100)) for r in range(rank)]
        stops = [str(self.__rnd.randint(1, 100)) for r in range(rank)]
        steps = [str(self.__rnd.randint(1, 100)) for r in range(rank)]
        form = SelectionDlg()
        form.starts = starts
        form.stops = stops
        form.steps = steps
        self.assertEqual(form.subItems, ["slice", "slab"])
        self.assertEqual(form.ui.__class__.__name__, "Ui_SelectionDlg")

        self.assertEqual(form.createGUI(), None)
        form.show()

        form.ui.rankSpinBox.setValue(rank)
        self.assertEqual(form.ui.rankSpinBox.value(), rank)
        form.accept()
        self.assertEqual(form.result(), 1)

        self.assertEqual(form.rank, rank)
        self.assertEqual(form.starts, starts)
        self.assertEqual(form.stops, stops)
        self.assertEqual(form.steps, steps)
        self.assertEqual(form.offsets, [])
        self.assertEqual(form.blocks, [])
        self.assertEqual(form.counts, [])
        self.assertEqual(form.strides, [])
        self.assertEqual(form.ui.rankSpinBox.value(), rank)
        self.assertEqual(form.ui.selTableWidget.columnCount(), 3)
        self.assertEqual(form.ui.selTableWidget.rowCount(), rank)
        elem = [starts, stops, steps]
        for r in range(rank):
            for cl in range(3):
                it = form.ui.selTableWidget.item(r, cl)
                self.assertEqual(it.text(), str(elem[cl][r]))


if __name__ == '__main__':
    if not app:
        app = QApplication([])
    unittest.main()
