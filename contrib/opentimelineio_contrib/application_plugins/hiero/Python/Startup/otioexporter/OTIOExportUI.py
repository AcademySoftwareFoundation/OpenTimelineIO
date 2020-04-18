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
import OTIOExportTask

try:
    # Hiero >= 11.x
    from PySide2 import QtCore
    from PySide2.QtWidgets import QCheckBox
    from hiero.ui.FnTaskUIFormLayout import TaskUIFormLayout as FormLayout

except ImportError:
    # Hiero <= 10.x
    from PySide import QtCore  # lint:ok
    from PySide.QtGui import QCheckBox, QFormLayout  # lint:ok

    FormLayout = QFormLayout  # lint:ok


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
        formLayout = FormLayout()

        # Hiero ~= 10.0v4
        if layout is None:
            layout = formLayout
            widget.setLayout(layout)

        else:
            layout.addLayout(formLayout)

        # Checkboxes for whether the OTIO should contain markers or not
        self.includeMarkersCheckbox = QCheckBox()
        self.includeMarkersCheckbox.setToolTip(
            "Enable to include Tags as markers in the exported OTIO file."
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
