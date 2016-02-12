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

import wx
import os
import tempfile
import uuid
import atexit
import glob
import sys

from robotide.pluginapi import Plugin, ActionInfo, RideLog
from robotide import widgets
from robotide import context
from robotide.postinstall import __main__ as postinstall

class ShortcutPlugin(Plugin):
    """Creator of RIDE Desktop Shortcuts."""

    def __init__(self, app):
        Plugin.__init__(self, app, default_settings={
            'desktop_shortcut_exists': False,
            'initial_project': None
        })
        self._log = []
        self._window = None
        self._path = os.path.join(
            tempfile.gettempdir(), '{}-ride.log'.format(uuid.uuid4()))
        self._outfile = None
        # self._remove_old_log_files()
        atexit.register(self._close)

    def _close(self):
        pass

    def enable(self):
        self._create_menu()
        # self.subscribe(self._log_message, RideLog)

    def disable(self):
        # self.unsubscribe_all()
        self.unregister_actions()
        if self._window:
            self._window.close(self.notebook)

    def _create_menu(self):
        self.unregister_actions()
        self.register_action(ActionInfo('Tools',
                                        'Create RIDE Desktop Shortcut',
                                        self.OnViewShortcutCreate,
                                        position=85))

    def OnViewShortcutCreate(self, event):
        if not self._window:
            self._window = _ShortcutCreateWindow(self.notebook, self._log)
            self._window.update_log()
        else:
            self.notebook.show_tab(self._window)


class _ShortcutCreateWindow(wx.TextCtrl):
    def __init__(self, notebook, log):
        wx.TextCtrl.__init__(
            self, notebook, style=wx.TE_READONLY | wx.TE_MULTILINE)
        self._log = log
        self._create_ui()
        self._add_to_notebook(notebook)
        self.SetFont(widgets.Font().fixed_log)

    def _create_ui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self)
        self.SetSizer(sizer)

    def _add_to_notebook(self, notebook):
        notebook.add_tab(self, 'Create RIDE Desktop Shortcut', allow_closing=True)
        notebook.show_tab(self)

    def close(self, notebook):
        notebook.delete_tab(self)

    def update_log(self):
        self.SetValue(self._decode_log(self._log))
        self.SetValue("\nGoing to call action.\n")
        postinstall.caller(self.GetParent(), sys.platform.lower())

    def _decode_log(self, log):
        result = "This is the Create RIDE Desktop Shortcut Plugin.\n"
        return result
