"""

"""


# Python
import json
import logging

# OTIO
import math

import opentimelineio as otio

# RV
try:
    import rv
except RuntimeError:
    raise Exception("otio_writer must be used in an RV context/plugin.")


class NoMappingForNodeTypeError(otio.exceptions.OTIOError):
    pass


# RV min-int, max-int
MIN_INT = int(rv.runtime.eval("int.min;", []))
MAX_INT = int(rv.runtime.eval("int.max;", []))

DEFAULT_FPS = 24.0


# TODO Currently, OTIO only supports Dissolves
TRANSITION_TYPE_MAP = {
#     "CrossDissolve": otio.schema.transition.TransitionTypes.SMPTE_Dissolve
}


def create_otio_from_rv_node(node_name, *args, **kwargs):
    """
    Create an OTIO Timeline instance from a given RV node.
    :param node_name: `str`
    :return: `otio.schema.*`
    """
    create_type_map = {
        "RVSequenceGroup": _create_track,
        "RVStackGroup": _create_stack,
        "RVSourceGroup": _create_item,
        "CrossDissolve": _create_transition
    }

    node_type = rv.commands.nodeType(node_name)
    if node_type in create_type_map:
        return create_type_map[node_type](node_name, *args, **kwargs)

    raise NoMappingForNodeTypeError(
        str(type(node_name)) + " on node: {}".format(node_name)
    )


def _create_timeline(node_name):
    """
    Create an OTIO Timeline for a given RVSequenceGroup.
    :param node_name: `str`
    :return: `otio.schema.Timeline`
    """
    return otio.schema.Timeline(
        name=get_node_ui_name(node_name),
        tracks=[_create_track(node_name)],
        metadata=get_node_otio_metadata(node_name)
    )


def _create_track(node_name):
    """
    Create an OTIO Track instance from an RVSequenceGroup.
    :param node_name: `str`
    :return: `otio.schema.Track`
    """
    track = otio.schema.Track(get_node_ui_name(node_name))
    input_node_names, _ = rv.commands.nodeConnections(node_name)

    # Set timing for Sequence elements
    seq_node = group_member_of_type(node_name, "RVSequence")
    edl = {
        "in_frame": rv.commands.getIntProperty(seq_node + ".edl.in"),
        "out_frame": rv.commands.getIntProperty(seq_node + ".edl.out"),
        "cut_in_frame": rv.commands.getIntProperty(seq_node + ".edl.frame"),
        "source": rv.commands.getIntProperty(seq_node + ".edl.source")
    }

    if edl["in_frame"] and edl["out_frame"] and edl["source"]:
        for edl_index, source_index in enumerate(edl["source"][:-1]):
            track.append(
                create_otio_from_rv_node(
                    input_node_names[source_index],
                    in_frame=edl["in_frame"][edl_index],
                    out_frame=edl["out_frame"][edl_index],
                    cut_in_frame=edl["cut_in_frame"][edl_index]
                )
            )
    else:
        for input_node_name in input_node_names:
            track.append(create_otio_from_rv_node(input_node_name))

    return track


def _create_stack(node_name, *args, **kwargs):
    """
    Create an OTIO Stack instance from an RVStackGroup.
    :param node_name: `str`
    :return: `otio.schema.Stack`
    """
    input_node_names, _ = rv.commands.nodeConnections(node_name)
    stack = otio.schema.Stack(get_node_ui_name(node_name))
    for input_node_name in input_node_names:
        stack.append(create_otio_from_rv_node(input_node_name))

    return stack


def _create_item(node_name, in_frame=None, out_frame=None, cut_in_frame=None):
    """
    Create an OTIO Clip or Gap for an RVSourceGroup.
    :param node_name: `str`
    :param in_frame: `int`
    :param out_frame: `int`
    :param cut_in_frame: `int`
    :return: `otio.schema.Clip` or `otio.schema.Gap`
    """
    source_node = (group_member_of_type(node_name, "RVFileSource") or
                   group_member_of_type(node_name, "RVImageSource"))
    source_path = rv.commands.getStringProperty(source_node + ".media.movie")[0]

    # Create TimeRange
    start_time, duration = frames_to_rational_times(
        start_frame=in_frame or get_source_start_frame(node_name),
        end_frame=out_frame or get_source_end_frame(node_name),
        fps=get_source_fps(node_name)
    )
    if start_time or duration:
        source_range = otio.opentime.TimeRange(
            start_time=start_time,
            duration=duration
        )
    else:
        duration = None
        source_range = None

    # Create OTIO Gap (for movieproc) or Clip (for movies or images)
    if source_path.endswith(".movieproc"):
        return otio.schema.Gap(
            name=get_node_ui_name(node_name),
            source_range=source_range,
            metadata=get_node_otio_metadata(node_name)
        )
    else:
        # Create the available range
        start_time, duration = frames_to_rational_times(
            start_frame=get_movie_first_frame(node_name),
            end_frame=get_movie_last_frame(node_name),
            fps=get_movie_fps(node_name)
        )
        available_range = otio.opentime.TimeRange(
            start_time=start_time,
            duration=duration
        )

        media_reference = otio.schema.ExternalReference(
            target_url=("file://" + source_path
                        if not source_path.startswith("file://")
                        else source_path),
            available_range=available_range,
            metadata=get_node_otio_metadata(source_node)
        )
        media_reference.name = get_node_ui_name(node_name)
        metadata = get_node_otio_metadata(node_name) or {}
        metadata["RVSourceGroup"] = node_name
        return otio.schema.Clip(
            name=get_node_ui_name(node_name),
            media_reference=media_reference,
            source_range=source_range,
            metadata=metadata
        )


def _create_transition(node_name, in_frame=None, out_frame=None,
                       cut_in_frame=None):
    """
    Create an OTIO Transition for a CrossDissolve node.
    :param node_name: `str`
    :return: `otio.schema.Transition`
    """
    transition_type = TRANSITION_TYPE_MAP.get(
        rv.commands.nodeType(node_name),
        otio.schema.transition.TransitionTypes.Custom
    )
    if not transition_type:
        return None

    input_node_names, _ = rv.commands.nodeConnections(node_name)

    # Assume FPS matches first input (RV Transition don't have FPS settings)
    fps = get_source_fps(input_node_names[0])

    durations_frames = rv.commands.getFloatProperty(
        node_name + ".parameters.numFrames")
    if not durations_frames:
        duration_frames = 20.0
    else:
        duration_frames = durations_frames[0]

    in_offset_frames = int(math.floor(duration_frames/2))
    in_offset = otio.opentime.RationalTime(in_offset_frames, rate=fps)
    out_offset = otio.opentime.RationalTime(duration_frames-in_offset_frames,
                                            rate=fps)

    transition = otio.schema.Transition(
        name=get_node_ui_name(node_name),
        transition_type=transition_type,
        in_offset=in_offset,
        out_offset=out_offset,
        metadata=get_node_otio_metadata(node_name)
    )
    return transition


def get_node_ui_name(node_name):
    """
    Retrieve the value of the UI Name property for a node, if it exists.
    :param node_name: `str`
    :return: `str`
    """
    prop_name = node_name + ".ui.name"
    if rv.commands.propertyExists(prop_name):
        return rv.commands.getStringProperty(prop_name)[0]

    return None


def get_node_otio_metadata(node_name):
    """
    Retrieve the value of the OTIO Metadata property for a node, if it exists.
    This is set by otio_reader.py application plugin.
    :param node_name: `str`
    :return: `str`
    """
    prop_name = node_name + ".attributes.otio_metadata"
    if rv.commands.propertyExists(prop_name):
        metadata_str = rv.commands.getStringProperty(prop_name)[0]
        try:
            metadata = json.loads(metadata_str)
        except TypeError:
            logging.error("{} not JSON compatible type ('{}')".format(
                prop_name, type(metadata_str)))
        except ValueError:
            logging.error("{} not JSON ({}: '{}')".format(
                prop_name, type(metadata_str), metadata_str))
        else:
            return metadata

    return None


def frames_to_rational_times(start_frame, end_frame, fps):
    """
    Convert the start and end frames and fps to OTIO Rational Times.
    :param start_frame: `int`
    :param end_frame: `int`
    :param fps: `float`
    :return: (`opentimelineio.opentime.RationalTime`, `opentimelineio.opentime.RationalTime`)
    """
    if start_frame is None or end_frame is None or not fps:
        return None, None

    duration = end_frame - start_frame + 1
    return (otio.opentime.RationalTime(start_frame, rate=fps),
            otio.opentime.RationalTime(duration, rate=fps))


def get_source_start_frame(node_name):
    """
    Get start frame prop for an RVSourceGroup.
    :param node_name: `str`
    :return: `int`
    """
    source_node = (group_member_of_type(node_name, "RVFileSource") or
                   group_member_of_type(node_name, "RVImageSource"))
    start_frame = rv.commands.getIntProperty(source_node + ".cut.in")[0]

    # NOTE: RV's min int can vary by 1 -- https://support.shotgunsoftware.com/hc/en-us/requests/96213
    if start_frame == MIN_INT or start_frame == -MAX_INT:
        return None

    return start_frame


def get_source_end_frame(node_name):
    """
    Get end frame prop for an RVSourceGroup.
    :param node_name: `str`
    :return: `int`
    """
    source_node = (group_member_of_type(node_name, "RVFileSource") or
                   group_member_of_type(node_name, "RVImageSource"))
    end_frame = rv.commands.getIntProperty(source_node + ".cut.out")[0]
    return end_frame if end_frame != MAX_INT else None


def get_source_fps(node_name):
    """
    Get fps prop for an RVSourceGroup.
    :param node_name: `str`
    :return: `int`
    """
    file_source = group_member_of_type(node_name, "RVFileSource")
    if file_source:
        fps = rv.commands.getFloatProperty(file_source + ".group.fps")[0]

    image_source = group_member_of_type(node_name, "RVImageSource")
    if image_source:
        fps = rv.commands.getFloatProperty(image_source + ".image.fps")[0]

    # TODO Should we check for the Sequence FPS or global playback FPS?
    return fps or DEFAULT_FPS


def get_movie_first_frame(node_name):
    """
    Get first frame from the Media Info
    :param node_name: `str`
    :return: `int`
    """
    source_node = (group_member_of_type(node_name, "RVFileSource") or
                   group_member_of_type(node_name, "RVImageSource"))
    return rv.commands.sourceMediaInfo(source_node).get("startFrame")


def get_movie_last_frame(node_name):
    """
    Get lsst frame from the Media Info
    :param node_name: `str`
    :return: `int`
    """
    source_node = (group_member_of_type(node_name, "RVFileSource") or
                   group_member_of_type(node_name, "RVImageSource"))
    return rv.commands.sourceMediaInfo(source_node).get("endFrame")


def get_movie_fps(node_name):
    """
    Get fps from the Media Info
    :param node_name: `str`
    :return: `int`
    """
    source_node = (group_member_of_type(node_name, "RVFileSource") or
                   group_member_of_type(node_name, "RVImageSource"))
    return rv.commands.sourceMediaInfo(source_node).get("fps", DEFAULT_FPS)


def group_member_of_type(node, member_type):
    """
    Because it isn't RV code without group_member_of_type.
    :param node: `str`
    :param member_type: `str`
    :return: `str`
    """
    for n in rv.commands.nodesInGroup(node):
        if rv.commands.nodeType(n) == member_type:
            return n
    return None
