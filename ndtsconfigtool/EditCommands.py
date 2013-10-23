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
## \file Command.py
# user commands of GUI application

""" Component Designer commands """

from PyQt4.QtGui import QMessageBox

from .DataSourceDlg import DataSourceDlg
from . import DataSource
from .Component import Component
from .Command import Command








## Command which opens dialog with the current component 
class ComponentEdit(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        self._cp = None
        self._cpEdit = None
        self._subwindow = None
        
        
    ## executes the command
    # \brief It opens dialog with the current component 
    def execute(self):
        if self._cp is None:
            self._cp = self.receiver.main.componentList.currentListComponent()
        if self._cp is None:                
            QMessageBox.warning(self.receiver.main, "Component not selected", 
                                "Please select one of the components")         
        else:
            if self._cp.instance is None:
                #                self._cpEdit = FieldWg()  
                self._cpEdit = Component()
                self._cpEdit.idc = self._cp.id
                self._cpEdit.directory = \
                    self.receiver.main.componentList.directory
                self._cpEdit.name = self.receiver.main.componentList.components[
                    self._cp.id].name
                self._cpEdit.createGUI()
                self._cpEdit.addContextMenu(
                    self.receiver.main.contextMenuActions)
                self._cpEdit.createHeader()
                self._cpEdit.dialog.setWindowTitle(
                    "%s [Component]*" % self._cp.name)
            else:
                self._cpEdit = self._cp.instance 
                

            if hasattr(self._cpEdit, "connectExternalActions"):     
                self._cpEdit.connectExternalActions(
                    **self.receiver.main.externalCPActions)


            subwindow = self.receiver.main.subWindow(
                self._cpEdit, self.receiver.main.mdi.subWindowList())
            if subwindow:
                self.receiver.main.mdi.setActiveSubWindow(subwindow) 
                self._cpEdit.reconnectSaveAction()
            else:    
                self._cpEdit.createGUI()

                self._cpEdit.addContextMenu(
                    self.receiver.main.contextMenuActions)
                if self._cpEdit.isDirty():
                    self._cpEdit.dialog.setWindowTitle(
                        "%s [Component]*" % self._cp.name)
                else:
                    self._cpEdit.dialog.setWindowTitle(
                        "%s [Component]" % self._cp.name)
                     
                self._cpEdit.reconnectSaveAction()
                self._subwindow = self.receiver.main.mdi.addSubWindow(
                    self._cpEdit.dialog)
                self._subwindow.resize(680, 560)
                self._cpEdit.dialog.show()
            self._cp.instance = self._cpEdit 

            
        print "EXEC componentEdit"

    ## unexecutes the command
    # \brief It does nothing
    def unexecute(self):
        print "UNDO componentEdit"


    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ComponentEdit(self.receiver, self.slot) 








## Command which copies the current datasource into the clipboard
class DataSourceCopy(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        self._ds = None
        self._oldstate = None
        self._newstate = None
        self._subwindow = None
        
        
    ## executes the command
    # \brief It copies the current datasource into the clipboard
    def execute(self):
        if self._ds is None:
            self._ds = self.receiver.main.sourceList.currentListDataSource()
        if self._ds is None:
            QMessageBox.warning(self.receiver.main, "DataSource not selected", 
                                "Please select one of the datasources")
        if self._ds is not None and self._ds.instance is not None:
            if self._newstate is None:
                if self._oldstate is None:
                    self._oldstate = self._ds.instance.getState() 
                self._ds.instance.copyToClipboard()
            else:
                self.receiver.main.sourceList.datasources[
                    self._ds.id].instance.setState(self._newstate)
                self._ds.instance.updateForm()


            subwindow = self.receiver.main.subWindow(
                self._ds.instance, self.receiver.main.mdi.subWindowList())
            if subwindow:
                self.receiver.main.mdi.setActiveSubWindow(subwindow) 
                self._ds.instance.reconnectSaveAction() 
            else:    
                self._ds.instance.createGUI()

                if self._ds.instance.isDirty():
                    self._ds.instance.dialog.setWindowTitle(
                        "%s [DataSource]*" % self._ds.name)
                else:
                    self._ds.instance.dialog.setWindowTitle(
                        "%s [DataSource]" % self._ds.name)
                     
                self._ds.instance.reconnectSaveAction()
                self._subwindow = self.receiver.main.mdi.addSubWindow(
                    self._ds.instance.dialog)
                self._subwindow.resize(440, 550)
                self._ds.instance.dialog.show()
                

            self._newstate = self._ds.instance.getState() 
            
        print "EXEC dsourceCopy"

    ## unexecutes the command
    # \brief It updates state of datasource to the old state
    def unexecute(self):
        if self._ds is not None and hasattr(self._ds,'instance') \
                and self._ds.instance is not None:
        
            self.receiver.main.sourceList.datasources[
                self._ds.id].instance.setState(self._oldstate)
            self.receiver.main.sourceList.datasources[
                self._ds.id].instance.updateForm()


            subwindow = self.receiver.main.subWindow(
                self._ds.instance, self.receiver.main.mdi.subWindowList())
            if subwindow:
                self.receiver.main.mdi.setActiveSubWindow(subwindow) 
                self._ds.instance.reconnectSaveAction() 
            else:    
                self._ds.instance.createGUI()

                if self._ds.instance.isDirty():
                    self._ds.instance.dialog.setWindowTitle(
                        "%s [DataSource]*" % self._ds.name)
                else:
                    self._ds.instance.dialog.setWindowTitle(
                        "%s [DataSource]" % self._ds.name)
                     
                self._ds.instance.reconnectSaveAction()
                self._subwindow = self.receiver.main.mdi.addSubWindow(
                    self._ds.instance.dialog)
                self._subwindow.resize(440, 550)
                self._ds.instance.dialog.show()
            
            
        print "UNDO dsourceCopy"
        

    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return DataSourceCopy(self.receiver, self.slot) 
        




## Command which moves the current datasource into the clipboard
class DataSourceCut(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        self._ds = None
        self._oldstate = None
        self._newstate = None
        self._subwindow = None
        
        
    ## executes the command
    # \brief It moves the current datasource into the clipboard
    def execute(self):
        if self._ds is None:
            self._ds = self.receiver.main.sourceList.currentListDataSource()
        if self._ds is None:
            QMessageBox.warning(self.receiver.main, "DataSource not selected", 
                                "Please select one of the datasources")
        if self._ds is not None and self._ds.instance is not None:
            if self._newstate is None:
                if self._oldstate is None:
                    self._oldstate = self._ds.instance.getState() 
                self._ds.instance.copyToClipboard()
                self._ds.instance.clear()
                self._ds.instance.updateForm()
                self._ds.instance.dialog.show()
            else:
                self.receiver.main.sourceList.datasources[
                    self._ds.id].instance.setState(self._newstate)
                self._ds.instance.updateForm()

            subwindow = self.receiver.main.subWindow(
                self._ds.instance, self.receiver.main.mdi.subWindowList())
            if subwindow:
                self.receiver.main.mdi.setActiveSubWindow(subwindow) 
                self._ds.instance.reconnectSaveAction() 
            else:    
                self._ds.instance.createGUI()

                if self._ds.instance.isDirty():
                    self._ds.instance.dialog.setWindowTitle(
                        "%s [DataSource]*" % self._ds.name)
                else:
                    self._ds.instance.dialog.setWindowTitle(
                        "%s [DataSource]" % self._ds.name)
                     
                self._ds.instance.reconnectSaveAction()
                self._subwindow = self.receiver.main.mdi.addSubWindow(
                    self._ds.instance.dialog)
                self._subwindow.resize(440, 550)
                self._ds.instance.dialog.show()
                
                

            self._newstate = self._ds.instance.getState() 
        if hasattr(self._ds , "id"):
            self.receiver.main.sourceList.populateDataSources(self._ds.id)
        else:
            self.receiver.main.sourceList.populateDataSources()
            
        print "EXEC dsourceCut"

    ## unexecutes the command
    # \brief It copy back the removed datasource
    def unexecute(self):
        if self._ds is not None and hasattr(self._ds,'instance') \
                and self._ds.instance is not None:
        
            self.receiver.main.sourceList.datasources[
                self._ds.id].instance.setState(self._oldstate)
            self.receiver.main.sourceList.datasources[
                self._ds.id].instance.updateForm()

            subwindow = self.receiver.main.subWindow(
                self._ds.instance, self.receiver.main.mdi.subWindowList())
            if subwindow:
                self.receiver.main.mdi.setActiveSubWindow(subwindow) 
                self._ds.instance.reconnectSaveAction() 
            else:    
                self._ds.instance.createGUI()

                if self._ds.instance.isDirty():
                    self._ds.instance.dialog.setWindowTitle(
                        "%s [DataSource]*" % self._ds.name)
                else:
                    self._ds.instance.dialog.setWindowTitle(
                        "%s [DataSource]" % self._ds.name)
                     
                self._ds.instance.reconnectSaveAction()
                self._subwindow = self.receiver.main.mdi.addSubWindow(
                    self._ds.instance.dialog)
                self._subwindow.resize(440, 550)
                self._ds.instance.dialog.show()
            
        if hasattr(self._ds , "id"):
            self.receiver.main.sourceList.populateDataSources(self._ds.id)
        else:
            self.receiver.main.sourceList.populateDataSources()
            
        print "UNDO dsourceCut"
        

    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return DataSourceCut(self.receiver, self.slot) 
        




## Command which pastes the current datasource from the clipboard
class DataSourcePaste(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        self._ds = None
        self._oldstate = None
        self._newstate = None
        self._subwindow = None
        
        
    ## executes the command
    # \brief It pastes the current datasource from the clipboard
    def execute(self):
        if self._ds is None:
            self._ds = self.receiver.main.sourceList.currentListDataSource()
        if self._ds is None:
            QMessageBox.warning(self.receiver.main, "DataSource not selected", 
                                "Please select one of the datasources")
        if self._ds is not None and self._ds.instance is not None:
            if self._newstate is None:
                if self._oldstate is None:
                    self._oldstate = self._ds.instance.getState() 
                self._ds.instance.clear()
                if not self._ds.instance.copyFromClipboard():
                    QMessageBox.warning(
                        self.receiver.main, "Pasting item not possible", 
                        "Probably clipboard does not contain datasource")
                    
                self._ds.instance.updateForm()
#                self._ds.instance.updateNode()
                self._ds.instance.dialog.setFrames(
                    self._ds.instance.dataSourceType)

#                self._ds.instance.updateForm()
                self._ds.instance.dialog.show()
            else:
                self.receiver.main.sourceList.datasources[
                    self._ds.id].instance.setState(self._newstate)
                self._ds.instance.updateForm()
#                self._ds.instance.updateNode()

            self._newstate = self._ds.instance.getState() 

            self.receiver.main.sourceList.datasources[
                self._ds.id].instance.setState(self._oldstate)
            self._ds.instance.updateNode()

            
            subwindow = self.receiver.main.subWindow(
                self._ds.instance, self.receiver.main.mdi.subWindowList())
            if subwindow:
                self.receiver.main.mdi.setActiveSubWindow(subwindow) 
                self._ds.instance.reconnectSaveAction() 
            else:    
                self._ds.instance.createDialog()

                if self._ds.instance.isDirty():
                    self._ds.instance.dialog.setWindowTitle(
                        "%s [DataSource]*" % self._ds.name)
                else:
                    self._ds.instance.dialog.setWindowTitle(
                        "%s [DataSource]" % self._ds.name)
                     
                self._ds.instance.reconnectSaveAction()
                self._subwindow = self.receiver.main.mdi.addSubWindow(
                    self._ds.instance.dialog)
                self._subwindow.resize(440, 550)
                self._ds.instance.dialog.show()
                                

            
            if hasattr(self._ds , "id"):
                self.receiver.main.sourceList.populateDataSources(self._ds.id)
            else:
                self.receiver.main.sourceList.populateDataSources()
        print "EXEC dsourcePaste"

    ## unexecutes the command
    # \brief It remove the pasted datasource
    def unexecute(self):
        if self._ds is not None and hasattr(self._ds,'instance') \
                and  self._ds.instance is not None:
        
            self.receiver.main.sourceList.datasources[
                self._ds.id].instance.setState(self._oldstate)
            self.receiver.main.sourceList.datasources[
                self._ds.id].instance.updateForm()


            subwindow = self.receiver.main.subWindow(
                self._ds.instance, self.receiver.main.mdi.subWindowList())
            if subwindow:
                self.receiver.main.mdi.setActiveSubWindow(subwindow) 
                self._ds.instance.reconnectSaveAction() 
            else:    
                self._ds.instance.createGUI()

                if self._ds.instance.isDirty():
                    self._ds.instance.dialog.setWindowTitle(
                        "%s [DataSource]*" % self._ds.name)
                else:
                    self._ds.instance.dialog.setWindowTitle(
                        "%s [DataSource]" % self._ds.name)
                     
                self._ds.instance.reconnectSaveAction()
                self._subwindow = self.receiver.main.mdi.addSubWindow(
                    self._ds.instance.dialog)
                self._subwindow.resize(440, 550)
                self._ds.instance.dialog.show()
            
            if hasattr(self._ds , "id"):
                self.receiver.main.sourceList.populateDataSources(self._ds.id)
            else:
                self.receiver.main.sourceList.populateDataSources()
            
        print "UNDO dsourcePaste"
        

    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return DataSourcePaste(self.receiver, self.slot) 
        



## Command which applies the changes from the form for the current datasource 
class DataSourceApply(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        self._ds = None
        self._oldstate = None
        self._newstate = None
        self._subwindow = None
        
        
    ## executes the command
    # \brief It applies the changes from the form for the current datasource  
    def execute(self):
        if self._ds is None:
            self._ds = self.receiver.main.sourceList.currentListDataSource()
        if self._ds is None:
            QMessageBox.warning(self.receiver.main, "DataSource not selected", 
                                "Please select one of the datasources")
        if self._ds.instance is None:
            #                self._dsEdit = FieldWg()  
            self._ds.instance  = DataSource.DataSource()
            self._ds.instance.ids = self._ds.id
            self._ds.instance.directory = \
                self.receiver.main.sourceList.directory
            self._ds.instance.name = self.receiver.main.sourceList.datasources[
                self._ds.id].name
        if not self._ds.instance.dialog:
            self._ds.instance.createDialog()
            self._ds.instance.dialog.setWindowTitle(
                "%s [DataSource]*" % self._ds.name)
            
            if hasattr(self._ds.instance, "connectExternalActions"):
                self._ds.instance.connectExternalActions(
                    **self.receiver.main.externalDSActions)
            self._subwindow = self.receiver.main.mdi.addSubWindow(
                self._ds.instance.dialog)
            self._subwindow.resize(440, 550)
            self._ds.instance.dialog.show()

    
        if self._ds is not None and self._ds.instance is not None:
            if self._newstate is None:
                if self._oldstate is None:
                    self._oldstate = self._ds.instance.getState() 
            else:
                self.receiver.main.sourceList.datasources[
                    self._ds.id].instance.setState(
                    self._newstate)
                if not hasattr(self._ds.instance.dialog.ui, "docTextEdit"):
                    self._ds.instance.createDialog()
                self._ds.instance.updateForm()
                


            subwindow = self.receiver.main.subWindow(
                self._ds.instance, self.receiver.main.mdi.subWindowList())
            if subwindow:
                self.receiver.main.mdi.setActiveSubWindow(subwindow) 
                self._ds.instance.reconnectSaveAction()
            else:    
                self._ds.instance.createGUI()

                if self._ds.instance.isDirty():
                    self._ds.instance.dialog.setWindowTitle(
                        "%s [Component]*" % self._ds.name)
                else:
                    self._ds.instance.dialog.setWindowTitle(
                        "%s [Component]" % self._ds.name)
                     
                self._ds.instance.reconnectSaveAction()
                self._subwindow = self.receiver.main.mdi.addSubWindow(
                    self._ds.instance.dialog)
                self._subwindow.resize(440, 550)
                self._ds.instance.dialog.show()
    
                    
            self._ds.instance.apply()    
            self._newstate = self._ds.instance.getState() 
            
            
            if hasattr(self._ds , "id"):
                self.receiver.main.sourceList.populateDataSources(self._ds.id)
            else:
                self.receiver.main.sourceList.populateDataSources()
        else:
            QMessageBox.warning(self.receiver.main, "DataSource not created", 
                                "Please edit one of the datasources")
            
        print "EXEC dsourceApply"


    ## unexecutes the command
    # \brief It recovers the old state of the current datasource
    def unexecute(self):
        if self._ds is not None and hasattr(self._ds,'instance') \
                and  self._ds.instance is not None:
        
            self.receiver.main.sourceList.datasources[
                self._ds.id].instance.setState(self._oldstate)

            subwindow = self.receiver.main.subWindow(
                self._ds.instance, self.receiver.main.mdi.subWindowList())
            if subwindow:
                self.receiver.main.mdi.setActiveSubWindow(subwindow) 
                self.receiver.main.sourceList.datasources[
                    self._ds.id].instance.updateForm()
                self._ds.instance.reconnectSaveAction()
                
            else:    
                self._ds.instance.createDialog()

                self.receiver.main.sourceList.datasources[
                    self._ds.id].instance.updateForm()
                     
                self._ds.instance.reconnectSaveAction()
                self._subwindow = self.receiver.main.mdi.addSubWindow(
                    self._ds.instance.dialog)
                self._subwindow.resize(440, 550)

            self._ds.instance.updateNode()
            if self._ds.instance.isDirty():
                self._ds.instance.dialog.setWindowTitle(
                    "%s [Component]*" % self._ds.name)
            else:
                self._ds.instance.dialog.setWindowTitle(
                    "%s [Component]" % self._ds.name)
            self._ds.instance.dialog.show()
    
            if hasattr(self._ds , "id"):
                self.receiver.main.sourceList.populateDataSources(self._ds.id)
            else:
                self.receiver.main.sourceList.populateDataSources()
            
            
        print "UNDO dsourceApply"


    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return DataSourceApply(self.receiver, self.slot) 







## Command which takes the datasources from the current component
class ComponentTakeDataSources(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        self._cp = None
       

    ## executes the command
    # \brief It reloads the datasources from the current datasource directory 
    #        into the datasource list
    def execute(self):

        if self._cp is None:
            self._cp = self.receiver.main.componentList.currentListComponent()
        if self._cp is None:
            QMessageBox.warning(self.receiver.main, "Component not selected", 
                                "Please select one of the components")
        else:
            if self._cp.instance is not None:
                datasources = self._cp.instance.getDataSources()
        
                if datasources:
                    dialogs = self.receiver.main.mdi.subWindowList()
                    if dialogs:
                        for dialog in dialogs:
                            if isinstance(dialog, DataSourceDlg):
                                self.receiver.main.mdi.setActiveSubWindow(
                                    dialog)
                                self.receiver.main.mdi.closeActiveSubWindow()
        
                    self.receiver.main.setDataSources(datasources, new = True)
                else:
                    QMessageBox.warning(
                        self.receiver.main, "DataSource item not selected", 
                        "Please select one of the datasource items")            


        print "EXEC componentTakeDataSources"

    ## unexecutes the command
    # \brief It does nothing
    def unexecute(self):
        print "UNDO componentTakeDataSources"


    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ComponentTakeDataSources(self.receiver, self.slot) 




## Command which takes the datasources from the current component
class ComponentTakeDataSource(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        self._cp = None
        self._ids = None
        self._ds = None
        self._lids = None

    ## executes the command
    # \brief It reloads the datasources from the current datasource directory 
    #        into the datasource list
    def execute(self):

        if not self._lids:
            self._lids = \
                self.receiver.main.sourceList.datasources.\
                itervalues().next().id \
                if len(self.receiver.main.sourceList.datasources) else None
        if self._ids and self._ds:       
            self.receiver.main.sourceList.addDataSource(self._ds)
            self.receiver.main.sourceList.populateDataSources(self._ids)
          
        else:    
            if self._cp is None:
                self._cp = \
                    self.receiver.main.componentList.currentListComponent()
            if self._cp is not None:
                if self._cp.instance is not None:

                    datasource = self._cp.instance.getCurrentDataSource()
                    if datasource:            
                        dialogs = self.receiver.main.mdi.subWindowList()
                        if dialogs:
                            for dialog in dialogs:
                                if isinstance(dialog, DataSourceDlg):
                                    self.receiver.main.mdi.setActiveSubWindow(
                                        dialog)
                                    self.receiver.main.mdi\
                                        .closeActiveSubWindow()
        
                        self._ids = self.receiver.main.setDataSources(
                            datasource, new = True)
                        self._ds = \
                            self.receiver.main.sourceList.datasources[self._ids]
                        self.receiver.main.sourceList.populateDataSources(
                            self._ids)
                    else:
                        QMessageBox.warning(
                            self.receiver.main, "DataSource item not selected", 
                            "Please select one of the datasource items")
                        
        print "EXEC componentTakeDataSource"

    ## unexecutes the command
    # \brief It does nothing
    def unexecute(self):
        print "UNDO componentTakeDataSource"
        

        self.receiver.main.sourceList.removeDataSource(self._ds, False)
        if hasattr(self._ds,'instance'):
            subwindow = self.receiver.main.subWindow(
                self._ds.instance, 
                self.receiver.main.mdi.subWindowList())
            if subwindow:
                self.receiver.main.mdi.setActiveSubWindow(subwindow) 
                self.receiver.main.mdi.closeActiveSubWindow() 


        self.receiver.main.sourceList.populateDataSources(self._lids)

    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ComponentTakeDataSource(self.receiver, self.slot) 





## Command which opens the dialog with the current datasource
class DataSourceEdit(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        self._ds = None
        self._dsEdit = None
        self._subwindow = None
        
        
    ## executes the command
    # \brief It opens the dialog with the current datasource
    def execute(self):
        if self._ds is None:
            self._ds = self.receiver.main.sourceList.currentListDataSource()
        if self._ds is None:
            QMessageBox.warning(self.receiver.main, "DataSource not selected", 
                                "Please select one of the datasources")
        else:
            if self._ds.instance is None:
                #                self._dsEdit = FieldWg()  
                self._dsEdit = DataSource.DataSource()
                
                self._dsEdit.ids = self._ds.id
                self._dsEdit.directory = self.receiver.main.sourceList.directory
                self._dsEdit.name = self.receiver.main.sourceList.datasources[
                    self._ds.id].name
                self._dsEdit.createDialog()
                self._dsEdit.dialog.setWindowTitle( 
                    "%s [DataSource]*" % self._ds.name)
                self._ds.instance = self._dsEdit 
            else:
                if not self._ds.instance.dialog:
                    self._ds.instance.createDialog()
                    self._ds.instance.dialog.setWindowTitle(
                        "%s [DataSource]*" % self._ds.name)
                self._dsEdit = self._ds.instance 
                
            if hasattr(self._dsEdit, "connectExternalActions"):     
                self._dsEdit.connectExternalActions(
                    **self.receiver.main.externalDSActions)

            subwindow = self.receiver.main.subWindow(
                self._dsEdit, self.receiver.main.mdi.subWindowList())
            if subwindow:
                self.receiver.main.mdi.setActiveSubWindow(subwindow) 
                self._ds.instance.reconnectSaveAction() 
            else:    
                if self._ds.instance.dialog is None:
                    self._ds.instance.createDialog()

                if self._ds.instance.isDirty():
                    self._ds.instance.dialog.setWindowTitle(
                        "%s [DataSource]*" % self._ds.name)
                else:
                    self._ds.instance.dialog.setWindowTitle(
                        "%s [DataSource]" % self._ds.name)
                     
                self._ds.instance.reconnectSaveAction()
                self._subwindow = self.receiver.main.mdi.addSubWindow(
                    self._ds.instance.dialog)
                self._subwindow.resize(440, 550)
                self._dsEdit.dialog.show()
                    


            
        print "EXEC dsourceEdit"

    ## unexecutes the command
    # \brief It does nothing
    def unexecute(self):
        print "UNDO dsourceEdit"


    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return DataSourceEdit(self.receiver, self.slot) 





## Empty undo command. It is no need to implement it 
class UndoCommand(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)


    ## executes the command
    # \brief It does nothing
    def execute(self):
        print "EXEC undo"

    ## unexecutes the command
    # \brief It does nothing
    def unexecute(self):
        pass


    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return UndoCommand(self.receiver, self.slot) 



## Empty undo command. It is no need to implement it 
class RedoCommand(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)

    ## executes the command
    # \brief It does nothing
    def execute(self):
        print "EXEC redo"

    ## unexecutes the command
    # \brief It does nothing
    def unexecute(self):
        pass


    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return RedoCommand(self.receiver, self.slot) 

        

if __name__ == "__main__":
    pass

