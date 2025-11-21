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
# \package nxsconfigtool nexdatas
# \file SlicesDlg.py
# Slices dialog class

""" slices widget """

from PyQt5.QtCore import (Qt, )
from PyQt5.QtWidgets import (QTableWidgetItem, QMessageBox, QDialog)
from PyQt5 import uic

import os
import sys

import logging
# message logger
logger = logging.getLogger("nxsdesigner")

_formclass, _baseclass = uic.loadUiType(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "ui", "selectionsdlg.ui"))

if sys.version_info > (3,):
    unicode = str
    long = int


# dialog defining a selections tag
class SelectionsDlg(QDialog):

    # constructor
    # \param parent patent instance
    def __init__(self, parent=None):
        super(SelectionsDlg, self).__init__(parent)

        # selections rank
        self.rank = 0
        # selections start
        self.starts = []
        # selections stops
        self.stops = []
        # selections stops
        self.steps = []
        # selections stops
        self.offsets = []
        # selections blocks
        self.blocks = []
        # selections counts
        self.counts = []
        # selections strides
        self.strides = []
        # key type
        self.keytype = "slices"

        # user interface
        self.ui = _formclass()

        # allowed subitems
        self.subItems = ["slice", "slab"]

    #  creates GUI
    # \brief It calls setupUi and  connects signals and slots
    def createGUI(self):
        self.ui.setupUi(self)
        if self.keytype.lower() == "slices":
            self.keytype = "slices"
            self.ui.keytypeComboBox.setCurrentIndex(0)
        else:
            self.keytype = "slab"
            self.ui.keytypeComboBox.setCurrentIndex(1)
        try:
            if self.rank is not None and int(self.rank) >= 0:
                self.rank = int(self.rank)
                for elem in [self.starts, self.stops, self.steps, self.offsets,
                             self.blocks, self.counts, self.strides]:
                    for i, ln in enumerate(elem):
                        if ln is not None:
                            if isinstance(ln, int) or \
                                   '$var.' not in ln and \
                                   '$datasources.' not in ln:

                                iln = int(ln)
                                elem[i] = ln
                                if iln < 1:
                                    elem[i] = None
                            else:
                                elem[i] = ln
                        else:
                            elem[i] = None
        except Exception:
            #  print(str(e))
            self.rank = 1
            self.starts = []
            self.stops = []
            self.steps = []
            self.offsets = []
            self.blocks = []
            self.counts = []
            self.strides = []

        if not self.starts:
            self.starts = []
        if not self.stops:
            self.stops = []
        if not self.steps:
            self.steps = []
        if not self.offsets:
            self.offsets = []
        if not self.blocks:
            self.blocks = []
        if not self.counts:
            self.counts = []
        if not self.strides:
            self.strides = []

        self.ui.rankSpinBox.setValue(self.rank)

        self.ui.selTableWidget.itemChanged.connect(
            self.__tableItemChanged)

        self.ui.selTableWidget.setSortingEnabled(False)
        self.__populateKeys()
        self.ui.rankSpinBox.setFocus()

        self.ui.rankSpinBox.valueChanged[int].connect(self.__valueChanged)
        self.ui.keytypeComboBox.currentIndexChanged[str].connect(
            self._currentIndexChanged)

    # calls updateUi when the name text is changing
    # \param text the edited text
    def _currentIndexChanged(self, text):
        if text == 'slices':
            self.keytype = 'slices'
        else:
            self.keytype = 'slabs'
        self.__populateKeys()

    # takes a name of the current dim
    # \returns name of the current dim
    def __currentTableDim(self):
        return (self.ui.selTableWidget.currentRow(),
                self.ui.selTableWidget.currentColumn())

    # changes the current value of the dim
    # \brief It changes the current value of the dim
    # and informs the user about wrong values
    def __tableItemChanged(self, item):
        row, col = self.__currentTableDim()

        if self.keytype.lower() == 'slices':
            elems = [self.starts, self.stops, self.steps]
        else:
            elems = [self.offsets, self.blocks,
                     self.counts, self.strides]

        if col not in range(len(elems)):
            return
        elem = elems[col]
        if row not in range(len(elem)):
            return
        try:
            if item.text():
                if '$var' not in str(item.text()) and  \
                        '$datasources' not in str(item.text()):
                    iln = int(item.text())
                    if iln < 0:
                        raise ValueError("Negative value")
                ln = str(item.text())
                elem[row] = ln
            else:
                elem[row] = None
        except Exception:
            # print(str(e))
            QMessageBox.warning(
                self, "Value Error", "Wrong value of the edited length")

        self.__populateKeys()

    # calls updateUi when the name text is changing
    # \param text the edited text
    def __valueChanged(self):
        self.rank = int(self.ui.rankSpinBox.value())
        self.__populateKeys(self.rank - 1)

    # fills in the dim table
    # \param selectedDim selected dim
    def __populateKeys(self, selectedDim=None):
        selected = None
        self.ui.selTableWidget.clear()
        self.ui.selTableWidget.setRowCount(self.rank)

        if self.keytype.lower() == 'slices':
            headers = ["Start", "Stop", "Step"]
        else:
            headers = ["Offset", "Block", "Count", "Stride"]
        self.ui.selTableWidget.setColumnCount(len(headers))
        self.ui.selTableWidget.setHorizontalHeaderLabels(headers)
        self.ui.selTableWidget.setVerticalHeaderLabels(
            [unicode(el + 1) for el in range(self.rank)])
        if self.keytype.lower() == 'slices':
            elems = [self.starts, self.stops, self.steps]
        else:
            elems = [self.offsets, self.blocks,
                     self.counts, self.strides]

        for col, elem in enumerate(elems):
            while self.rank > len(elem):
                elem.append(None)
            for row, ln in enumerate(elem):
                if ln:
                    item = QTableWidgetItem(unicode(ln))
                else:
                    item = QTableWidgetItem("")
                print(row, col, ln)
                item.setData(Qt.UserRole, (long(row)))
                if selectedDim is not None and selectedDim == row:
                    selected = item
                self.ui.selTableWidget.setItem(row, col, item)
        self.ui.selTableWidget.resizeColumnsToContents()
        self.ui.selTableWidget.horizontalHeader().setStretchLastSection(True)
        if selected is not None:
            selected.setSelected(True)
            self.ui.selTableWidget.setCurrentItem(selected)
            self.ui.selTableWidget.editItem(selected)

    # accepts input text strings
    # \brief It copies the selections name and type from lineEdit widgets
    #        and accept the dialog
    def accept(self):
        if self.keytype.lower() == 'slices':
            elems = [self.starts, self.stops, self.steps]
        else:
            elems = [self.offsets, self.blocks,
                     self.counts, self.strides]

        for elem in elems:
            while len(elem) > self.rank:
                elem.pop()
        QDialog.accept(self)


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    logging.basicConfig(level=logging.DEBUG)

    # Qt application
    app = QApplication(sys.argv)
    # selections form
    form = SelectionsDlg()
    form.rank = 2
    form.keytype = "slices"
    form.starts = [2, None]
    form.stops = [10, 20]
    form.steps = [None, 2]
    # form.keytype = "slabs"
    form.offsets = [2, None]
    form.blocks = [10, 20]
    form.counts = [None, 2]
    form.strides = [None, 21]
    form.createGUI()
    form.show()
    app.exec_()

    if form.result():
        if form.rank:
            logger.info("Selections: rank = %s" % (form.rank))
        if form.keytype:
            logger.info("Selections: keytype = %s" % (form.keytype))

        logger.info("Selections: starts = %s" % (form.starts))
        logger.info("Selections: stops = %s" % (form.stops))
        logger.info("Selections: steps = %s" % (form.steps))
        logger.info("Selections: offsets = %s" % (form.offsets))
        logger.info("Selections: blocks = %s" % (form.blocks))
        logger.info("Selections: counts = %s" % (form.counts))
        logger.info("Selections: strides = %s" % (form.strides))

        #     logger.info("Lengths:")
        #     for mrow, mln in enumerate(form.lengths):
        #         logger.info(" %s: %s " % (mrow + 1, mln))
