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

"""OpenTimelineIO Final Cut Pro 7 XML Adapter."""

import collections
import functools
import itertools
import math
import os
from xml.etree import cElementTree
from xml.dom import minidom

# urlparse's name changes in Python 3
try:
    # Python 2.7
    import urlparse as urllib_parse
except ImportError:
    # Python 3
    import urllib.parse as urllib_parse

# Same with the ABC classes from collections
try:
    # Python 3
    from collections.abc import Mapping
except ImportError:
    # Python 2.7
    from collections import Mapping

import opentimelineio as otio

META_NAMESPACE = 'fcp_xml'  # namespace to use for metadata


"""
Adapter TODOs:
    - Support start timecode on sequences
    - Support top-level objects other than sequences: project, bin, clip
"""

# ---------
# utilities
# ---------


class _Context(Mapping):
    """
    An inherited value context.

    In FCP XML there is a concept of inheritance down the element heirarchy.
    For instance, a ``clip`` element may not specify the ``rate`` locally, but
    instead inherit it from the parent ``track`` element.

    This object models that as a stack of elements. When a value needs to be
    queried from the context, it will be gathered by walking from the top of
    the stack until the value is found.

    For example, to find the ``rate`` element as an immediate child most
    appropriate to the current context, you would do something like::
        ``my_current_context["./rate"]``

    This object can be thought of as immutable. You get a new context when you
    push an element. This prevents inadvertant tampering with parent contexts
    that may be used at levels above.

    This DOES NOT support ``id`` attribute dereferencing, please make sure to
    do that prior to using this structure.

    .. seealso:: https://developer.apple.com/library/archive/documentation\
            /AppleApplications/Reference/FinalCutPro_XML/Basics/Basics.html#\
            //apple_ref/doc/uid/TP30001154-TPXREF102
    """

    def __init__(self, element=None, parent_elements=None):
        if parent_elements is not None:
            self.elements = parent_elements[:]
        else:
            self.elements = []

        if element is not None:
            self.elements.append(element)

    def _all_keys(self):
        """
        Returns a set of all the keys available in the context stack.
        """
        return set(
            itertools.chain.fromiterable(e.keys() for e in self.elements)
        )

    def __getitem__(self, key):
        # Walk down the contexts until the item is found
        for element in reversed(self.elements):
            found_element = element.find(key)
            if found_element is not None:
                return found_element

        raise KeyError(key)

    def __iter__(self):
        # This is unlikely to be used, so we'll do it the expensive way
        return iter(self._all_keys)

    def __len__(self):
        # This is unlikely to be used, so we'll do it the expensive way
        return len(self._all_keys)

    def context_pushing_element(self, element):
        """
        Pushes an element to the top of the stack.

        :param element: Element to push to the stack.
        :return: The new context with the provided element pushed to the top
            of the stack.
        :raises: :class:`ValueError` if the element is already in the stack.
        """
        for context_element in self.elements:
            if context_element == element:
                raise ValueError(
                    "element {} already in context".format(element)
                )

        return _Context(element, self.elements)


def _url_to_path(url):
    parsed = urllib_parse.urlparse(url)
    return parsed.path


def _bool_value(element):
    """
    Given an xml element, returns the tag text converted to a bool.

    :param element: The element to fetch the value from.

    :return: A boolean.
    """
    return (element.text.lower() == "true")


def _element_identification_string(element):
    """
    Gets a string that will hopefully help in identifing an element when there
    is an error.
    """
    info_string = "tag: {}".format(element.tag)
    try:
        elem_id = element.attrib["id"]
        info_string += " id: {}".format(elem_id)
    except KeyError:
        pass

    return info_string


def _name_from_element(element):
    """
    Fetches the name from the ``name`` element child of the provided element.
    If no element exists, returns ``None``.

    :param element: The element to find the name for.

    :return: The name string or ``None``
    """
    name_elem = element.find("./name")
    if name_elem is not None:
        return name_elem.text

    return None


def _rate_for_element(element):
    """
    Takes an FCP rate element and returns a rate to use with otio.

    :param element: An FCP rate element.

    :return: The float rate.
    """
    # rate is encoded as a timebase (int) which can be drop-frame
    base = float(element.find("./timebase").text)
    if _bool_value(element.find("./ntsc")):
        base *= 1000.0 / 1001

    return base


def _rate_from_context(context):
    """
    Given the context object, gets the appropriate rate.

    :param context: The :class:`_Context` instance to find the rate in.

    :return: The rate value or ``None`` if no rate is available in the context.
    """
    try:
        rate_element = context["./rate"]
    except KeyError:
        return None

    return _rate_for_element(rate_element)


def _time_from_timecode_element(tc_element, context=None):
    """
    Given a timecode xml element, returns the time that represents.

    .. todo:: Non Drop-Frame timecode is not yet supported by OTIO.

    :param tc_element: The ``timecode`` element.
    :param context: The context dict under which this timecode is being gotten.

    :return: The :class:`otio.opentime.RationalTime` representation of the
        timecode.
    """
    if context is not None:
        local_context = context.context_pushing_element(tc_element)
    else:
        local_context = _Context(tc_element)

    # Resolve the rate
    rate = _rate_from_context(local_context)

    # Try using the display format and frame number
    display_format = tc_element.find("./displayformat")
    frame = tc_element.find("./frame")

    # Use frame number, if available
    if frame is not None:
        frame_num = int(frame.text)
        return otio.opentime.RationalTime(frame_num, rate)

    # If a TC string is provided, parse rate from it
    tc_string_element = tc_element.find("./string")
    if tc_string_element is None:
        raise ValueError("Timecode element missing required elements")

    tc_string = tc_string_element.text

    # Determine if it's drop, non-drop, or unspecified
    is_non_drop = None
    if display_format is not None:
        is_non_drop = (display_format.text.lower() == "ndf")

    # There is currently a bug where OTIO does not properly support NDF for
    # fractional framerates
    if round(rate) != rate and is_non_drop:
        raise ValueError("Only drop TC supported: {}".format(tc_string))

    return otio.opentime.from_timecode(tc_string, rate)


def _track_kind_from_element(media_element):
    """
    Given an FCP XML media sub-element, returns an appropriate
    :class:`otio.schema.TrackKind` value corresponding to that media type.

    :param media_element: An XML element that is a child of the ``media`` tag.

    :return: The corresponding :class`otio.schema.TrackKind` value.
    :raises: :class:`ValueError` When the media type is unsupported.
    """
    element_tag = media_element.tag.lower()
    if element_tag == "audio":
        return otio.schema.TrackKind.Audio
    elif element_tag == "video":
        return otio.schema.TrackKind.Video

    raise ValueError("Unsupported media kind: {}".format(media_element.tag))


def _is_primary_audio_channel(track):
    """
    Determines whether or not this is the "primary" audio track.

    audio may be structured in stereo where each channel occupies a separate
    track. This importer keeps stereo pairs ganged together as a single track.

    :param track: An XML track element.

    :return: A boolean ``True`` if this is the first track.
    """
    exploded_index = track.attrib.get('currentExplodedTrackIndex', '0')
    exploded_count = track.attrib.get('totalExplodedTrackCount', '1')

    return (exploded_index == '0' or exploded_count == '1')


def _transition_cut_point(transition_item, context):
    """
    Returns the end time at which the transition progresses from one clip to
    the next.

    :param transition_item: The XML element for the transition.
    :param context: The context dictionary applying to this transition.

    :return: The :class:`otio.opentime.RationalTime` the transition cuts at.
    """
    alignment = transition_item.find('./alignment').text
    start = int(transition_item.find('./start').text)
    end = int(transition_item.find('./end').text)

    # start/end time is in the parent context's rate
    local_context = context.context_pushing_element(transition_item)
    rate = _rate_from_context(local_context)

    if alignment in ('end', 'end-black'):
        value = end
    elif alignment in ('start', 'start-black'):
        value = start
    elif alignment in ('center',):
        value = int((start + end) / 2)
    else:
        value = int((start + end) / 2)

    return otio.opentime.RationalTime(value, rate)


def _xml_tree_to_dict(node, ignore_tags=None, ignore_recursive=False):
    """
    Translates the tree under a provided node mapping to a dictionary/list
    representation. XML tag attributes are placed in the dictionary with an
    ``@`` prefix.

    :param node: The root xml element to express childeren of in the
        dictionary.
    :param ignore_tags: A collection of tagnames to skip when converting.
    :param ignore_recursive: If ``True``, will use ``ignore_tags`` not only at
        the top-level, but all the way down the heirarchy.

    :return: The dictionary representation.
    """
    out_dict = {}

    # Handle the attributes
    out_dict.update(
        {"@{}".format(k): v for k, v in node.attrib.items()}
    )

    # Now traverse the child tags
    encountered_tags = set()
    list_tags = set()
    for info_node in node:
        # Skip tags we explicitly parse
        node_tag = info_node.tag
        if ignore_tags and node_tag in ignore_tags:
            continue

        # If there are children, make this a sub-dictionary by recursing
        if len(info_node):
            node_value = _xml_tree_to_dict(info_node)
        else:
            node_value = info_node.text

        # If we've seen this node before, then treat it as a list
        if node_tag in list_tags:
            # We've established that this tag is a list, append to that
            out_dict[node_tag].append(node_value)
        elif node_tag in encountered_tags:
            # This appears to be a list we didn't know about, convert
            out_dict[node_tag] = [
                out_dict[node_tag], node_value
            ]
            list_tags.add(node_tag)
        else:
            # Store the value
            out_dict[node_tag] = node_value
            encountered_tags.add(node_tag)

    return out_dict


def _make_pretty_string(tree_e):
    # most of the parsing in this adapter is done with cElementTree because it
    # is simpler and faster. However, the string representation it returns is
    # far from elegant. Therefor we feed it through minidom to provide an xml
    # with indentations.
    string = cElementTree.tostring(tree_e, encoding="UTF-8", method="xml")
    dom = minidom.parseString(string)
    return dom.toprettyxml(indent='    ')


def marker_for_element(marker_element, rate):
    """
    Creates an :class:`otio.schema.Marker` for the provided element.

    :param marker_element: The XML element for the marker.
    :param rate: The rate for the object the marker is attached to.

    :return: The :class:`otio.schema.Marker` instance.
    """
    # TODO: The spec doc indicates that in and out are required, but doesn't
    #       say they have to be locally specified, so is it possible they
    #       could be inherited?
    marker_in = otio.opentime.RationalTime(
        float(marker_element.find("./in").text), rate
    )
    marker_out_value = float(marker_element.find("./out").text)
    if marker_out_value > 0:
        marker_out = otio.opentime.RationalTime(
            marker_out_value, rate
        )
        marker_duration = (marker_out - marker_in)
    else:
        marker_duration = otio.opentime.RationalTime(rate=rate)

    marker_range = otio.opentime.TimeRange(marker_in, marker_duration)

    md_dict = _xml_tree_to_dict(marker_element, {"in", "out", "name"})
    metadata = {META_NAMESPACE: md_dict} if md_dict else None

    return otio.schema.Marker(
        name=_name_from_element(marker_element),
        marked_range=marker_range,
        metadata=metadata
    )


def markers_from_element(element, context=None):
    """
    Given an element, returns the list of markers attached to it.

    :param element: An element with one or more ``marker`` child elements.
    :param context: The context for this element.

    :return: A :class:`list` of :class:`otio.schema.Marker` instances attached
        to the provided element.
    """
    if context is not None:
        local_context = context.context_pushing_element(element)
    else:
        local_context = _Context(element)
    rate = _rate_from_context(local_context)

    return [marker_for_element(e, rate) for e in element.iterfind("./marker")]


class FCP7XMLParser:
    """
    Implements parsing of an FCP XML file into an OTIO timeline.

    Parsing FCP XML elements include two concepts that require carrying state:
        1. Inheritance
        2. The id Attribute

    .. seealso:: https://developer.apple.com/library/archive/documentation/\
            AppleApplications/Reference/FinalCutPro_XML/Basics/Basics.html\
            #//apple_ref/doc/uid/TP30001154-TPXREF102

    Inheritance is implemented using a _Context object that is pushed down
    through layers of parsing. A given parsing method is passed the element to
    parse into an otio object along with the context that element exists under
    (e.x. a track element parsing method is given the track element and the
    sequence context for that track).

    The id attribute dereferencing is handled through a lookup table stored on
    parser instances and using the ``_derefed_`` methods to take an element and
    find dereference elements.
    """

    _etree = None
    """ The root etree for the FCP XML. """

    _id_map = None
    """ A mapping of id to the first element encountered with that id. """

    def __init__(self, element_tree):
        """
        Constructor, must be init with an xml etree.
        """
        self._etree = element_tree

        self._id_map = {}

    def _derefed_element(self, element):
        """
        Given an element, dereferences it by it's id attribute if needed. If
        the element has an id attribute and it's our first time encountering
        it, store the id.
        """
        if element is None:
            return element

        try:
            elem_id = element.attrib["id"]
        except KeyError:
            return element

        return self._id_map.setdefault(elem_id, element)

    def _derefed_iterfind(self, element, path):
        """
        Given an elemnt, finds elements with the provided path below and
        returns an iterator of the dereferenced versions of those.

        :param element: The XML etree element.
        :param path: The path to find subelements.

        :return: iterator of subelements dereferenced by id.
        """
        return (
            self._derefed_element(e) for e in element.iterfind(path)
        )

    def top_level_sequences(self):
        """"
        Returns a list of timelines for the top-level sequences in the file.
        """
        context = _Context()

        # If the tree has just sequences at the top level, this will catch them
        top_iter = self._derefed_iterfind(self._etree, "./sequence")

        # If there is a project or bin at the top level, this should cath them
        project_and_bin_iter = self._derefed_iterfind(
            self._etree, ".//children/sequence"
        )

        # Make an iterator that will exhaust both the above
        sequence_iter = itertools.chain(top_iter, project_and_bin_iter)

        return [self.timeline_for_sequence(s, context) for s in sequence_iter]

    def timeline_for_sequence(self, sequence_element, context):
        """
        Returns either an :class`otio.schema.Timeline` parsed from a sequence
        element.

        :param sequence_element: The sequence element.
        :param context: The context dictionary.

        :return: The appropriate OTIO object for the element.
        """
        local_context = context.context_pushing_element(sequence_element)

        name = _name_from_element(sequence_element)
        parsed_tags = {"name", "media", "marker", "duration"}
        md_dict = _xml_tree_to_dict(sequence_element, parsed_tags)

        sequence_timecode = self._derefed_element(
            sequence_element.find("./timecode")
        )
        if sequence_timecode is not None:
            seq_start_time = _time_from_timecode_element(
                sequence_timecode, local_context
            )
        else:
            seq_start_time = None

        media_element = self._derefed_element(sequence_element.find("./media"))
        if media_element is None:
            tracks = None
        else:
            # Reach down into the media block and escalate metadata to the
            # sequence
            for media_type in media_element:
                media_info_dict = _xml_tree_to_dict(media_type, {"track"})
                if media_info_dict:
                    media_dict = md_dict.setdefault("media", {})
                    media_dict[media_type.tag] = media_info_dict

            tracks = self.stack_for_element(media_element, local_context)
            tracks.name = name

        # TODO: Should we be parsing the duration tag and pad out a track with
        #       gap to match?

        timeline = otio.schema.Timeline(
            name=name,
            global_start_time=seq_start_time,
            metadata={META_NAMESPACE: md_dict} if md_dict else {},
        )
        timeline.tracks = tracks

        # Push the sequence markers onto the top stack
        markers = markers_from_element(sequence_element, context)
        timeline.tracks.markers.extend(markers)

        return timeline

    def stack_for_element(self, element, context):
        """
        Given an element, parses out track information as a stack.

        :param element: The element under which to find the tracks (typically
            a ``media`` element.
        :param context: The current parser context.

        :return: A :class:`otio.schema.Stack` of the tracks.
        """
        # Determine the context
        local_context = context.context_pushing_element(element)

        tracks = []
        media_type_elements = self._derefed_iterfind(element, "./")
        for media_type_element in media_type_elements:
            try:
                track_kind = _track_kind_from_element(media_type_element)
            except ValueError:
                # Unexpected element
                continue

            is_audio = (track_kind == otio.schema.TrackKind.Audio)
            track_elements = self._derefed_iterfind(
                media_type_element, "./track"
            )
            for track_element in track_elements:
                if is_audio and not _is_primary_audio_channel(track_element):
                    continue

                tracks.append(
                    self.track_for_element(
                        track_element, track_kind, local_context
                    )
                )

        markers = markers_from_element(element, context)

        stack = otio.schema.Stack(
            children=tracks,
            markers=markers,
            name=_name_from_element(element),
        )

        return stack

    def track_for_element(self, track_element, track_kind, context):
        """
        Given a track element, constructs the OTIO track.

        :param track_element: The track XML element.
        :param track_kind: The :class:`otio.schema.TrackKind` for the track.
        :param context: The context dict for this track.
        """
        local_context = context.context_pushing_element(track_element)
        name_element = track_element.find("./name")
        track_name = (name_element.text if name_element is not None else None)

        timeline_item_tags = {"clipitem", "generatoritem", "transitionitem"}

        md_dict = _xml_tree_to_dict(track_element, timeline_item_tags)
        track_metadata = {META_NAMESPACE: md_dict} if md_dict else None

        track = otio.schema.Track(
            name=track_name,
            kind=track_kind,
            metadata=track_metadata,
        )

        # Iterate through and parse track items
        track_rate = _rate_from_context(local_context)
        current_timeline_time = otio.opentime.RationalTime(0, track_rate)
        head_transition_element = None
        for i, item_element in enumerate(track_element):
            if item_element.tag not in timeline_item_tags:
                continue

            item_element = self._derefed_element(item_element)

            # Do a lookahead to try and find the tail transition item
            try:
                tail_transition_element = track_element[i + 1]
                if tail_transition_element.tag != "transitionitem":
                    tail_transition_element = None
                else:
                    tail_transition_element = self._derefed_element(
                        tail_transition_element
                    )
            except IndexError:
                tail_transition_element = None

            track_item, item_range = self.item_and_timing_for_element(
                item_element,
                head_transition_element,
                tail_transition_element,
                local_context,
            )

            # Insert gap between timeline cursor and the new item if needed.
            if current_timeline_time < item_range.start_time:
                gap_duration = (item_range.start_time - current_timeline_time)
                gap_range = otio.opentime.TimeRange(
                    duration=gap_duration.rescaled_to(track_rate)
                )
                track.append(otio.schema.Gap(source_range=gap_range))

            # Add the item and advance the timeline cursor
            track.append(track_item)
            current_timeline_time = item_range.end_time_exclusive()

            # Stash the element for the next iteration if it's a transition
            if item_element.tag == "transitionitem":
                head_transition_element = item_element

        return track

    def media_reference_for_file_element(self, file_element, context):
        """
        Given a file XML element, returns the
        :class`otio.schema.ExternalReference`.

        :param file_element: The file xml element.
        :param context: The parent context dictionary.

        :return: An :class:`otio.schema.ExternalReference`.
        """
        local_context = context.context_pushing_element(file_element)
        media_ref_rate = _rate_from_context(local_context)

        name = _name_from_element(file_element)

        # Get the full metadata
        metadata_ignore_keys = {"duration", "name", "pathurl"}
        md_dict = _xml_tree_to_dict(file_element, metadata_ignore_keys)
        metadata_dict = {META_NAMESPACE: md_dict} if md_dict else None

        # Determine the file path
        path_element = file_element.find("./pathurl")
        if path_element is not None:
            path = path_element.text
        else:
            # TODO: Support others declared in mediaSource tag (like Slug)
            return otio.schema.MissingReference(
                name=name,
                metadata=metadata_dict,
            )

        # Find the timing
        timecode_element = file_element.find("./timecode")
        if timecode_element is not None:
            start_time = _time_from_timecode_element(timecode_element)
        else:
            start_time = otio.opentime.RationalTime()

        duration_element = file_element.find("./duration")
        if duration_element is not None:
            duration = otio.opentime.RationalTime(
                float(duration_element.text), media_ref_rate
            )
            available_range = otio.opentime.TimeRange(
                start_time.rescaled_to(media_ref_rate), duration
            )
        else:
            available_range = None

        media_reference = otio.schema.ExternalReference(
            target_url=path,
            available_range=available_range,
            metadata=metadata_dict,
        )
        media_reference.name = name

        return media_reference

    def media_reference_for_effect_element(self, effect_element):
        """
        Given an effect element, returns a generator reference.

        :param effect_element: The effect for the generator.

        :return: An :class:`otio.schema.GeneratorReference` instance.
        """
        name = _name_from_element(effect_element)
        md_dict = _xml_tree_to_dict(effect_element, {"name"})

        return otio.schema.GeneratorReference(
            name=name,
            metadata=({META_NAMESPACE: md_dict} if md_dict else None)
        )

    def item_and_timing_for_element(
        self, item_element, head_transition, tail_transition, context
    ):
        """
        Given a track item, returns a tuple with the appropriate OpenTimelineIO
        schema item as the first element and an
        :class:`otio.opentime.TimeRange`of theresolved timeline range the clip
        occupies.

        :param item_element: The track item XML node.
        :param head_transition: The xml element for the transition immediately
            before or ``None``.
        :param tail_transition: The xml element for the transition immediately
            after or ``None``.
        :param context: The context dictionary.

        :return: An :class:`otio.core.Item` subclass instance and
            :class:`otio.opentime.TimeRange` for the item.
        """
        parent_rate = _rate_from_context(context)

        # Establish the start/end time in the timeline
        start_value = int(item_element.find("./start").text)
        end_value = int(item_element.find("./end").text)

        if start_value == -1:
            # determine based on the cut point of the head transition
            start = _transition_cut_point(head_transition, context)

            # This offset is needed to determing how much to advance from the
            # clip media's in time. Duration accounts for this offset for the
            # out time.
            transition_rate = _rate_from_context(
                context.context_pushing_element(head_transition)
            )
            start_offset = start - otio.opentime.RationalTime(
                int(head_transition.find('./start').text), transition_rate
            )
        else:
            start = otio.opentime.RationalTime(start_value, parent_rate)
            start_offset = otio.opentime.RationalTime()

        if end_value == -1:
            # determine based on the cut point of the tail transition
            end = _transition_cut_point(tail_transition, context)
        else:
            end = otio.opentime.RationalTime(end_value, parent_rate)

        item_range = otio.opentime.TimeRange(start, (end - start))

        # Get the metadata dictionary for the item
        item_metadata_ignore_keys = {
            "name",
            "start",
            "end",
            "in",
            "out",
            "duration",
            "file",
            "marker",
            "effect",
            "sequence",
        }
        metadata_dict = _xml_tree_to_dict(
            item_element, item_metadata_ignore_keys
        )

        # deserialize the item
        if item_element.tag in {"clipitem", "generatoritem"}:
            item = self.clip_for_element(
                item_element, item_range, start_offset, context
            )
        elif item_element.tag == "transitionitem":
            item = self.transition_for_element(item_element, context)
        else:
            name = "unknown-{}".format(item_element.tag)
            item = otio.core.Item(name=name, source_range=item_range)

        if metadata_dict:
            item.metadata.setdefault(META_NAMESPACE, {}).update(metadata_dict)

        return (item, item_range)

    def clip_for_element(
        self, clipitem_element, item_range, start_offset, context
    ):
        """
        Given a clipitem xml element, returns an :class:`otio.schema.Clip`.

        :param clipitem_element: The element to create a clip for.
        :param item_range: The time range in the timeline the clip occupies.
        :param start_offset: The amount by which the ``in`` time of the clip
            source should be advanced (usually due to a transition).
        :param context: The parent context for the clip.

        :return: The :class:`otio.schema.Clip` instance.
        """
        local_context = context.context_pushing_element(clipitem_element)

        name = _name_from_element(clipitem_element)

        file_element = self._derefed_element(clipitem_element.find("./file"))
        sequence_element = self._derefed_element(
            clipitem_element.find("./sequence")
        )
        if clipitem_element.tag == "generatoritem":
            generator_effect_element = clipitem_element.find(
                "./effect[effecttype='generator']"
            )
        else:
            generator_effect_element = None

        media_start_time = otio.opentime.RationalTime()
        if sequence_element is not None:
            item = self.stack_for_element(sequence_element, local_context)
            # TODO: is there an applicable media start time we should be
            #       using from nested sequences?
        elif file_element is not None or generator_effect_element is not None:
            if file_element is not None:
                media_reference = self.media_reference_for_file_element(
                    file_element, local_context
                )
                # See if there is a start offset
                timecode_element = file_element.find("./timecode")
                if timecode_element is not None:
                    media_start_time = _time_from_timecode_element(
                        timecode_element
                    )
            elif generator_effect_element is not None:
                media_reference = self.media_reference_for_effect_element(
                    generator_effect_element
                )

            item = otio.schema.Clip(
                name=name,
                media_reference=media_reference,
            )
        else:
            raise TypeError(
                'Type of clip item is not supported {}'.format(
                    _element_identification_string(clipitem_element)
                )
            )

        # Add the markers
        markers = markers_from_element(clipitem_element, context)
        item.markers.extend(markers)

        # Find the in time (source time relative to media start)
        clip_rate = _rate_from_context(local_context)
        in_value = float(clipitem_element.find('./in').text)
        in_time = otio.opentime.RationalTime(in_value, clip_rate)

        # Offset the "in" time by the start offset of the media
        soure_start_time = in_time + media_start_time + start_offset
        duration = item_range.duration

        # Source Range is the item range expressed in the clip's rate (for now)
        source_range = otio.opentime.TimeRange(
            soure_start_time.rescaled_to(clip_rate),
            duration.rescaled_to(clip_rate),
        )

        item.source_range = source_range

        # Parse the filters
        filter_iter = self._derefed_iterfind(clipitem_element, "./filter")
        for filter_element in filter_iter:
            item.effects.append(
                self.effect_from_filter_element(filter_element)
            )

        return item

    def effect_from_filter_element(self, filter_element):
        """
        Given a filter element, creates an :class:`otio.schema.Effect`.

        :param filter_element: The ``filter`` element containing the effect.

        :return: The effect instance.
        """
        effect_element = filter_element.find("./effect")

        if effect_element is None:
            raise ValueError(
                "could not find effect in filter: {}".format(filter_element)
            )

        name = effect_element.find("./name").text

        effect_metadata = _xml_tree_to_dict(effect_element, {"name"})

        return otio.schema.Effect(
            name,
            metadata={META_NAMESPACE: effect_metadata},
        )

    def transition_for_element(self, item_element, context):
        """
        Creates an OTIO transition for the provided transition element.

        :param item_element: The element to create a transition for.
        :param context: The parent context for the element.

        :return: The :class:`otio.schema.Transition` instance.
        """
        # start and end times are in the parent's rate
        rate = _rate_from_context(context)
        start = otio.opentime.RationalTime(
            int(item_element.find('./start').text),
            rate
        )
        end = otio.opentime.RationalTime(
            int(item_element.find('./end').text),
            rate
        )
        cut_point = _transition_cut_point(item_element, context)

        transition = otio.schema.Transition(
            name=item_element.find('./effect/name').text,
            transition_type=otio.schema.TransitionTypes.SMPTE_Dissolve,
            in_offset=cut_point - start,
            out_offset=end - cut_point,
        )

        return transition


# ------------------------
# building single track
# ------------------------


def _populate_backreference_map(item, br_map):
    if isinstance(item, otio.core.MediaReference):
        tag = 'file'
    elif isinstance(item, otio.schema.Track):
        tag = 'sequence'
    else:
        tag = None

    if isinstance(item, otio.schema.ExternalReference):
        item_hash = hash(str(item.target_url))
    elif isinstance(item, otio.schema.MissingReference):
        item_hash = 'missing_ref'
    else:
        item_hash = hash(id(item))

    # skip unspecified tags
    if tag is not None:
        br_map[tag].setdefault(
            item_hash,
            1 if not br_map[tag] else max(br_map[tag].values()) + 1
        )

    # populate children
    if isinstance(item, otio.schema.Timeline):
        for sub_item in item.tracks:
            _populate_backreference_map(sub_item, br_map)
    elif isinstance(
        item,
        (otio.schema.Clip, otio.schema.Gap, otio.schema.Transition)
    ):
        pass
    else:
        for sub_item in item:
            _populate_backreference_map(sub_item, br_map)


def _backreference_build(tag):
    # We can also encode these back-references if an item is accessed multiple
    # times. To do this we store an id attribute on the element. For back-
    # references we then only need to return an empty element of that type with
    # the id we logged before

    def singleton_decorator(func):
        @functools.wraps(func)
        def wrapper(item, *args, **kwargs):
            br_map = args[-1]
            if isinstance(item, otio.schema.ExternalReference):
                item_hash = hash(str(item.target_url))
            elif isinstance(item, otio.schema.MissingReference):
                item_hash = 'missing_ref'
            else:
                item_hash = item.__hash__()
            item_id = br_map[tag].get(item_hash, None)
            if item_id is not None:
                return cElementTree.Element(
                    tag,
                    id='{}-{}'.format(tag, item_id)
                )
            item_id = br_map[tag].setdefault(
                item_hash,
                1 if not br_map[tag] else max(br_map[tag].values()) + 1
            )
            elem = func(item, *args, **kwargs)
            elem.attrib['id'] = '{}-{}'.format(tag, item_id)
            return elem

        return wrapper

    return singleton_decorator


def _insert_new_sub_element(into_parent, tag, attrib=None, text=''):
    elem = cElementTree.SubElement(into_parent, tag, **attrib or {})
    elem.text = text
    return elem


def _build_rate(time):
    rate = math.ceil(time.rate)

    rate_e = cElementTree.Element('rate')
    _insert_new_sub_element(rate_e, 'timebase', text=str(int(rate)))
    _insert_new_sub_element(
        rate_e,
        'ntsc',
        text='FALSE' if rate == time.rate else 'TRUE'
    )
    return rate_e


def _build_item_timings(
    item_e,
    item,
    timeline_range,
    transition_offsets,
    timecode
):
    # source_start is absolute time taking into account the timecode of the
    # media. But xml regards the source in point from the start of the media.
    # So we subtract the media timecode.
    item_rate = item.source_range.start_time.rate
    source_start = (item.source_range.start_time - timecode) \
        .rescaled_to(item_rate)
    source_end = (item.source_range.end_time_exclusive() - timecode) \
        .rescaled_to(item_rate)
    start = '{:.0f}'.format(timeline_range.start_time.value)
    end = '{:.0f}'.format(timeline_range.end_time_exclusive().value)

    if transition_offsets[0] is not None:
        start = '-1'
        source_start -= transition_offsets[0]
    if transition_offsets[1] is not None:
        end = '-1'
        source_end += transition_offsets[1]

    _insert_new_sub_element(
        item_e, 'duration',
        text='{:.0f}'.format(item.source_range.duration.value)
    )
    _insert_new_sub_element(item_e, 'start', text=start)
    _insert_new_sub_element(item_e, 'end', text=end)
    _insert_new_sub_element(
        item_e,
        'in',
        text='{:.0f}'.format(source_start.value)
    )
    _insert_new_sub_element(
        item_e,
        'out',
        text='{:.0f}'.format(source_end.value)
    )


@_backreference_build('file')
def _build_empty_file(media_ref, source_start, br_map):
    file_e = cElementTree.Element('file')
    file_e.append(_build_rate(source_start))
    file_media_e = _insert_new_sub_element(file_e, 'media')
    _insert_new_sub_element(file_media_e, 'video')

    return file_e


@_backreference_build('file')
def _build_file(media_reference, br_map):
    file_e = cElementTree.Element('file')

    available_range = media_reference.available_range
    url_path = _url_to_path(media_reference.target_url)

    _insert_new_sub_element(file_e, 'name', text=os.path.basename(url_path))
    file_e.append(_build_rate(available_range.start_time))
    _insert_new_sub_element(
        file_e, 'duration',
        text='{:.0f}'.format(available_range.duration.value)
    )
    _insert_new_sub_element(file_e, 'pathurl', text=media_reference.target_url)

    # timecode
    timecode = available_range.start_time
    timecode_e = _insert_new_sub_element(file_e, 'timecode')
    timecode_e.append(_build_rate(timecode))
    # TODO: This assumes the rate on the start_time is the framerate
    _insert_new_sub_element(
        timecode_e,
        'string',
        text=otio.opentime.to_timecode(timecode, rate=timecode.rate)
    )
    _insert_new_sub_element(
        timecode_e,
        'frame',
        text='{:.0f}'.format(timecode.value)
    )
    display_format = (
        'DF' if (
            math.ceil(timecode.rate) == 30 and math.ceil(timecode.rate) != timecode.rate
        ) else 'NDF'
    )
    _insert_new_sub_element(timecode_e, 'displayformat', text=display_format)

    # we need to flag the file reference with the content types, otherwise it
    # will not get recognized
    file_media_e = _insert_new_sub_element(file_e, 'media')
    content_types = []
    if not os.path.splitext(url_path)[1].lower() in ('.wav', '.aac', '.mp3'):
        content_types.append('video')
    content_types.append('audio')

    for kind in content_types:
        _insert_new_sub_element(file_media_e, kind)

    return file_e


def _build_transition_item(
    transition_item,
    timeline_range,
    transition_offsets,
    br_map
):
    transition_e = cElementTree.Element('transitionitem')
    _insert_new_sub_element(
        transition_e,
        'start',
        text='{:.0f}'.format(timeline_range.start_time.value)
    )
    _insert_new_sub_element(
        transition_e,
        'end',
        text='{:.0f}'.format(timeline_range.end_time_exclusive().value)
    )

    if not transition_item.in_offset.value:
        _insert_new_sub_element(transition_e, 'alignment', text='start-black')
    elif not transition_item.out_offset.value:
        _insert_new_sub_element(transition_e, 'alignment', text='end-black')
    else:
        _insert_new_sub_element(transition_e, 'alignment', text='center')
    # todo support 'start' and 'end' alignment

    transition_e.append(_build_rate(timeline_range.start_time))

    effectid = transition_item.metadata.get(META_NAMESPACE, {}).get(
        'effectid',
        'Cross Dissolve'
    )

    effect_e = _insert_new_sub_element(transition_e, 'effect')
    _insert_new_sub_element(effect_e, 'name', text=transition_item.name)
    _insert_new_sub_element(effect_e, 'effectid', text=effectid)
    _insert_new_sub_element(effect_e, 'effecttype', text='transition')
    _insert_new_sub_element(effect_e, 'mediatype', text='video')

    return transition_e


def _build_clip_item_without_media(clip_item, timeline_range,
                                   transition_offsets, br_map):
    clip_item_e = cElementTree.Element('clipitem', frameBlend='FALSE')
    start_time = clip_item.source_range.start_time

    _insert_new_sub_element(clip_item_e, 'name', text=clip_item.name)
    clip_item_e.append(_build_rate(start_time))
    clip_item_e.append(
        _build_empty_file(clip_item.media_reference, start_time, br_map)
    )
    clip_item_e.extend([_build_marker(m) for m in clip_item.markers])
    timecode = otio.opentime.RationalTime(0, timeline_range.start_time.rate)

    _build_item_timings(
        clip_item_e,
        clip_item,
        timeline_range,
        transition_offsets,
        timecode
    )

    return clip_item_e


def _build_clip_item(clip_item, timeline_range, transition_offsets, br_map):
    clip_item_e = cElementTree.Element('clipitem', frameBlend='FALSE')

    # set the clip name from the media reference if not defined on the clip
    if clip_item.name is not None:
        name = clip_item.name
    else:
        url_path = _url_to_path(clip_item.media_reference.target_url)
        name = os.path.basename(url_path)

    _insert_new_sub_element(
        clip_item_e,
        'name',
        text=name
    )
    clip_item_e.append(_build_file(clip_item.media_reference, br_map))
    if clip_item.media_reference.available_range:
        clip_item_e.append(
            _build_rate(clip_item.source_range.start_time)
        )
    clip_item_e.extend(_build_marker(m) for m in clip_item.markers)

    if clip_item.media_reference.available_range:
        timecode = clip_item.media_reference.available_range.start_time

        _build_item_timings(
            clip_item_e,
            clip_item,
            timeline_range,
            transition_offsets,
            timecode
        )

    return clip_item_e


def _build_track_item(track, timeline_range, transition_offsets, br_map):
    clip_item_e = cElementTree.Element('clipitem', frameBlend='FALSE')

    _insert_new_sub_element(
        clip_item_e,
        'name',
        text=os.path.basename(track.name)
    )

    track_e = _build_track(track, timeline_range, br_map)

    clip_item_e.append(_build_rate(track.source_range.start_time))
    clip_item_e.extend([_build_marker(m) for m in track.markers])
    clip_item_e.append(track_e)
    timecode = otio.opentime.RationalTime(0, timeline_range.start_time.rate)

    _build_item_timings(
        clip_item_e,
        track,
        timeline_range,
        transition_offsets,
        timecode
    )

    return clip_item_e


def _build_item(item, timeline_range, transition_offsets, br_map):
    if isinstance(item, otio.schema.Transition):
        return _build_transition_item(
            item,
            timeline_range,
            transition_offsets,
            br_map
        )
    elif isinstance(item, otio.schema.Clip):
        if isinstance(
            item.media_reference,
            otio.schema.MissingReference
        ):
            return _build_clip_item_without_media(
                item,
                timeline_range,
                transition_offsets,
                br_map
            )
        else:
            return _build_clip_item(
                item,
                timeline_range,
                transition_offsets,
                br_map
            )
    elif isinstance(item, otio.schema.Stack):
        return _build_track_item(
            item,
            timeline_range,
            transition_offsets,
            br_map
        )
    else:
        raise ValueError('Unsupported item: ' + str(item))


def _build_top_level_track(track, track_rate, br_map):
    track_e = cElementTree.Element('track')

    for n, item in enumerate(track):
        if isinstance(item, otio.schema.Gap):
            continue

        transition_offsets = [None, None]
        previous_item = track[n - 1] if n > 0 else None
        next_item = track[n + 1] if n + 1 < len(track) else None
        if not isinstance(item, otio.schema.Transition):
            # find out if this item has any neighboring transition
            if isinstance(previous_item, otio.schema.Transition):
                if previous_item.out_offset.value:
                    transition_offsets[0] = previous_item.in_offset
                else:
                    transition_offsets[0] = None
            if isinstance(next_item, otio.schema.Transition):
                if next_item.in_offset.value:
                    transition_offsets[1] = next_item.out_offset
                else:
                    transition_offsets[1] = None

        timeline_range = track.range_of_child_at_index(n)
        timeline_range = otio.opentime.TimeRange(
            timeline_range.start_time.rescaled_to(track_rate),
            timeline_range.duration.rescaled_to(track_rate)
        )
        track_e.append(
            _build_item(item, timeline_range, transition_offsets, br_map)
        )

    return track_e


def _build_marker(marker):
    marker_e = cElementTree.Element('marker')

    comment = marker.metadata.get(META_NAMESPACE, {}).get('comment', '')
    marked_range = marker.marked_range

    _insert_new_sub_element(marker_e, 'comment', text=comment)
    _insert_new_sub_element(marker_e, 'name', text=marker.name)
    _insert_new_sub_element(
        marker_e, 'in',
        text='{:.0f}'.format(marked_range.start_time.value)
    )
    _insert_new_sub_element(marker_e, 'out', text='-1')

    return marker_e


@_backreference_build('sequence')
def _build_track(stack, timeline_range, br_map):
    track_e = cElementTree.Element('sequence')
    _insert_new_sub_element(track_e, 'name', text=stack.name)
    _insert_new_sub_element(
        track_e, 'duration',
        text='{:.0f}'.format(timeline_range.duration.value)
    )
    track_e.append(_build_rate(timeline_range.start_time))
    track_rate = timeline_range.start_time.rate

    media_e = _insert_new_sub_element(track_e, 'media')
    video_e = _insert_new_sub_element(media_e, 'video')
    audio_e = _insert_new_sub_element(media_e, 'audio')

    for track in stack:
        if track.kind == otio.schema.TrackKind.Video:
            video_e.append(_build_top_level_track(track, track_rate, br_map))
        elif track.kind == otio.schema.TrackKind.Audio:
            audio_e.append(_build_top_level_track(track, track_rate, br_map))

    for marker in stack.markers:
        track_e.append(_build_marker(marker))

    return track_e


def _build_collection(collection, br_map):
    tracks = []
    for item in collection:
        if not isinstance(item, otio.schema.Timeline):
            continue

        timeline_range = otio.opentime.TimeRange(
            start_time=item.global_start_time,
            duration=item.duration()
        )
        tracks.append(_build_track(item.tracks, timeline_range, br_map))

    return tracks


# --------------------
# adapter requirements
# --------------------

def read_from_string(input_str):
    tree = cElementTree.fromstring(input_str)

    parser = FCP7XMLParser(tree)
    sequences = parser.top_level_sequences()

    if len(sequences) == 1:
        return sequences[0]
    elif len(sequences) > 1:
        return otio.schema.SerializableCollection(
            name="Sequences",
            children=sequences,
        )
    else:
        raise ValueError('No top-level sequences found')


def write_to_string(input_otio):
    tree_e = cElementTree.Element('xmeml', version="4")
    project_e = _insert_new_sub_element(tree_e, 'project')
    _insert_new_sub_element(project_e, 'name', text=input_otio.name)
    children_e = _insert_new_sub_element(project_e, 'children')

    br_map = collections.defaultdict(dict)
    _populate_backreference_map(input_otio, br_map)

    if isinstance(input_otio, otio.schema.Timeline):
        timeline_range = otio.opentime.TimeRange(
            start_time=input_otio.global_start_time,
            duration=input_otio.duration()
        )
        children_e.append(
            _build_track(input_otio.tracks, timeline_range, br_map)
        )
    elif isinstance(input_otio, otio.schema.SerializableCollection):
        children_e.extend(
            _build_collection(input_otio, br_map)
        )

    return _make_pretty_string(tree_e)
