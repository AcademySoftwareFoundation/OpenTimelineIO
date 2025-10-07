#!/usr/bin/env python
#
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Simple otio viewer"""

import os
import sys
import argparse
try:
    from PySide6 import QtWidgets, QtGui
    from PySide6.QtGui import QAction
except ImportError:
    from PySide2 import QtWidgets, QtGui
    from PySide2.QtWidgets import QAction

import opentimelineio as otio
import opentimelineio.console as otio_console
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
        '-H',
        '--hook-function-arg',
        type=str,
        default=[],
        action='append',
        help='Extra arguments to be passed to the hook functions in the form of '
        'key=value. Values are strings, numbers or Python literals: True, '
        'False, etc. Can be used multiple times: -H burrito="bar" -H taco=12.'
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
    parser.add_argument(
        '-M',
        '--media-linker-arg',
        type=str,
        default=[],
        action='append',
        help='Extra arguments to be passed to the media linker in the form of '
        'key=value. Values are strings, numbers or Python literals: True, '
        'False, etc. Can be used multiple times: -M burrito="bar" -M taco=12.'
    )

    return parser.parse_args()


class TimelineWidgetItem(QtWidgets.QListWidgetItem):
    def __init__(self, timeline, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timeline = timeline


class Main(QtWidgets.QMainWindow):
    def __init__(
            self,
            adapter_argument_map,
            hook_function_argument_map,
            media_linker,
            media_linker_argument_map,
            *args,
            **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.adapter_argument_map = adapter_argument_map or {}
        self.media_linker = media_linker
        self.media_linker_argument_map = media_linker_argument_map
        self.hook_function_argument_map = hook_function_argument_map

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

        file_load = QAction('Open...', menubar)
        file_load.setShortcut(QtGui.QKeySequence.Open)
        file_load.triggered.connect(self._file_load)

        exit_action = QAction('Exit', menubar)
        exit_action.setShortcut(QtGui.QKeySequence.Quit)
        exit_action.triggered.connect(self.close)

        file_menu = menubar.addMenu('File')
        file_menu.addAction(file_load)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        # navigation menu
        navigation_menu = QtWidgets.QMenu()
        navigation_menu.setTitle("Navigation")
        menubar.addMenu(navigation_menu)
        self._create_navigation_menu(navigation_menu)

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

        extensions_string = ' '.join(f'*.{x}' for x in extensions)

        path = str(
            QtWidgets.QFileDialog.getOpenFileName(
                self,
                'Open OpenTimelineIO',
                start_folder,
                f'OTIO ({extensions_string})'
            )[0]
        )

        if path:
            self.load(path)

    def load(self, path):
        self._current_file = path
        self.setWindowTitle(f'OpenTimelineIO View: "{path}"')
        self.details_widget.set_item(None)
        self.tracks_widget.clear()
        file_contents = otio.adapters.read_from_file(
            path,
            hook_function_argument_map=self.hook_function_argument_map,
            media_linker_name=self.media_linker,
            media_linker_argument_map=self.media_linker_argument_map,
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

    def _create_navigation_menu(self, navigation_menu):

        actions = otioViewWidget.timeline_widget.build_menu(navigation_menu)

        def __callback():
            self._navigation_filter_callback(actions)
        navigation_menu.triggered.connect(__callback)

    def _navigation_filter_callback(self, filters):
        nav_filter = 0
        filter_dict = otioViewWidget.timeline_widget.get_nav_menu_data()
        for filter in filters:
            if filter.isChecked():
                nav_filter += filter_dict[filter.text()].bitmask

        self.timeline_widget.navigationfilter_changed.emit(nav_filter)

    def center(self):
        screens = QtWidgets.QApplication.screens()
        if screens:
            style = QtWidgets.QApplication.style()
            title_bar_height = style.pixelMetric(QtWidgets.QStyle.PM_TitleBarHeight)

            screen = screens[0]
            screen_geo = screen.availableGeometry()
            screen_w = screen_geo.width()
            screen_h = screen_geo.height() - title_bar_height

            frame_geo = self.frameGeometry()
            frame_w = frame_geo.width()
            frame_h = frame_geo.height()

            new_frame_w = screen_w if frame_w > screen_w else frame_w
            new_frame_h = screen_h if frame_h > screen_h else frame_h
            if new_frame_w != frame_w or new_frame_h != frame_h:
                self.resize(new_frame_w, new_frame_h)
                frame_geo = self.frameGeometry()
                frame_w = frame_geo.width()
                frame_h = frame_geo.height()

            center_point = screen_geo.center()
            center_point.setY(center_point.y() - title_bar_height // 2)
            frame_geo.moveCenter(center_point)
            self.move(frame_geo.topLeft())

    def show(self):
        super().show()
        self.timeline_widget.frame_all()


def main():
    args = _parsed_args()

    media_linker_name = otio_console.console_utils.media_linker_name(
        args.media_linker
    )

    try:
        read_adapter_arg_map = otio_console.console_utils.arg_list_to_map(
            args.adapter_arg,
            "adapter"
        )
        media_linker_argument_map = otio_console.console_utils.arg_list_to_map(
            args.media_linker_arg,
            "media linker"
        )
        hook_function_argument_map = otio_console.console_utils.arg_list_to_map(
            args.hook_function_arg,
            "hook function"
        )
    except ValueError as exc:
        sys.stderr.write("\n" + str(exc) + "\n")
        sys.exit(1)

    application = QtWidgets.QApplication(sys.argv)

    window = Main(
        read_adapter_arg_map,
        hook_function_argument_map,
        media_linker_name,
        media_linker_argument_map
    )

    if args.input is not None:
        window.load(args.input)

    window.center()
    window.show()
    window.raise_()
    application.exec_()


if __name__ == '__main__':
    main()
