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
## \package ndtsconfigtool nexdatas
## \file ComponentList.py
# Data component list class


""" component list widget """

import os

from PyQt4.QtCore import (Qt, QString, QVariant)
from PyQt4.QtGui import (QWidget, QMenu, QMessageBox, QListWidgetItem)

from .ui.ui_elementlist import Ui_ElementList
from .Component import Component
from .LabeledObject import LabeledObject
from .ElementList import ElementList

## dialog defining a group tag
class ComponentList(ElementList):
    
    ## constructor
    # \param directory element directory
    # \param parent patent instance
    def __init__(self, directory, parent=None):
        super(ComponentList, self).__init__(parent)

        ## directory from which elements are loaded by default
        self.directory = directory
        
        ## group elements
        self.elements = {}

        ## actions
        self._actions = []
        
        ## show all attribures or only the type attribute
        self._allAttributes = False

        ## user interface
        self.ui = Ui_ElementList()
        
        ## widget title
        self.title = "Components"
        ## element name
        self.name = "components"
        ## element name
        self.clName = "Component"

    ##  creates GUI
    # \brief It calls setupUi and  connects signals and slots    
    def createGUI(self):

        self.ui.setupUi(self)

        self.ui.elementTabWidget.setTabText(0,self.title)
        self.ui.elementListWidget.setEditTriggers(
            self.ui.elementListWidget.SelectedClicked)


        self.populateElements()


    ## switches between all attributes in the try or only type attribute
    # \param status all attributes are shown if True
    def viewAttributes(self, status = None):
        if status is None:
            return self._allAttributes
        self._allAttributes = True if status else False
        for k in self.elements.keys():
            if hasattr(self.elements[k], "instance") \
                    and self.elements[k].instance:
                self.elements[k].instance.viewAttributes(
                    self._allAttributes)
            

    ## opens context Menu        
    # \param position in the element list
    def _openMenu(self, position):
        menu = QMenu()
        for action in self._actions:
            if action is None:
                menu.addSeparator()
            else:
                menu.addAction(action)
        menu.exec_(self.ui.elementListWidget.viewport().mapToGlobal(position))


    ## sets context menu actions for the element list
    # \param actions tuple with actions 
    def setActions(self, actions):
        self.ui.elementListWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.elementListWidget.customContextMenuRequested.connect(
            self._openMenu)
        self._actions = actions
        
        

    ## adds an element    
    #  \brief It runs the Element Dialog and fetches element name 
    #         and value    
    def addElement(self, obj, flag = True):

        self.elements[obj.id] = obj
        self.populateElements(obj.id, flag)
                
                
    ## takes a name of the current element
    # \returns name of the current element            
    def currentListElement(self):
        item = self.ui.elementListWidget.currentItem()
        if item is None:
            return None    
        return self.elements[item.data(Qt.UserRole).toLongLong()[0]] 


    ## removes the current element    
    #  \brief It removes the current element asking before about it
    def removeElement(self, obj = None, question = True):
        if obj is not None:
            oid = obj.id
        else:
            cds = self.currentListElement()
            if cds is None:
                return
            oid = cds.id
        if oid is None:
            return
        if oid in self.elements.keys():
            if question :
                if QMessageBox.question(
                    self, "%s - Close" % self.clName,
                    "Close %s: %s ".encode() \
                        % (self.clName, self.elements[oid].name),
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes ) == QMessageBox.No :
                    return

            self.elements.pop(oid)
            self.populateElements()

        attr = self.currentListElement()
        if attr is None:
            return
        if QMessageBox.question(
            self, "%s - Remove" % self.clName,
            "Remove %s: %s = \'%s\'".encode() \
                %  (self.clName, attr, self.elements[unicode(attr)]),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes ) == QMessageBox.No :
            return
        if unicode(attr) in self.elements.keys():
            self.elements.pop(unicode(attr))
            self.populateElements()


    ## changes the current value of the element        
    # \brief It changes the current value of the element and informs 
    #        the user that element names arenot editable
    def listItemChanged(self, item, name = None):
        ide = self.currentListElement().id

        if ide in self.elements.keys():
            old = self.elements[ide] 
            oname = self.elements[ide].name
            if name is None:
                self.elements[ide].name = unicode(item.text())
            else:
                self.elements[ide].name = name
            self.populateElements()
            return old, oname


    ## fills in the element list
    # \param selectedElement selected element    
    # \param edit flag if edit the selected item
    def populateElements(self, selectedElement = None, edit = False):
        selected = None
        self.ui.elementListWidget.clear()
        
        slist = [(self.elements[key].name, key) 
                 for key in self.elements.keys()]
        slist.sort()
        
        for name, el in slist:
            item  = QListWidgetItem(QString("%s" % name))
            item.setData(Qt.UserRole, QVariant(self.elements[el].id))
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            dirty = False
            if hasattr(self.elements[el],"isDirty") \
                    and self.elements[el].isDirty():
                dirty = True
            if self.elements[el].instance is not None:
                if hasattr(self.elements[el].instance,"isDirty") \
                        and self.elements[el].instance.isDirty():
                    dirty = True
            if dirty:
                item.setForeground(Qt.red) 
            else:
                item.setForeground(Qt.black)

            self.ui.elementListWidget.addItem(item)
            if selectedElement is not None \
                    and selectedElement == self.elements[el].id:
                selected = item
                               
            if self.elements[el].instance is not None \
                    and self.elements[el].instance.dialog is not None:
                try:
                    if dirty:
                        self.elements[el].instance.dialog.setWindowTitle(
                            "%s [%s]*" % (name, self.clName))
                    else:
                        self.elements[el].instance.dialog.setWindowTitle(
                            "%s [%s]" % (name, self.clName))
                except:
#                    print "C++", self.elements[el].name
                    self.elements[el].instance.dialog =  None
        if selected is not None:
            selected.setSelected(True)
            self.ui.elementListWidget.setCurrentItem(selected)
            if edit:
                self.ui.elementListWidget.editItem(selected)


            
    ## loads the element list from the given dictionary
    # \param itemActions actions of the context menu
    # \param externalActions dictionary with external actions
    def loadList(self, itemActions, externalActions = None):
        actions = externalActions if externalActions else {}
        try:
            dirList = [l for l in os.listdir(self.directory) \
                         if l.endswith(".xml")]
        except:
            try:
                if os.path.exists(os.path.join(os.getcwd(),self.name)):
                    self.directory = os.path.abspath(os.path.join(
                            os.getcwd(),self.name))
                else:
                    self.directory = os.getcwd()
                dirList = [l for l in os.listdir(self.directory) \
                               if l.endswith(".xml")]
            except:
                return
            
        for fname in dirList:
            if fname[-4:] == '.xml':
                name = fname[:-4]
            else:
                name = fname
                
            dlg = Component()
            dlg.directory = self.directory
            dlg.name = name
            dlg.createGUI()
            dlg.addContextMenu(itemActions)

            dlg.load()    
            if hasattr(dlg,"connectExternalActions"):     
                dlg.connectExternalActions(**actions)    

            cp = LabeledObject(name, dlg)
            self.elements[id(cp)] =  cp
            if cp.instance is not None:
                cp.instance.id = cp.id
            print name
            


    ## sets the elements
    # \param elements dictionary with the elements, i.e. name:xml
    # \param itemActions actions of the tree context menu
    # \param externalActions dictionary with external actions
    def setList(self, elements,  itemActions, externalActions = None):
        actions = externalActions if externalActions else {}
        if not os.path.isdir(self.directory):
            try:
                if os.path.exists(os.path.join(os.getcwd(),self.name)):
                    self.directory = os.path.abspath(
                        os.path.join(os.getcwd(),self.name))
                else:
                    self.directory = os.getcwd() 
            except:
                ## todo
                return
            
        for name in elements.keys():
                
            dlg = Component()
            dlg.directory = self.directory
            dlg.name = name
            dlg.createGUI()
            dlg.addContextMenu(itemActions)
            try:
                if str(elements[name]).strip():
                    dlg.set(elements[name])    
                else:    
                    dlg.createHeader()
                    QMessageBox.warning(self, "Element cannot be loaded",
                                        "Element %s without content" % name)
            except:
                QMessageBox.warning(self, "Component cannot be loaded",
                                    "Component %s cannot be loaded" % name)

                
            if hasattr(dlg,"connectExternalActions"):     
                dlg.connectExternalActions(**actions)    

            cp = LabeledObject(name, dlg)
            self.elements[id(cp)] =  cp
            if cp.instance is not None:
                cp.instance.id = cp.id
            print name
            





if __name__ == "__main__":
    import sys
    from PyQt4.QtGui import QApplication

    ## Qt application
    app = QApplication(sys.argv)
    ## group form
    form = ComponentList("../components")
    form.createGUI()
    form.show()
    app.exec_()


    if form.elements:
        print "Other components:"
        for mk in form.elements.keys():
            print  " %s = '%s' " % (mk, form.elements[mk])
    
