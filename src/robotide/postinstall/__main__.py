#!/usr/bin/env python
# encoding=utf-8
#  TODO: Copyright 2016 Robot Framework Organization
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.


import sys
from os.path import exists, join

__doc__ = """
Usage: python -m robotide.postinstall <-install|-remove>
""".strip()
# TODO: Add -remove, to remove desktop shortcut


def verify_install():
    try:
        from wx import version
    except ImportError as err:
        print("No wxPython installation detected!")
        print("")
        print("Please ensure that you have wxPython installed before running \
RIDE.")
        print("You can obtain wxPython 2.8.12.1 from \
http://sourceforge.net/projects/wxpython/files/wxPython/2.8.12.1/")
        sys.exit(1)
    else:
        print("Installation successful.")


def _askyesno(title, message, frame=None):
    import wx
    if frame is None:
        _ = wx.App()
        parent = wx.Frame(None, size=(0, 0))
    else:
        parent = wx.Frame(frame, size=(0, 0))
    parent.CenterOnScreen()
    dlg = wx.MessageDialog(parent, message, title, wx.YES_NO |
                           wx.ICON_QUESTION)
    result = dlg.ShowModal() == wx.ID_YES
    dlg.Destroy()
    parent.Destroy()
    return result


def _askdirectory(title, initialdir, frame=None):
    import wx
    if frame is None:
        _ = wx.App()
        parent = wx.Frame(None, size=(0, 0))
    else:
        parent = wx.Frame(frame, size=(0, 0))
    parent.CenterOnScreen()
    dlg = wx.DirDialog(parent, title, initialdir, style=wx.DD_DIR_MUST_EXIST)
    if dlg.ShowModal() == wx.ID_OK:
        result = dlg.GetPath()
    else:
        result = None
    dlg.Destroy()
    parent.Destroy()
    return result


def _create_desktop_shortcut_linux(frame=None):
    import os
    import subprocess
    import pwd
    DEFAULT_LANGUAGE = os.environ.get('LANG', '').split(':')
    # TODO: Add more languages
    desktop = {"de": "Desktop", "en": "Desktop", "es": "Escritorio",
               "fi": r"Työpöytä", "fr": "Bureau", "it": "Scrivania",
               "pt": r"Área de Trabalho"}
    user = subprocess.check_output(['logname']).strip()
    try:
        ndesktop = desktop[DEFAULT_LANGUAGE[0][:2]]
        directory = os.path.join("/home", user, ndesktop)
        defaultdir = os.path.join("/home", user, "Desktop")
        if not exists(directory):
            if exists(defaultdir):
                directory = defaultdir
            else:
                directory = _askdirectory(title="Locate Desktop Directory",
                                          initialdir=os.path.join(
                                              os.path.expanduser('~')),
                                          frame=frame)
    except KeyError as kerr:
        directory = _askdirectory(title="Locate Desktop Directory",
                                  initialdir=os.path.join(os.path.expanduser(
                                                          '~')), frame=frame)
    if directory is None:
        print("Desktop shortcut creation aborted!")
        return
    try:
        directory.decode('utf-8')
        link = join(directory, "RIDE.desktop")
        print "directory is UTF-8, length %d bytes" % len(directory)
    except UnicodeError:
        link = join(directory.encode('utf-8'), "RIDE.desktop")
        print "directory is not UTF-8"
    if exists(link) or _askyesno("Setup", "Create desktop shortcut?", frame):
        roboticon = "/usr/lib/python{0}/site-packages/robotide/widgets/robot.p\
ng".format(sys.version[:3])
        with open(link, "w+") as shortcut:
            shortcut.write("#!/usr/bin/env xdg-open\n[Desktop Entry]\nExec=\
ride.py\nComment=A Robot Framework IDE\nGenericName=RIDE\n")
            shortcut.write("Icon={0}\n".format(roboticon))
            shortcut.write("Name=RIDE\nStartupNotify=true\nTerminal=false\nTyp\
e=Application\nX-KDE-SubstituteUID=false\n")
            uid = pwd.getpwnam(user).pw_uid
            os.chown(link, uid, -1)  # groupid == -1 means keep unchanged
# .encode('utf-8')

def _create_desktop_shortcut_mac():
    import os
    import subprocess
    import pwd
    user = subprocess.check_output(['logname']).strip()
    link = os.path.join("/Users", user, "Desktop", "RIDE")
    if exists(link) or _askyesno("Setup", "Create desktop shortcut?"):
        roboticon = "/Library/Python/{0}/site-packages/robotide/widgets/robot.p\
ng".format(sys.version[:3])  # TODO: Find a way to change shortcut icon
        with open(link, "w+") as shortcut:
            shortcut.write("#!/bin/sh\n/usr/local/bin/ride.py $* &\n")
        uid = pwd.getpwnam(user).pw_uid
        os.chown(link, uid, -1)  # groupid == -1 means keep unchanged
        os.chmod(link, 0744)


def _create_desktop_shortcut_windows():
    # Dependency of http://sourceforge.net/projects/pywin32/
    import os
    import sys
    from win32com.shell import shell, shellcon
    desktop = shell.SHGetFolderPath(0, shellcon.CSIDL_DESKTOP, None, 0)
    link = os.path.join(desktop, 'RIDE.lnk')
    icon = os.path.join(sys.prefix, 'Lib', 'site-packages', 'robotide',
                        'widgets', 'robot.ico')
    if not exists(link):
        from Tkinter import Tk
        from tkMessageBox import askyesno
        Tk().withdraw()
        if not askyesno('Setup', 'Create desktop shortcut?'):
            sys.exit("Users can create a Desktop shortcut to RIDE with:\
\nride_postinstall.py -install\n")
        import pythoncom
        shortcut = pythoncom.CoCreateInstance(shell.CLSID_ShellLink, None,
                                              pythoncom.CLSCTX_INPROC_SERVER,
                                              shell.IID_IShellLink)
        command_args = " -c \"from robotide import main; main()\""
        shortcut.SetPath("pythonw.exe")  # sys.executable
        shortcut.SetArguments(command_args)
        shortcut.SetDescription("Robot Framework testdata editor")
        shortcut.SetIconLocation(icon, 0)
        persist_file = shortcut.QueryInterface(pythoncom.IID_IPersistFile)
        persist_file.Save(link, 0)
        if __name__ != '__main__':
            file_created(link)  # Only in Windows installer. How to detect?


def create_desktop_shortcut(platform, frame=None):
    if platform.startswith("linux"):
        _create_desktop_shortcut_linux(frame)
    elif platform.startswith("darwin"):
        _create_desktop_shortcut_mac()
    elif platform.startswith("win"):
        _create_desktop_shortcut_windows()
    else:
        sys.exit("Unknown platform {0}: Failed to create desktop shortcut.".
                 format(platform))


def caller(frame, platform):
    create_desktop_shortcut(platform, frame)


def main(args):
    arg = args[-1] if len(args) and args[-1] in ['-install', '-remove', '-help'] else None
    if arg == '-install':
        platform = sys.platform.lower()
        if not platform.startswith("win"):
            verify_install()
        create_desktop_shortcut(platform)
    elif arg == '-remove':
        sys.exit("Sorry, -remove is not implemented yet.")
    else:
        print(__doc__)
        sys.exit(0)


if __name__ == '__main__':
    main(sys.argv[1:])