#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012 Jan Kotanski
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
## \package ndtsconfigtool nexdatas
## \file DefinitionDlg.py
# Definition dialog class

import re
from PyQt4.QtCore import (SIGNAL, QString, Qt, QVariant, QModelIndex)
from PyQt4.QtGui import (QMessageBox, QTableWidgetItem)
from ui.ui_definitiondlg import  Ui_DefinitionDlg

import copy 

from AttributeDlg import AttributeDlg
from NodeDlg import NodeDlg 

## dialog defining a definition tag
class DefinitionDlg(NodeDlg, Ui_DefinitionDlg):
    
    ## constructor
    # \param parent patent instance
    def __init__(self, parent=None):
        super(DefinitionDlg, self).__init__(parent)
        
        ## definition name
        self.name = u''
        ## definition type
        self.nexusType = u''
        ## definition doc
        self.doc = u''
        ## definition attributes
        self.attributes = {}
        self._attributes = {}

        ## allowed subitems
        self.subItems = ["group", "field", "attribute", "link", "component", "doc", "symbols"]




    ## updates the definition dialog
    # \brief It sets the form local variables
    def updateForm(self):

        if self.name is not None:
            self.nameLineEdit.setText(self.name) 
        if self.nexusType is not None:
            self.typeLineEdit.setText(self.nexusType) 
        if self.doc is not None:
            self.docTextEdit.setText(self.doc)


        self._attributes.clear()
        for at in self.attributes.keys():
            self._attributes[unicode(at)]=self.attributes[(unicode(at))]

        self.populateAttributes()
        


        
    ## provides the state of the definition dialog        
    # \returns state of the definition in tuple
    def getState(self):
        attributes = copy.copy(self.attributes)

        state = (self.name,
                 self.nexusType,
                 self.doc,
                 attributes
                 )
#        print  "GET", unicode(state)
        return state



    ## sets the state of the definition dialog        
    # \param state definition state written in tuple 
    def setState(self, state):

        (self.name,
         self.nexusType,
         self.doc,
         attributes
         ) = state
#        print "SET",  unicode(state)
        self.attributes = copy.copy(attributes)



    ##  creates GUI
    # \brief It calls setupUi and  connects signals and slots    
    def createGUI(self):
        self.setupUi(self)
        
        self.updateForm()

        self._updateUi()

#        self.connect(self.applyPushButton, SIGNAL("clicked()"), self.apply)
        self.connect(self.resetPushButton, SIGNAL("clicked()"), self.reset)
        self.connect(self.attributeTableWidget, SIGNAL("itemChanged(QTableWidgetItem*)"),
                     self._tableItemChanged)
        self.connect(self.addPushButton, SIGNAL("clicked()"), self._addAttribute)
        self.connect(self.removePushButton, SIGNAL("clicked()"), self._removeAttribute)

        self.connect(self.typeLineEdit, SIGNAL("textEdited(QString)"), self._updateUi)


    ## sets the form from the DOM node
    # \param node DOM node
    def setFromNode(self, node=None):
        if node:
            ## defined in NodeDlg class
            self.node = node
        attributeMap = self.node.attributes()
        nNode = unicode(self.node.nodeName())

        self.name = unicode(attributeMap.namedItem("name").nodeValue() if attributeMap.contains("name") else "")
        self.nexusType = unicode(attributeMap.namedItem("type").nodeValue() if attributeMap.contains("type") else "")

        self.attributes.clear()    
        self._attributes.clear()    
        for i in range(attributeMap.count()):
            attribute = attributeMap.item(i)
            attrName = unicode(attribute.nodeName())
            if attrName != "name" and attrName != "type":
                self.attributes[attrName] = unicode(attribute.nodeValue())
                self._attributes[attrName] = unicode(attribute.nodeValue())

        doc = self.node.firstChildElement(QString("doc"))           
        text = self._getText(doc)    
        self.doc = unicode(text).strip() if text else ""
             
    ## adds an attribute    
    #  \brief It runs the Definition Dialog and fetches attribute name and value    
    def _addAttribute(self):
        aform  = AttributeDlg()
        if aform.exec_():
            name = aform.name
            value = aform.value
            
            if not aform.name in self._attributes.keys():
                self._attributes[aform.name] = aform.value
                self.populateAttributes(aform.name)
            else:
                QMessageBox.warning(self, "Attribute name exists", "To change the attribute value, please edit the value in the attribute table")
                
                
    ## takes a name of the current attribute
    # \returns name of the current attribute            
    def _currentTableAttribute(self):
        item = self.attributeTableWidget.item(self.attributeTableWidget.currentRow(), 0)
        if item is None:
            return None
        return item.data(Qt.UserRole).toString()


    ## removes an attribute    
    #  \brief It removes the current attribute asking before about it
    def _removeAttribute(self):
        attr = self._currentTableAttribute()
        if attr is None:
            return
        if QMessageBox.question(self, "Attribute - Remove",
                                "Remove attribute: %s = \'%s\'".encode() %  (attr, self._attributes[unicode(attr)]),
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.No :
            return
        if unicode(attr) in self._attributes.keys():
            self._attributes.pop(unicode(attr))
            self.populateAttributes()


    ## changes the current value of the attribute        
    # \brief It changes the current value of the attribute and informs the user that attribute names arenot editable
    def _tableItemChanged(self, item):
        attr = self._currentTableAttribute()
        if unicode(attr)  not in self._attributes.keys():
            return
        column = self.attributeTableWidget.currentColumn()
        if column == 1:
            self._attributes[unicode(attr)] = unicode(item.text())
        if column == 0:
            QMessageBox.warning(self, "Attribute name is not editable", "To change the attribute name, please remove the attribute and add the new one")
        self.populateAttributes()


    ## fills in the attribute table      
    # \param selectedAttribute selected attribute    
    def populateAttributes(self, selectedAttribute = None):
        selected = None
        self.attributeTableWidget.clear()
        self.attributeTableWidget.setSortingEnabled(False)
        self.attributeTableWidget.setRowCount(len(self._attributes))
        headers = ["Name", "Value"]
        self.attributeTableWidget.setColumnCount(len(headers))
        self.attributeTableWidget.setHorizontalHeaderLabels(headers)	
        for row, name in enumerate(self._attributes):
            item = QTableWidgetItem(name)
            item.setData(Qt.UserRole, QVariant(name))
            self.attributeTableWidget.setItem(row, 0, item)
            item2 =  QTableWidgetItem(self._attributes[name])
            self.attributeTableWidget.setItem(row, 1, item2)
            if selectedAttribute is not None and selectedAttribute == name:
                selected = item2
        self.attributeTableWidget.setSortingEnabled(True)
        self.attributeTableWidget.resizeColumnsToContents()
        self.attributeTableWidget.horizontalHeader().setStretchLastSection(True)
        if selected is not None:
            selected.setSelected(True)
            self.attributeTableWidget.setCurrentItem(selected)
            


    ## updates definition user interface
    # \brief It sets enable or disable the OK button
    def _updateUi(self):
        pass
#        enable = not self.typeLineEdit.text().isEmpty()
#        self.applyPushButton.setEnabled(enable)



    ## applys input text strings
    # \brief It copies the definition name and type from lineEdit widgets and apply the dialog
    def apply(self):
        self.name = unicode(self.nameLineEdit.text())
        self.nexusType = unicode(self.typeLineEdit.text())

        self.doc = unicode(self.docTextEdit.toPlainText())
        
        index = self.view.currentIndex()
        finalIndex = self.view.model().createIndex(index.row(),2,index.parent().internalPointer())

        self.attributes.clear()
        for at in self._attributes.keys():
            self.attributes[at] = self._attributes[at]

        if self.node  and self.root and self.node.isElement():
            self.updateNode(index)

        if  index.column() != 0:
            index = self.view.model().index(index.row(), 0, index.parent())
        self.view.model().emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index,finalIndex)


    ## updates the Node
    # \brief It sets node from the dialog variables
    def updateNode(self,index=QModelIndex()):
        elem=self.node.toElement()
            
        attributeMap = self.node.attributes()
        for i in range(attributeMap.count()):
            attributeMap.removeNamedItem(attributeMap.item(i).nodeName())
        if self.name:    
            elem.setAttribute(QString("name"), QString(self.name))
        if self.nexusType:
            elem.setAttribute(QString("type"), QString(self.nexusType))

        for attr in self.attributes.keys():
            elem.setAttribute(QString(attr), QString(self.attributes[attr]))

                
        doc = self.node.firstChildElement(QString("doc"))           
        if not self.doc and doc and doc.nodeName() == "doc" :
            self._removeElement(doc, index)
        elif self.doc:
            newDoc = self.root.createElement(QString("doc"))
            newText = self.root.createTextNode(QString(self.doc))
            newDoc.appendChild(newText)
            if doc and doc.nodeName() == "doc" :
                self._replaceElement(doc, newDoc, index)
            else:
                self._appendElement(newDoc, index)

        
if __name__ == "__main__":
    import sys
    from PyQt4.QtGui import QApplication

    ## Qt application
    app = QApplication(sys.argv)
    ## definition form
    form = DefinitionDlg()
    form.name = 'entry'
    form.nexusType = 'NXentry'
    form.doc = 'The main entry'
    form.attributes={"title":"Test run 1", "run_cycle":"2012-1"}
    form.createGUI()
    form.show()
    app.exec_()


    if form.nexusType:
        print "Definition: name = \'%s\' type = \'%s\'" % ( form.name, form.nexusType )
    if form.attributes:
        print "Other attributes:"
        for k in form.attributes.keys():
            print  " %s = '%s' " % (k, form.attributes[k])
    if form.doc:
        print "Doc: \n%s" % form.doc
    
