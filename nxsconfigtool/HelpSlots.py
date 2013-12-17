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
## \package nxsconfigtool nexdatas
## \file HelpSlots.py
# user pool commands of GUI application

""" Help slots """

import platform

from PyQt4.QtGui import  (QKeySequence, QMessageBox) 
from PyQt4.QtCore import (QT_VERSION_STR, PYQT_VERSION_STR)

from . import __version__
from .HelpForm import HelpForm

## stack with the application commands
class HelpSlots(object):

    ## constructor
    # \param main the main window dialog
    def __init__(self, main):
        ## main window
        self.main = main
        ## command stack
        self.undoStack = main.undoStack
        
        ## action data
        self.actions = {

        "actionAboutComponentDesigner":[
            "&About Component Designer",
            "helpAbout", "", "icon", "About Component Designer"],

        "actionComponentDesignerHelp":[
            "Component Desigener &Help", "helpHelp",
            QKeySequence.HelpContents, "help", "Detail help"]

            }



    ## shows help about
    # \brief It shows message box with help about
    def helpAbout(self):
        QMessageBox.about(self.main, "About Component Designer",
                """<b>Component Designer</b> v %s
                <p>Copyright &copy; 2012-2013 DESY, GNU GENERAL PUBLIC LICENSE
                <p>This application can be used to create
                XML configuration files for Nexus Data Writer.
                <p>Python %s - Qt %s - PyQt %s on %s""" % (
                unicode(__version__), 
                unicode(platform.python_version()),
                unicode(QT_VERSION_STR), 
                unicode(PYQT_VERSION_STR),
                unicode(platform.system())))



    ## shows the detail help 
    # \brief It shows the detail help from help directory
    def helpHelp(self):
        form = HelpForm("index.html", self.main)
        form.show()




if __name__ == "__main__":   
    pass