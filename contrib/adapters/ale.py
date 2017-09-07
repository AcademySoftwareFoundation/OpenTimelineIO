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


def read_from_string(input_str, fps=24):

    collection = otio.schema.SerializableCollection()
    header = {}
    columns = []

    lines = input_str.split("\n")
    while len(lines):
        line = lines.pop(0)

        # skip blank lines
        if line.strip() == "":
            continue

        if line.strip() == "Heading":
            while len(lines):
                line = lines.pop(0)

                if line.strip() == "":
                    break

                if "\t" not in line:
                    raise ALEParseError("Invalid Heading line: "+line)

                line = line.strip('\r')
                segments = line.split("\t")
                while len(segments)>=2:
                    key, val = segments.pop(0), segments.pop(0)
                    header[key] = val
                if len(segments)!=0:
                    raise ALEParseError("Invalid Heading line: "+line)

        if "FPS" in header:
            fps = float(header["FPS"])

        if line.strip() == "Column":
            if len(lines) == 0:
                raise ALEParseError("Unexpected end of file after: "+line)

            line = lines.pop(0)
            columns = line.split("\t")

        if line.strip() == "Data":
            while len(lines):
                line = lines.pop(0)

                if line.strip() == "":
                    continue

                row = line.split("\t")

                if len(row) < len(columns):
                    raise ALEParseError("Too few values on row: "+line)

                if len(row) > len(columns):
                    raise ALEParseError("Too many values on row: "+line)

                metadata = dict(zip(columns, row))

                clip = otio.schema.Clip()
                clip.name = metadata.get("Name")
                del metadata["Name"]

                if "Start" in metadata:
                    start = otio.opentime.from_timecode(metadata["Start"], fps)
                    del metadata["Start"]
                    duration = None
                    end = None
                    if "Duration" in metadata:
                        duration = otio.opentime.from_timecode(
                            metadata["Duration"], fps
                        )
                        del metadata["Duration"]
                    if "End" in metadata:
                        end = otio.opentime.from_timecode(metadata["End"], fps)
                        del metadata["End"]
                    if duration is None:
                        duration = end - start
                    if end is None:
                        end = start + duration
                    if end != start + duration:
                        raise ALEParseError(
                            "Inconsistent Start, End, Duration: "+line
                        )
                    clip.source_range = otio.opentime.TimeRange(
                        start,
                        duration
                    )

                clip.metadata["ALE"] = metadata

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
    for c in ["Duration", "End", "Start", "Name"]:
        if c not in columns:
            columns.insert(0, c)

    result += "\nColumn\n{}\n".format("\t".join(columns))

    result += "\nData\n"

    def val_for_column(column, clip):
        if column == "Name":
            return clip.name
        elif column == "Start":
            return otio.opentime.to_timecode(
                clip.source_range.start_time, fps
            )
        elif column == "Duration":
            return otio.opentime.to_timecode(
                clip.source_range.duration, fps
            )
        elif column == "End":
            return otio.opentime.to_timecode(
                clip.source_range.end_time_exclusive(), fps
            )
        else:
            return clip.metadata.get("ALE", {}).get(column)

    for clip in clips:
        row = []
        for column in columns:
            val = val_for_column(column, clip) or ""
            val.replace("\t", " ")  # don't allow tabs inside a value
            row.append(val)
        result += "\t".join(row) + "\n"

    return result
