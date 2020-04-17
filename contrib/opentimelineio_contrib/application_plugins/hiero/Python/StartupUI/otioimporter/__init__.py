# MIT License
#
# Copyright (c) 2018 Daniel Flehner Heen (Storm Studios)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import hiero.ui
import hiero.core

from otioimporter.OTIOImport import load_otio


def OTIO_menu_action(event):
    otio_action = hiero.ui.createMenuAction(
        'Import OTIO',
        open_otio_file,
        icon=None
    )
    hiero.ui.registerAction(otio_action)
    for action in event.menu.actions():
        if action.text() == 'Import':
            action.menu().addAction(otio_action)
            break


def open_otio_file():
    files = hiero.ui.openFileBrowser(
        caption='Please select an OTIO file of choice',
        pattern='*.otio',
        requiredExtension='.otio'
    )
    for otio_file in files:
        load_otio(otio_file)


# HieroPlayer is quite limited and can't create transitions etc.
if not hiero.core.isHieroPlayer():
    hiero.core.events.registerInterest(
        "kShowContextMenu/kBin",
        OTIO_menu_action
    )
