#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Licensed under the GNU General Public License, version 2
# See the file http://www.gnu.org/copyleft/gpl.txt

from pisi.actionsapi import autotools
from pisi.actionsapi import pisitools
from pisi.actionsapi import get

def setup():
    autotools.autoreconf("-fiv")
    autotools.configure("--disable-static \
                         --enable-gtk \
                         --with-gtk=3.0 \
                         --enable-silent-rules")

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())

    #workaround to run gnome-shell
    pisitools.remove("/usr/lib/girepository-1.0/GConf-2.0.typelib")

    pisitools.dodoc("README", "COPYING", "TODO", "NEWS", "ChangeLog", "AUTHORS")
