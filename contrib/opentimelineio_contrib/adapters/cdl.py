# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""CDL Export Adapter"""
import os
import sys
import xml.etree.cElementTree as ET

def convert_to_cdl(timeline_event):
    color_decision_list = ET.Element("ColorDecisionList", xmlns="urn:ASC:CDL:v1.01")
    color_decision = ET.SubElement(color_decision_list, "ColorDecision")
    color_correction = ET.SubElement(color_decision, "ColorCorrection", id=timeline_event.metadata["cmx_3600"]["reel"])

    sop_node = ET.SubElement(color_correction, "SOPNode")
    slope = ET.SubElement(sop_node, "Slope").text = " ".join(str("{:.6f}".format(x)) for x in timeline_event.metadata["cdl"]["asc_sop"]["slope"])
    offset = ET.SubElement(sop_node, "Offset").text = " ".join(str("{:.6f}".format(x)) for x in timeline_event.metadata["cdl"]["asc_sop"]["offset"])
    power = ET.SubElement(sop_node, "Power").text = " ".join(str("{:.6f}".format(x)) for x in timeline_event.metadata["cdl"]["asc_sop"]["power"])

    sat_node = ET.SubElement(color_correction, "SATNode")
    saturation = ET.SubElement(sat_node, "Saturation").text = str("{:.6f}".format(timeline_event.metadata["cdl"]["asc_sat"]))

    tree = ET.ElementTree(color_decision_list)
    ET.indent(tree)
    return tree


def write_to_file(input_otio, filepath):
    """
      Required OTIO function hook.
      Actually writes to multiple .cdl files (one per clip/event in timeline)
      filepath parameter should be a directory where the CDLs should be saved.
    """
    for track in input_otio.tracks:
        for timeline_event in track:
            if timeline_event.metadata["cdl"]:
                cdl_filepath = os.path.join(filepath, timeline_event.name + ".cdl")
                cdl_et_tree = convert_to_cdl(timeline_event)
                cdl_et_tree.write(cdl_filepath, encoding='utf-8', xml_declaration=True)