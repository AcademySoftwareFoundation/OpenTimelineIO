#!/usr/bin/env python2.7

import os
import sys
import argparse
import itertools
from PySide import QtGui

import opentimelineio as otio
import opentimelineioViewWidget as otioViewWidget

__doc__ = """ Simple otio viewer """


def _parsed_args():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '-i',
        '--input',
        type=str,
        required=False,
        help='path to input file',
    )

    return parser.parse_args()


class Main(QtGui.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(Main, self).__init__(*args, **kwargs)

        self._current_file = None

        # window options
        self.setWindowTitle('OTIO viewer')
        self.resize(900, 500)

        # widgets
        self.timeline = otioViewWidget.timeline.Timeline(parent=self)
        self.details = otioViewWidget.details.Details(parent=self)

        # layout
        widg = QtGui.QWidget(parent=self)
        layout = QtGui.QVBoxLayout()

        self.setCentralWidget(widg)
        widg.setLayout(layout)

        layout.addWidget(self.details)
        layout.addWidget(self.timeline)

        # menu
        menubar = self.menuBar()

        file_load = QtGui.QAction('load...', menubar)
        file_load.triggered.connect(self._file_load)

        file_menu = menubar.addMenu('file')
        file_menu.addAction(file_load)

        # signals
        self.timeline.selection_changed.connect(self.details.set_item)

    def _file_load(self):
        start_folder = None
        if self._current_file is not None:
            start_folder = os.path.dirname(self._current_file)

        extensions = set(
            itertools.chain.from_iterable(
                adp.suffixes for adp in otio.adapters.MANIFEST.adapters
            )
        )

        extensions_string = ' '.join(
            ('*.{ext}'.format(ext=x) for x in extensions)
        )

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
        self.setWindowTitle('OTIO viewer - ' + path)
        self.details.set_item(None)
        self.timeline.set_timeline(otio.adapters.read_from_file(path))


def main():
    args = _parsed_args()

    application = QtGui.QApplication(sys.argv)
    window = Main()

    if args.input is not None:
        window.load(args.input)

    window.show()
    application.exec_()

if __name__ == '__main__':
    main()
