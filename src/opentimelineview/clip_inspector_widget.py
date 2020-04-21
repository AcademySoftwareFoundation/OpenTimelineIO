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
from PySide2.QtCore import QUrl, QSize, QRectF, QSizeF
from PySide2.QtGui import QImage, QPainter, QBrush, QPen, QPixmap
from PySide2.QtMultimedia import QMediaPlayer
from PySide2.QtCore import Qt
from PySide2.QtMultimediaWidgets import QGraphicsVideoItem

import opentimelineio as otio
from PySide2.QtWidgets import QWidget, QStackedLayout, QLabel, \
    QGraphicsScene, QGraphicsView, QVBoxLayout, QHBoxLayout, QComboBox


class ClipInspector(QWidget):

    def __init__(self, *args, **kwargs):
        super(ClipInspector, self).__init__(*args, **kwargs)
        self.clipWidth = 640
        self.clipHeight = 360
        self.scene = QGraphicsScene(self)
        self.graphicsView = QGraphicsView(self.scene)
        self.graphicsView.setBackgroundBrush(QBrush(Qt.black, Qt.SolidPattern))
        self.videoItem = QGraphicsVideoItem()
        self.videoItem.setSize(QSizeF(self.clipWidth, self.clipHeight))
        self.scene.addItem(self.videoItem)
        self.player = QMediaPlayer()
        self.player.setVideoOutput(self.videoItem)
        self.player.error.connect(self.handle_error)
        self.player.setVolume(100)
        self.unresolvedMediaErrorImage = QImage(QSize(self.clipWidth, self.clipHeight),
                                                QImage.Format_RGB32)
        self.unsupportedMediaErrorImage = QImage(QSize(self.clipWidth, self.clipHeight),
                                                 QImage.Format_RGB32)
        self.create_error_images()
        # unresolved media error QLabel
        self.unresolvedMediaErrorLabel = QLabel()
        self.unresolvedMediaErrorLabel.setPixmap(
            QPixmap.fromImage(self.unresolvedMediaErrorImage))
        # unresolved media error QLabel
        self.unsupportedMediaErrorLabel = QLabel()
        self.unsupportedMediaErrorLabel.setPixmap(
            QPixmap.fromImage(self.unsupportedMediaErrorImage))
        # create stacked layout for video and error messages
        self.videoLayout = QStackedLayout()
        # Clip Inspector widget stack
        # index 0 - video and banners
        # index 1 - unresolved media error message
        # index 2 - unsupported media error message
        self.videoLayout.addWidget(self.graphicsView)
        self.videoLayout.addWidget(self.unresolvedMediaErrorLabel)
        self.videoLayout.addWidget(self.unsupportedMediaErrorLabel)
        self.videoWidget = QWidget()
        self.videoWidget.setLayout(self.videoLayout)
        # TODO: find fix for constant widget size
        self.videoWidget.setFixedWidth(self.clipWidth + 10)
        # self.videoWidget.setFixedHeight(self.clipHeight + 10)
        self.effectsLabel = QLabel()
        self.effectsLabel.setText("Effects: ")
        self.effectsLabel.setStyleSheet("QLabel {color : white }")
        self.effectsLabel.setAlignment(Qt.AlignLeft)
        self.rangeComboBox = QComboBox()
        self.rangeComboBox.addItem("Entire clip")
        self.rangeComboBox.addItem("Source Range")
        self.rangeComboBox.currentIndexChanged.connect(self.combobox_selection_changed)
        self.optionLayout = QHBoxLayout()
        self.optionLayout.addWidget(self.effectsLabel, 3)
        self.optionLayout.addWidget(self.rangeComboBox, 1)
        self.widgetLayout = QVBoxLayout()
        self.widgetLayout.addWidget(self.videoWidget)
        self.widgetLayout.addItem(self.optionLayout)
        self.setLayout(self.widgetLayout)
        # TODO: find fix for constant widget size
        self.setFixedWidth(self.clipWidth + 20)
        self.setFixedHeight(self.clipHeight * 1.2)
        # utility variables
        self.clip_start_duration = 0.0
        self.clip_end_duration = 0.0
        self.range_type = 0
        self.clip = None

    def combobox_selection_changed(self, i):
        self.range_type = i
        self.update_clip(self.clip)

    def update_clip(self, clip):
        self.videoLayout.setCurrentIndex(0)  # show video player widget
        self.player.stop()  # stop player before changing media state
        if isinstance(clip, otio.schema.Clip):
            self.clip = clip
            if self.range_type == 0:
                self.clip_start_duration = (clip.available_range().start_time.value /
                                            clip.available_range().start_time.rate)
                self.clip_end_duration = (self.clip_start_duration +
                                          (clip.available_range().duration.value /
                                           clip.available_range().duration.rate))
                self.clip_start_duration *= 1000
                self.clip_end_duration *= 1000
            elif self.range_type == 1:
                self.clip_start_duration = (clip.trimmed_range().start_time.value /
                                            clip.trimmed_range().start_time.rate)
                self.clip_end_duration = (self.clip_start_duration +
                                          (clip.trimmed_range().duration.value /
                                           clip.trimmed_range().duration.rate))
                self.clip_start_duration *= 1000
                self.clip_end_duration *= 1000
            if len(clip.effects) != 0:  # show effects banner if effects present
                effectsString = " | "
                effectsString = effectsString.join(
                    effect.effect_name for effect in clip.effects)
                self.effectsLabel.setText("Effects: " + effectsString)
            else:
                self.effectsLabel.setText("Effects: ")
            path = clip.media_reference.target_url
            if path.startswith('file://'):
                path = path[7:]
                self.player.setMedia(QUrl.fromLocalFile(path))
            elif path.startswith('http'):
                self.player.setMedia(QUrl(path))

    def play_clip(self):
        self.player.play()

    def pause_clip(self):
        self.player.pause()

    def stop_clip(self):
        self.player.stop()

    def set_clip_position(self, position):
        self.player.setPosition(position)

    def create_error_images(self):
        # painter for unresolved media error image
        painter = QPainter(self.unresolvedMediaErrorImage)
        painter.setBrush(QBrush(Qt.green))
        painter.fillRect(QRectF(0, 0, self.clipWidth, self.clipHeight), Qt.green)
        painter.setPen(QPen(Qt.black))
        # use larger font size
        font = painter.font()
        font.setPointSize(font.pointSize() * 3)
        painter.setFont(font)
        painter.drawText(QRectF(self.clipWidth * 0.25, self.clipHeight * 0.25,
                                self.clipWidth * 0.5, self.clipHeight * 0.6),
                         "Media Reference can't be resolved.")
        # painter for unsupported media error image
        painter = QPainter(self.unsupportedMediaErrorImage)
        painter.setBrush(QBrush(Qt.green))
        painter.fillRect(QRectF(0, 0, self.clipWidth, self.clipHeight), Qt.green)
        painter.setPen(QPen(Qt.black))
        painter.setFont(font)
        painter.drawText(QRectF(self.clipWidth * 0.25, self.clipHeight * 0.25,
                                self.clipWidth * 0.5, self.clipHeight * 0.6),
                         "Unsupported Media format.")

    def handle_error(self):
        if self.player.errorString() == 'Resource not found.' or \
                self.player.errorString() == 'Not Found':
            self.videoLayout.setCurrentIndex(1)  # display unresolved media error
        elif self.player.errorString().startswith('Cannot play stream of type:'):
            self.videoLayout.setCurrentIndex(2)  # display unsupported media error
