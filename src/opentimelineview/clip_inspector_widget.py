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

from PySide2.QtCore import QUrl, QSize, QRectF, QRect, QSizeF
from PySide2.QtGui import QImage, QPainter, QBrush, QPen, QPixmap, QColor
from PySide2.QtMultimedia import QMediaPlayer
from PySide2.QtCore import Qt
from PySide2.QtMultimediaWidgets import QGraphicsVideoItem

import opentimelineio as otio
from PySide2.QtWidgets import QWidget, QStackedLayout, QLabel,\
    QGraphicsScene, QGraphicsView, QGraphicsTextItem, QGraphicsRectItem


class ClipInspector(QWidget):

    def __init__(self, *args, **kwargs):
        super(ClipInspector, self).__init__(*args, **kwargs)
        self.scene = QGraphicsScene(self)
        self.graphicsView = QGraphicsView(self.scene)
        self.graphicsView.setBackgroundBrush(QBrush(Qt.black, Qt.SolidPattern))
        self.videoItem = QGraphicsVideoItem()
        self.videoItem.setSize(QSizeF(640, 360))
        self.scene.addItem(self.videoItem)
        self.player = QMediaPlayer()
        self.player.setVideoOutput(self.videoItem)
        self.player.error.connect(self.handle_error)
        self.player.setVolume(100)
        self.errorImage = QImage(QSize(640, 360), QImage.Format_RGB32)
        self.create_error_image()
        self.errorLabel = QLabel()
        self.errorLabel.setPixmap(QPixmap.fromImage(self.errorImage))
        self.videoLayout = QStackedLayout()
        # self.videoLayout.addWidget(self.videoWidget)
        self.videoLayout.addWidget(self.graphicsView)
        self.videoLayout.addWidget(self.errorLabel)
        self.setLayout(self.videoLayout)
        self.setFixedWidth(650)
        self.setFixedHeight(370)
        self.effectTextItem = QGraphicsTextItem("effect")
        self.effectRectItem = QGraphicsRectItem(0, 0, 640, 360)
        self.effectRectItem.setBrush(QBrush(QColor(255, 255, 255, 40)))

    def show(self):
        # self.videoWidget.show()
        pass

    def update_clip(self, clip):
        self.videoLayout.setCurrentIndex(0)
        self.player.stop()
        self.scene.removeItem(self.effectTextItem)
        self.scene.removeItem(self.effectRectItem)
        if isinstance(clip, otio.schema.Clip):
            if len(clip.effects) != 0:
                self.scene.addItem(self.effectRectItem)
                self.effectTextItem = QGraphicsTextItem(clip.effects[0].effect_name +
                                                        " effect")
                textFont = self.effectTextItem.font()
                textFont.setPointSize(textFont.pointSize() * 3)
                self.effectTextItem.setFont(textFont)
                self.effectTextItem.setPos(100, 150)
                self.scene.addItem(self.effectTextItem)
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

    def create_error_image(self):
        painter = QPainter(self.errorImage)
        painter.setBrush(QBrush(Qt.green))
        painter.fillRect(QRectF(0, 0, 640, 360), Qt.green)
        painter.setPen(QPen(Qt.black))
        font = painter.font()
        font.setPointSize(font.pointSize() * 3)
        painter.setFont(font)
        painter.drawText(QRect(160, 90, 320, 180), "Media Reference can't be resolved.")

    def handle_error(self):
        if self.player.errorString() == 'Resource not found.' or\
                self.player.errorString() == 'Not Found':
            self.videoLayout.setCurrentIndex(1)
