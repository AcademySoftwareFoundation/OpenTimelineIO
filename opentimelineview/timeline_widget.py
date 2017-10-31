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

from PySide import QtGui
from PySide import QtCore

import opentimelineio as otio

TIME_SLIDER_HEIGHT = 20
MEDIA_TYPE_SEPARATOR_HEIGHT = 5
TRACK_HEIGHT = 45
TRANSITION_HEIGHT = 10
TIME_MULTIPLIER = 25
LABEL_MARGIN = 5
MARKER_SIZE = 10


class _BaseItem(QtGui.QGraphicsRectItem):
    def __init__(self, item, timeline_range, *args, **kwargs):
        super(_BaseItem, self).__init__(*args, **kwargs)
        self.item = item
        self.timeline_range = timeline_range

        self.setFlags(QtGui.QGraphicsItem.ItemIsSelectable)
        self.setBrush(
            QtGui.QBrush(QtGui.QColor(180, 180, 180, 255))
        )

        self.source_in_label = QtGui.QGraphicsSimpleTextItem(self)
        self.source_out_label = QtGui.QGraphicsSimpleTextItem(self)
        self.source_name_label = QtGui.QGraphicsSimpleTextItem(self)

        self._add_markers()
        self._set_labels()

    def paint(self, *args, **kwargs):
        new_args = [args[0], QtGui.QStyleOptionGraphicsItem()] + list(args[2:])
        super(_BaseItem, self).paint(*new_args, **kwargs)

    def itemChange(self, change, value):
        if change == QtGui.QGraphicsItem.ItemSelectedHasChanged:
            self.setPen(
                QtGui.QColor(0, 255, 0, 255) if self.isSelected()
                else QtGui.QColor(0, 0, 0, 255)
            )
            self.setZValue(
                self.zValue() + 1 if self.isSelected() else self.zValue() - 1
            )

        return super(_BaseItem, self).itemChange(change, value)

    def _add_markers(self):
        trimmed_range = self.item.trimmed_range()

        for m in self.item.markers:
            marked_time = m.marked_range.start_time
            if not trimmed_range.overlaps(marked_time):
                continue

            # @TODO: set the marker color if its set from the OTIO object
            marker = Marker(m, None, None)
            marker.setY(0.5 * MARKER_SIZE)
            marker.setX(
                (
                    otio.opentime.to_seconds(m.marked_range.start_time)
                    - otio.opentime.to_seconds(trimmed_range.start_time)
                ) * TIME_MULTIPLIER
            )
            marker.setParentItem(self)

    def _position_labels(self):
        self.source_in_label.setY(LABEL_MARGIN)
        self.source_out_label.setY(LABEL_MARGIN)
        self.source_name_label.setY(
            TRACK_HEIGHT
            - LABEL_MARGIN
            - self.source_name_label.boundingRect().height()
        )

    def _set_labels_rational_time(self):
        trimmed_range = self.item.trimmed_range()
        self.source_in_label.setText(
            '{value}\n@{rate}'.format(
                value=trimmed_range.start_time.value,
                rate=trimmed_range.start_time.rate
            )
        )
        self.source_out_label.setText(
            '{value}\n@{rate}'.format(
                value=trimmed_range.end_time_exclusive().value,
                rate=trimmed_range.end_time_exclusive().rate
            )
        )

    def _set_labels_timecode(self):
        self.source_in_label.setText('{timeline}\n{source}'.format(
                timeline=otio.opentime.to_timecode(
                    self.timeline_range.start_time,
                    self.timeline_range.start_time.rate
                ),
                source=otio.opentime.to_timecode(
                    self.item.trimmed_range.start_time,
                    self.item.trimmed_range.start_time.rate
                )
            )
        )

        self.source_out_label.setText('{timeline}\n{source}'.format(
                timeline=otio.opentime.to_timecode(
                    self.timeline_range.end_time_exclusive(),
                    self.timeline_range.end_time_exclusive().rate
                ),
                source=otio.opentime.to_timecode(
                    self.item.trimmed_range.end_time_exclusive(),
                    self.item.trimmed_range.end_time_exclusive().rate
                )
            )
        )

    def _set_labels(self):
        self._set_labels_rational_time()
        self.source_name_label.setText('PLACEHOLDER')
        self._position_labels()

    def counteract_zoom(self, zoom_level=1.0):
        for label in (
            self.source_name_label,
            self.source_in_label,
            self.source_out_label
        ):
            label.setTransform(QtGui.QTransform.fromScale(zoom_level, 1.0))

        self_rect = self.boundingRect()
        name_width = self.source_name_label.boundingRect().width() * zoom_level
        in_width = self.source_in_label.boundingRect().width() * zoom_level
        out_width = self.source_out_label.boundingRect().width() * zoom_level

        frames_space = in_width + out_width + 3 * LABEL_MARGIN * zoom_level

        if frames_space > self_rect.width():
            self.source_in_label.setVisible(False)
            self.source_out_label.setVisible(False)
        else:
            self.source_in_label.setVisible(True)
            self.source_out_label.setVisible(True)

            self.source_in_label.setX(LABEL_MARGIN * zoom_level)

            self.source_out_label.setX(
                self_rect.width() - LABEL_MARGIN * zoom_level - out_width
            )

        total_width = (name_width + frames_space + LABEL_MARGIN * zoom_level)
        if total_width > self_rect.width():
            self.source_name_label.setVisible(False)
        else:
            self.source_name_label.setVisible(True)
            self.source_name_label.setX(0.5 * (self_rect.width() - name_width))


class GapItem(_BaseItem):
    def __init__(self, *args, **kwargs):
        super(GapItem, self).__init__(*args, **kwargs)
        self.setBrush(
            QtGui.QBrush(QtGui.QColor(100, 100, 100, 255))
        )
        self.source_name_label.setText('GAP')


class TransitionItem(_BaseItem):
    def __init__(self, item, timeline_range, rect, *args, **kwargs):
        rect.setHeight(TRANSITION_HEIGHT)
        super(TransitionItem, self).__init__(
            item,
            timeline_range,
            rect,
            *args,
            **kwargs
        )
        self.setBrush(
            QtGui.QBrush(QtGui.QColor(237, 228, 148, 255))
        )
        self.setY(TRACK_HEIGHT - TRANSITION_HEIGHT)
        self.setZValue(2)

        # add extra bit of shading
        shading_poly_f = QtGui.QPolygonF()
        shading_poly_f.append(QtCore.QPointF(0, 0))
        shading_poly_f.append(QtCore.QPointF(rect.width(), 0))
        shading_poly_f.append(QtCore.QPointF(0, rect.height()))

        shading_poly = QtGui.QGraphicsPolygonItem(shading_poly_f, parent=self)
        shading_poly.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0, 30)))

        try:
            shading_poly.setPen(QtCore.Qt.NoPen)
        except TypeError:
            shading_poly.setPen(QtCore.Qt.transparent)

    def _add_markers(self):
        return

    def _set_labels(self):
        return


class ClipItem(_BaseItem):
    def __init__(self, *args, **kwargs):
        super(ClipItem, self).__init__(*args, **kwargs)
        self.setBrush(QtGui.QBrush(QtGui.QColor(168, 197, 255, 255)))
        self.source_name_label.setText(self.item.name)


class NestedItem(_BaseItem):
    def __init__(self, *args, **kwargs):
        super(NestedItem, self).__init__(*args, **kwargs)
        self.setBrush(
            QtGui.QBrush(QtGui.QColor(255, 113, 91, 255))
        )

        self.source_name_label.setText(self.item.name)

    def mouseDoubleClickEvent(self, event):
        super(_BaseItem, self).mouseDoubleClickEvent(event)
        self.scene().views()[0].open_stack.emit(self.item)


class TrackWidget(QtGui.QGraphicsRectItem):
    def __init__(self, track, *args, **kwargs):
        super(TrackWidget, self).__init__(*args, **kwargs)
        self.track = track

        self.setBrush(QtGui.QBrush(QtGui.QColor(43, 52, 59, 255)))
        self._populate()

    def _populate(self):
        for n, item in enumerate(self.track):
            timeline_range = self.track.trimmed_range_of_child_at_index(n)

            rect = QtCore.QRectF(
                0,
                0,
                otio.opentime.to_seconds(timeline_range.duration) *
                TIME_MULTIPLIER,
                TRACK_HEIGHT
            )

            if isinstance(item, otio.schema.Clip):
                new_item = ClipItem(item, timeline_range, rect)
            elif isinstance(item, otio.schema.Stack):
                new_item = NestedItem(item, timeline_range, rect)
            elif isinstance(item, otio.schema.Track):
                new_item = NestedItem(item, timeline_range, rect)
            elif isinstance(item, otio.schema.Gap):
                new_item = GapItem(item, timeline_range, rect)
            elif isinstance(item, otio.schema.Transition):
                new_item = TransitionItem(item, timeline_range, rect)
            else:
                print("Warning: could not add item {} to UI.".format(item))
                continue

            new_item.setParentItem(self)
            new_item.setX(
                otio.opentime.to_seconds(timeline_range.start_time)
                * TIME_MULTIPLIER
            )
            new_item.counteract_zoom()


class Marker(QtGui.QGraphicsPolygonItem):
    def __init__(self, marker, *args, **kwargs):
        self.item = marker

        poly = QtGui.QPolygonF()
        poly.append(QtCore.QPointF(0.5 * MARKER_SIZE, -0.5 * MARKER_SIZE))
        poly.append(QtCore.QPointF(0.5 * MARKER_SIZE, 0.5 * MARKER_SIZE))
        poly.append(QtCore.QPointF(0, MARKER_SIZE))
        poly.append(QtCore.QPointF(-0.5 * MARKER_SIZE, 0.5 * MARKER_SIZE))
        poly.append(QtCore.QPointF(-0.5 * MARKER_SIZE, -0.5 * MARKER_SIZE))
        super(Marker, self).__init__(poly, *args, **kwargs)

        self.setFlags(QtGui.QGraphicsItem.ItemIsSelectable)
        self.setBrush(QtGui.QBrush(QtGui.QColor(121, 212, 177, 255)))

    def paint(self, *args, **kwargs):
        new_args = [args[0], QtGui.QStyleOptionGraphicsItem()] + list(args[2:])
        super(Marker, self).paint(*new_args, **kwargs)

    def itemChange(self, change, value):
        if change == QtGui.QGraphicsItem.ItemSelectedHasChanged:
            self.setPen(
                QtGui.QColor(0, 255, 0, 255) if self.isSelected()
                else QtGui.QColor(0, 0, 0, 255)
            )
        return super(Marker, self).itemChange(change, value)

    def counteract_zoom(self, zoom_level=1.0):
        self.setTransform(QtGui.QTransform.fromScale(zoom_level, 1.0))


class TimeSlider(QtGui.QGraphicsRectItem):
    def __init__(self, *args, **kwargs):
        super(TimeSlider, self).__init__(*args, **kwargs)
        self.setBrush(QtGui.QBrush(QtGui.QColor(64, 78, 87, 255)))


class CompositionWidget(QtGui.QGraphicsScene):
    def __init__(self, composition, *args, **kwargs):
        super(CompositionWidget, self).__init__(*args, **kwargs)
        self.composition = composition

        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(64, 78, 87, 255)))

        self._adjust_scene_size()
        self._add_time_slider()
        self._add_tracks()
        self._add_markers()

    def _adjust_scene_size(self):
        scene_range = self.composition.trimmed_range()

        start_time = otio.opentime.to_seconds(scene_range.start_time)
        duration = otio.opentime.to_seconds(scene_range.end_time_exclusive())

        if isinstance(self.composition, otio.schema.Stack):
            # non audio tracks are sorted into one area
            has_video_tracks = any(
                t.kind != otio.schema.TrackKind.Audio
                for t in self.composition
            )
            has_audio_tracks = any(
                t.kind == otio.schema.TrackKind.Audio
                for t in self.composition
            )
        elif isinstance(self.composition, otio.schema.TrackKind):
            has_video_tracks = (
                self.composition.kind != otio.schema.TrackKind.Audio
            )
            has_audio_tracks = (
                self.composition.kind == otio.schema.TrackKind.Audio
            )
        else:
            raise otio.exceptions.NotSupportedError(
                "Error: file includes composition '{}', of type '{}',"
                " not supported by opentimeview.  Only supports children of"
                " otio.schema.Stack and otio.schema.Track".format(
                    self.composition,
                    type(self.composition)
                )
            )

        height = (
            TIME_SLIDER_HEIGHT
            + (
                int(has_video_tracks and has_audio_tracks)
                * MEDIA_TYPE_SEPARATOR_HEIGHT
            )
            + len(self.composition) * TRACK_HEIGHT
        )

        self.setSceneRect(
            start_time * TIME_MULTIPLIER,
            0,
            duration * TIME_MULTIPLIER,
            height
        )

    def _add_time_slider(self):
        scene_rect = self.sceneRect()

        scene_rect.setWidth(scene_rect.width() * 10)
        scene_rect.setHeight(TIME_SLIDER_HEIGHT)
        self.addItem(TimeSlider(scene_rect))

    def _add_track(self, track, y_pos):
        scene_rect = self.sceneRect()
        rect = QtCore.QRectF(0, 0, scene_rect.width() * 10, TRACK_HEIGHT)
        new_track = TrackWidget(track, rect)
        self.addItem(new_track)
        new_track.setPos(scene_rect.x(), y_pos)

    def _add_tracks(self):
        video_tracks_top = TIME_SLIDER_HEIGHT
        audio_tracks_top = TIME_SLIDER_HEIGHT

        video_tracks = []
        audio_tracks = []
        other_tracks = []

        if isinstance(self.composition, otio.schema.Stack):
            video_tracks = [
                t for t in self.composition
                if t.kind == otio.schema.TrackKind.Video and list(t)
            ]
            audio_tracks = [
                t for t in self.composition
                if t.kind == otio.schema.TrackKind.Audio and list(t)
            ]
            video_tracks.reverse()

            other_tracks = [
                t for t in self.composition
                if (
                    t.kind not in (
                        otio.schema.TrackKind.Video,
                        otio.schema.TrackKind.Audio
                    )
                    and list(t)
                )
            ]
        else:
            if self.composition.kind == otio.schema.TrackKind.Video:
                video_tracks = [self.composition]
            elif self.composition.kind == otio.schema.TrackKind.Audio:
                audio_tracks = [self.composition]
            else:
                other_tracks = [self.composition]

        if other_tracks:
            for t in other_tracks:
                print(
                    "Warning: track named '{}' has nonstandard track type:"
                    " '{}'".format(t.name, t.kind)
                )

            video_tracks.extend(other_tracks)

        video_tracks_top = TIME_SLIDER_HEIGHT
        audio_tracks_top = (
            TIME_SLIDER_HEIGHT
            + len(video_tracks) * TRACK_HEIGHT
            + int(
                bool(video_tracks) and bool(audio_tracks)
            ) * MEDIA_TYPE_SEPARATOR_HEIGHT
        )

        for i, track in enumerate(audio_tracks):
            self._add_track(track, audio_tracks_top + i * TRACK_HEIGHT)

        for i, track in enumerate(video_tracks):
            self._add_track(track, video_tracks_top + i * TRACK_HEIGHT)

    def _add_markers(self):
        for m in self.composition.markers:
            marker = Marker(m, None, self)
            marker.setX(
                otio.opentime.to_seconds(m.marked_range.start_time)
                * TIME_MULTIPLIER
            )
            marker.setY(TIME_SLIDER_HEIGHT - MARKER_SIZE)
            self.addItem(marker)


class CompositionView(QtGui.QGraphicsView):

    open_stack = QtCore.Signal(otio.schema.Stack)
    selection_changed = QtCore.Signal(otio.core.SerializableObject)

    def __init__(self, stack, *args, **kwargs):
        super(CompositionView, self).__init__(*args, **kwargs)
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setScene(CompositionWidget(stack, parent=self))
        self.setAlignment((QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop))

        self.scene().selectionChanged.connect(self.parse_selection_change)

    def parse_selection_change(self):
        selection = self.scene().selectedItems()
        if selection:
            self.selection_changed.emit(selection[-1].item)

    def mousePressEvent(self, mouse_event):
        modifiers = QtGui.QApplication.keyboardModifiers()
        self.setDragMode(
            QtGui.QGraphicsView.ScrollHandDrag
            if modifiers == QtCore.Qt.AltModifier
            else QtGui.QGraphicsView.NoDrag
        )
        self.setInteractive(not modifiers == QtCore.Qt.AltModifier)
        super(CompositionView, self).mousePressEvent(mouse_event)

    def mouseReleaseEvent(self, mouse_event):
        super(CompositionView, self).mouseReleaseEvent(mouse_event)
        self.setDragMode(QtGui.QGraphicsView.NoDrag)

    def wheelEvent(self, event):
        scale_by = 1.0 + float(event.delta()) / 1000
        self.scale(scale_by, 1)
        zoom_level = 1.0 / self.matrix().m11()

        # some items we do want to keep the same visual size. So we need to
        # inverse the effect of the zoom
        items_to_scale = [
            i for i in self.scene().items()
            if isinstance(i, _BaseItem) or isinstance(i, Marker)
        ]

        for item in items_to_scale:
            item.counteract_zoom(zoom_level)


class Timeline(QtGui.QTabWidget):

    selection_changed = QtCore.Signal(otio.core.SerializableObject)

    def __init__(self, *args, **kwargs):
        super(Timeline, self).__init__(*args, **kwargs)
        self.timeline = None

        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self._close_tab)

    def _close_tab(self, index):
        self.widget(index).deleteLater()
        self.removeTab(index)

    def set_timeline(self, timeline):
        # close all the tabs
        for i in reversed(range(self.count())):
            self._close_tab(i)

        # load new timeline
        self.timeline = timeline
        if timeline is not None:
            self.add_stack(timeline.tracks)

    def add_stack(self, stack):
        """open a tab for the stack or go to it if already present"""

        # find the tab for the stack if the tab has already been opened
        tab_index = next(
            (
                i for i in range(self.count())
                if stack is self.widget(i).scene().composition
            ),
            None
        )

        if tab_index is not None:
            self.setCurrentIndex(tab_index)
            return

        new_stack = CompositionView(stack, parent=self)
        self.addTab(new_stack, stack.name)

        # cannot close the first tab
        if self.count() == 1:
            button = self.tabBar().tabButton(0, QtGui.QTabBar.RightSide)
            if button:
                button.resize(0, 0)

        new_stack.open_stack.connect(self.add_stack)
        new_stack.selection_changed.connect(self.selection_changed)
        self.setCurrentIndex(self.count() - 1)
