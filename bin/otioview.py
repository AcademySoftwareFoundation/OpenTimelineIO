#!/usr/bin/env python2.7
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
from PySide import QtGui

import opentimelineio as otio
import opentimelineview as otioViewWidget


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

    return parser.parse_args()


class TimelineWidgetItem(QtGui.QListWidgetItem):
    def __init__(self, timeline, *args, **kwargs):
        super(TimelineWidgetItem, self).__init__(*args, **kwargs)
        self.timeline = timeline


class Main(QtGui.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(Main, self).__init__(*args, **kwargs)

        self._current_file = None

        # window options
        self.setWindowTitle('OpenTimelineIO Viewer')
        self.resize(900, 500)

        # widgets
        self.tracks_widget = QtGui.QListWidget(parent=self)
        self.timeline_widget = otioViewWidget.timeline_widget.Timeline(
            parent=self
        )
        self.details_widget = otioViewWidget.details_widget.Details(
            parent=self
        )

        # layout
        splitter = QtGui.QSplitter(parent=self)
        self.setCentralWidget(splitter)

        widg = QtGui.QWidget(parent=self)
        layout = QtGui.QVBoxLayout()
        widg.setLayout(layout)
        layout.addWidget(self.details_widget)
        layout.addWidget(self.timeline_widget)

        splitter.addWidget(self.tracks_widget)
        splitter.addWidget(widg)
        splitter.setSizes([200, 700])

        # menu
        menubar = self.menuBar()

        file_load = QtGui.QAction('load...', menubar)
        file_load.triggered.connect(self._file_load)

        file_menu = menubar.addMenu('file')
        file_menu.addAction(file_load)

        # signals
        self.tracks_widget.itemSelectionChanged.connect(
            self._change_track
        )
        self.timeline_widget.selection_changed.connect(
            self.details_widget.set_item
        )

    def _file_load(self):
        start_folder = None
        if self._current_file is not None:
            start_folder = os.path.dirname(self._current_file)

        extensions = otio.adapters.suffixes_with_defined_adapters(read=True)

        extensions_string = ' '.join('*.{}'.format(x) for x in extensions)

        path = str(
            QtGui.QFileDialog.getOpenFileName(
                self,
                'load otio',
                start_folder,
                'Otio ({extensions})'.format(extensions=extensions_string)
            )[0]
        )

        if path:
            self.load(path)

    def load(self, path):
        self._current_file = path
        self.setWindowTitle('OpenTimelineIO View: "{}"'.format(path))
        self.details_widget.set_item(None)
        self.tracks_widget.clear()
        file_contents = otio.adapters.read_from_file(path)

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


def main():
    args = _parsed_args()

    application = QtGui.QApplication(sys.argv)
    window = Main()

    if args.input is not None:
        window.load(args.input)

    window.show()
    window.raise_()
    application.exec_()


if __name__ == '__main__':
    main()
