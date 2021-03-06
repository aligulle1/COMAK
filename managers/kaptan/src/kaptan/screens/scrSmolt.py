# -*- coding: utf-8 -*-
#
# Copyright (C) 2009, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import sys
import pardus.netutils

from PyQt4 import QtGui
from PyQt4 import QtCore

# from PyKDE4 import kdecore

# Pds Stuff
import kaptan.screens.context as ctx
from kaptan.screens.context import *
from kaptan.plugins import Desktop

from kaptan.screen import Screen
FOR_LXDE = ctx.Pds.session == ctx.pds.LXDE
FOR_ENLIGHTENMENT = ctx.Pds.session == ctx.pds.Enlightenment
FOR_FLUXBOX = ctx.Pds.session == ctx.pds.Fluxbox
FOR_GNOME = ctx.Pds.session == ctx.pds.Gnome
FOR_XFCE=ctx.Pds.session == ctx.pds.Xfce
FOR_GNOME3 = ctx.Pds.session == ctx.pds.Gnome3
SHOW_COMAK_UI = FOR_LXDE | FOR_ENLIGHTENMENT | FOR_FLUXBOX | FOR_GNOME | FOR_XFCE | FOR_GNOME3
if SHOW_COMAK_UI:
    from kaptan.screens.ui_scrSmolt_comak import Ui_smoltWidget
else:
    from kaptan.screens.ui_scrSmolt import Ui_smoltWidget

sys.path.append('/usr/share/smolt/client')

import smolt

class Widget(QtGui.QWidget, Screen):
    screenSettings = {}
    screenSettings["profileSend"] = False

    title = i18n("Smolt")
    desc = i18n("Help Pardus Improve!")

    def __init__(self, *args):
        QtGui.QWidget.__init__(self,None)
        self.ui = Ui_smoltWidget()
        self.ui.setupUi(self)

        self.actions()

        self.profile = smolt.Hardware()

        self.setTableWidget()
        self.fillTableWidget()

    def fillTableWidget(self):
        ''' Fill the host information '''

        row = 0
        labels = self.getLabels()

        for label, value in self.profile.hostIter():
            self.ui.tableWidget.insertRow(row)

            labelItem = QtGui.QTableWidgetItem(labels[row])
            self.setRowColor(self.ui.tableWidget, labelItem)
            self.ui.tableWidget.setItem(row, 0, labelItem)

            dataItem = QtGui.QTableWidgetItem(str(value))
            self.setRowColor(self.ui.tableWidget, dataItem)
            self.ui.tableWidget.setItem(row, 1, dataItem)

            row = row + 1

    def setTableWidget(self):
        ''' Specify the tableWidget properties '''

        colLabel = i18n("Label")
        colData = i18n("Data")
        item = QtGui.QTableWidgetItem(colLabel)
        self.ui.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem(colData)
        self.ui.tableWidget.setHorizontalHeaderItem(1, item)

        # self.ui.tableWidget.setHorizontalHeaderLabels(labels)
        self.ui.tableWidget.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.ui.tableWidget.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)

        self.ui.tableWidget.verticalHeader().hide()
        self.ui.tableWidget.setShowGrid(False)
        self.ui.tableWidget.setSortingEnabled(False)
        self.ui.tableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.ui.tableWidget.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.ui.tableWidget.horizontalHeader().setCascadingSectionResizes(True)

    def actions(self):
        QtCore.QObject.connect(self.ui.privacyButton, QtCore.SIGNAL("clicked()"), self.changePage)
        QtCore.QObject.connect(self.ui.checkBox, QtCore.SIGNAL("stateChanged(int)"), self.activateSend)

    def activateSend(self, state):
        if state:
            self.__class__.screenSettings["profileSend"] = True
        else:
            self.__class__.screenSettings["profileSend"] = False

    def setRowColor(self, widget, tableItem):
        ''' Set row background to two colors consecutively like KTableWidget does '''

        if widget.rowCount() % 2 == 0:
            tableItem.setBackgroundColor(QtGui.QColor('#e1e1e1')) #Light gray
        else:
            tableItem.setBackgroundColor(QtGui.QColor('#ffffff')) # White

    def changePage(self):

        if self.ui.stackedWidget.currentIndex() == 0:
            self.ui.stackedWidget.setCurrentIndex(1)
            self.ui.privacyButton.setText(i18n("&Host Information"))
        else:
            self.ui.stackedWidget.setCurrentIndex(0)
            self.ui.privacyButton.setText(i18n("&Privacy policy"))

    def getLabels(self):
        self.sendable_host_labels = [ i18n("UUID"),
                                      i18n("OS"),
                                      i18n("Default Run Level"),
                                      i18n("Language"),
                                      i18n("Platform"),
                                      i18n("BogoMIPS"),
                                      i18n("CPU Vendor"),
                                      i18n("CPU Model"),
                                      i18n("CPU Stepping"),
                                      i18n("CPU Family"),
                                      i18n("CPU Model Num"),
                                      i18n("Number of CPUs"),
                                      i18n("CPU Speed"),
                                      i18n("System Memory"),
                                      i18n("System Swap"),
                                      i18n("Vendor"),
                                      i18n("System"),
                                      i18n("Form Factor"),
                                      i18n("Kernel"),
                                      i18n("SELinux Enabled"),
                                      i18n("SELinux Policy"),
                                      i18n("SELinux Enforce") ]

        return self.sendable_host_labels

    def disableSend(self):
        if pardus.netutils.waitNet(3):
            self.ui.checkBox.setEnabled(True)

    def shown(self):
        self.disableSend()

    def execute(self):
        if self.__class__.screenSettings["profileSend"]:
            self.__class__.screenSettings["summaryMessage"] = i18n("Yes")
        else:
            self.__class__.screenSettings["summaryMessage"] = i18n("No")

        return True
