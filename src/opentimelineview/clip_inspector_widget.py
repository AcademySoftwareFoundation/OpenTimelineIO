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

from PySide2.QtCore import QUrl
from PySide2.QtMultimedia import QMediaPlayer, QMediaPlaylist
from PySide2.QtMultimediaWidgets import QVideoWidget

import opentimelineio as otio


class ClipInspector(QVideoWidget):

    def __init__(self, *args, **kwargs):
        super(ClipInspector, self).__init__(*args, **kwargs)
        self.player = QMediaPlayer()
        self.player.setVideoOutput(self)
        # self.setScaleMode()
        # self.show()

    def update_clip(self, clip):
        self.player.stop()
        if isinstance(clip, otio.schema.Clip):
            path = clip.media_reference.target_url
            if path.startswith('file://'):
                path = path[7:]
            self.player.setMedia(QUrl.fromLocalFile(path))
            self.player.setVolume(100)
            # self.player.play()

    def play_clip(self):
        print('here')
        self.player.play()

    def pause_clip(self):
        self.player.pause()

    def stop_clip(self):
        self.player.stop()

    def set_clip_position(self, position):
        self.player.setPosition(position)
