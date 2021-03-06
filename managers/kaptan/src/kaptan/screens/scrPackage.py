# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2009, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

#PyQt4 Stuff
from PyQt4 import QtGui
from PyQt4.QtGui import QMessageBox
from PyQt4.QtCore import SIGNAL,QSettings

# Pds
import kaptan.screens.context as ctx

from kaptan.screens.context import *
from kaptan.screens.ui_scrPackage_comak import Ui_packageWidget
from kaptan.screen import Screen

import subprocess, os, pisi, comar, platform
isUpdateOn = False

FOR_GNOME = ctx.Pds.session == ctx.pds.Gnome or ctx.Pds.session == ctx.pds.Gnome3

class Widget(QtGui.QWidget, Screen):
    screenSettings = {}
    title = i18n("Packages")
    desc = i18n("Install / Remove Programs")

    # min update time
    updateTime = 12
    CONFIG_packagemanager = QSettings("%s/.config/Pardus/Package-Manager.conf" %os.environ["HOME"], QSettings.IniFormat)


    def __init__(self, *args):
        QtGui.QWidget.__init__(self,None)
        self.ui = Ui_packageWidget()
        self.ui.setupUi(self)
        self.ui.checkBox.setChecked(False)
        if self.CONFIG_packagemanager.value("SystemTray")=="true":
            self.ui.showTray_2.setChecked(True)
        else:
            self.ui.showTray_2.setChecked(False)
        if self.CONFIG_packagemanager.value("UpdateCheck")=="true":
            self.ui.checkUpdate_2.setChecked(True)
        else:
            self.ui.checkUpdate_2.setChecked(False)
        self.ui.checkUpdate_2.setVisible(False)
        self.ui.updateInterval_2.setVisible(False)
        try:
            self.ui.updateInterval_2.setValue(int(self.CONFIG_packagemanager.value("UpdateCheckInterval").toString())/60)
        except:
            self.ui.updateInterval_2.setValue(2)
        self.ui.checkUpdate_2.connect(self.ui.showTray_2 , SIGNAL("toggled(bool)"),self.visibleCheckUpdates)
        self.ui.checkUpdate_2.connect(self.ui.checkUpdate_2 , SIGNAL("toggled(bool)"),self.enabledUpdateInterval)

        self.__class__.screenSettings["hasChanged_repo"] = self.ui.checkBox.isChecked()
        self.__class__.screenSettings["hasChanged_showTray"] = False

        self.flagRepo = 0
        self.repoName = "comak-repo"
        self.ui.showTray_2.setChecked(False)
        ####
        if not FOR_GNOME:
            if platform.machine() == "x86_64":
                platform_machine = "64"
            if platform.machine() == "i686":
                platform_machine ="32"
            self.repoAddress ="http://comak%s.comu.edu.tr/comak/pisi-index.xml.xz" % platform_machine
        else:
            if platform.machine() == "x86_64":
                platform_machine = "64"
            if platform.machine() == "i686":
                platform_machine = ""
            self.repoAddress ="http://gnome3.comu.edu.tr/comak%s/pisi-index.xml.xz" % platform_machine
        self.ui.information_label.setText("")
        # create a db object
        self.repodb = pisi.db.repodb.RepoDB()
        n = 1 # temporary index variable for repo names
        self.connect(self.ui.checkBox,SIGNAL("stateChanged(int)"),self.comakRepo)
        self.ui.add_repo.setText("Add COMAK Repository")
        # control if we already have lxden repo
        if self.repodb.has_repo(self.repoName):
            #self.pushDelete.setEnabled(False)
            self.ui.checkBox.setEnabled(False)
            errorMessage= i18n("comak-repo is already available on your system.")
            self.ui.information_label.setText(errorMessage)

    def visibleCheckUpdates(self):
        self.ui.checkUpdate_2.setVisible(self.ui.showTray_2.isChecked())
        self.ui.updateInterval_2.setVisible(self.ui.showTray_2.isChecked())

    def enabledUpdateInterval(self):
        self.ui.updateInterval_2.setEnabled(self.ui.checkUpdate_2.isChecked())

    def controlRepo(self):
        if self.repodb.has_repo_url(self.repoAddress):
            self.ui.checkBox.setCheckState(False)
            errorMessage= i18n("comak-repo is already available on your system.")
            self.ui.information_label.setText(errorMessage)
            return False
        else:
            # control if we already have the same repo name
            if self.repodb.has_repo(self.repoName):
                tmpRepoName = self.repoName
                # if so, try to give a name like "enlightenmentn"
                for r in self.repodb.list_repos():
                    if self.repodb.has_repo(tmpRepoName):
                        tmpRepoName = self.repoName + str(n)
                        n = n +1
                    else:
                        break
                self.repoName = tmpRepoName
            return True

    def comakRepo(self):
        if self.ui.checkBox.isChecked():
            if not self.addRepo(self.repoName, self.repoAddress):
                self.flagRepo = 1
                self.ui.checkBox.setChecked(0)
                errorTitle = i18n("Authentication Error")
                errorMessage= i18n("You are not authorized for this operation.")
                self.messageBox = QMessageBox(errorTitle, errorMessage, QMessageBox.Critical, QMessageBox.Ok, 0, 0)
                self.messageBox.show()
        else:
            if self.flagRepo != 1:
                self.removeRepo(self.repoName)

    def addRepo(self, r_name, r_address):
            try:
                link = comar.Link()
                link.setLocale()
                link.System.Manager["pisi"].addRepository(r_name, r_address)
                self.ui.information_label.setText("comak-repo added to your repo list.")
                self.__class__.screenSettings["hasChanged_repo"] = True
                return True
            except:
                return False

    def removeRepo(self, r_name):
        if self.controlRepo():
            try:
                link = comar.Link()
                link.setLocale()
                link.System.Manager["pisi"].removeRepository(r_name)
                self.ui.information_label.setText("comak-repo deleted from your repo list.")
                return True
            except:
                return False

    def shown(self):
        pass

    def execute(self):
        self.__class__.screenSettings["hasChanged_showTray"] = self.ui.showTray_2.isChecked()

        self.__class__.screenSettings["summaryMessage"] ={}

        self.__class__.screenSettings["summaryMessage"].update({"Show in System Tray": "false" if not self.ui.showTray_2.isChecked()  else "true"})
        self.__class__.screenSettings["summaryMessage"].update({"checkUpdate": "false" if not self.ui.checkUpdate_2.isChecked() else "true"})
        self.__class__.screenSettings["summaryMessage"].update({"time limit": self.ui.updateInterval_2.value()*60})
        self.__class__.screenSettings["summaryMessage"].update({"addRepo": "false" if not self.ui.checkBox.isChecked()  else "true"})

        return True

