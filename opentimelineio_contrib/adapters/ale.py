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

"""OpenTimelineIO Avid Log Exchange (ALE) Adapter"""

import opentimelineio as otio


class ALEParseError(otio.exceptions.OTIOError):
    pass


def _parse_data_line(line, columns, fps):
    row = line.split("\t")

    if len(row) < len(columns):
        # Fill in blanks for any missing fields in this row
        row.extend([""] * (len(columns) - len(row)))

    if len(row) > len(columns):
        raise ALEParseError("Too many values on row: "+line)

    try:

        # Gather all the columns into a dictionary
        # For expected columns, like Name, Start, etc. we will pop (remove)
        # those from metadata, leaving the rest alone.
        metadata = dict(zip(columns, row))

        clip = otio.schema.Clip()
        clip.name = metadata.pop("Name", None)

        # When looking for Start, Duration and End, they might be missing
        # or blank. Treat None and "" as the same via: get(k,"")!=""
        # To have a valid source range, you need Start and either Duration
        # or End. If all three are provided, we check to make sure they match.
        if metadata.get("Start", "") != "":
            value = metadata.pop("Start")
            try:
                start = otio.opentime.from_timecode(value, fps)
            except (ValueError, TypeError):
                raise ALEParseError("Invalid Start timecode: {}".format(value))
            duration = None
            end = None
            if metadata.get("Duration", "") != "":
                value = metadata.pop("Duration")
                try:
                    duration = otio.opentime.from_timecode(value, fps)
                except (ValueError, TypeError):
                    raise ALEParseError("Invalid Duration timecode: {}".format(
                        value
                    ))
            if metadata.get("End", "") != "":
                value = metadata.pop("End")
                try:
                    end = otio.opentime.from_timecode(value, fps)
                except (ValueError, TypeError):
                    raise ALEParseError("Invalid End timecode: {}".format(
                        value
                    ))
            if duration is None:
                duration = end - start
            if end is None:
                end = start + duration
            if end != start + duration:
                raise ALEParseError("Inconsistent Start, End, Duration: "+line)
            clip.source_range = otio.opentime.TimeRange(
                start,
                duration
            )

        if metadata.get("Source File"):
            source = metadata.pop("Source File")
            clip.media_reference = otio.schema.ExternalReference(
                target_url=source
            )

        # We've pulled out the key/value pairs that we treat specially.
        # Put the remaining key/values into clip.metadata["ALE"]
        clip.metadata["ALE"] = metadata

        return clip
    except Exception as ex:
        raise ALEParseError("Error parsing line: {}\n{}".format(
            line, repr(ex)
        ))


def read_from_string(input_str, fps=24):

    collection = otio.schema.SerializableCollection()
    header = {}
    columns = []

    def nextline(lines):
        return lines.pop(0)

    lines = input_str.splitlines()
    while len(lines):
        line = nextline(lines)

        # skip blank lines
        if line.strip() == "":
            continue

        if line.strip() == "Heading":
            while len(lines):
                line = nextline(lines)

                if line.strip() == "":
                    break

                if "\t" not in line:
                    raise ALEParseError("Invalid Heading line: "+line)

                segments = line.split("\t")
                while len(segments) >= 2:
                    key, val = segments.pop(0), segments.pop(0)
                    header[key] = val
                if len(segments) != 0:
                    raise ALEParseError("Invalid Heading line: "+line)

        if "FPS" in header:
            fps = float(header["FPS"])

        if line.strip() == "Column":
            if len(lines) == 0:
                raise ALEParseError("Unexpected end of file after: "+line)

            line = nextline(lines)
            columns = line.split("\t")

        if line.strip() == "Data":
            while len(lines):
                line = nextline(lines)

                if line.strip() == "":
                    continue

                clip = _parse_data_line(line, columns, fps)

                collection.append(clip)

    collection.metadata["ALE"] = {
        "header": header,
        "columns": columns
    }

    return collection


def write_to_string(input_otio, columns=None, fps=None):

    result = ""

    result += "Heading\n"
    header = dict(input_otio.metadata.get("ALE", {}).get("header", {}))

    # Force this, since we've hard coded tab delimiters
    header["FIELD_DELIM"] = "TABS"

    if fps is None:
        # If we weren't given a FPS, is there one in the header metadata?
        if "FPS" in header:
            fps = float(header["FPS"])
        else:
            # Would it be better to infer this by inspecting the input clips?
            fps = 24
            header["FPS"] = str(fps)
    else:
        # Put the value we were given into the header
        header["FPS"] = str(fps)

    headers = list(header.items())
    headers.sort()  # make the output predictable
    for key, val in headers:
        result += "{}\t{}\n".format(key, val)

    # Get all the clips we're going to export
    clips = list(input_otio.each_clip())

    # If the caller passed in a list of columns, use that, otherwise
    # we need to discover the columns that should be output.
    if columns is None:
        # Is there a hint about the columns we want (and column ordering)
        # at the top level?
        columns = input_otio.metadata.get("ALE", {}).get("columns", [])

        # Scan all the clips for any extra columns
        for clip in clips:
            fields = clip.metadata.get("ALE", {})
            for key in fields.keys():
                if key not in columns:
                    columns.append(key)

    # Always output these
    for c in ["Duration", "End", "Start", "Name", "Source File"]:
        if c not in columns:
            columns.insert(0, c)

    result += "\nColumn\n{}\n".format("\t".join(columns))

    result += "\nData\n"

    def val_for_column(column, clip):
        if column == "Name":
            return clip.name
        elif column == "Source File":
            if (
                clip.media_reference and
                hasattr(clip.media_reference, 'target_url') and
                clip.media_reference.target_url
            ):
                return clip.media_reference.target_url
            else:
                return ""
        elif column == "Start":
            if not clip.source_range:
                return ""
            return otio.opentime.to_timecode(
                clip.source_range.start_time, fps
            )
        elif column == "Duration":
            if not clip.source_range:
                return ""
            return otio.opentime.to_timecode(
                clip.source_range.duration, fps
            )
        elif column == "End":
            if not clip.source_range:
                return ""
            return otio.opentime.to_timecode(
                clip.source_range.end_time_exclusive(), fps
            )
        else:
            return clip.metadata.get("ALE", {}).get(column)

    for clip in clips:
        row = []
        for column in columns:
            val = str(val_for_column(column, clip) or "")
            val.replace("\t", " ")  # don't allow tabs inside a value
            row.append(val)
        result += "\t".join(row) + "\n"

    return result
