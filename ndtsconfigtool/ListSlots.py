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
## \file ListSlots.py
# user pool commands of GUI application

""" List slots """

from PyQt4.QtGui import  (QAction, QIcon, QKeySequence) 
from PyQt4.QtCore import (QString, SIGNAL)

from .ListCommands import (
    ComponentNew,
    ComponentRemove,
    ComponentListChanged,
    DataSourceNew,
    DataSourceRemove,
    DataSourceListChanged,
    CloseApplication
    )


## stack with the application commands
class ListSlots(object):

    ## constructor
    # \param length maximal length of the stack
    def __init__(self, main):
        self.main = main
        self.undoStack = main.undoStack

        self.actions = {
            "actionClose":[
                "&Remove", "componentRemove",
                "Ctrl+P", "componentremove", "Close the component"],
            "actionCloseDataSource":[
                "&Remove DataSource", "dsourceRemove",
                "Ctrl+Shift+P", "dsourceremove", 
                "Close the data source"],
            "actionNew":[
                "&New", "componentNew", 
                QKeySequence.New, "componentnew", "Create a new component"],
            "actionNewDataSource":[
                "&New DataSource", "dsourceNew",
                "Ctrl+Shift+N", "dsourceadd", 
                "Create a new data source"], 
            "actionQuit":[
                "&Quit", "closeApp", 
                "Ctrl+Q", "filequit", "Close the application"],


            }

        tasks = [
            [ "dsourceChanged",
              self.main.sourceList.ui.elementListWidget, 
              "itemChanged(QListWidgetItem*)"],
            ["componentChanged",
             self.main.componentList.ui.elementListWidget, 
             "itemChanged(QListWidgetItem*)"]
            ]






    ## remove component action
    # \brief It removes from the component list the current component
    def componentRemove(self):
        cmd = DataSourceOpen(self.main)
        cmd.execute()
        self.undoStack.push(cmd)
        cmd = self.pool.getCommand('componentRemove').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      



    ## remove datasource action
    # \brief It removes the current datasource      
    def dsourceRemove(self):
        cmd = self.pool.getCommand('dsourceRemove').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      

 
        

    ## new component action
    # \brief It creates a new component
    def componentNew(self):
        cmd = self.pool.getCommand('componentNew').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      

    ## new datasource action
    # \brief It creates a new datasource      
    def dsourceNew(self):
        cmd = self.pool.getCommand('dsourceNew').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")   



    ## close application action
    # \brief It closes the main application
    def closeApp(self):
        cmd = self.pool.getCommand('closeApp').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      

    # edit    




    ## component change action
    # \param item new selected item on the component list
    def componentChanged(self, item): 
        cmd = self.pool.getCommand('componentEdit').clone()
        cmd.execute()
        cmd = self.pool.getCommand('componentChanged').clone()
        cmd.item = item
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      

    ## datasource change action
    # \param item new selected item ond the datasource list
    def dsourceChanged(self, item):
        cmd = self.pool.getCommand('dsourceEdit').clone()
        cmd.execute()
        cmd = self.pool.getCommand('dsourceChanged').clone()
        cmd.item = item
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      

if __name__ == "__main__":   
    pass
