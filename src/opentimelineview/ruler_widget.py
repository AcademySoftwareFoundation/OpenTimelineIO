# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

try:
    from PySide6 import QtGui, QtCore, QtWidgets
except ImportError:
    from PySide2 import QtGui, QtCore, QtWidgets
import collections
import math
from . import track_widgets

RULER_SIZE = 10


class FrameNumber(QtWidgets.QGraphicsRectItem):

    def __init__(self, text, position, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
                self.setX(-rect.width() - 2)
            else:
                self.setX(2)
        else:
            self.hide()


class Ruler(QtWidgets.QGraphicsPolygonItem):
    #  @TODO pending on Global Space implementation
    #  ("external_space", "External Space"),
    time_space = collections.OrderedDict([("media_space", "Media Space"),
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
        super().__init__(poly, *args, **kwargs)

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
        self._bounded_data = collections.namedtuple("bounded_data",
                                                    ["f",
                                                     "is_bounded",
                                                     "is_tail",
                                                     "is_head"])
        self.init()

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu()
        for name, label in self.time_space.items():
            def __callback():
                self.set_time_space_callback(name)
            menu.addAction(label, __callback)
        menu.exec_(event.screenPos())

        super().contextMenuEvent(event)

    def set_time_space_callback(self, time_space):
        self._time_space = time_space
        self.update_frame()

    def mouseMoveEvent(self, mouse_event):
        pos = self.mapToScene(mouse_event.pos())
        self.setPos(QtCore.QPointF(max(pos.x() - track_widgets.CURRENT_ZOOM_LEVEL *
                                       track_widgets.TRACK_NAME_WIDGET_WIDTH, 0),
                                   track_widgets.TIME_SLIDER_HEIGHT -
                                   track_widgets.MARKER_SIZE))
        self.update_frame()

        super().mouseMoveEvent(mouse_event)

    def mouseReleaseEvent(self, mouse_event):
        self.setSelected(False)
        super().mouseReleaseEvent(mouse_event)

    def hoverEnterEvent(self, event):
        self.setSelected(True)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.setSelected(False)
        super().hoverLeaveEvent(event)

    def init(self):
        for track_item in self.composition.items():
            if isinstance(track_item, track_widgets.Track):
                frameNumber_tail = FrameNumber("", position=-1)
                frameNumber_tail.setParentItem(self)
                frameNumber_head = FrameNumber("", position=1)
                frameNumber_head.setParentItem(self)
                frameNumber_tail.setY(track_item.pos().y())
                frameNumber_head.setY(track_item.pos().y())
                items = list()
                for item in track_item.childItems():
                    if not (isinstance(item, track_widgets.ClipItem) or
                            isinstance(item, track_widgets.NestedItem)):
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
        super().setParentItem(timeSlider)

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
        ratio = -1.0
        width = float(item.rect().width())

        if width > 0.0:
            ratio = (self.x() - item.x() +
                     track_widgets.CURRENT_ZOOM_LEVEL *
                     track_widgets.TRACK_NAME_WIDGET_WIDTH) / width
        else:
            print(f"Warning: zero width item: {item}.")

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

        for tw, frameNumber_tail, frameNumber_head in self.labels:
            f_tail = ""
            f_head = ""
            highlight_head = False
            for item_widget in tw:
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

        for tw, frameNumber_tail, frameNumber_head in self.labels:
            for item in tw:
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
        super().paint(*new_args, **kwargs)

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemSelectedHasChanged:
            self.setPen(
                QtGui.QColor(0, 255, 0, 255) if self.isSelected()
                else QtGui.QColor(0, 0, 0, 255)
            )
        return super().itemChange(change, value)

    def counteract_zoom(self, zoom_level=1.0):
        self.setTransform(QtGui.QTransform.fromScale(zoom_level, 1.0))
