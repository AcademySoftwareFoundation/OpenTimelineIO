"""
Adapter that prints to string.
"""
import io

import opentimelineio as otio

# @TODO: add a unit test for this


def timing_info_as_timecode(ti):
    try:
        return "[{}, {}]".format(
            otio.opentime.to_timecode(ti.start_time),
            otio.opentime.to_timecode(ti.duration),
        )
    except KeyError:
        return "{}"


def write_to_string(input_otio):
    return from_base_object(input_otio.tracks) + "\n"


def from_base_object(base_object, indent=0):
    lines = [""]

    indent_str = " " * indent

    try:
        lines.append("{}name: {}".format(indent_str, base_object.name))
    except KeyError:
        pass

    indent_str = " " * (indent + 2)

    lines.append(
        "{}source_range: {}".format(indent_str, base_object.source_range)
    )

    if hasattr(base_object, "media_reference"):
        lines.append(
            "{}source range: {}".format(
                indent_str,
                timing_info_as_timecode(base_object.source_range)
            )
        )

    parent_indent = indent_str
    indent_str = indent_str + 2 * " "

    lines.append("{}metadata: ".format(parent_indent))
    for key, val in base_object.metadata.items():
        lines.append("{}{}: {}".format(indent_str, key, str(val)))

    if hasattr(base_object, "children"):
        lines.append("{}children: ".format(parent_indent))
        children = base_object.children
        lines.append(
            "{}composition kind: {}".format(
                indent_str,
                base_object.composition_kind
            )
        )

        for i, child in enumerate(children):
            lines.append(
                "{}child {}: {}".format(
                    indent_str,
                    i,
                    from_base_object(child, indent + 8)
                )
            )
    if hasattr(base_object, "media_reference"):
        if "target_url" in base_object.media_reference.data:
            lines.append(
                "{}target file path: {}".format(
                    indent_str,
                    base_object.media_reference.data['target_url']
                )
            )

    result = io.StringIO()
    result.write('\n'.join(lines))
    return result.getvalue()
