# encoding=utf-8

import sys
from os.path import exists, join
from Tkinter import Tk
from tkMessageBox import askyesno

__doc__ = """
Usage: ride_postinstall.py <install|uninstall>
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
    import subprocess
    version = subprocess.check_output("ride.py --version", shell=True)
    print("Installation successful (version {0}).".format(version.strip()))


def _create_desktop_shortcut_linux():
    import os
    Tk().withdraw()
    DEFAULT_LANGUAGES = os.environ.get('LANG', '').split(':')
    # print("Lang {0}.\n".format(DEFAULT_LANGUAGES[0]))
    desktop = {"pt": r"Área de Trabalho", "en": "Desktop"}  # TODO: Add more\
    # languages
    try:
        ndesktop = desktop[DEFAULT_LANGUAGES[0][:2]]
    except KeyError as kerr:
        ndesktop = desktop["en"]  # TODO: Ask desktop directory name
    link = join(os.path.join(os.path.expanduser('~'), ndesktop),
                "RIDE.desktop")
    if exists(link) or askyesno("Setup", "Create desktop shortcut?"):
        roboticon = "/usr/lib/python{0}/site-packages/robotide/widgets/robot.p\
ng".format(sys.version[:3])
        # print("Creating {0}.\nIcon {1}".format(link, roboticon))
        with open(link, "w+") as shortcut:
            shortcut.write("[Desktop Entry]\nExec=ride.py\nComment=A Robot Fra\
mework IDE\nGenericName=RIDE\n")
            shortcut.write("Icon={0}\n".format(roboticon))
            shortcut.write("Name=RIDE\nStartupNotify=true\nTerminal=false\nTyp\
e=Application\nX-KDE-SubstituteUID=false\n")


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


if len(sys.argv) > 1 and sys.argv[1] == 'install':
    verify_install()
    create_desktop_shortcut()
else:
    print(__doc__)
    sys.exit(0)
