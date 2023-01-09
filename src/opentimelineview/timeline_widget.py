# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

try:
    from PySide6 import QtGui, QtCore, QtWidgets
except ImportError:
    from PySide2 import QtGui, QtCore, QtWidgets
from collections import OrderedDict, namedtuple

import opentimelineio as otio
from . import (
    ruler_widget,
    track_widgets,
)


KEY_SYM = {
    QtCore.Qt.Key_Left: QtCore.Qt.Key_Right,
    QtCore.Qt.Key_Right: QtCore.Qt.Key_Left,
    QtCore.Qt.Key_Up: QtCore.Qt.Key_Down,
    QtCore.Qt.Key_Down: QtCore.Qt.Key_Up
}


def get_nav_menu_data():
    _nav_menu = namedtuple(
        "nav_menu",
        ["bitmask", "otioItem", "default", "exclusive"]
    )

    filter_dict = OrderedDict(
        [
            (
                "Clip",
                _nav_menu(0b00000001, track_widgets.ClipItem, True, False)
            ),
            (
                "Nested Clip",
                _nav_menu(0b00000010, track_widgets.NestedItem, True, False)
            ),
            (
                "Gap",
                _nav_menu(0b00000100, track_widgets.GapItem, True, False)
            ),
            (
                "Transition",
                _nav_menu(0b00001000, track_widgets.TransitionItem, True, False)
            ),
            (
                "Only with Marker",
                _nav_menu(0b00010000, track_widgets.Marker, False, True)
            ),
            (
                "Only with Effect",
                _nav_menu(0b00100000, track_widgets.EffectItem, False, True)
            ),
            # ("All", nav_menu(0b01000000, "None", False)) @TODO
        ]
    )
    return filter_dict


def get_filters(filter_dict, bitmask):
    filters = list()
    for item in filter_dict.values():
        if bitmask & item.bitmask:
            filters.append(item)
    return filters


def build_menu(navigation_menu):
    filter_dict = get_nav_menu_data()
    actions = list()
    for label, nav in filter_dict.items():
        if label == "Only with Marker":
            navigation_menu.addSeparator()

        action = navigation_menu.addAction(label)
        action.setCheckable(True)
        action.setChecked(nav.default)
        actions.append(action)

    return actions


def group_filters(bitmask):
    inclusive_filters = list()
    exclusive_filters = list()
    filter_dict = get_nav_menu_data()
    for item in get_filters(filter_dict, bitmask):
        if item.exclusive:
            exclusive_filters.append(item)
        else:
            inclusive_filters.append(item)
    return inclusive_filters, exclusive_filters


class CompositionWidget(QtWidgets.QGraphicsScene):

    def __init__(self, composition, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.composition = composition
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(33, 33, 33)))

        self._adjust_scene_size()
        self._add_tracks()
        self._add_time_slider()
        self._add_markers()
        self._ruler = self._add_ruler()

        self._data_cache = self._cache_tracks()

    def track_name_width(self):
        # Choose track name item from the longest track, since that track will
        # define the composition's scene width.
        width = track_widgets.TRACK_NAME_WIDGET_WIDTH
        longest_track = None
        max_end_time = 0

        for item in self.items():
            if isinstance(item, track_widgets.Track):
                track_range = item.track.trimmed_range_in_parent()
                end_time = track_range.end_time_inclusive().to_seconds()
                if end_time > max_end_time:
                    max_end_time = end_time
                    longest_track = item

        if longest_track is not None:
            if longest_track.track_name_item is not None:
                width = longest_track.track_name_item.rect().width()

        return width

    def _adjust_scene_size(self, zoom_level=1.0):
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
            track_widgets.TIME_SLIDER_HEIGHT +
            (
                int(has_video_tracks and has_audio_tracks) *
                track_widgets.MEDIA_TYPE_SEPARATOR_HEIGHT
            ) +
            len(self.composition) * track_widgets.TRACK_HEIGHT
        )

        self.setSceneRect(
            start_time * track_widgets.TIME_MULTIPLIER,
            0,
            duration * track_widgets.TIME_MULTIPLIER +
            self.track_name_width() * zoom_level,
            height
        )

    def counteract_zoom(self, zoom_level=1.0):
        # some items we do want to keep the same visual size. So we need to
        # inverse the effect of the zoom
        items_to_scale = [
            i for i in self.items()
            if (isinstance(i, (track_widgets.BaseItem, track_widgets.Marker,
                               ruler_widget.Ruler, track_widgets.TimeSlider)))
        ]

        for item in items_to_scale:
            item.counteract_zoom(zoom_level)

        self._adjust_scene_size(zoom_level)

    def _add_time_slider(self):
        scene_rect = self.sceneRect()
        scene_rect.setWidth(scene_rect.width() * 10)
        scene_rect.setHeight(track_widgets.TIME_SLIDER_HEIGHT)
        self._time_slider = track_widgets.TimeSlider(scene_rect)
        self.addItem(self._time_slider)
        # Make sure that the ruler is on top of the selected Track items
        self._time_slider.setZValue(float('inf'))

    def _add_track(self, track, y_pos):
        scene_rect = self.sceneRect()
        rect = QtCore.QRectF(0, 0, scene_rect.width() * 10,
                             track_widgets.TRACK_HEIGHT)
        new_track = track_widgets.Track(track, rect)
        self.addItem(new_track)
        new_track.setPos(scene_rect.x(), y_pos)

    def _add_tracks(self):
        video_tracks_top = track_widgets.TIME_SLIDER_HEIGHT
        audio_tracks_top = track_widgets.TIME_SLIDER_HEIGHT

        video_tracks = []
        audio_tracks = []
        other_tracks = []

        if isinstance(self.composition, otio.schema.Stack):
            video_tracks = [
                t for t in self.composition
                if t.kind == otio.schema.TrackKind.Video
            ]
            audio_tracks = [
                t for t in self.composition
                if t.kind == otio.schema.TrackKind.Audio
            ]
            video_tracks.reverse()

            other_tracks = [
                t for t in self.composition
                if (
                    t.kind not in (
                        otio.schema.TrackKind.Video,
                        otio.schema.TrackKind.Audio
                    )
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

        video_tracks_top = track_widgets.TIME_SLIDER_HEIGHT
        audio_tracks_top = (
            track_widgets.TIME_SLIDER_HEIGHT +
            len(video_tracks) * track_widgets.TRACK_HEIGHT +
            int(
                bool(video_tracks) and bool(audio_tracks)
            ) * track_widgets.MEDIA_TYPE_SEPARATOR_HEIGHT
        )

        for i, track in enumerate(audio_tracks):
            self._add_track(track, audio_tracks_top + i *
                            track_widgets.TRACK_HEIGHT)

        for i, track in enumerate(video_tracks):
            self._add_track(track, video_tracks_top + i *
                            track_widgets.TRACK_HEIGHT)

    def _add_markers(self):
        for m in self.composition.markers:
            marker = track_widgets.Marker(m, None)
            marker.setX(
                otio.opentime.to_seconds(m.marked_range.start_time) *
                track_widgets.TIME_MULTIPLIER
            )
            marker.setY(track_widgets.TIME_SLIDER_HEIGHT -
                        track_widgets.MARKER_SIZE)
            marker.setParentItem(self._time_slider)
            marker.counteract_zoom()

    def _add_ruler(self):
        scene_rect = self.sceneRect()
        ruler = ruler_widget.Ruler(scene_rect.height(), composition=self)
        ruler.setParentItem(self._time_slider)
        ruler.setX(scene_rect.width() / 2)
        ruler.setY(track_widgets.TIME_SLIDER_HEIGHT -
                   track_widgets.MARKER_SIZE)

        ruler.counteract_zoom()
        return ruler

    def get_ruler(self):
        return self._ruler

    def get_next_item(self, item, key):
        otio_item = item.item
        next_item = None
        if key in [QtCore.Qt.Key_Right, QtCore.Qt.Key_Left]:
            head, tail = otio_item.parent().neighbors_of(otio_item)
            next_item = head if key == QtCore.Qt.Key_Left else tail
        elif key in [QtCore.Qt.Key_Up, QtCore.Qt.Key_Down]:
            track = item.parentItem()
            if self._data_cache[track][key]:
                next_track = self._data_cache[track][key]
            else:
                # No more track in that direction.
                return item
            at_time = otio_item.trimmed_range_in_parent().start_time

            # If at_time is out of track_range, then get the latest item
            # in the track.
            at_time = min(at_time,
                          self._data_cache[next_track]["end_time_inclusive"])

            next_item = next_track.track.child_at_time(at_time)

        # need the widget, not the otio instance.
        if next_item:
            next_item = self._data_cache["map_to_widget"][next_item]

        return next_item

    def _get_closest_item(self, item, start_time, filters):
        next_item = item
        tail = self.get_next_item_filters(item, QtCore.Qt.Key_Right, filters)
        head = self.get_next_item_filters(item, QtCore.Qt.Key_Left, filters)

        # 3 cases
        # 1. tail and head are both valid => get the closest one
        if not tail == item and not head == item:
            tail_start_time = tail.item.trimmed_range_in_parent().start_time
            head_end_time = head.item.trimmed_range_in_parent().\
                end_time_inclusive()

            time_to_tail = tail_start_time - start_time
            time_to_head = start_time - head_end_time

            next_item = tail if time_to_tail < time_to_head else head

        # 2. only tail is valid
        elif not tail == item and head == item:
            next_item = tail

        # 3. only head is valid
        elif tail == item and not head == item:
            next_item = head

        return next_item

    def get_next_item_filters(self, item, key, filters):
        original_item = item
        next_item = None
        while not match_filters(next_item, filters):
            next_item = self.get_next_item(item, key)

            if key in [QtCore.Qt.Key_Up, QtCore.Qt.Key_Down] and \
               not match_filters(next_item, filters):
                start_time = item.item.trimmed_range_in_parent().start_time
                next_item = self._get_closest_item(next_item, start_time,
                                                   filters)

            if next_item is None or next_item == item:
                next_item = original_item
                break

            item = next_item

        return next_item

    def _cache_tracks(self):
        '''
        Create a doubly linked list to navigate from track to track:
            track->get_next_up & track->get_next_up
        "map_to_widget" : Create a map to retrieve the pyside widget from
        the otio item
        '''
        data_cache = dict()
        tracks = list()
        data_cache["map_to_widget"] = dict()
        for track_item in self.items():
            if not isinstance(track_item, track_widgets.Track):
                continue
            tracks.append(track_item)
            track_range = track_item.track.available_range()
            data_cache[track_item] = {QtCore.Qt.Key_Up: None,
                                      QtCore.Qt.Key_Down: None,
                                      "end_time_inclusive":
                                      track_range.end_time_inclusive()
                                      }

            for item in track_item.childItems():
                data_cache["map_to_widget"][item.item] = item

        tracks.sort(key=lambda y: y.pos().y())
        index_last_track = len(tracks) - 1
        for i, track_item in enumerate(tracks):
            data_cache[track_item][QtCore.Qt.Key_Up] = \
                tracks[i - 1] if i > 0 else None
            data_cache[track_item][QtCore.Qt.Key_Down] = \
                tracks[i + 1] if i < index_last_track else None

        return data_cache


def match_filters(item, filters=None):
    if not item:
        return None
    if filters is None:
        return item

    otio_children = list()
    if isinstance(item, track_widgets.BaseItem):
        otio_children = item.get_otio_sub_items()

    for filter in filters.exclusive:
        excl_item = [i for i in otio_children
                     if isinstance(i, filter.otioItem)]
        if not excl_item:
            return None

    for filter in filters.inclusive:
        if isinstance(item, filter.otioItem):
            return item

    return None


class CompositionView(QtWidgets.QGraphicsView):

    open_stack = QtCore.Signal(otio.schema.Stack)
    selection_changed = QtCore.Signal(otio.core.SerializableObject)

    def __init__(self, stack, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setScene(CompositionWidget(stack, parent=self))
        self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.setStyleSheet('border: 0px;')
        self.scene().selectionChanged.connect(self.parse_selection_change)
        self._navigation_filter = None
        self._last_item_cache = {"key": None, "item": None,
                                 "previous_item": None}

    def parse_selection_change(self):
        selection = self.scene().selectedItems()
        if not selection:
            return
        # Exclude ruler from selection
        for item in selection:
            if isinstance(item, ruler_widget.Ruler):
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

        super().mousePressEvent(mouse_event)

    def mouseReleaseEvent(self, mouse_event):
        super().mouseReleaseEvent(mouse_event)
        self.setDragMode(QtWidgets.QGraphicsView.NoDrag)

    def wheelEvent(self, event):
        try:
            # PySide6:
            # https://doc.qt.io/qtforpython/PySide6/QtGui/QWheelEvent.html
            delta_point = event.angleDelta()
            delta = delta_point.y()

        except AttributeError:
            # PySide2:
            # https://doc.qt.io/qtforpython-5/PySide2/QtGui/QWheelEvent.html
            delta = event.delta()

        scale_by = 1.0 + float(delta) / 1000
        self.scale(scale_by, 1)
        zoom_level = 1.0 / self.transform().m11()
        track_widgets.CURRENT_ZOOM_LEVEL = zoom_level
        self.scene().counteract_zoom(zoom_level)

    def _get_first_item(self):
        newXpos = 0
        newYpos = track_widgets.TIME_SLIDER_HEIGHT

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
            newYpos = curTrackYpos - track_widgets.TRACK_HEIGHT

            newSelectedItem = self.scene().itemAt(
                QtCore.QPointF(
                    newXpos,
                    newYpos
                ),
                QtGui.QTransform()
            )

            if (
                    not newSelectedItem
                    or isinstance(newSelectedItem, otio.schema.Track)
            ):
                newYpos = newYpos - track_widgets.TRANSITION_HEIGHT
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
            newYpos = curTrackYpos + track_widgets.TRACK_HEIGHT

            newSelectedItem = self.scene().itemAt(
                QtCore.QPointF(
                    newXpos,
                    newYpos
                ),
                QtGui.QTransform()
            )

            if (
                    not newSelectedItem
                    or isinstance(newSelectedItem, otio.schema.Track)
            ):
                newYpos = newYpos + track_widgets.TRANSITION_HEIGHT

            if newYpos < track_widgets.TRACK_HEIGHT:
                newYpos = track_widgets.TRACK_HEIGHT
        else:
            newXpos = curItemXpos
            newYpos = (
                track_widgets.MARKER_SIZE + track_widgets.TIME_SLIDER_HEIGHT + 1
            )
            newYpos = track_widgets.TIME_SLIDER_HEIGHT
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
            not isinstance(newSelectedItem, track_widgets.Track) and
            newSelectedItem
        ):
            self._deselect_all_items()
            newSelectedItem.setSelected(True)
            self.centerOn(newSelectedItem)

    def _get_new_item(self, key_event, curSelectedItem):
        key = key_event.key()
        modifier = key_event.modifiers()
        if not (key in (
                QtCore.Qt.Key_Left,
                QtCore.Qt.Key_Right,
                QtCore.Qt.Key_Up,
                QtCore.Qt.Key_Down,
                QtCore.Qt.Key_Return,
                QtCore.Qt.Key_Enter
        ) and not (modifier & QtCore.Qt.ControlModifier)):
            return None

        if key in [QtCore.Qt.Key_Left, QtCore.Qt.Key_Right,
                   QtCore.Qt.Key_Up, QtCore.Qt.Key_Down]:

            # check if last key was the opposite direction of current one
            if KEY_SYM[key] == self._last_item_cache["key"] and \
               curSelectedItem == self._last_item_cache["item"] and \
               not curSelectedItem == self._last_item_cache["previous_item"]:
                newSelectedItem = self._last_item_cache["previous_item"]
            else:
                filters = self.get_filters()
                # make sure that the selected item is a BaseItem
                while (not
                       isinstance(curSelectedItem, track_widgets.BaseItem) and
                       curSelectedItem):
                    curSelectedItem = curSelectedItem.parentItem()
                if not curSelectedItem:
                    return None

                newSelectedItem = self.scene().get_next_item_filters(
                    curSelectedItem,
                    key,
                    filters
                )

            # self._last_item_cache["item"] = curSelectedItem
            self._last_item_cache["item"] = newSelectedItem
            self._last_item_cache["previous_item"] = curSelectedItem
            self._last_item_cache["key"] = key
        elif key in [QtCore.Qt.Key_Return, QtCore.Qt.Key_Return]:
            if isinstance(curSelectedItem, track_widgets.NestedItem):
                curSelectedItem.keyPressEvent(key_event)
                newSelectedItem = None

        return newSelectedItem

    def keyPressEvent(self, key_event):
        super().keyPressEvent(key_event)
        self.setInteractive(True)

        # Remove ruler_widget.Ruler instance from selection
        selections = [
            x for x in self.scene().selectedItems()
            if not isinstance(x, ruler_widget.Ruler)
        ]

        # Based on direction key, select new selected item
        if not selections:
            newSelectedItem = self._get_first_item()
        # No item selected, so select the first item
        else:
            curSelectedItem = selections[0]

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
        self.resetTransform()
        track_widgets.CURRENT_ZOOM_LEVEL = 1.0
        self.scene().counteract_zoom()

        track_name_width = self.scene().track_name_width()
        view_width = self.size().width() - track_name_width
        scene_width = self.sceneRect().width() - track_name_width
        if not view_width or not scene_width:
            # Prevent zero division errors
            return

        scale_by = view_width / scene_width
        self.scale(scale_by, 1)
        zoom_level = 1.0 / self.transform().m11()
        track_widgets.CURRENT_ZOOM_LEVEL = zoom_level
        self.scene().counteract_zoom(zoom_level)

    def navigationfilter_changed(self, bitmask):
        '''
        Update the navigation filter according to the filters checked in the
        navigation menu. Reset _last_item_cache
        '''
        nav_d = namedtuple("navigation_filter", ["inclusive", "exclusive"])
        incl_filter, excl_filter = group_filters(bitmask)
        self._navigation_filter = nav_d(incl_filter, excl_filter)
        self._last_item_cache = {"key": None, "item": None,
                                 "previous_item": None}

    def get_filters(self):
        return self._navigation_filter


class Timeline(QtWidgets.QTabWidget):

    selection_changed = QtCore.Signal(otio.core.SerializableObject)
    navigationfilter_changed = QtCore.Signal(int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
        """Open a tab for the stack or go to it if already present"""

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
        self.navigationfilter_changed.connect(
            new_stack.navigationfilter_changed
        )
        self.setCurrentIndex(self.count() - 1)
        self.frame_all()

    def frame_all(self):
        if self.currentWidget():
            self.currentWidget().frame_all()
