import sys
from os.path import exists, join
from Tkinter import Tk
from tkMessageBox import askyesno


def verify_install():
    try:
        import wx
    except ImportError:
        print("No wxPython installation detected!")
        print()
        print("Please ensure that you have wxPython installed before running \
RIDE.")
        print("You can obtain wxPython 2.8.12.1 from \
http://sourceforge.net/projects/wxpython/files/wxPython/2.8.12.1/")
    else:
        print("Installation successful.")


def _create_desktop_shortcut_linux():
    print(sys.platform)
    pass


def _create_desktop_shortcut_mac():
    print(sys.platform)
    pass


def _create_desktop_shortcut_windows():
    Tk().withdraw()
    link = join(get_special_folder_path("CSIDL_DESKTOPDIRECTORY"), 'RIDE.lnk')
    icon = join(sys.prefix, 'Lib', 'site-packages', 'robotide', 'widgets',
                'robot.ico')
    if exists(link) or askyesno('Setup', 'Create desktop shortcut?'):
        create_shortcut('pythonw', "Robot Framework testdata editor", link,
                        '-c "from robotide import main; main()"', '', icon)
        file_created(link)


def create_desktop_shortcut():
    platform = sys.platform.lower()
    if platform.startswith("linux"):
        _create_desktop_shortcut_linux()
    elif platform.startswith("darwin"):
        _create_desktop_shortcut_mac()
    elif platform.startswith("windows"):
        _create_desktop_shortcut_windows()
    else:
        print("Failed to create desktop shortcut.")


if sys.argv[1] == '-install':
    verify_install()
    create_desktop_shortcut()
