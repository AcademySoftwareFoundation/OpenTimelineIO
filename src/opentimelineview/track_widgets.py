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

from PySide2 import QtGui, QtCore, QtWidgets
import opentimelineio as otio


TIME_SLIDER_HEIGHT = 20
MEDIA_TYPE_SEPARATOR_HEIGHT = 5
TRACK_HEIGHT = 45
TRANSITION_HEIGHT = 10
TIME_MULTIPLIER = 25
LABEL_MARGIN = 5
MARKER_SIZE = 10
EFFECT_HEIGHT = (1.0 / 3.0) * TRACK_HEIGHT
HIGHLIGHT_WIDTH = 5


class BaseItem(QtWidgets.QGraphicsRectItem):

    def __init__(self, item, timeline_range, *args, **kwargs):
        super(BaseItem, self).__init__(*args, **kwargs)
        self.item = item
        self.timeline_range = timeline_range

        # List of otio.core.SerializableObject
        # it excludes decorator widgets as QLabel ...
        self._otio_sub_items = list()

        self.setFlags(QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.setBrush(
            QtGui.QBrush(QtGui.QColor(180, 180, 180, 255))
        )

        pen = QtGui.QPen()
        pen.setWidth(0)
        pen.setCosmetic(True)
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
        super(BaseItem, self).paint(*new_args, **kwargs)

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemSelectedHasChanged:
            pen = self.pen()
            pen.setColor(
                QtGui.QColor(0, 255, 0, 255) if self.isSelected()
                else QtGui.QColor(0, 0, 0, 255)
            )
            pen.setWidth(HIGHLIGHT_WIDTH if self.isSelected() else 0)
            self.setPen(pen)
            self.setZValue(
                self.zValue() + 1 if self.isSelected() else self.zValue() - 1
            )
            self.parentItem().setZValue(
                self.parentItem().zValue() + 1 if self.isSelected() else
                self.parentItem().zValue() - 1
            )

        return super(BaseItem, self).itemChange(change, value)

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
            self._add_otio_sub_item(marker)

    def _add_effects(self):
        if not hasattr(self.item, "effects"):
            return
        if not self.item.effects:
            return
        effect = EffectItem(self.item.effects, self.rect())
        effect.setParentItem(self)
        self._add_otio_sub_item(effect)

    def _add_otio_sub_item(self, item):
        self._otio_sub_items.append(item)

    def get_otio_sub_items(self):
        return self._otio_sub_items

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


class GapItem(BaseItem):

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
            QtCore.QPointF(0, self.boundingRect().top()),
            QtCore.QPointF(0, self.boundingRect().bottom())
        )
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


class TransitionItem(BaseItem):

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


class ClipItem(BaseItem):

    def __init__(self, *args, **kwargs):
        super(ClipItem, self).__init__(*args, **kwargs)
        self.setBrush(QtGui.QBrush(QtGui.QColor(168, 197, 255, 255)))
        self.source_name_label.setText(self.item.name)


class NestedItem(BaseItem):

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
                                          TIME_SLIDER_HEIGHT -
                                          MARKER_SIZE))
        self._ruler.update_frame()

        super(TimeSlider, self).mousePressEvent(mouse_event)

    def add_ruler(self, ruler):
        self._ruler = ruler
