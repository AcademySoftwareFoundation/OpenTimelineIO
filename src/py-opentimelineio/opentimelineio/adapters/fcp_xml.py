# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""OpenTimelineIO Final Cut Pro 7 XML Adapter."""

import collections
import functools
import itertools
import math
import os
import re
from xml.etree import cElementTree
from xml.dom import minidom

import urllib.parse as urllib_parse
from collections.abc import Mapping

from .. import (
    core,
    opentime,
    schema,
)

# namespace to use for metadata
META_NAMESPACE = 'fcp_xml'

# Regex to match identifiers like clipitem-22
ID_RE = re.compile(r"^(?P<tag>[a-zA-Z]*)-(?P<id>\d*)$")


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
        :raises: :class: `ValueError` if the element is already in the stack.
        """
        for context_element in self.elements:
            if context_element == element:
                raise ValueError(
                    f"element {element} already in context"
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
    info_string = f"tag: {element.tag}"
    try:
        elem_id = element.attrib["id"]
        info_string += f" id: {elem_id}"
    except KeyError:
        pass

    return info_string


def _name_from_element(element):
    """
    Fetches a name suitable for OTIO objects from the ``name`` element child
    of the provided element.
    If no element exists, returns empty string.

    :param element: The element to find the name for.

    :return: The name string or and empty string
    """
    name_elem = element.find("./name")
    if name_elem is not None:
        return name_elem.text if name_elem.text is not None else ""

    return ""


def _otio_rate(timebase, ntsc):
    """
    Given an FCP XML timebase and NTSC boolean, returns the float framerate.
    """
    if not ntsc:
        return timebase

    return (timebase * 1000.0 / 1001)


def _rate_from_context(context):
    """
    Given the context object, gets the appropriate rate.

    :param context: The :class: `_Context` instance to find the rate in.

    :return: The rate value or ``None`` if no rate is available in the context.
    """
    timebase = context.get("./rate/timebase")
    ntsc = context.get("./rate/ntsc")

    if timebase is None:
        return None

    return _otio_rate(
        float(timebase.text),
        _bool_value(ntsc) if ntsc is not None else None,
    )


def _time_from_timecode_element(tc_element, context=None):
    """
    Given a timecode xml element, returns the time that represents.

    .. todo:: Non Drop-Frame timecode is not yet supported by OTIO.

    :param tc_element: The ``timecode`` element.
    :param context: The context dict under which this timecode is being gotten.

    :return: The :class: `opentime.RationalTime` representation of the
        timecode.
    """
    if context is not None:
        local_context = context.context_pushing_element(tc_element)
    else:
        local_context = _Context(tc_element)

    # Resolve the rate
    rate = _rate_from_context(local_context)

    # Try using the display format and frame number
    frame = tc_element.find("./frame")

    # Use frame number, if available
    if frame is not None:
        frame_num = int(frame.text)
        return opentime.RationalTime(frame_num, rate)

    # If a TC string is provided, parse rate from it
    tc_string_element = tc_element.find("./string")
    if tc_string_element is None:
        raise ValueError("Timecode element missing required elements")

    tc_string = tc_string_element.text

    return opentime.from_timecode(tc_string, rate)


def _track_kind_from_element(media_element):
    """
    Given an FCP XML media sub-element, returns an appropriate
    :class: `schema.TrackKind` value corresponding to that media type.

    :param media_element: An XML element that is a child of the ``media`` tag.

    :return: The corresponding :class`schema.TrackKind` value.
    :raises: :class: `ValueError` When the media type is unsupported.
    """
    element_tag = media_element.tag.lower()
    if element_tag == "audio":
        return schema.TrackKind.Audio
    elif element_tag == "video":
        return schema.TrackKind.Video

    raise ValueError(f"Unsupported media kind: {media_element.tag}")


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

    :return: The :class: `opentime.RationalTime` the transition cuts at.
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

    return opentime.RationalTime(value, rate)


def _xml_tree_to_dict(node, ignore_tags=None, omit_timing=True):
    """
    Translates the tree under a provided node mapping to a dictionary/list
    representation. XML tag attributes are placed in the dictionary with an
    ``@`` prefix.

    .. note:: In addition to the provided ignore tags, this filters a subset of
    timing metadata such as ``frame`` and ``string`` elements within timecode
    elements.

    .. warning:: This scheme does not allow for leaf elements to have
    attributes.  for the moment this doesn't seem to be an issue.

    :param node: The root xml element to express childeren of in the
        dictionary.
    :param ignore_tags: A collection of tagnames to skip when converting.
    :param omit_timing: If ``True``, omits timing-specific tags.

    :return: The dictionary representation.
    """
    if node.tag == "timecode":
        additional_ignore_tags = {"frame", "string"}
    else:
        additional_ignore_tags = tuple()

    out_dict = collections.OrderedDict()

    # Handle the attributes
    out_dict.update(
        collections.OrderedDict(
            (f"@{k}", v) for k, v in node.attrib.items()
        )
    )

    # Now traverse the child tags
    encountered_tags = set()
    list_tags = set()
    for info_node in node:
        # Skip tags we were asked to omit
        node_tag = info_node.tag
        if ignore_tags and node_tag in ignore_tags:
            continue

        # Skip some special case tags related to timing information
        if node_tag in additional_ignore_tags:
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


def _dict_to_xml_tree(data_dict, tag):
    """
    Given a dictionary, returns an element tree storing the data. This is the
    inverse of :func:`_xml_tree_to_dict`.

    Any key/value pairs in the dictionary heirarchy where the key is prefixed
    with ``@`` will be treated as attributes on the containing element.

    .. note:: This will automatically omit some kinds of metadata it should
    be up to the xml building functions to manage (such as timecode and id).

    :param data_dict: The dictionary to turn into an XML tree.
    :param tag: The tag name to use for the top-level element.

    :return: The top element for the dictionary
    """
    top_attributes = collections.OrderedDict(
        (k[1:], v) for k, v in data_dict.items()
        if k != "@id" and k.startswith("@")
    )
    top_element = cElementTree.Element(tag, **top_attributes)

    def elements_for_value(python_value, element_tag):
        """ Creates a list of appropriate XML elements given a value. """

        # XXX because our API creates python-wrapped versions of OTIO's
        #     AnyDictionary, AnyVector instead of "real" python dict/list
        #     instances, this uses a more duck-typing friendly approach to
        #     figuring out how to translate objects into xml.
        #
        #     This also works with the OrderedDict that are produced by this
        #     API.

        # test for dictionary like objects
        try:
            python_value.items()
            element = _dict_to_xml_tree(python_value, element_tag)
            return [element]
        except AttributeError:
            pass

        # test for list-like objects (but not string-derived)
        if not isinstance(python_value, str):
            try:
                iter(python_value)
                return itertools.chain.from_iterable(
                    elements_for_value(item, element_tag) for item in python_value
                )
            except TypeError:
                pass

        # everything else goes in as a string
        element = cElementTree.Element(element_tag)
        if python_value is not None:
            element.text = str(python_value)
        return [element]

    # Drop timecode, rate, and link elements from roundtripping because they
    # may become stale with timeline updates.
    default_ignore_keys = {"timecode", "rate", "link"}
    specific_ignore_keys = {"samplecharacteristics": {"timecode"}}
    ignore_keys = specific_ignore_keys.get(tag, default_ignore_keys)

    # push the elements into the tree
    for key, value in data_dict.items():
        if key in ignore_keys:
            continue

        # We already handled the attributes
        if key.startswith("@"):
            continue

        elements = elements_for_value(value, key)
        top_element.extend(elements)

    return top_element


def _element_with_item_metadata(tag, item):
    """
    Given a tag name, gets the FCP XML metadata dict and creates a tree of XML
    with that metadata under a top element with the provided tag.

    :param tag: The XML tag for the root element.
    :param item: An otio object with a metadata dict.
    """
    item_meta = item.metadata.get(META_NAMESPACE)
    if item_meta:
        return _dict_to_xml_tree(item_meta, tag)

    return cElementTree.Element(tag)


def _get_or_create_subelement(parent_element, tag):
    """
    Given an element and tag name, either gets the direct child of parent with
    that tag name or creates a new subelement with that tag and returns it.

    :param parent_element: The element to get or create the subelement from.
    :param tag: The tag for the subelement.
    """
    sub_element = parent_element.find(tag)
    if sub_element is None:
        sub_element = cElementTree.SubElement(parent_element, tag)

    return sub_element


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
    Creates an :class: `schema.Marker` for the provided element.

    :param marker_element: The XML element for the marker.
    :param rate: The rate for the object the marker is attached to.

    :return: The :class: `schema.Marker` instance.
    """
    # TODO: The spec doc indicates that in and out are required, but doesn't
    #       say they have to be locally specified, so is it possible they
    #       could be inherited?
    marker_in = opentime.RationalTime(
        float(marker_element.find("./in").text), rate
    )
    marker_out_value = float(marker_element.find("./out").text)
    if marker_out_value > 0:
        marker_out = opentime.RationalTime(
            marker_out_value, rate
        )
        marker_duration = (marker_out - marker_in)
    else:
        marker_duration = opentime.RationalTime(rate=rate)

    marker_range = opentime.TimeRange(marker_in, marker_duration)

    md_dict = _xml_tree_to_dict(marker_element, {"in", "out", "name"})
    metadata = {META_NAMESPACE: md_dict} if md_dict else None

    return schema.Marker(
        name=_name_from_element(marker_element),
        marked_range=marker_range,
        metadata=metadata
    )


def markers_from_element(element, context=None):
    """
    Given an element, returns the list of markers attached to it.

    :param element: An element with one or more ``marker`` child elements.
    :param context: The context for this element.

    :return: A :class: `list` of :class: `schema.Marker` instances attached
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

    .. seealso:: https://developer.apple.com/library/archive/documentation/AppleApplications/Reference/FinalCutPro_XML/Basics/Basics.html#//apple_ref/doc/uid/TP30001154-TPXREF102 # noqa

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
        Returns either an :class`schema.Timeline` parsed from a sequence
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
                    media_dict = md_dict.setdefault(
                        "media", collections.OrderedDict()
                    )
                    media_dict[media_type.tag] = media_info_dict

            tracks = self.stack_for_element(media_element, local_context)
            tracks.name = name

        # TODO: Should we be parsing the duration tag and pad out a track with
        #       gap to match?

        timeline = schema.Timeline(
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

        :return: A :class: `schema.Stack` of the tracks.
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

            is_audio = (track_kind == schema.TrackKind.Audio)
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

        stack = schema.Stack(
            children=tracks,
            markers=markers,
            name=_name_from_element(element),
        )

        return stack

    def track_for_element(self, track_element, track_kind, context):
        """
        Given a track element, constructs the OTIO track.

        :param track_element: The track XML element.
        :param track_kind: The :class: `schema.TrackKind` for the track.
        :param context: The context dict for this track.
        """
        local_context = context.context_pushing_element(track_element)
        name_element = track_element.find("./name")
        track_name = (name_element.text if name_element is not None else None)

        timeline_item_tags = {"clipitem", "generatoritem", "transitionitem"}

        md_dict = _xml_tree_to_dict(track_element, timeline_item_tags)
        track_metadata = {META_NAMESPACE: md_dict} if md_dict else None

        track = schema.Track(
            name=track_name,
            kind=track_kind,
            metadata=track_metadata,
        )

        # Iterate through and parse track items
        track_rate = _rate_from_context(local_context)
        current_timeline_time = opentime.RationalTime(0, track_rate)
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
                gap_range = opentime.TimeRange(
                    duration=gap_duration.rescaled_to(track_rate)
                )
                track.append(schema.Gap(source_range=gap_range))

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
        :class`schema.ExternalReference`.

        :param file_element: The file xml element.
        :param context: The parent context dictionary.

        :return: An :class: `schema.ExternalReference`.
        """
        local_context = context.context_pushing_element(file_element)
        media_ref_rate = _rate_from_context(local_context)

        name = _name_from_element(file_element)

        # Get the full metadata
        metadata_ignore_keys = {"duration", "name", "pathurl", "mediaSource"}
        md_dict = _xml_tree_to_dict(file_element, metadata_ignore_keys)
        metadata_dict = {META_NAMESPACE: md_dict} if md_dict else None

        # Determine the file path
        path_element = file_element.find("./pathurl")
        if path_element is not None:
            path = path_element.text
        else:
            path = None

        # Determine the mediasource
        mediasource_element = file_element.find("./mediaSource")
        if mediasource_element is not None:
            mediasource = mediasource_element.text
        else:
            mediasource = None

        # Find the timing
        timecode_element = file_element.find("./timecode")
        if timecode_element is not None:
            start_time = _time_from_timecode_element(
                timecode_element, local_context
            )
            start_time = start_time.rescaled_to(media_ref_rate)
        else:
            start_time = opentime.RationalTime(0, media_ref_rate)

        duration_element = file_element.find("./duration")
        if duration_element is not None:
            duration = opentime.RationalTime(
                float(duration_element.text), media_ref_rate
            )
            available_range = opentime.TimeRange(start_time, duration)
        elif timecode_element is not None:
            available_range = opentime.TimeRange(
                start_time,
                opentime.RationalTime(0, media_ref_rate),
            )
        else:
            available_range = None

        if path is not None:
            media_reference = schema.ExternalReference(
                target_url=path,
                available_range=available_range,
                metadata=metadata_dict,
            )
            media_reference.name = name
        elif mediasource is not None:
            media_reference = schema.GeneratorReference(
                name=name,
                generator_kind=mediasource,
                available_range=available_range,
                metadata=metadata_dict,
            )
        else:
            media_reference = schema.MissingReference(
                name=name,
                available_range=available_range,
                metadata=metadata_dict,
            )

        return media_reference

    def media_reference_for_effect_element(self, effect_element):
        """
        Given an effect element, returns a generator reference.

        :param effect_element: The effect for the generator.

        :return: An :class: `schema.GeneratorReference` instance.
        """
        name = _name_from_element(effect_element)
        md_dict = _xml_tree_to_dict(effect_element, {"name", "effectid"})

        effectid_element = effect_element.find("./effectid")
        generator_kind = (
            effectid_element.text if effectid_element is not None else ""
        )

        return schema.GeneratorReference(
            name=name,
            generator_kind=generator_kind,
            metadata=({META_NAMESPACE: md_dict} if md_dict else None)
        )

    def item_and_timing_for_element(
        self, item_element, head_transition, tail_transition, context
    ):
        """ Given a track item, returns a tuple with the appropriate OpenTimelineIO
        schema item as the first element and an :class: `opentime.TimeRange` of
        the resolved timeline range the clip
        occupies.

        :param item_element: The track item XML node.
        :param head_transition: The xml element for the transition immediately
            before or ``None``.
        :param tail_transition: The xml element for the transition immediately
            after or ``None``.
        :param context: The context dictionary.

        :return: An :class: `core.Item` subclass instance and
            :class: `opentime.TimeRange` for the item.
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
            start_offset = start - opentime.RationalTime(
                int(head_transition.find('./start').text), transition_rate
            )
        else:
            start = opentime.RationalTime(start_value, parent_rate)
            start_offset = opentime.RationalTime()

        if end_value == -1:
            # determine based on the cut point of the tail transition
            end = _transition_cut_point(tail_transition, context)
        else:
            end = opentime.RationalTime(end_value, parent_rate)

        item_range = opentime.TimeRange(start, (end - start))

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
            "rate",
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
            name = f"unknown-{item_element.tag}"
            item = core.Item(name=name, source_range=item_range)

        if metadata_dict:
            item.metadata.setdefault(META_NAMESPACE, {}).update(metadata_dict)

        return (item, item_range)

    def clip_for_element(
        self, clipitem_element, item_range, start_offset, context
    ):
        """
        Given a clipitem xml element, returns an :class: `schema.Clip`.

        :param clipitem_element: The element to create a clip for.
        :param item_range: The time range in the timeline the clip occupies.
        :param start_offset: The amount by which the ``in`` time of the clip
            source should be advanced (usually due to a transition).
        :param context: The parent context for the clip.

        :return: The :class: `schema.Clip` instance.
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

        media_start_time = opentime.RationalTime()
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
                        timecode_element, local_context
                    )
            elif generator_effect_element is not None:
                media_reference = self.media_reference_for_effect_element(
                    generator_effect_element
                )

            item = schema.Clip(
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
        in_time = opentime.RationalTime(in_value, clip_rate)

        # Offset the "in" time by the start offset of the media
        soure_start_time = in_time + media_start_time + start_offset
        duration = item_range.duration

        # Source Range is the item range expressed in the clip's rate (for now)
        source_range = opentime.TimeRange(
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
        Given a filter element, creates an :class: `schema.Effect`.

        :param filter_element: The ``filter`` element containing the effect.

        :return: The effect instance.
        """
        effect_element = filter_element.find("./effect")

        if effect_element is None:
            raise ValueError(
                f"could not find effect in filter: {filter_element}"
            )

        name = _name_from_element(effect_element)

        effect_metadata = _xml_tree_to_dict(effect_element, {"name"})

        return schema.Effect(
            name,
            metadata={META_NAMESPACE: effect_metadata},
        )

    def transition_for_element(self, item_element, context):
        """
        Creates an OTIO transition for the provided transition element.

        :param item_element: The element to create a transition for.
        :param context: The parent context for the element.

        :return: The :class: `schema.Transition` instance.
        """
        # start and end times are in the parent's rate
        rate = _rate_from_context(context)
        start = opentime.RationalTime(
            int(item_element.find('./start').text),
            rate
        )
        end = opentime.RationalTime(
            int(item_element.find('./end').text),
            rate
        )
        cut_point = _transition_cut_point(item_element, context)

        transition = schema.Transition(
            name=_name_from_element(item_element.find('./effect')),
            transition_type=schema.TransitionTypes.SMPTE_Dissolve,
            in_offset=cut_point - start,
            out_offset=end - cut_point,
        )

        return transition


# ------------------------
# building single track
# ------------------------


def _backreference_for_item(item, tag, br_map):
    """
    Given an item, determines what the id in the backreference map should be.
    If the item is already tracked in the map, it will be returned, otherwise
    a new id will be minted.

    .. note:: ``br_map`` may be mutated by this function. ``br_map`` is
    intended to be an opaque data structure and only accessed through this
    function, the structure of data in br_map may change.

    :param item: The :class: `core.SerializableObject` to create an id for.
    :param tag: The tag name that will be used for object in xml.
    :param br_map: The dictionary containing backreference information
        generated so far.

    :return: A 2-tuple of (id_string, is_new_id) where the ``id_string`` is
        the value for the xml id attribute and ``is_new_id`` is ``True`` when
        this is the first time that id was encountered.
    """
    # br_map is structured as a dictionary with tags as keys, and dictionaries
    # of hash to id int as values.

    def id_string(id_int):
        return f"{tag}-{id_int}"

    # Determine how to uniquely identify the referenced item
    if isinstance(item, schema.ExternalReference):
        item_hash = hash(str(item.target_url))
    else:
        # TODO: This may become a performance issue. It means that every
        #       non-ref object is serialized to json and hashed each time it's
        #       encountered.
        item_hash = hash(
            core.serialize_json_to_string(item)
        )

    is_new_id = False
    item_id = br_map.get(tag, {}).get(item_hash)
    if item_id is not None:
        return (id_string(item_id), is_new_id)

    # This is a new id, figure out what it should be.
    is_new_id = True

    # Attempt to preserve the ID from the input metadata.
    preferred_id = None
    orig_id_string = item.metadata.get(META_NAMESPACE, {}).get("@id")
    if orig_id_string is not None:
        orig_id_match = ID_RE.match(orig_id_string)
        if orig_id_match is not None:
            match_groups = orig_id_match.groupdict()
            orig_tagname = match_groups["tag"]
            if orig_tagname == tag:
                preferred_id = int(match_groups["id"])

    # Generate an id by finding the lowest value in a contiguous range not
    # colliding with an existing value
    tag_id_map = br_map.setdefault(tag, {})
    existing_ids = set(tag_id_map.values())
    if preferred_id is not None and preferred_id not in existing_ids:
        item_id = preferred_id
    else:
        # Make a range from 1 including the ID after the largest assigned
        # (hence the +2 since range is non-inclusive on the upper bound)
        max_assigned_id = max(existing_ids) if existing_ids else 0
        max_possible_id = (max_assigned_id + 2)
        possible_ids = set(range(1, max_possible_id))

        # Select the lowest unassigned ID
        item_id = min(possible_ids.difference(existing_ids))

    # Store the created id
    tag_id_map[item_hash] = item_id

    return (id_string(item_id), is_new_id)


def _backreference_build(tag):
    """
    A decorator for functions creating XML elements to implement the id system
    described in FCP XML.

    This wrapper determines if the otio item is equivalent to one encountered
    before with the provided tag name. If the item hasn't been encountered then
    the wrapped function will be invoked and the XML element from that function
    will have the ``id`` attribute set and be stored in br_map.
    If the item is equivalent to a previously provided item, the wrapped
    function won't be invoked and a simple tag with the previous instance's id
    will be returned instead.

    The wrapped function must:
        - Have the otio item as the first positional argument.
        - Have br_map (backreference map, a dictionary) as the last positional
        arg. br_map stores the state for encountered items.

    :param tag: The xml tag of the element the wrapped function generates.
    """
    # We can also encode these back-references if an item is accessed multiple
    # times. To do this we store an id attribute on the element. For back-
    # references we then only need to return an empty element of that type with
    # the id we logged before

    def singleton_decorator(func):
        @functools.wraps(func)
        def wrapper(item, *args, **kwargs):
            if "br_map" in kwargs:
                br_map = kwargs["br_map"]
            else:
                br_map = args[-1]

            item_id, id_is_new = _backreference_for_item(item, tag, br_map)

            # if the item exists in the map already, we should use the
            # abbreviated XML element referring to the original
            if not id_is_new:
                return cElementTree.Element(tag, id=item_id)

            # This is the first time for this unique item, it needs it's full
            # XML. Get the element generated by the wrapped function and add
            # the id attribute.
            elem = func(item, *args, **kwargs)
            elem.attrib["id"] = item_id

            return elem

        return wrapper

    return singleton_decorator


def _append_new_sub_element(parent, tag, attrib=None, text=None):
    """
    Creates a sub-element with the provided tag, attributes, and text.

    This is a convenience because the :class: `SubElement` constructor does not
    provide the ability to set ``text``.

    :param parent: The parent element.
    :param tag: The tag string for the element.
    :param attrib: An optional dictionary of attributes for the element.
    :param text: Optional text value for the element.

    :return: The new XML element.
    """
    elem = cElementTree.SubElement(parent, tag, **attrib or {})
    if text is not None:
        elem.text = text

    return elem


def _build_rate(fps):
    """
    Given a framerate, makes a ``rate`` xml tree.

    :param fps: The framerate.
    :return: The fcp xml ``rate`` tree.
    """
    rate = math.ceil(fps)

    rate_e = cElementTree.Element('rate')
    _append_new_sub_element(rate_e, 'timebase', text=str(int(rate)))
    _append_new_sub_element(
        rate_e,
        'ntsc',
        text='FALSE' if rate == fps else 'TRUE'
    )
    return rate_e


def _build_timecode(time, fps, drop_frame=False, additional_metadata=None):
    """
    Makes a timecode xml element tree.

    .. warning:: The drop_frame parameter is currently ignored and
        auto-determined by rate. This is because the underlying otio timecode
        conversion assumes DFTC based on rate.

    :param time: The :class: `opentime.RationalTime` for the timecode.
    :param fps: The framerate for the timecode.
    :param drop_frame: If True, generates drop-frame timecode.
    :param additional_metadata: A dictionary with other metadata items like
        ``field``, ``reel``, ``source``, and ``format``. It is assumed this
        dictionary is of the form generated by :func:`_xml_tree_to_dict` when
        the file was read originally.

    :return: The ``timecode`` element.
    """

    if additional_metadata:
        # Only allow legal child items for the timecode element
        filtered = {
            k: v for k, v in additional_metadata.items()
            if k in ("field", "reel", "source", "format")
        }
        tc_element = _dict_to_xml_tree(filtered, "timecode")
    else:
        tc_element = cElementTree.Element("timecode")

    tc_element.append(_build_rate(fps))
    rate_is_not_ntsc = (tc_element.find('./rate/ntsc').text == "FALSE")
    if drop_frame and rate_is_not_ntsc:
        tc_fps = fps * (1000 / 1001.0)
    else:
        tc_fps = fps

    # Get the time values
    tc_time = opentime.RationalTime(time.value_rescaled_to(fps), tc_fps)
    tc_string = opentime.to_timecode(tc_time, tc_fps, drop_frame)

    _append_new_sub_element(tc_element, "string", text=tc_string)

    frame_number = int(round(time.value))
    _append_new_sub_element(
        tc_element, "frame", text=f"{frame_number:.0f}"
    )

    drop_frame = (";" in tc_string)
    display_format = "DF" if drop_frame else "NDF"
    _append_new_sub_element(tc_element, "displayformat", text=display_format)

    return tc_element


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
    source_start = (item.source_range.start_time - timecode)
    source_start = source_start.rescaled_to(item_rate)

    source_end = (item.source_range.end_time_exclusive() - timecode)
    source_end = source_end.rescaled_to(item_rate)

    start = f'{timeline_range.start_time.value:.0f}'
    end = f'{timeline_range.end_time_exclusive().value:.0f}'

    item_e.append(_build_rate(item_rate))

    if transition_offsets[0] is not None:
        start = '-1'
        source_start -= transition_offsets[0]
    if transition_offsets[1] is not None:
        end = '-1'
        source_end += transition_offsets[1]

    _append_new_sub_element(
        item_e, 'duration',
        text=f'{item.source_range.duration.value:.0f}'
    )
    _append_new_sub_element(item_e, 'start', text=start)
    _append_new_sub_element(item_e, 'end', text=end)
    _append_new_sub_element(
        item_e,
        'in',
        text=f'{source_start.value:.0f}'
    )
    _append_new_sub_element(
        item_e,
        'out',
        text=f'{source_end.value:.0f}'
    )


@_backreference_build('file')
def _build_empty_file(media_ref, parent_range, br_map):
    file_e = _element_with_item_metadata("file", media_ref)
    _append_new_sub_element(file_e, "name", text=media_ref.name)

    if media_ref.available_range is not None:
        available_range = media_ref.available_range
    else:
        available_range = opentime.TimeRange(
            opentime.RationalTime(0, parent_range.start_time.rate),
            parent_range.duration,
        )

    ref_rate = available_range.start_time.rate
    file_e.append(_build_rate(ref_rate))

    # Only provide a duration if one came from the media, don't invent one.
    # For example, Slugs have no duration specified.
    if media_ref.available_range:
        duration = available_range.duration.rescaled_to(ref_rate)
        _append_new_sub_element(
            file_e,
            'duration',
            text=f'{duration.value:.0f}',
        )

    # timecode
    ref_tc_metadata = media_ref.metadata.get(META_NAMESPACE, {}).get(
        "timecode"
    )
    tc_element = _build_timecode_from_metadata(
        available_range.start_time, ref_tc_metadata
    )
    file_e.append(tc_element)

    file_media_e = _get_or_create_subelement(file_e, "media")
    if file_media_e.find("video") is None:
        _append_new_sub_element(file_media_e, "video")

    return file_e


@_backreference_build('file')
def _build_file(media_reference, br_map):
    file_e = _element_with_item_metadata("file", media_reference)

    available_range = media_reference.available_range

    # If the media reference is of one of the supported types, populate
    # the appropriate source info element
    if isinstance(media_reference, schema.ExternalReference):
        _append_new_sub_element(
            file_e, 'pathurl', text=media_reference.target_url
        )
        url_path = _url_to_path(media_reference.target_url)

        fallback_file_name = (
            media_reference.name if media_reference.name
            else os.path.basename(url_path)
        )
    elif isinstance(media_reference, schema.GeneratorReference):
        _append_new_sub_element(
            file_e, 'mediaSource', text=media_reference.generator_kind
        )
        fallback_file_name = media_reference.generator_kind

    _append_new_sub_element(
        file_e,
        'name',
        text=(media_reference.name or fallback_file_name),
    )

    # timing info
    file_e.append(_build_rate(available_range.start_time.rate))
    _append_new_sub_element(
        file_e, 'duration',
        text=f'{available_range.duration.value:.0f}'
    )

    # timecode
    ref_tc_metadata = media_reference.metadata.get(META_NAMESPACE, {}).get(
        "timecode"
    )
    tc_element = _build_timecode_from_metadata(
        available_range.start_time, ref_tc_metadata
    )
    file_e.append(tc_element)

    # we need to flag the file reference with the content types, otherwise it
    # will not get recognized
    # TODO: We should use a better method for this. Perhaps pre-walk the
    #       timeline and find all the track kinds this media is present in?
    if not file_e.find("media"):
        file_media_e = _get_or_create_subelement(file_e, "media")

        audio_exts = {'.wav', '.aac', '.mp3', '.aif', '.aiff', '.m4a'}
        has_video = (os.path.splitext(url_path)[1].lower() not in audio_exts)
        if has_video and file_media_e.find("video") is None:
            _append_new_sub_element(file_media_e, "video")

        # TODO: This is assuming all files have an audio track. Not sure what
        # the implications of that are.
        if file_media_e.find("audio") is None:
            _append_new_sub_element(file_media_e, "audio")

    return file_e


def _build_transition_item(
    transition_item,
    timeline_range,
    transition_offsets,
    br_map,
):
    transition_e = _element_with_item_metadata(
        "transitionitem", transition_item
    )
    _append_new_sub_element(
        transition_e,
        'start',
        text=f'{timeline_range.start_time.value:.0f}'
    )
    _append_new_sub_element(
        transition_e,
        'end',
        text=f'{timeline_range.end_time_exclusive().value:.0f}'
    )

    # Only add an alignment if it didn't already come in from the metadata dict
    if transition_e.find("alignment") is None:
        # default center aligned
        alignment = "center"
        if not transition_item.in_offset.value:
            alignment = 'start-black'
        elif not transition_item.out_offset.value:
            alignment = 'end-black'

        _append_new_sub_element(transition_e, 'alignment', text=alignment)
        # todo support 'start' and 'end' alignment

    transition_e.append(_build_rate(timeline_range.start_time.rate))

    # Only add an effect if it didn't already come in from the metadata dict
    if not transition_e.find("./effect"):
        try:
            effectid = transition_item.metadata[META_NAMESPACE]["effectid"]
        except KeyError:
            effectid = "Cross Dissolve"

        effect_e = _append_new_sub_element(transition_e, 'effect')
        _append_new_sub_element(effect_e, 'name', text=transition_item.name)
        _append_new_sub_element(effect_e, 'effectid', text=effectid)
        _append_new_sub_element(effect_e, 'effecttype', text='transition')
        _append_new_sub_element(effect_e, 'mediatype', text='video')

    return transition_e


@_backreference_build("clipitem")
def _build_clip_item_without_media(
    clip_item,
    timeline_range,
    transition_offsets,
    br_map,
):
    # TODO: Does this need to be a separate function or could it be unified
    #       with _build_clip_item?
    clip_item_e = _element_with_item_metadata("clipitem", clip_item)
    if "frameBlend" not in clip_item_e.attrib:
        clip_item_e.attrib["frameBlend"] = "FALSE"

    if clip_item.media_reference.available_range:
        media_start_time = clip_item.media_reference.available_range.start_time
    else:
        media_start_time = opentime.RationalTime(
            0, timeline_range.start_time.rate
        )

    _append_new_sub_element(clip_item_e, 'name', text=clip_item.name)
    clip_item_e.append(
        _build_empty_file(
            clip_item.media_reference, timeline_range, br_map
        )
    )
    clip_item_e.extend([_build_marker(m) for m in clip_item.markers])

    _build_item_timings(
        clip_item_e,
        clip_item,
        timeline_range,
        transition_offsets,
        media_start_time,
    )

    return clip_item_e


@_backreference_build("clipitem")
def _build_clip_item(clip_item, timeline_range, transition_offsets, br_map):
    # This is some wacky logic, but here's why:
    # Pretty much any generator from Premiere just reports as being a clip that
    # uses Slug as mediaSource rather than a pathurl (color matte seems to be
    # the exception). I think this is becasue it is aiming to roundtrip effects
    # with itself rather than try to make them backward compatable with FCP 7.
    # This allows Premiere generators to still come in as slugs and still exist
    # as placeholders for effects that may not have a true analog in FCP 7.
    # Since OTIO does not yet interpret these generators into specific
    # first-class schema objects (e.x. color matte, bars, etc.), the
    # "artificial" mediaSources on clipitem and generatoritem both interpret as
    # generator references. So, for the moment, to detect if likely have the
    # metadata to make an fcp 7 style generatoritem we look for the effecttype
    # field, if that is missing we write the generator using mediaSource in the
    # Premiere Pro style.
    # This adapter is currently built to effectively round-trip and let savvy
    # users push the correct data into the metadata dictionary to drive
    # behavior, but in the future when there are specific generator schema in
    # otio we could  correctly translate a first-class OTIO generator concept
    # into an equivalent FCP 7 generatoritem or a Premiere Pro style overloaded
    # clipitem.
    is_generator = isinstance(
        clip_item.media_reference, schema.GeneratorReference
    )

    media_ref_fcp_md = clip_item.media_reference.metadata.get('fcp_xml', {})
    is_generatoritem = (
        is_generator and 'effecttype' in media_ref_fcp_md
    )

    tagname = "generatoritem" if is_generatoritem else "clipitem"
    clip_item_e = _element_with_item_metadata(tagname, clip_item)
    if "frameBlend" not in clip_item_e.attrib:
        clip_item_e.attrib["frameBlend"] = "FALSE"

    if is_generatoritem:
        clip_item_e.append(_build_generator_effect(clip_item, br_map))
    else:
        clip_item_e.append(_build_file(clip_item.media_reference, br_map))

    # set the clip name from the media reference if not defined on the clip
    if clip_item.name is not None:
        name = clip_item.name
    elif is_generator:
        name = clip_item.media_reference.name
    else:
        url_path = _url_to_path(clip_item.media_reference.target_url)
        name = os.path.basename(url_path)

    _append_new_sub_element(clip_item_e, 'name', text=name)

    if clip_item.media_reference.available_range:
        clip_item_e.append(
            _build_rate(clip_item.source_range.start_time.rate)
        )
    clip_item_e.extend(_build_marker(m) for m in clip_item.markers)

    if clip_item.media_reference.available_range:
        timecode = clip_item.media_reference.available_range.start_time
    else:
        timecode = opentime.RationalTime(
            0, clip_item.source_range.start_time.rate
        )

    _build_item_timings(
        clip_item_e,
        clip_item,
        timeline_range,
        transition_offsets,
        timecode
    )

    return clip_item_e


def _build_generator_effect(clip_item, br_map):
    """
    Builds an effect element for the generator ref on the provided clip item.

    :param clip_item: a clip with a :class: `schema.GeneratorReference` as
        its ``media_reference``.
    :param br_map: The backreference map.
    """
    # Since we don't support effects in a standard way, just try and build
    # based on the metadata provided at deserialization so we can roundtrip
    generator_ref = clip_item.media_reference
    try:
        fcp_xml_effect_info = generator_ref.metadata[META_NAMESPACE]
    except KeyError:
        return _build_empty_file(
            generator_ref,
            clip_item.source_range,
            br_map,
        )

    # Get the XML Tree built from the metadata
    effect_element = _dict_to_xml_tree(fcp_xml_effect_info, "effect")

    # Validate the metadata and make sure it contains the required elements
    for required in ("effecttype", "mediatype", "effectcategory"):
        if effect_element.find(required) is None:
            return _build_empty_file(
                generator_ref,
                clip_item.source_range,
                br_map,
            )

    # Add the name
    _append_new_sub_element(effect_element, "name", text=generator_ref.name)
    _append_new_sub_element(
        effect_element, "effectid", text=generator_ref.generator_kind
    )

    return effect_element


@_backreference_build("clipitem")
def _build_track_item(track, timeline_range, transition_offsets, br_map):
    clip_item_e = _element_with_item_metadata("clipitem", track)
    if "frameBlend" not in clip_item_e.attrib:
        clip_item_e.attrib["frameBlend"] = "FALSE"

    _append_new_sub_element(
        clip_item_e,
        'name',
        text=os.path.basename(track.name)
    )

    track_e = _build_sequence_for_stack(track, timeline_range, br_map)

    clip_item_e.append(_build_rate(track.source_range.start_time.rate))
    clip_item_e.extend([_build_marker(m) for m in track.markers])
    clip_item_e.append(track_e)
    timecode = opentime.RationalTime(0, timeline_range.start_time.rate)

    _build_item_timings(
        clip_item_e,
        track,
        timeline_range,
        transition_offsets,
        timecode
    )

    return clip_item_e


def _build_item(item, timeline_range, transition_offsets, br_map):
    if isinstance(item, schema.Transition):
        return _build_transition_item(
            item,
            timeline_range,
            transition_offsets,
            br_map
        )
    elif isinstance(item, schema.Clip):
        if isinstance(
            item.media_reference,
            schema.MissingReference
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
    elif isinstance(item, schema.Stack):
        return _build_track_item(
            item,
            timeline_range,
            transition_offsets,
            br_map
        )
    else:
        raise ValueError('Unsupported item: ' + str(item))


def _build_top_level_track(track, track_rate, br_map):
    track_e = _element_with_item_metadata("track", track)

    for n, item in enumerate(track):
        if isinstance(item, schema.Gap):
            continue

        transition_offsets = [None, None]
        previous_item = track[n - 1] if n > 0 else None
        next_item = track[n + 1] if n + 1 < len(track) else None
        if not isinstance(item, schema.Transition):
            # find out if this item has any neighboring transition
            if isinstance(previous_item, schema.Transition):
                if previous_item.out_offset.value:
                    transition_offsets[0] = previous_item.in_offset
                else:
                    transition_offsets[0] = None
            if isinstance(next_item, schema.Transition):
                if next_item.in_offset.value:
                    transition_offsets[1] = next_item.out_offset
                else:
                    transition_offsets[1] = None

        timeline_range = track.range_of_child_at_index(n)
        timeline_range = opentime.TimeRange(
            timeline_range.start_time.rescaled_to(track_rate),
            timeline_range.duration.rescaled_to(track_rate)
        )
        track_e.append(
            _build_item(item, timeline_range, transition_offsets, br_map)
        )

    return track_e


def _build_marker(marker):
    marker_e = _element_with_item_metadata("marker", marker)

    marked_range = marker.marked_range

    _append_new_sub_element(marker_e, 'name', text=marker.name)
    _append_new_sub_element(
        marker_e, 'in',
        text=f'{marked_range.start_time.value:.0f}'
    )
    _append_new_sub_element(
        marker_e, 'out',
        text='{:.0f}'.format(
            marked_range.start_time.value + marked_range.duration.value
        )
    )

    return marker_e


def _build_timecode_from_metadata(time, tc_metadata=None):
    """
    Makes a timecode element with the given time and (if available)
    ```timecode`` metadata stashed on input.

    :param time: The :class: `opentime.RationalTime` to encode.
    :param tc_metadata: The xml dict for the ``timecode`` element populated
        on read.

    :return: A timecode element.
    """
    if tc_metadata is None:
        tc_metadata = {}

    try:

        # Parse the rate in the preserved metadata, if available
        tc_rate = _otio_rate(
            tc_metadata["timebase"], _bool_value(tc_metadata["ntsc"])
        )
    except KeyError:
        # Default to the rate in the start time
        tc_rate = time.rate

    drop_frame = (tc_metadata.get("displayformat", "NDF") == "DF")

    return _build_timecode(
        time,
        tc_rate,
        drop_frame,
        additional_metadata=tc_metadata,
    )


@_backreference_build('sequence')
def _build_sequence_for_timeline(timeline, timeline_range, br_map):
    sequence_e = _element_with_item_metadata("sequence", timeline)

    _add_stack_elements_to_sequence(
        timeline.tracks, sequence_e, timeline_range, br_map
    )

    # In the case of timelines, use the timeline name rather than the stack
    # name.
    if timeline.name:
        sequence_e.find('./name').text = timeline.name

    # Add the sequence global start
    if timeline.global_start_time is not None:
        seq_tc_metadata = timeline.metadata.get(META_NAMESPACE, {}).get(
            "timecode"
        )
        tc_element = _build_timecode_from_metadata(
            timeline.global_start_time, seq_tc_metadata
        )
        sequence_e.append(tc_element)

    return sequence_e


@_backreference_build('sequence')
def _build_sequence_for_stack(stack, timeline_range, br_map):
    sequence_e = _element_with_item_metadata("sequence", stack)

    _add_stack_elements_to_sequence(stack, sequence_e, timeline_range, br_map)

    return sequence_e


def _add_stack_elements_to_sequence(stack, sequence_e, timeline_range, br_map):
    _append_new_sub_element(sequence_e, 'name', text=stack.name)
    _append_new_sub_element(
        sequence_e, 'duration',
        text=f'{timeline_range.duration.value:.0f}'
    )
    sequence_e.append(_build_rate(timeline_range.start_time.rate))
    track_rate = timeline_range.start_time.rate

    media_e = _get_or_create_subelement(sequence_e, "media")
    video_e = _get_or_create_subelement(media_e, 'video')
    audio_e = _get_or_create_subelement(media_e, 'audio')

    # This is a fix for Davinci Resolve. After the "video" tag, it expects
    # a <format> tag, even if empty. See issue 839
    _get_or_create_subelement(video_e, "format")

    # XXX: Due to the way that backreferences are created later on, the XML
    #      is assumed to have its video tracks serialized before its audio
    #      tracks.  Because the order that they are added to the media is
    #      dependent on what order the metadata is in in the fcp_xml metadata
    #      (as a previous function is usually creating them), this code
    #      enforces the order.
    media_e.clear()
    media_e.extend([video_e, audio_e])

    for track in stack:
        track_elements = _build_top_level_track(track, track_rate, br_map)
        if track.kind == schema.TrackKind.Video:
            video_e.append(track_elements)
        elif track.kind == schema.TrackKind.Audio:
            audio_e.append(track_elements)

    for marker in stack.markers:
        sequence_e.append(_build_marker(marker))


def _build_collection(collection, br_map):
    tracks = []
    for item in collection:
        if not isinstance(item, schema.Timeline):
            continue

        timeline_range = opentime.TimeRange(
            start_time=item.global_start_time,
            duration=item.duration()
        )
        tracks.append(
            _build_sequence_for_timeline(item, timeline_range, br_map)
        )

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
        return schema.SerializableCollection(
            name="Sequences",
            children=sequences,
        )
    else:
        raise ValueError('No top-level sequences found')


def write_to_string(input_otio):
    tree_e = cElementTree.Element('xmeml', version="4")
    project_e = _append_new_sub_element(tree_e, 'project')
    _append_new_sub_element(project_e, 'name', text=input_otio.name)
    children_e = _append_new_sub_element(project_e, 'children')

    br_map = collections.defaultdict(dict)

    if isinstance(input_otio, schema.Timeline):
        timeline_range = opentime.TimeRange(
            start_time=input_otio.global_start_time,
            duration=input_otio.duration()
        )
        children_e.append(
            _build_sequence_for_timeline(
                input_otio, timeline_range, br_map
            )
        )
    elif isinstance(input_otio, schema.SerializableCollection):
        children_e.extend(
            _build_collection(input_otio, br_map)
        )

    return _make_pretty_string(tree_e)
