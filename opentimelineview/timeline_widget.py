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

from PySide2 import QtGui, QtCore, QtWidgets
from collections import OrderedDict, namedtuple
import math

import opentimelineio as otio

TIME_SLIDER_HEIGHT = 20
MEDIA_TYPE_SEPARATOR_HEIGHT = 5
TRACK_HEIGHT = 45
TRANSITION_HEIGHT = 10
TIME_MULTIPLIER = 25
LABEL_MARGIN = 5
MARKER_SIZE = 10
RULER_SIZE = 10
EFFECT_HEIGHT = 1/3.0 * TRACK_HEIGHT


class _BaseItem(QtWidgets.QGraphicsRectItem):

    def __init__(self, item, timeline_range, *args, **kwargs):
        super(_BaseItem, self).__init__(*args, **kwargs)
        self.item = item
        self.timeline_range = timeline_range

        self.setFlags(QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.setBrush(
            QtGui.QBrush(QtGui.QColor(180, 180, 180, 255))
        )

        pen = QtGui.QPen()
        pen.setWidth(0)
        self.setPen(pen)

        self.source_in_label = QtWidgets.QGraphicsSimpleTextItem(self)
        self.source_out_label = QtWidgets.QGraphicsSimpleTextItem(self)
        self.source_name_label = QtWidgets.QGraphicsSimpleTextItem(self)

        self._add_markers()
        self._add_effects()
        self._set_labels()
        self._set_tooltip()

    def paint(self, *args, **kwargs):
        new_args = [args[0],
                    QtWidgets.QStyleOptionGraphicsItem()] + list(args[2:])
        super(_BaseItem, self).paint(*new_args, **kwargs)

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemSelectedHasChanged:
            pen = self.pen()
            pen.setColor(
                QtGui.QColor(0, 255, 0, 255) if self.isSelected()
                else QtGui.QColor(0, 0, 0, 255)
            )
            self.setPen(pen)
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
            marker = Marker(m, None)
            marker.setY(0.5 * MARKER_SIZE)
            marker.setX(
                (
                    otio.opentime.to_seconds(m.marked_range.start_time) -
                    otio.opentime.to_seconds(trimmed_range.start_time)
                ) * TIME_MULTIPLIER
            )
            marker.setParentItem(self)

    def _add_effects(self):
        if not hasattr(self.item, "effects"):
            return
        if not self.item.effects:
            return
        effect = EffectItem(self.item.effects, self.rect())
        effect.setParentItem(self)

    def _position_labels(self):
        self.source_in_label.setY(LABEL_MARGIN)
        self.source_out_label.setY(LABEL_MARGIN)
        self.source_name_label.setY(
            (TRACK_HEIGHT -
             self.source_name_label.boundingRect().height()) / 2.0
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
                value=trimmed_range.end_time_inclusive().value,
                rate=trimmed_range.end_time_inclusive().rate
            )
        )

    def _set_labels_timecode(self):
        self.source_in_label.setText(
            '{timeline}\n{source}'.format(
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

        self.source_out_label.setText(
            '{timeline}\n{source}'.format(
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

    def _set_tooltip(self):
        self.setToolTip(self.item.name)

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


class EffectItem(QtWidgets.QGraphicsRectItem):

    def __init__(self, item, rect, *args, **kwargs):
        super(EffectItem, self).__init__(rect, *args, **kwargs)
        self.item = item
        self.setFlags(QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.init()
        self._set_tooltip()

    def init(self):
        rect = self.rect()
        rect.setY(TRACK_HEIGHT - EFFECT_HEIGHT)
        rect.setHeight(EFFECT_HEIGHT)
        self.setRect(rect)

        dark = QtGui.QColor(0, 0, 0, 150)
        colour = QtGui.QColor(255, 255, 255, 200)
        gradient = QtGui.QLinearGradient(
                   QtCore.QPointF(0,
                                  self.boundingRect().top()),
                   QtCore.QPointF(0,
                                  self.boundingRect().bottom()))
        gradient.setColorAt(0.2, QtCore.Qt.transparent)
        gradient.setColorAt(0.45, colour)
        gradient.setColorAt(0.7, QtCore.Qt.transparent)
        gradient.setColorAt(1.0, dark)
        self.setBrush(QtGui.QBrush(gradient))

        pen = self.pen()
        pen.setColor(QtGui.QColor(0, 0, 0, 80))
        pen.setWidth(0)
        self.setPen(pen)

    def _set_tooltip(self):
        tool_tips = list()
        for effect in self.item:
            name = effect.name if effect.name else ""
            effect_name = effect.effect_name if effect.effect_name else ""
            tool_tips.append("{} {}".format(name, effect_name))
        self.setToolTip("\n".join(tool_tips))

    def paint(self, *args, **kwargs):
        new_args = [args[0],
                    QtWidgets.QStyleOptionGraphicsItem()] + list(args[2:])
        super(EffectItem, self).paint(*new_args, **kwargs)

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemSelectedHasChanged:
            pen = self.pen()
            pen.setColor(
                QtGui.QColor(0, 255, 0, 255) if self.isSelected()
                else QtGui.QColor(0, 0, 0, 80)
            )
            self.setPen(pen)
            self.setZValue(
                self.zValue() + 1 if self.isSelected() else self.zValue() - 1
            )

        return super(EffectItem, self).itemChange(change, value)


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

        shading_poly = QtWidgets.QGraphicsPolygonItem(
            shading_poly_f, parent=self)
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
        super(NestedItem, self).mouseDoubleClickEvent(event)
        self.scene().views()[0].open_stack.emit(self.item)

    def keyPressEvent(self, key_event):
        super(NestedItem, self).keyPressEvent(key_event)
        key = key_event.key()

        if key == QtCore.Qt.Key_Return:
            self.scene().views()[0].open_stack.emit(self.item)


class Track(QtWidgets.QGraphicsRectItem):

    def __init__(self, track, *args, **kwargs):
        super(Track, self).__init__(*args, **kwargs)
        self.track = track

        self.setBrush(QtGui.QBrush(QtGui.QColor(43, 52, 59, 255)))
        self._populate()

    def _populate(self):
        track_map = self.track.range_of_all_children()
        for n, item in enumerate(self.track):
            timeline_range = track_map[item]

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
                otio.opentime.to_seconds(timeline_range.start_time) *
                TIME_MULTIPLIER
            )
            new_item.counteract_zoom()


class Marker(QtWidgets.QGraphicsPolygonItem):

    def __init__(self, marker, *args, **kwargs):
        self.item = marker

        poly = QtGui.QPolygonF()
        poly.append(QtCore.QPointF(0.5 * MARKER_SIZE, -0.5 * MARKER_SIZE))
        poly.append(QtCore.QPointF(0.5 * MARKER_SIZE, 0.5 * MARKER_SIZE))
        poly.append(QtCore.QPointF(0, MARKER_SIZE))
        poly.append(QtCore.QPointF(-0.5 * MARKER_SIZE, 0.5 * MARKER_SIZE))
        poly.append(QtCore.QPointF(-0.5 * MARKER_SIZE, -0.5 * MARKER_SIZE))
        super(Marker, self).__init__(poly, *args, **kwargs)

        self.setFlags(QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.setBrush(
            QtGui.QBrush(QtGui.QColor(121, 212, 177, 255))
        )

    def paint(self, *args, **kwargs):
        new_args = [args[0],
                    QtWidgets.QStyleOptionGraphicsItem()] + list(args[2:])
        super(Marker, self).paint(*new_args, **kwargs)

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemSelectedHasChanged:
            self.setPen(
                QtGui.QColor(0, 255, 0, 255) if self.isSelected()
                else QtGui.QColor(0, 0, 0, 255)
            )
        return super(Marker, self).itemChange(change, value)

    def counteract_zoom(self, zoom_level=1.0):
        self.setTransform(QtGui.QTransform.fromScale(zoom_level, 1.0))


class TimeSlider(QtWidgets.QGraphicsRectItem):

    def __init__(self, *args, **kwargs):
        super(TimeSlider, self).__init__(*args, **kwargs)
        self.setBrush(QtGui.QBrush(QtGui.QColor(64, 78, 87, 255)))
        pen = QtGui.QPen()
        pen.setWidth(0)
        self.setPen(pen)
        self._ruler = None

    def mousePressEvent(self, mouse_event):
        pos = self.mapToScene(mouse_event.pos())
        self._ruler.setPos(QtCore.QPointF(pos.x(),
                                          TIME_SLIDER_HEIGHT - MARKER_SIZE))
        self._ruler.update_frame()

        super(TimeSlider, self).mousePressEvent(mouse_event)

    def add_ruler(self, ruler):
        self._ruler = ruler


class FrameNumber(QtWidgets.QGraphicsRectItem):

    def __init__(self, text, position, *args, **kwargs):
        super(FrameNumber, self).__init__(*args, **kwargs)
        self.frameNumber = QtWidgets.QGraphicsSimpleTextItem(self)
        self.frameNumber.setText("%s" % text)
        self.setBrush(
            QtGui.QBrush(QtGui.QColor(5, 55, 0, 255))
        )
        self.setPen(
            QtCore.Qt.NoPen
        )
        self.frameNumber.setBrush(
            QtGui.QBrush(QtGui.QColor(25, 255, 10, 255))
        )
        # if position < 0 then the frameNumber will appear on the left side
        # of the ruler
        self.position = position

    def setText(self, txt, highlight=False):
        if txt:
            self.show()
            self.frameNumber.setText("%s" % txt)
            rect = self.frameNumber.boundingRect()
            self.setRect(self.frameNumber.boundingRect())
            if highlight:
                # paint with a different color when on
                # the first frame of a clip
                self.setBrush(
                    QtGui.QBrush(QtGui.QColor(55, 5, 0, 120))
                )
                self.frameNumber.setBrush(
                    QtGui.QBrush(QtGui.QColor(255, 250, 250, 255))
                )
            else:
                self.frameNumber.setBrush(
                    QtGui.QBrush(QtGui.QColor(25, 255, 10, 255))
                )
                self.setBrush(
                    QtGui.QBrush(QtGui.QColor(5, 55, 0, 120))
                )
            if self.position < 0:
                self.setX(-rect.width()-2)
            else:
                self.setX(2)
        else:
            self.hide()


class Ruler(QtWidgets.QGraphicsPolygonItem):
    #  @TODO pending on Global Space implementation
    #  ("external_space", "External Space"),
    time_space = OrderedDict([("media_space", "Media Space"),
                              ("trimmed_space", "Trimmed Space")])

    time_space_default = "media_space"

    def __init__(self, height, composition, *args, **kwargs):

        poly = QtGui.QPolygonF()
        poly.append(QtCore.QPointF(0.5 * RULER_SIZE, -0.5 * RULER_SIZE))
        poly.append(QtCore.QPointF(0.5 * RULER_SIZE, 0.5 * RULER_SIZE))
        poly.append(QtCore.QPointF(0, RULER_SIZE))
        poly.append(QtCore.QPointF(0, height))
        poly.append(QtCore.QPointF(0, RULER_SIZE))
        poly.append(QtCore.QPointF(-0.5 * RULER_SIZE, 0.5 * RULER_SIZE))
        poly.append(QtCore.QPointF(-0.5 * RULER_SIZE, -0.5 * RULER_SIZE))
        super(Ruler, self).__init__(poly, *args, **kwargs)

        # to retrieve tracks and its children
        self.composition = composition
        self.setBrush(
            QtGui.QBrush(QtGui.QColor(50, 255, 20, 255))
        )

        self.setAcceptHoverEvents(True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsFocusable, True)

        self.labels = list()
        self._time_space = self.time_space_default
        self._bounded_data = namedtuple("bounded_data", ["f",
                                                         "is_bounded",
                                                         "is_tail",
                                                         "is_head"])
        self.init()

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu()
        for name, label in self.time_space.items():
            callback = lambda name_str = name: \
                self.set_time_space_callback(name_str)
            menu.addAction(label, callback)
        menu.exec_(event.screenPos())

        super(Ruler, self).contextMenuEvent(event)

    def set_time_space_callback(self, time_space):
        self._time_space = time_space
        self.update_frame()

    def mouseMoveEvent(self, mouse_event):
        pos = self.mapToScene(mouse_event.pos())
        self.setPos(QtCore.QPointF(pos.x(),
                                   TIME_SLIDER_HEIGHT - MARKER_SIZE))
        self.update_frame()

        super(Ruler, self).mouseMoveEvent(mouse_event)

    def hoverEnterEvent(self, event):
        self.setSelected(True)
        super(Ruler, self).hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.setSelected(False)
        super(Ruler, self).hoverLeaveEvent(event)

    def init(self):
        for track_item in self.composition.items():
            if isinstance(track_item, Track):
                frameNumber_tail = FrameNumber("", position=-1)
                frameNumber_tail.setParentItem(self)
                frameNumber_head = FrameNumber("", position=1)
                frameNumber_head.setParentItem(self)
                frameNumber_tail.setY(track_item.pos().y())
                frameNumber_head.setY(track_item.pos().y())
                items = list()
                for item in track_item.childItems():
                    if not (isinstance(item, ClipItem) or
                            isinstance(item, NestedItem)):
                        continue
                    items.append(item)
                items.sort(key=lambda x: x.x())
                self.labels.append([items, frameNumber_tail, frameNumber_head])

        self.update_frame()

    def setParentItem(self, timeSlider):
        '''
        subclass in order to add the rule to the timeSlider item.
        '''
        timeSlider.add_ruler(self)
        super(Ruler, self).setParentItem(timeSlider)

    def map_to_time_space(self, item):
        '''
        Temporary implementation.
        @TODO: modify this function once Time Coordinates Spaces
        feature is implemented.
        '''

        is_bounded = False
        is_head = False
        is_tail = False
        f = "-?-"

        ratio = (self.x() - item.x()) / float(item.rect().width())

        # The 'if' condition should be : ratio < 0 or ration >= 1
        # However, we are cheating in order to display the last frame of
        # a clip (tail) and the first frame of the following clip (head)
        # when we know that we cannot be on 2 frames at the same time
        if ratio < 0 or ratio > 1:
            return self._bounded_data(f, is_bounded, is_tail, is_head)

        is_bounded = True
        trimmed_range = item.item.trimmed_range()
        duration = trimmed_range.duration.value
        start_time = trimmed_range.start_time.value

        f_nb = ratio * duration + start_time
        if self._time_space == "trimmed_space":
            f = ratio * duration
        elif self._time_space == "media_space":
            f = duration * ratio + start_time

        f = math.floor(f)
        f_nb = math.floor(f_nb)
        if f_nb == start_time:
            is_head = True

        last_item_frame = start_time + duration - 1
        if f_nb >= (last_item_frame):
            is_tail = True
            # As we cheated in the first place by saying that the ruler
            # was within the boundary of this item when it is not...
            if ratio == 1.0:
                f -= 1

        return self._bounded_data(f, is_bounded, is_tail, is_head)

    def update_frame(self):

        for track_widgets, frameNumber_tail, frameNumber_head in self.labels:
            f_tail = ""
            f_head = ""
            highlight_head = False
            for item_widget in track_widgets:
                bounded_data = self.map_to_time_space(item_widget)
                # check if ruler is within an item boundary
                # in other word, start_frame <= ruler < end_frame
                if not bounded_data.is_bounded:
                    continue
                f = int(round(bounded_data.f))
                if bounded_data.is_head:
                    highlight_head = True
                if bounded_data.is_tail:
                    f_tail = f
                else:
                    f_head = f
                    break
            frameNumber_head.setText("%s" % f_head, highlight_head)
            frameNumber_tail.setText("%s" % f_tail)

    def snap(self, direction, scene_width):
        ruler_pos = self.x() + direction
        closest_left = scene_width - ruler_pos
        closest_right = 0 - ruler_pos
        move_to_item = None

        for track_widgets, frameNumber_tail, frameNumber_head in self.labels:
            for item in track_widgets:
                d = item.x() - ruler_pos
                if direction > 0 and d > 0 and d < closest_left:
                    closest_left = d
                    move_to_item = item
                elif direction < 0 and d < 0 and d > closest_right:
                    closest_right = d
                    move_to_item = item

        if move_to_item:
            self.setX(move_to_item.x())
            self.update_frame()

    def paint(self, *args, **kwargs):
        new_args = [args[0],
                    QtWidgets.QStyleOptionGraphicsItem()] + list(args[2:])
        super(Ruler, self).paint(*new_args, **kwargs)

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemSelectedHasChanged:
            self.setPen(
                QtGui.QColor(0, 255, 0, 255) if self.isSelected()
                else QtGui.QColor(0, 0, 0, 255)
            )
        return super(Ruler, self).itemChange(change, value)

    def counteract_zoom(self, zoom_level=1.0):
        self.setTransform(QtGui.QTransform.fromScale(zoom_level, 1.0))


class CompositionWidget(QtWidgets.QGraphicsScene):

    def __init__(self, composition, *args, **kwargs):
        super(CompositionWidget, self).__init__(*args, **kwargs)
        self.composition = composition
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(33, 33, 33)))

        self._adjust_scene_size()
        self._add_tracks()
        self._add_time_slider()
        self._add_markers()
        self._ruler = self._add_ruler()

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
        elif isinstance(self.composition, otio.schema.Track):
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
            TIME_SLIDER_HEIGHT +
            (
                int(has_video_tracks and has_audio_tracks) *
                MEDIA_TYPE_SEPARATOR_HEIGHT
            ) +
            len(self.composition) * TRACK_HEIGHT
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
        self._time_slider = TimeSlider(scene_rect)
        self.addItem(self._time_slider)

    def _add_track(self, track, y_pos):
        scene_rect = self.sceneRect()
        rect = QtCore.QRectF(0, 0, scene_rect.width() * 10, TRACK_HEIGHT)
        new_track = Track(track, rect)
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
                    ) and
                    list(t)
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
            TIME_SLIDER_HEIGHT +
            len(video_tracks) * TRACK_HEIGHT +
            int(
                bool(video_tracks) and bool(audio_tracks)
            ) * MEDIA_TYPE_SEPARATOR_HEIGHT
        )

        for i, track in enumerate(audio_tracks):
            self._add_track(track, audio_tracks_top + i * TRACK_HEIGHT)

        for i, track in enumerate(video_tracks):
            self._add_track(track, video_tracks_top + i * TRACK_HEIGHT)

    def _add_markers(self):
        for m in self.composition.markers:
            marker = Marker(m, None)
            marker.setX(
                otio.opentime.to_seconds(m.marked_range.start_time) *
                TIME_MULTIPLIER
            )
            marker.setY(TIME_SLIDER_HEIGHT - MARKER_SIZE)
            marker.setParentItem(self._time_slider)
            marker.counteract_zoom()

    def _add_ruler(self):
        scene_rect = self.sceneRect()
        ruler = Ruler(scene_rect.height(), composition=self)
        ruler.setParentItem(self._time_slider)
        ruler.setX(scene_rect.width() / 2)
        ruler.setY(TIME_SLIDER_HEIGHT - MARKER_SIZE)

        ruler.counteract_zoom()
        return ruler

    def get_ruler(self):
        return self._ruler


class CompositionView(QtWidgets.QGraphicsView):

    open_stack = QtCore.Signal(otio.schema.Stack)
    selection_changed = QtCore.Signal(otio.core.SerializableObject)

    def __init__(self, stack, *args, **kwargs):
        super(CompositionView, self).__init__(*args, **kwargs)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setScene(CompositionWidget(stack, parent=self))
        self.setAlignment((QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop))
        self.setStyleSheet('border: 0px;')
        self.scene().selectionChanged.connect(self.parse_selection_change)

    def parse_selection_change(self):
        selection = self.scene().selectedItems()
        if not selection:
            return
        # Exclude ruler from selection
        for item in selection:
            if isinstance(item, Ruler):
                continue
            self.selection_changed.emit(item.item)
            break

    def mousePressEvent(self, mouse_event):
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        self.setDragMode(
            QtWidgets.QGraphicsView.ScrollHandDrag
            if modifiers == QtCore.Qt.AltModifier
            else QtWidgets.QGraphicsView.NoDrag
        )
        self.setInteractive(not modifiers == QtCore.Qt.AltModifier)

        super(CompositionView, self).mousePressEvent(mouse_event)

    def mouseReleaseEvent(self, mouse_event):
        super(CompositionView, self).mouseReleaseEvent(mouse_event)
        self.setDragMode(QtWidgets.QGraphicsView.NoDrag)

    def wheelEvent(self, event):
        scale_by = 1.0 + float(event.delta()) / 1000
        self.scale(scale_by, 1)
        zoom_level = 1.0 / self.matrix().m11()

        # some items we do want to keep the same visual size. So we need to
        # inverse the effect of the zoom
        items_to_scale = [
            i for i in self.scene().items()
            if isinstance(i, _BaseItem) or
            isinstance(i, Marker) or
            isinstance(i, Ruler)
        ]

        for item in items_to_scale:
            item.counteract_zoom(zoom_level)

    def _get_first_item(self):
        newXpos = 0
        newYpos = TIME_SLIDER_HEIGHT

        newPosition = QtCore.QPointF(newXpos, newYpos)

        return self.scene().itemAt(newPosition, QtGui.QTransform())

    def _get_left_item(self, curSelectedItem):
        curItemXpos = curSelectedItem.pos().x()

        if curSelectedItem.parentItem():
            curTrackYpos = curSelectedItem.parentItem().pos().y()

            newXpos = curItemXpos - 1
            newYpos = curTrackYpos

            if newXpos < 0:
                newXpos = 0
        else:
            newXpos = curItemXpos
            newYpos = curSelectedItem.y()

        newPosition = QtCore.QPointF(newXpos, newYpos)

        return self.scene().itemAt(newPosition, QtGui.QTransform())

    def _get_right_item(self, curSelectedItem):
        curItemXpos = curSelectedItem.pos().x()

        if curSelectedItem.parentItem():
            curTrackYpos = curSelectedItem.parentItem().pos().y()

            newXpos = curItemXpos + curSelectedItem.rect().width()
            newYpos = curTrackYpos
        else:
            newXpos = curItemXpos
            newYpos = curSelectedItem.y()

        newPosition = QtCore.QPointF(newXpos, newYpos)

        return self.scene().itemAt(newPosition, QtGui.QTransform())

    def _get_up_item(self, curSelectedItem):
        curItemXpos = curSelectedItem.pos().x()

        if curSelectedItem.parentItem():
            curTrackYpos = curSelectedItem.parentItem().pos().y()

            newXpos = curItemXpos
            newYpos = curTrackYpos - TRACK_HEIGHT

            newSelectedItem = self.scene().itemAt(
                QtCore.QPointF(
                    newXpos,
                    newYpos
                ),
                QtGui.QTransform()
            )

            if not newSelectedItem or isinstance(newSelectedItem, Track):
                newYpos = newYpos - TRANSITION_HEIGHT
        else:
            newXpos = curItemXpos
            newYpos = curSelectedItem.y()

        newPosition = QtCore.QPointF(newXpos, newYpos)

        return self.scene().itemAt(newPosition, QtGui.QTransform())

    def _get_down_item(self, curSelectedItem):
        curItemXpos = curSelectedItem.pos().x()

        if curSelectedItem.parentItem():
            curTrackYpos = curSelectedItem.parentItem().pos().y()
            newXpos = curItemXpos
            newYpos = curTrackYpos + TRACK_HEIGHT

            newSelectedItem = self.scene().itemAt(
                QtCore.QPointF(
                    newXpos,
                    newYpos
                ),
                QtGui.QTransform()
            )

            if not newSelectedItem or isinstance(newSelectedItem, Track):
                newYpos = newYpos + TRANSITION_HEIGHT

            if newYpos < TRACK_HEIGHT:
                newYpos = TRACK_HEIGHT
        else:
            newXpos = curItemXpos
            newYpos = MARKER_SIZE + TIME_SLIDER_HEIGHT + 1
            newYpos = TIME_SLIDER_HEIGHT
        newPosition = QtCore.QPointF(newXpos, newYpos)

        return self.scene().itemAt(newPosition, QtGui.QTransform())

    def _deselect_all_items(self):
        if self.scene().selectedItems:
            for selectedItem in self.scene().selectedItems():
                selectedItem.setSelected(False)

    def _select_new_item(self, newSelectedItem):
        # Check for text item
        # Text item shouldn't be selected,
        # maybe a bug in the population of timeline.
        if isinstance(newSelectedItem, QtWidgets.QGraphicsSimpleTextItem):
            newSelectedItem = newSelectedItem.parentItem()

        # Validate new item for edge cases
        # If valid, set selected
        if (
            not isinstance(newSelectedItem, Track) and newSelectedItem
        ):
            self._deselect_all_items()
            newSelectedItem.setSelected(True)
            self.centerOn(newSelectedItem)

    def _get_new_item(self, key_event, curSelectedItem):
        key = key_event.key()
        modifier = key_event.modifiers()
        if key in (
                QtCore.Qt.Key_Left,
                QtCore.Qt.Key_Right,
                QtCore.Qt.Key_Up,
                QtCore.Qt.Key_Down,
                QtCore.Qt.Key_Return,
                QtCore.Qt.Key_Enter
        ) and not (modifier & QtCore.Qt.ControlModifier):
            if key == QtCore.Qt.Key_Left:
                newSelectedItem = self._get_left_item(curSelectedItem)
            elif key == QtCore.Qt.Key_Right:
                newSelectedItem = self._get_right_item(curSelectedItem)
            elif key == QtCore.Qt.Key_Up:
                newSelectedItem = self._get_up_item(curSelectedItem)
            elif key == QtCore.Qt.Key_Down:
                newSelectedItem = self._get_down_item(curSelectedItem)
            elif key in [QtCore.Qt.Key_Return, QtCore.Qt.Key_Return]:
                if isinstance(curSelectedItem, NestedItem):
                    curSelectedItem.keyPressEvent(key_event)
                    newSelectedItem = None
        else:
            newSelectedItem = None

        return newSelectedItem

    def keyPressEvent(self, key_event):
        super(CompositionView, self).keyPressEvent(key_event)
        self.setInteractive(True)

        # No item selected, so select the first item
        if len(self.scene().selectedItems()) <= 0:
            newSelectedItem = self._get_first_item()
        # Based on direction key, select new selected item
        else:
            curSelectedItem = self.scene().selectedItems()[0]

            # Check to see if the current selected item is a rect item
            # If current selected item is not a rect, then extra tests
            # are needed.
            if not isinstance(curSelectedItem, QtWidgets.QGraphicsRectItem):
                if curSelectedItem.parentItem():
                    curSelectedItem = curSelectedItem.parentItem()

            newSelectedItem = self._get_new_item(key_event, curSelectedItem)
            self._keyPress_frame_all(key_event)
            self._snap(key_event, curSelectedItem)
        if newSelectedItem:
            self._select_new_item(newSelectedItem)

    def _snap(self, key_event, curSelectedItem):
        key = key_event.key()
        modifier = key_event.modifiers()
        if key in (
                QtCore.Qt.Key_Left,
                QtCore.Qt.Key_Right,
        ) and (modifier & QtCore.Qt.ControlModifier):
            direction = 0
            if key == QtCore.Qt.Key_Left:
                direction = -1.0
            elif key == QtCore.Qt.Key_Right:
                direction = 1.0
            if direction:
                ruler = self.scene().get_ruler()
                ruler.snap(direction=direction,
                           scene_width=self.sceneRect().width())
                self.ensureVisible(ruler)

    def _keyPress_frame_all(self, key_event):
        key = key_event.key()
        modifier = key_event.modifiers()
        if key == QtCore.Qt.Key_F and (modifier & QtCore.Qt.ControlModifier):
            self.frame_all()

    def frame_all(self):
        zoom_level = 1.0 / self.matrix().m11()
        scaleFactor = self.size().width() / self.sceneRect().width()
        self.scale(scaleFactor * zoom_level, 1)
        zoom_level = 1.0 / self.matrix().m11()

        items_to_scale = [
            i for i in self.scene().items()
            if (
                isinstance(i, _BaseItem) or
                isinstance(i, Marker) or
                isinstance(i, Ruler)
            )
        ]
        # some items we do want to keep the same visual size. So we need to
        # inverse the effect of the zoom

        for item in items_to_scale:
            item.counteract_zoom(zoom_level)


class Timeline(QtWidgets.QTabWidget):

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
            button = self.tabBar().tabButton(0, QtWidgets.QTabBar.RightSide)
            if button:
                button.resize(0, 0)

        new_stack.open_stack.connect(self.add_stack)
        new_stack.selection_changed.connect(self.selection_changed)
        self.setCurrentIndex(self.count() - 1)
        self.frame_all()

    def frame_all(self):
        self.currentWidget().frame_all()
