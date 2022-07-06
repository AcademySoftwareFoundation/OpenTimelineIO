# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""
CDL Export Adapter
This simple adapter allows users to export a collection of .cdl files from an OTIO timeline.
The ColorCorrection ID within the .cdl will use the reel name/Tape of the clip, while the file itself will be named using the timeline event name.

To use: otio.adapters.write_to_file(timeline, cdl_output_directory, adapter_name='cdl')
"""
import os
import sys
import xml.etree.cElementTree as ET

def convert_to_cdl(timeline_event):
    slope = " ".join(str("{:.6f}".format(x)) for x in timeline_event.metadata["cdl"]["asc_sop"]["slope"])
    offset = " ".join(str("{:.6f}".format(x)) for x in timeline_event.metadata["cdl"]["asc_sop"]["offset"])
    power = " ".join(str("{:.6f}".format(x)) for x in timeline_event.metadata["cdl"]["asc_sop"]["power"])
    saturation = str("{:.6f}".format(timeline_event.metadata["cdl"]["asc_sat"]))

    color_decision_list = ET.Element("ColorDecisionList", xmlns="urn:ASC:CDL:v1.01")
    color_decision = ET.SubElement(color_decision_list, "ColorDecision")
    color_correction = ET.SubElement(color_decision, "ColorCorrection", id=timeline_event.metadata["cmx_3600"]["reel"])

    sop_node = ET.SubElement(color_correction, "SOPNode")
    ET.SubElement(sop_node, "Slope").text = slope
    ET.SubElement(sop_node, "Offset").text = offset
    ET.SubElement(sop_node, "Power").text = power

    sat_node = ET.SubElement(color_correction, "SATNode")
    ET.SubElement(sat_node, "Saturation").text = saturation

    tree = ET.ElementTree(color_decision_list)
    ET.indent(tree)
    return tree


def write_to_file(input_otio, filepath):
    """
      Required OTIO function hook.
      Actually writes to multiple .cdl files (one per clip/event in timeline)
      filepath parameter should be a directory where the CDLs should be saved.
    """
    if os.path.isdir(filepath):
        for track in input_otio.tracks:
            for timeline_event in track:
                if timeline_event.metadata["cdl"]:
                    try:
                        cdl_filepath = os.path.join(filepath, timeline_event.name + ".cdl")
                        cdl_et_tree = convert_to_cdl(timeline_event)
                        cdl_et_tree.write(cdl_filepath, encoding='utf-8', xml_declaration=True)
                    finally:
                       pass
    else:
        raise RuntimeError(f"{filepath} is not a valid directory, please create it and run again.")