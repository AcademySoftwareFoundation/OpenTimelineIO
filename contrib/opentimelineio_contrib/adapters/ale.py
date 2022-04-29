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


__doc__ = """OpenTimelineIO Avid Log Exchange (ALE) Adapter"""


import re
import opentimelineio as otio

DEFAULT_VIDEO_FORMAT = '1080'
ASC_SOP_REGEX = re.compile(r'(-*\d+\.\d+)')


def AVID_VIDEO_FORMAT_FROM_WIDTH_HEIGHT(width, height):
    """Utility function to map a width and height to an Avid Project Format"""

    format_map = {
        '1080': "1080",
        '720': "720",
        '576': "PAL",
        '486': "NTSC",
    }
    mapped = format_map.get(str(height), "CUSTOM")
    # check for the 2K DCI 1080 format
    if mapped == '1080' and width > 1920:
        mapped = "CUSTOM"
    return mapped


class ALEParseError(otio.exceptions.OTIOError):
    pass


def _parse_data_line(line, columns, fps, ale_name_column_key='Name'):
    row = line.split("\t")

    if len(row) < len(columns):
        # Fill in blanks for any missing fields in this row
        row.extend([""] * (len(columns) - len(row)))

    if len(row) > len(columns):
        raise ALEParseError("Too many values on row: " + line)

    try:

        # Gather all the columns into a dictionary
        # For expected columns, like Name, Start, etc. we will pop (remove)
        # those from metadata, leaving the rest alone.
        metadata = dict(zip(columns, row))

        clip = otio.schema.Clip()
        clip.name = metadata.get(ale_name_column_key, '')

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
                raise ALEParseError(
                    "Inconsistent Start, End, Duration: " + line
                )
            clip.source_range = otio.opentime.TimeRange(
                start,
                duration
            )

        if metadata.get("Source File"):
            source = metadata.pop("Source File")
            clip.media_reference = otio.schema.ExternalReference(
                target_url=source
            )

        # If available, collect cdl values in the same way we do for CMX EDL
        cdl = {}

        if metadata.get('CDL'):
            cdl = _cdl_values_from_metadata(metadata['CDL'])
            if cdl:
                del metadata['CDL']

        # If we have more specific metadata, let's use them
        if metadata.get('ASC_SOP'):
            cdl = _cdl_values_from_metadata(metadata['ASC_SOP'])

            if cdl:
                del metadata['ASC_SOP']

        if metadata.get('ASC_SAT'):
            try:
                asc_sat_value = float(metadata['ASC_SAT'])
                cdl.update(asc_sat=asc_sat_value)
                del metadata['ASC_SAT']
            except ValueError:
                pass

        if cdl:
            clip.metadata['cdl'] = cdl

        # We've pulled out the key/value pairs that we treat specially.
        # Put the remaining key/values into clip.metadata["ALE"]
        clip.metadata["ALE"] = metadata

        return clip
    except Exception as ex:
        raise ALEParseError("Error parsing line: {}\n{}".format(
            line, repr(ex)
        ))


def _cdl_values_from_metadata(asc_sop_string):

    if not isinstance(asc_sop_string, (type(''), type(u''))):
        return {}

    asc_sop_values = ASC_SOP_REGEX.findall(asc_sop_string)

    cdl_data = {}

    if len(asc_sop_values) >= 9:

        cdl_data.update(
            asc_sop={
                'slope': [float(v) for v in asc_sop_values[:3]],
                'offset': [float(v) for v in asc_sop_values[3:6]],
                'power': [float(v) for v in asc_sop_values[6:9]]
            })

        if len(asc_sop_values) == 10:
            cdl_data.update(asc_sat=float(asc_sop_values[9]))

    return cdl_data


def _video_format_from_metadata(clips):
    # Look for clips with Image Size metadata set
    max_height = 0
    max_width = 0
    for clip in clips:
        fields = clip.metadata.get("ALE", {})
        res = fields.get("Image Size", "")
        m = re.search(r'([0-9]{1,})\s*[xX]\s*([0-9]{1,})', res)
        if m and len(m.groups()) >= 2:
            width = int(m.group(1))
            height = int(m.group(2))
            if height > max_height:
                max_height = height
            if width > max_width:
                max_width = width

    # We don't have any image size information, use the defaut
    if max_height == 0:
        return DEFAULT_VIDEO_FORMAT
    else:
        return AVID_VIDEO_FORMAT_FROM_WIDTH_HEIGHT(max_width, max_height)


def read_from_string(input_str, fps=24, **adapter_argument_map):
    ale_name_column_key = adapter_argument_map.get('ale_name_column_key', 'Name')

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
                    raise ALEParseError("Invalid Heading line: " + line)

                segments = line.split("\t")
                while len(segments) >= 2:
                    key, val = segments.pop(0), segments.pop(0)
                    header[key] = val
                if len(segments) != 0:
                    raise ALEParseError("Invalid Heading line: " + line)

        if "FPS" in header:
            fps = float(header["FPS"])

        if line.strip() == "Column":
            if len(lines) == 0:
                raise ALEParseError("Unexpected end of file after: " + line)

            line = nextline(lines)
            columns = line.split("\t")

        if line.strip() == "Data":
            while len(lines):
                line = nextline(lines)

                if line.strip() == "":
                    continue

                clip = _parse_data_line(line,
                                        columns,
                                        fps,
                                        ale_name_column_key=ale_name_column_key)

                collection.append(clip)

    collection.metadata["ALE"] = {
        "header": header,
        "columns": columns
    }

    return collection


def write_to_string(input_otio, columns=None, fps=None, video_format=None):

    # Get all the clips we're going to export
    clips = list(input_otio.each_clip())

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

    # Check if we have been supplied a VIDEO_FORMAT, if not lets set one
    if video_format is None:
        # Do we already have it in the header?  If so, lets leave that as is
        if "VIDEO_FORMAT" not in header:
            header["VIDEO_FORMAT"] = _video_format_from_metadata(clips)
    else:
        header["VIDEO_FORMAT"] = str(video_format)

    headers = list(header.items())
    headers.sort()  # make the output predictable
    for key, val in headers:
        result += "{}\t{}\n".format(key, val)

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
        
        # If otio contains CDL data add ASC_SOP and/or ASC_SAT columns
        cdl = clip.metadata.get('cdl', None)
        if cdl is not None:
            if cdl.get('asc_sop') and 'ASC_SOP' not in columns:
                columns.append('ASC_SOP')
            if cdl.get('asc_sat') and 'ASC_SAT' not in columns:
                columns.append('ASC_SAT')
            

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
        elif column == "ASC_SOP":
            asc_sop = clip.metadata.get("cdl", {}).get("asc_sop", {})
            offset = asc_sop.get("offset", None)
            power = asc_sop.get("power", None)
            slope = asc_sop.get("slope", None)
            asc_sop_arr = [offset, power, slope]
            if None in asc_sop_arr:
                return clip.metadata.get("ALE", {}).get(column)
            asc_sop = ""
            for i in range(3):
                asc_sop += "("
                asc_sop += str(asc_sop_arr[i][0]) + " "
                asc_sop += str(asc_sop_arr[i][1]) + " "
                asc_sop += str(asc_sop_arr[i][2]) + ")"
            return asc_sop
        elif column == "ASC_SAT":
            asc_sat = clip.metadata.get("cdl", {}).get("asc_sat", None)
            if asc_sat is not None:
                return asc_sat
            else:
                return clip.metadata.get("ALE", {}).get(column)
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
