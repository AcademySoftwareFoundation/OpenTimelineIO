#!/usr/bin/env python
#
# Copyright 2017 Pixar Animation Studios
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

"""Simple otio viewer"""

import os
import sys
import argparse
import ast
from PySide2 import QtWidgets, QtGui

import opentimelineio as otio
import opentimelineview as otioViewWidget
from opentimelineview import settings


def _parsed_args():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        'input',
        type=str,
        help='path to input file',
    )
    parser.add_argument(
        '-a',
        '--adapter-arg',
        type=str,
        default=[],
        action='append',
        help='Extra arguments to be passed to adapter in the form of '
        'key=value. Values are strings, numbers or Python literals: True, '
        'False, etc. Can be used multiple times: -a burrito="bar" -a taco=12.'
    )
    parser.add_argument(
        '-m',
        '--media-linker',
        type=str,
        default="Default",
        help=(
            "Specify a media linker.  'Default' means use the "
            "$OTIO_DEFAULT_MEDIA_LINKER if set, 'None' or '' means explicitly "
            "disable the linker, and anything else is interpreted as the name"
            " of the media linker to use."
        )
    )

    return parser.parse_args()


class TimelineWidgetItem(QtWidgets.QListWidgetItem):
    def __init__(self, timeline, *args, **kwargs):
        super(TimelineWidgetItem, self).__init__(*args, **kwargs)
        self.timeline = timeline


class Main(QtWidgets.QMainWindow):
    def __init__(self, adapter_argument_map, media_linker, *args, **kwargs):
        super(Main, self).__init__(*args, **kwargs)
        self.adapter_argument_map = adapter_argument_map or {}
        self.media_linker = media_linker

        self._current_file = None

        # window options
        self.setWindowTitle('OpenTimelineIO Viewer')
        self.resize(1900, 1200)

        # widgets
        self.tracks_widget = QtWidgets.QListWidget(
            parent=self
        )
        self.timeline_widget = otioViewWidget.timeline_widget.Timeline(
            parent=self
        )
        self.details_widget = otioViewWidget.details_widget.Details(
            parent=self
        )

        root = QtWidgets.QWidget(parent=self)
        layout = QtWidgets.QVBoxLayout(root)

        splitter = QtWidgets.QSplitter(parent=root)
        splitter.addWidget(self.tracks_widget)
        splitter.addWidget(self.timeline_widget)
        splitter.addWidget(self.details_widget)

        splitter.setSizes([100, 700, 300])

        layout.addWidget(splitter)
        self.setCentralWidget(root)

        # menu
        menubar = self.menuBar()

        file_load = QtWidgets.QAction('Open...', menubar)
        file_load.setShortcut(QtGui.QKeySequence.Open)
        file_load.triggered.connect(self._file_load)

        exit_action = QtWidgets.QAction('Exit', menubar)
        exit_action.setShortcut(QtGui.QKeySequence.Quit)
        exit_action.triggered.connect(self.close)

        file_menu = menubar.addMenu('File')
        file_menu.addAction(file_load)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        # signals
        self.tracks_widget.itemSelectionChanged.connect(
            self._change_track
        )
        self.timeline_widget.selection_changed.connect(
            self.details_widget.set_item
        )

        self.setStyleSheet(settings.VIEW_STYLESHEET)

    def _file_load(self):
        start_folder = None
        if self._current_file is not None:
            start_folder = os.path.dirname(self._current_file)

        extensions = otio.adapters.suffixes_with_defined_adapters(read=True)

        extensions_string = ' '.join('*.{}'.format(x) for x in extensions)

        path = str(
            QtWidgets.QFileDialog.getOpenFileName(
                self,
                'Open OpenTimelineIO',
                start_folder,
                'OTIO ({extensions})'.format(extensions=extensions_string)
            )[0]
        )

        if path:
            self.load(path)

    def load(self, path):
        self._current_file = path
        self.setWindowTitle('OpenTimelineIO View: "{}"'.format(path))
        self.details_widget.set_item(None)
        self.tracks_widget.clear()
        file_contents = otio.adapters.read_from_file(
            path,
            media_linker_name=self.media_linker,
            **self.adapter_argument_map
        )

        if isinstance(file_contents, otio.schema.Timeline):
            self.timeline_widget.set_timeline(file_contents)
            self.tracks_widget.setVisible(False)
        elif isinstance(
            file_contents,
            otio.schema.SerializableCollection
        ):
            for s in file_contents:
                TimelineWidgetItem(s, s.name, self.tracks_widget)
            self.tracks_widget.setVisible(True)
            self.timeline_widget.set_timeline(None)

    def _change_track(self):
        selection = self.tracks_widget.selectedItems()
        if selection:
            self.timeline_widget.set_timeline(selection[0].timeline)

    def center(self):
        frame = self.frameGeometry()
        desktop = QtWidgets.QApplication.desktop()
        screen = desktop.screenNumber(
            desktop.cursor().pos()
        )
        centerPoint = desktop.screenGeometry(screen).center()
        frame.moveCenter(centerPoint)
        self.move(frame.topLeft())

    def show(self):
        super(Main, self).show()
        self.timeline_widget.frame_all()



def main():
    args = _parsed_args()

    # allow user to explicitly set or pass to default or disable the linker.
    if args.media_linker.lower() == 'default':
        ml = otio.media_linker.MediaLinkingPolicy.ForceDefaultLinker
    elif args.media_linker.lower() in ['none', '']:
        ml = otio.media_linker.MediaLinkingPolicy.DoNotLinkMedia
    else:
        ml = args.media_linker

    argument_map = {}
    for pair in args.adapter_arg:
        if '=' in pair:
            key, val = pair.split('=', 1)  # only split on the 1st '='
            try:
                # Sometimes we need to pass a bool, int, list, etc.
                parsed_value = ast.literal_eval(val)
            except (ValueError, SyntaxError):
                # Fall back to a simple string
                parsed_value = val
            argument_map[key] = parsed_value
        else:
            print(
                "error: adapter arguments must be in the form key=value"
                " got: {}".format(pair)
            )
            sys.exit(1)

    application = QtWidgets.QApplication(sys.argv)

    window = Main(argument_map, ml)

    if args.input is not None:
        window.load(args.input)

    window.center()
    window.show()
    window.raise_()
    application.exec_()

if __name__ == '__main__':
    main()
