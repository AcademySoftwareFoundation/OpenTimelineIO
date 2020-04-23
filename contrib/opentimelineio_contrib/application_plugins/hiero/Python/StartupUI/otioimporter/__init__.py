#
# Copyright Contributors to the OpenTimelineIO project
#
# Licensed under the Apache License, Version 2.0 (the "Apache License")
# with the following modification; you may not use this file except in
# compliance with the Apache License and the following modification to it:
# Section 6. Trademarks. is deleted and replaced with:
#
# 6. Trademarks. This License does not grant permission to use the trade
#    names, trademarks, service marks, or product names of the Licensor
#    and its affiliates, except as required to comply with Section 4(c) of
#    the License and to reproduce the content of the NOTICE file.
#
# You may obtain a copy of the Apache License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the Apache License with the above modification is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the Apache License for the specific
# language governing permissions and limitations under the Apache License.
#


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

    view = hiero.ui.currentContextMenuView()
    selection = view.selection()
    project = None

    if selection:
        project = selection[0].project()

    elif len(hiero.core.projects()) > 1:
        bar = hiero.ui.mainWindow().statusBar()
        bar.showMessage(
            'Unable to get project from BinView, using the most current',
            timeout=3000
        )
        project = hiero.core.projects()[-1]

    for otio_file in files:
        load_otio(otio_file, project)


# HieroPlayer is quite limited and can't create transitions etc.
if not hiero.core.isHieroPlayer():
    hiero.core.events.registerInterest(
        "kShowContextMenu/kBin",
        OTIO_menu_action
    )
