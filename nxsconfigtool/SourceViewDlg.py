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
# \file SourceViewDlg.py
# SourceView dialog class

""" sourceview widget """

import copy

from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QModelIndex
from PyQt5 import uic

import os
import sys


try:
    from .DimensionsDlg import DimensionsDlg
except Exception:
    from DimensionsDlg import DimensionsDlg
try:
    from .SelectionDlg import SelectionDlg
except Exception:
    from SelectionDlg import SelectionDlg
try:
    from .NodeDlg import NodeDlg
except Exception:
    from NodeDlg import NodeDlg
try:
    from .DomTools import DomTools
except Exception:
    from DomTools import DomTools

import logging
# message logger
logger = logging.getLogger("nxsdesigner")

_formclass, _baseclass = uic.loadUiType(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "ui", "sourceviewdlg.ui"))

if sys.version_info > (3,):
    unicode = str


# dialog defining a sourceview tag
class SourceViewDlg(NodeDlg):

    # constructor
    # \param parent patent instance
    def __init__(self, parent=None):
        super(SourceViewDlg, self).__init__(parent)

        # sourceview doc
        self.doc = u''

        # rank
        self.rank = 0
        # dimensions
        self.dimensions = []
        self.__dimensions = []

        # key type
        self.keytype = "slices"
        # starts
        self.__starts = []
        # stops
        self.__stops = []
        # steps
        self.__steps = []

        # offsets
        self.__offsets = []
        # blocks
        self.__blocks = []
        # counts
        self.__counts = []
        # strides
        self.__strides = []

        # selection
        self.selection = []
        self.__selection = []

        # allowed subitems
        self.subItems = ["datasource", "doc",
                         "dimensions",
                         "selection",
                         "enumeration", "strategy"]

        # user interface
        self.ui = _formclass()

    # provides the state of the sourceview dialog
    # \returns state of the sourceview in tuple
    def getState(self):
        dimensions = copy.copy(self.dimensions)
        selection = copy.copy(self.selection)

        state = (self.doc,
                 self.rank,
                 dimensions,
                 selection,
                 )
        return state

    # sets the state of the sourceview dialog
    # \param state sourceview state written in tuple
    def setState(self, state):

        (self.doc,
         self.rank,
         dimensions,
         selection,
         ) = state
        self.dimensions = copy.copy(dimensions)
        self.selection = copy.copy(selection)
        if selection and selection[0] and len(selection) == 4:
            self.keytype = "slabs"
        else:
            self.keytype = "slices"

    # updates the sourceview dialog
    # \brief It sets the form local variables
    def updateForm(self):
        if self.doc is not None:
            self.ui.docTextEdit.setText(self.doc)

        if self.rank < len(self.dimensions):
            self.rank = len(self.dimensions)

        if self.dimensions:
            label = self.dimensions.__str__()
            self.ui.dimLabel.setText("%s" % label.replace('None', '*'))
        elif self.rank > 0:
            label = ([None] * (self.rank)).__str__()
            self.ui.dimLabel.setText("%s" % label.replace('None', '*'))
        else:
            self.ui.dimLabel.setText("[]")

        self.__dimensions = []
        for dm in self.dimensions:
            self.__dimensions.append(dm)

        if self.rank < len(self.selection):
            self.rank = len(self.selection)

        if self.selection:
            label = self.selection.__str__()
            self.ui.selLabel.setText("%s" % label.replace('None', '*'))
        elif self.rank > 0:
            label = ([None] * (self.rank)).__str__()
            self.ui.selLabel.setText("%s" % label.replace('None', '*'))
        else:
            self.ui.selLabel.setText("[]")

        self.__selection = []
        for idx, dm in enumerate(self.selection):
            self.__selection.append(dm)
            if hasattr(dm, "__len__") and len(dm) == 4:
                self.keytype = "slabs"
                for elems in [self.__offsets, self.__blocks,
                              self.__counts, self.__strides]:
                    while len(elems) <= idx:
                        elems.append(None)
                self.__offsets[idx] = dm[0]
                self.__blocks[idx] = dm[1]
                self.__counts[idx] = dm[2]
                self.__strides[idx] = dm[3]
            elif hasattr(dm, "__len__") and len(dm) == 3:
                self.keytype = "slices"
                for elems in [self.__starts, self.__steps, self.__stops]:
                    while len(elems) <= idx:
                        elems.append(None)
                self.__starts[idx] = dm[0]
                self.__stops[idx] = dm[1]
                self.__steps[idx] = dm[2]

    #  creates GUI
    # \brief It calls setupUi and  connects signals and slots
    def createGUI(self):
        self.ui.setupUi(self)

        self.updateForm()

        self.__updateUi()

        self.ui.resetPushButton.clicked.connect(self.reset)
        self.ui.dimPushButton.clicked.connect(
            self.__changeDimensions)
        self.ui.selPushButton.clicked.connect(
            self.__changeSelection)

    # sets the form from the DOM node
    # \param node DOM node
    def setFromNode(self, node=None):
        if node:
            # defined in NodeDlg
            self.node = node
        if not self.node:
            return

        text = DomTools.getText(self.node)
        self.value = unicode(text).strip() if text else ""

        dimens = self.node.firstChildElement(str("dimensions"))
        attributeMap = dimens.attributes()

        self.dimensions = []
        self.__dimensions = []
        if attributeMap.contains("rank"):
            try:
                self.rank = int(attributeMap.namedItem("rank").nodeValue())
                if self.rank < 0:
                    self.rank = 0
            except Exception:
                self.rank = 0
        else:
            self.rank = 0
        if self.rank > 0:
            child = dimens.firstChild()
            while not child.isNull():
                if child.isElement() and child.nodeName() == "dim":
                    attributeMap = child.attributes()
                    index = None
                    value = None
                    try:
                        if attributeMap.contains("index"):
                            index = int(
                                attributeMap.namedItem("index").nodeValue())
                        if attributeMap.contains("value"):
                            value = str(
                                attributeMap.namedItem("value").nodeValue())
                    except Exception:
                        pass

                    text = DomTools.getText(child)
                    if text and "$datasources." in text:
                        value = str(text).strip()
                    if index < 1:
                        index = None
                    if index is not None:
                        while len(self.dimensions) < index:
                            self.dimensions.append(None)
                            self.__dimensions.append(None)
                        self.__dimensions[index - 1] = value
                        self.dimensions[index - 1] = value

                child = child.nextSibling()

        if self.rank < len(self.dimensions):
            self.rank = len(self.dimensions)
            self.rank = len(self.__dimensions)
        elif self.rank > len(self.dimensions):
            self.dimensions.extend(
                [None] * (self.rank - len(self.dimensions)))
            self.__dimensions.extend(
                [None] * (self.rank - len(self.__dimensions)))

        selects = self.node.firstChildElement(str("selection"))
        attributeMap = selects.attributes()

        self.selection = []
        self.__selection = []
        if attributeMap.contains("rank"):
            try:
                self.rank = int(attributeMap.namedItem("rank").nodeValue())
                if self.rank < 0:
                    self.rank = 0
            except Exception:
                self.rank = 0
        else:
            self.rank = 0
        if self.rank > 0:
            child = selects.firstChild()
            while not child.isNull():
                if child.isElement() and child.nodeName() == "slice":
                    attributeMap = child.attributes()
                    index = None
                    start = None
                    stop = None
                    step = None
                    try:
                        if attributeMap.contains("index"):
                            index = int(
                                attributeMap.namedItem("index").nodeValue())
                        if attributeMap.contains("start"):
                            start = str(
                                attributeMap.namedItem("start").nodeValue())
                        if attributeMap.contains("stop"):
                            stop = str(
                                attributeMap.namedItem("stop").nodeValue())
                        if attributeMap.contains("step"):
                            step = str(
                                attributeMap.namedItem("step").nodeValue())
                    except Exception:
                        pass

                    text = DomTools.getText(child)
                    value = ""
                    if text and "$datasources." in text:
                        value = str(text).strip()

                    if index < 1:
                        index = None
                    if index is not None:
                        while len(self.__starts) < index:
                            self.__starts.append(None)
                        self.__starts[index - 1] = value or start
                        while len(self.__stops) < index:
                            self.__stops.append(None)
                        self.__stops[index - 1] = stop
                        while len(self.__steps) < index:
                            self.__steps.append(None)
                        self.__steps[index - 1] = step

                        while len(self.selection) < index:
                            self.selection.append([None, None, None])
                            self.__selection.append([None, None, None])
                        self.__selection[index - 1] = [
                            self.__starts[index - 1],
                            self.__stops[index - 1],
                            self.__steps[index - 1]]
                        self.selection[index - 1] = [
                            self.__starts[index - 1],
                            self.__stops[index - 1],
                            self.__steps[index - 1]]

                elif child.isElement() and child.nodeName() == "slab":
                    attributeMap = child.attributes()
                    index = None
                    offset = None
                    block = None
                    count = None
                    stride = None
                    value = None
                    try:
                        if attributeMap.contains("index"):
                            index = int(
                                attributeMap.namedItem("index").nodeValue())
                        if attributeMap.contains("offset"):
                            offset = str(
                                attributeMap.namedItem("offset").nodeValue())
                        if attributeMap.contains("block"):
                            block = str(
                                attributeMap.namedItem("block").nodeValue())
                        if attributeMap.contains("count"):
                            count = str(
                                attributeMap.namedItem("count").nodeValue())
                        if attributeMap.contains("stride"):
                            stride = str(
                                attributeMap.namedItem("stride").nodeValue())
                    except Exception:
                        pass

                    text = DomTools.getText(child)
                    if text and "$datasources." in text:
                        value = str(text).strip()

                    if index < 1:
                        index = None
                    if index is not None:
                        while len(self.__offsets) < index:
                            self.__offsets.append(None)
                        self.__offsets[index - 1] = value or offset

                        while len(self.__blocks) < index:
                            self.__blocks.append(None)
                        self.__blocks[index - 1] = block

                        while len(self.__counts) < index:
                            self.__counts.append(None)
                        self.__counts[index - 1] = count

                        while len(self.__strides) < index:
                            self.__strides.append(None)
                        self.__strides[index - 1] = stride

                        while len(self.selection) < index:
                            self.selection.append([None, None, None, None])
                            self.__selection.append([None, None, None, None])
                        self.__selection[index - 1] = [
                            self.__offsets[index - 1],
                            self.__blocks[index - 1],
                            self.__counts[index - 1],
                            self.__strides[index - 1]]
                        self.selection[index - 1] = [
                            self.__offsets[index - 1],
                            self.__blocks[index - 1],
                            self.__counts[index - 1],
                            self.__strides[index - 1]]

                child = child.nextSibling()

        if self.keytype == "slices":
            elems = [self.__starts, self.__stops, self.__steps]
        else:
            elems = [self.__offsets, self.__blocks,
                     self.__counts, self.__strides]
        for el, elem in enumerate(elems):
            if self.rank < len(elem):
                self.rank = len(elem)
            elif self.rank > len(elem):
                elem.extend(
                    [None] * (self.rank - len(elem)))

        if self.rank < len(self.selection):
            self.rank = len(self.selection)
            self.rank = len(self.__selection)
        elif self.rank > len(self.selection):
            if self.keytype == "slices":
                self.selection.extend(
                    [None, None, None] * (
                        self.rank - len(self.selection)))
                self.__selection.extend(
                    [None, None, None] * (
                        self.rank - len(self.__selection)))
            else:
                self.selection.extend(
                    [None, None, None, None] * (
                        self.rank - len(self.selection)))
                self.__selection.extend(
                    [None, None, None, None] * (
                        self.rank - len(self.__selectixsons)))

        doc = self.node.firstChildElement(str("doc"))
        text = DomTools.getText(doc)
        self.doc = unicode(text).strip() if text else ""

    # changing dimensions of the map
    #  \brief It runs the Dimensions Dialog and fetches rank
    #         and dimensions from it
    def __changeDimensions(self):
        dform = DimensionsDlg(self)
        dform.rank = self.rank
        dform.lengths = [ln for ln in self.__dimensions]
        dform.createGUI()
        if dform.exec_():
            self.rank = dform.rank
            if self.rank:
                self.__dimensions = [dm for dm in dform.lengths]
            else:
                self.__dimensions = []
            label = self.__dimensions.__str__()
            self.ui.dimLabel.setText("%s" % label.replace('None', '*'))

    # changing selection of the sourceview
    #  \brief It runs the Selection Dialog and fetches rank
    #         and selection from it
    def __changeSelection(self):
        dform = SelectionDlg(self)
        dform.rank = self.rank
        dform.keytype = self.keytype
        dform.starts = [ln for ln in self.__starts]
        dform.stops = [ln for ln in self.__stops]
        dform.steps = [ln for ln in self.__steps]
        dform.offsets = [ln for ln in self.__offsets]
        dform.blocks = [ln for ln in self.__blocks]
        dform.counts = [ln for ln in self.__counts]
        dform.strides = [ln for ln in self.__strides]
        dform.createGUI()
        if dform.exec_():
            self.rank = dform.rank
            self.keytype = dform.keytype
            if self.rank:
                self.__starts = [dm for dm in dform.starts]
                self.__stops = [dm for dm in dform.stops]
                self.__steps = [dm for dm in dform.steps]
                self.__offsets = [dm for dm in dform.offsets]
                self.__blocks = [dm for dm in dform.blocks]
                self.__counts = [dm for dm in dform.counts]
                self.__strides = [dm for dm in dform.strides]
            else:
                self.__starts = []
                self.__stops = []
                self.__steps = []
                self.__offsets = []
                self.__blocks = []
                self.__counts = []
                self.__strides = []

            self.__selection = []
            if self.keytype == "slices":
                for rk in range(self.rank):
                    self.__selection.append(
                        [self.__starts[rk]
                         if rk < len(self.__starts) else None,
                         self.__stops[rk]
                         if rk < len(self.__stops) else None,
                         self.__steps[rk]
                         if rk < len(self.__steps) else None
                         ]
                    )
            else:
                for rk in range(self.rank):
                    self.__selection.append(
                        [self.__offsets[rk]
                         if rk < len(self.__offsets) else None,
                         self.__blocks[rk]
                         if rk < len(self.__blocks) else None,
                         self.__counts[rk]
                         if rk < len(self.__counts) else None,
                         self.__strides[rk]
                         if rk < len(self.__strides) else None
                         ]
                    )
            label = self.__selection.__str__()
            # print("SEL", self.__selection)
            self.ui.selLabel.setText("%s" % label.replace('None', '*'))

    # updates sourceview user interface
    # \brief It sets enable or disable the OK button
    def __updateUi(self):
        self.ui.applyPushButton.setEnabled(True)

    # appends newElement
    # \param newElement DOM node to append
    # \param parent parent DOM node
    def appendElement(self, newElement, parent):
        singles = {"datasource": "DataSource", "strategy": "Strategy"}
        if unicode(newElement.nodeName()) in singles:
            if not self.node:
                return
            child = self.node.firstChild()
            while not child.isNull():
                if child.nodeName() == unicode(newElement.nodeName()):
                    QMessageBox.warning(
                        self,
                        "%s exists" % singles[str(newElement.nodeName())],
                        "To add a new %s please remove the old one"
                        % newElement.nodeName())
                    return False
                child = child.nextSibling()

        return NodeDlg.appendElement(self, newElement, parent)

    # applys input text strings
    # \brief It copies the sourceview name and type from lineEdit widgets
    #        and apply the dialog
    def apply(self):
        self.doc = unicode(self.ui.docTextEdit.toPlainText())

        index = self.view.currentIndex()
        finalIndex = self.view.model().createIndex(
            index.row(), 2, index.parent().internalPointer())

        self.view.expand(index)

        self.dimensions = []
        for dm in self.__dimensions:
            self.dimensions.append(dm)

        self.selection = []
        for dm in self.__selection:
            self.selection.append(dm)

        if self.node and self.root and self.node.isElement():
            self.updateNode(index)

        if index.column() != 0:
            index = self.view.model().index(index.row(), 0, index.parent())
        self.view.expand(index)
        self.view.model().dataChanged.emit(index, finalIndex)
        self.view.model().dataChanged.emit(index, index)

    # updates the Node
    # \brief It sets node from the dialog variables
    def updateNode(self, index=QModelIndex()):
        elem = self.node.toElement()

        mindex = self.view.currentIndex() if not index.isValid() else index

        doc = self.node.firstChildElement(str("doc"))
        if not self.doc and doc and doc.nodeName() == "doc":
            self.removeElement(doc, mindex)
        elif self.doc:
            newDoc = self.root.createElement(str("doc"))
            newText = self.root.createTextNode(str(self.doc))
            newDoc.appendChild(newText)
            if doc and doc.nodeName() == "doc":
                self.replaceElement(doc, newDoc, mindex)
            else:
                self.appendElement(newDoc, mindex)

        dimens = self.node.firstChildElement(str("dimensions"))
        if not self.dimensions and dimens \
                and dimens.nodeName() == "dimensions":
            self.removeElement(dimens, mindex)
        elif self.dimensions:
            newDimens = self.root.createElement(str("dimensions"))
            newDimens.setAttribute(str("rank"),
                                   str(unicode(self.rank)))
            dimDefined = True
            for i in range(min(self.rank, len(self.dimensions))):
                if self.dimensions[i] is None:
                    dimDefined = False
            if dimDefined:
                for i in range(min(self.rank, len(self.dimensions))):
                    dim = self.root.createElement(str("dim"))
                    dim.setAttribute(str("index"), str(unicode(i + 1)))
                    if "$datasources." not in unicode(self.dimensions[i]):

                        dim.setAttribute(str("value"),
                                         str(unicode(self.dimensions[i])))
                    else:
                        dsText = self.root.createTextNode(
                            str(unicode(self.dimensions[i])))
                        dstrategy = self.root.createElement(
                            str("strategy"))
                        dstrategy.setAttribute(
                            str("mode"),
                            str(unicode("CONFIG")))
                        dim.appendChild(dsText)
                        dim.appendChild(dstrategy)

                    newDimens.appendChild(dim)

            if dimens and dimens.nodeName() == "dimensions":
                self.replaceElement(dimens, newDimens, mindex)
            else:
                self.appendElement(newDimens, mindex)

        selects = self.node.firstChildElement(str("selection"))
        if not self.selection and selects \
                and selects.nodeName() == "selection":
            self.removeElement(selects, mindex)
        elif self.selection:
            newDimens = self.root.createElement(str("selection"))
            newDimens.setAttribute(str("rank"),
                                   str(unicode(self.rank)))
            dimDefined = True
            for i in range(min(self.rank, len(self.selection))):
                if self.selection[i] is None:
                    dimDefined = False
            if dimDefined:
                for i in range(min(self.rank, len(self.selection))):
                    dm = self.selection[i]
                    if hasattr(dm, "__len__") and len(dm) == 4:
                        dim = self.root.createElement(str("slab"))
                        elem = ["offset", "block", "count", "stride"]
                    elif hasattr(dm, "__len__") and len(dm) == 3:
                        dim = self.root.createElement(str("slice"))
                        elem = ["start", "stop", "step"]
                    else:
                        continue
                    dim.setAttribute(str("index"), str(unicode(i + 1)))
                    for di, sel in enumerate(dm):
                        if "$datasources." not in unicode(sel):

                            dim.setAttribute(str(elem[di]),
                                             str(unicode(sel)))
                        else:
                            dsText = self.root.createTextNode(
                                str(unicode(sel)))
                            dstrategy = self.root.createElement(
                                str("strategy"))
                            dstrategy.setAttribute(
                                str("mode"),
                                str(unicode("CONFIG")))
                            dim.appendChild(dsText)
                            dim.appendChild(dstrategy)

                    newDimens.appendChild(dim)

            if dimens and dimens.nodeName() == "selection":
                self.replaceElement(dimens, newDimens, mindex)
            else:
                self.appendElement(newDimens, mindex)


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    logging.basicConfig(level=logging.DEBUG)

    # Qt application
    app = QApplication(sys.argv)
    # sourceview form
    form = SourceViewDlg()
    form.doc = """Distance between the source and the mca detector.
It should be defined by client."""
    form.dimensions = [3]
    form.selection = [[2, 3, None]]
    form.value = "1.23,3.43,4.23"
    form.createGUI()
    form.show()
    app.exec_()
    if form.dimensions:
        logger.info("Dimensions:")
        for mrow, mln in enumerate(form.dimensions):
            logger.info(" %s: %s " % (mrow + 1, mln))

    if form.doc:
        logger.info("Doc: \n%s" % form.doc)
