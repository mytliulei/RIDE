#!/usr/bin/env python
# encoding=utf-8

import sys
from os.path import exists, join

__doc__ = """
Usage: ride_postinstall.py <-install|-remove>
""".strip()


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


def _askyesno(title, message):
    import wx
    _ = wx.App()
    parent = wx.Frame(None, size=(0, 0))
    parent.CenterOnScreen()
    dlg = wx.MessageDialog(parent, message, title, wx.YES_NO |
                           wx.ICON_QUESTION)
    result = dlg.ShowModal() == wx.ID_YES
    dlg.Destroy()
    return result


def _askdirectory(title, initialdir):
    import wx
    _ = wx.App()
    parent = wx.Frame(None, size=(0, 0))
    dlg = wx.DirDialog(parent, title, initialdir, style=wx.DD_DIR_MUST_EXIST)
    if dlg.ShowModal() == wx.ID_OK:
        result = dlg.GetPath()
    else:
        result = None
    dlg.Destroy()
    return result


def _create_desktop_shortcut_linux():
    import os
    DEFAULT_LANGUAGE = os.environ.get('LANG', '').split(':')
    # TODO: Add more languages
    desktop = {"pt": r"Área de Trabalho", "en": "Desktop"}
    try:
        ndesktop = desktop[DEFAULT_LANGUAGE[0][:2]]
        link = join(os.path.join(os.path.expanduser('~'), ndesktop), "RIDE.desktop")
    except KeyError as kerr:
        directory = _askdirectory(title="Locate Desktop Directory",
                                  initialdir=os.path.join(os.path.expanduser('~')))
        if not directory:
            sys.exit("Desktop shortcut creation aborted!")
        else:
            link = join(directory, "RIDE.desktop")
    if exists(link) or _askyesno("Setup", "Create desktop shortcut?"):
        roboticon = "/usr/lib/python{0}/site-packages/robotide/widgets/robot.p\
ng".format(sys.version[:3])
        with open(link, "w+") as shortcut:
            shortcut.write("#!/usr/bin/env xdg-open\n[Desktop Entry]\nExec=\
ride.py\nComment=A Robot Framework IDE\nGenericName=RIDE\n")
            shortcut.write("Icon={0}\n".format(roboticon))
            shortcut.write("Name=RIDE\nStartupNotify=true\nTerminal=false\nTyp\
e=Application\nX-KDE-SubstituteUID=false\n")


def _create_desktop_shortcut_mac():
    import os
    link = join(os.path.join(os.path.expanduser('~'), "Desktop"), "RIDE")
    if exists(link) or _askyesno("Setup", "Create desktop shortcut?"):
        roboticon = "/Library/Python/{0}/site-packages/robotide/widgets/robot.p\
ng".format(sys.version[:3])  # TODO: Find a way to change shortcut icon
        with open(link, "w+") as shortcut:
            shortcut.write("#!/bin/sh\n/usr/local/bin/ride.py $* &\n")
        os.chmod(link, 0744)


def _create_desktop_shortcut_windows():
    link = join(get_special_folder_path("CSIDL_DESKTOPDIRECTORY"), 'RIDE.lnk')
    icon = join(sys.prefix, 'Lib', 'site-packages', 'robotide', 'widgets',
                'robot.ico')
    if exists(link) or _askyesno('Setup', 'Create desktop shortcut?'):
        create_shortcut('pythonw', "Robot Framework testdata editor", link,
                        '-c "from robotide import main; main()"', '', icon)
        file_created(link)


def create_desktop_shortcut():
    platform = sys.platform.lower()
    if platform.startswith("linux"):
        _create_desktop_shortcut_linux()
    elif platform.startswith("darwin"):
        _create_desktop_shortcut_mac()
    elif platform.startswith("win"):
        _create_desktop_shortcut_windows()
    else:
        sys.exit("Unknown platform {0}: Failed to create desktop shortcut.".
                 format(platform))


if len(sys.argv) > 1 and sys.argv[1] == '-install':
    verify_install()
    create_desktop_shortcut()
else:
    print(__doc__)
    sys.exit(0)
