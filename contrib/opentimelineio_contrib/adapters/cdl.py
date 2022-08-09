# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""
CDL Export Adapter
This simple adapter allows users to export a collection of .cdl files
from an OTIO timeline. The ColorCorrection Node ID within the .cdl will use the
CMX_3600 reel name/Tape of the clip, while the file itself will be named
using the timeline event name.

To use: otio.adapters.write_to_file(timeline, cdl_output_directory, adapter_name='cdl')
"""
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom


def convert_to_cdl(timeline_event):
    slope_src = timeline_event.metadata["cdl"]["asc_sop"]["slope"]
    offset_src = timeline_event.metadata["cdl"]["asc_sop"]["offset"]
    power_src = timeline_event.metadata["cdl"]["asc_sop"]["power"]
    saturation_src = timeline_event.metadata["cdl"]["asc_sat"]
    reel_name = timeline_event.metadata["cmx_3600"]["reel"]

    slope = " ".join(str("{:.6f}".format(x)) for x in slope_src)
    offset = " ".join(str("{:.6f}".format(x)) for x in offset_src)
    power = " ".join(str("{:.6f}".format(x)) for x in power_src)
    saturation = str("{:.6f}".format(saturation_src))

    color_decision_list = ET.Element("ColorDecisionList", xmlns="urn:ASC:CDL:v1.01")
    color_decision = ET.SubElement(color_decision_list, "ColorDecision")
    color_correction = ET.SubElement(color_decision, "ColorCorrection", id=reel_name)

    sop_node = ET.SubElement(color_correction, "SOPNode")
    ET.SubElement(sop_node, "Slope").text = slope
    ET.SubElement(sop_node, "Offset").text = offset
    ET.SubElement(sop_node, "Power").text = power

    sat_node = ET.SubElement(color_correction, "SATNode")
    ET.SubElement(sat_node, "Saturation").text = saturation

    tree = ET.ElementTree(color_decision_list)

    # Python 3.8 doesn't support ET.indent(), using minidom as a workaround.
    stringified = ET.tostring(tree.getroot(), 'utf-8')
    reparsed = minidom.parseString(stringified)

    return reparsed.toprettyxml(indent="    ", encoding='utf-8')


def create_cdl_file(timeline_event, output_dir_path):
    try:
        cdl_filepath = os.path.join(output_dir_path, timeline_event.name + ".cdl")
        cdl_string = convert_to_cdl(timeline_event)

        with open(cdl_filepath, "w") as f:
            f.write(str(cdl_string.decode('utf-8')))
    finally:
        pass


def write_to_file(input_otio, filepath):
    """
      Required OTIO function hook.
      Actually writes to multiple .cdl files (one per clip/event in timeline)
      filepath parameter should be a directory where the CDLs should be saved.
    """
    output_dir_path = filepath

    if os.path.isdir(output_dir_path):
        for track in input_otio.tracks:
            for timeline_event in track:
                if "cdl" in timeline_event.metadata:
                    create_cdl_file(timeline_event, output_dir_path)
    else:
        err = filepath + " is not a valid directory, please create it and run again."
        raise RuntimeError(err)
