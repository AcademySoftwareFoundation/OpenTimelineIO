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

try:
    # Hiero >= 11.x
    from PySide2 import QtCore
    from PySide2.QtWidgets import QCheckBox

except ImportError:
    # Hiero <= 10.x
    from PySide import QtCore  # lint:ok
    from PySide.QtGui import QCheckBox  # lint:ok

import hiero.ui
import OTIOExportTask
from hiero.ui.FnTaskUIFormLayout import TaskUIFormLayout


class OTIOExportUI(hiero.ui.TaskUIBase):
    def __init__(self, preset):
        """Initialize"""
        hiero.ui.TaskUIBase.__init__(
                                self,
                                OTIOExportTask.OTIOExportTask,
                                preset,
                                "OTIO Exporter"
                                )

    def includeMarkersCheckboxChanged(self, state):
        # Slot to handle change of checkbox state
        self._preset.properties()["includeTags"] = state == QtCore.Qt.Checked

    def populateUI(self, widget, exportTemplate):
        layout = widget.layout()
        formLayout = TaskUIFormLayout()
        layout.addLayout(formLayout)

        # create checkboxes for whether the XML should contain timeline markers
        self.includeMarkersCheckbox = QCheckBox()
        self.includeMarkersCheckbox.setToolTip(
                    "Enable to include Tags as markers in the exported XML."
                    )
        self.includeMarkersCheckbox.setCheckState(QtCore.Qt.Unchecked)

        if self._preset.properties()["includeTags"]:
            self.includeMarkersCheckbox.setCheckState(QtCore.Qt.Checked)

        self.includeMarkersCheckbox.stateChanged.connect(
                                            self.includeMarkersCheckboxChanged
                                            )

        # Add Checkbox to layout
        formLayout.addRow("Include Tags:", self.includeMarkersCheckbox)


hiero.ui.taskUIRegistry.registerTaskUI(
                                OTIOExportTask.OTIOExportPreset,
                                OTIOExportUI
                                )
