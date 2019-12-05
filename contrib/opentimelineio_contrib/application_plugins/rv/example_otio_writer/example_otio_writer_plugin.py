# DreamWorks Animation LLC Confidential Information.
# TM and (c) 2019 DreamWorks Animation LLC.  All Rights Reserved.
# Reproduction in whole or in part without prior written permission of a
# duly authorized representative is prohibited.

"""
RV Plugin for writing OTIO's.

"""

import logging
import os
import re
import traceback

# RV
import rv
import PySide.QtGui as QtGui
import PySide.QtCore as QtCore

import opentimelineio as otio

from otio_writer import create_otio_from_rv_node


class ExampleOTIOWriterMode(rv.rvtypes.MinorMode):
    """
    OTIO plugin for creating an OTIO file from an RV Node.

    """

    def __init__(self):
        super(ExampleOTIOWriterMode, self).__init__()

        self.init(
            "otio_writer",
            [
                (
                    "key-down--control--shift--e",
                    self.export_otio,
                    "Export OTIO to File"
                )
            ],
            None,
            [
                (
                    "File",
                    [
                        (
                            "Export",
                            [
                                (
                                    "OTIO...",
                                    self.export_otio,
                                    "Ctrl+Shift+E",
                                    self.export_otio_menu_state
                                )
                            ]
                        )
                    ]
                )
            ]
        )

    @staticmethod
    def export_otio_menu_state():
        """
        Return the menu state of the menu item.
        :return: `rv.commands.{Checked/Unchecked/Disabled}MenuState`
        """
        inputs, _ = rv.commands.nodeConnections(rv.commands.viewNode())
        if rv.commands.nodeType(rv.commands.viewNode()) != "RVSequenceGroup":
            return rv.commands.DisabledMenuState

        return True

    def export_otio(self, event):
        """
        When "Menu Item" menu item is selected.
        :param event: `rv.rvtypes.Event`
        :return:
        """
        if event:
            event.reject()

        file_name = QtGui.QFileDialog.getSaveFileName(
            rv.qtutils.sessionWindow(),
            "Export OTIO",
            selectedFilter='OTIO\'s (*.otio)'
        )

        if file_name and file_name[0]:
            file_path = file_name[0]
            otio_timeline = otio_timeline_from_rv_sequence(
                rv.commands.viewNode()
            )
            if otio_timeline:
                otio.adapters.write_to_file(otio_timeline, file_path)
                rv.extra_commands.displayFeedback(
                    "Exported {}".format(file_path), 4.0)
            else:
                rv.extra_commands.displayFeedback(
                    "Failed to export {}".format(file_path), 4.0)


def otio_timeline_from_rv_sequence(rv_sequence_group):
    """
    Write out an OTIO for the current view node to a given path.
    :param rv_sequence_group: `str`
    :param hook_function_argument_map: `dict`
    :return: `bool`
    """
    otio_track = create_otio_from_rv_node(rv_sequence_group)

    name = otio_track.name
    otio_track.name = otio_track.name
    otio_timeline = otio.schema.Timeline(name=name)
    otio_timeline.tracks[:] = [otio_track]

    return otio_timeline


def createMode():
    return ExampleOTIOWriterMode()


# TM and (c) 2019 DreamWorks Animation LLC.  All Rights Reserved.
# Reproduction in whole or in part without prior written permission of a
# duly authorized representative is prohibited.
