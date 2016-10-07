#!/usr/bin/env python2.7

"""Test builtin adapters."""

# python
import os
import tempfile
import unittest

import opentimelineio as otio

from opentimelineio.adapters import (
    otio_json,
    hls_playlist
)

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
SCREENING_EXAMPLE_PATH = os.path.join(SAMPLE_DATA_DIR, "screening_example.edl")
HLS_EXAMPLE_PATH = os.path.join(SAMPLE_DATA_DIR, "v1_prog_index.m3u8")

class BuiltInAdapterTest(unittest.TestCase):

    def test_disk_io(self):
        edl_path = SCREENING_EXAMPLE_PATH
        timeline = otio.adapters.read_from_file(edl_path)
        otiotmp = tempfile.mkstemp(suffix=".otio", text=True)[1]
        otio.adapters.write_to_file(timeline, otiotmp)
        decoded = otio.adapters.read_from_file(otiotmp)
        self.assertEqual(timeline, decoded)

    def test_otio_round_trip(self):
        tl = otio.adapters.read_from_file(SCREENING_EXAMPLE_PATH)

        baseline_json = otio.adapters.otio_json.write_to_string(tl)

        self.assertEqual(tl.name, "Example_Screening.01")

        otio.adapters.otio_json.write_to_file(tl, "/var/tmp/test.otio")
        new = otio.adapters.otio_json.read_from_file(
            "/var/tmp/test.otio"
        )

        new_json = otio.adapters.otio_json.write_to_string(new)

        self.assertMultiLineEqual(baseline_json, new_json)
        self.assertEqual(tl, new)

    def test_disk_vs_string(self):
        """ Writing to disk and writing to a string should
        produce the same result
        """
        timeline = otio.adapters.read_from_file(SCREENING_EXAMPLE_PATH)

        tmp = tempfile.mkstemp(suffix=".otio", text=True)[1]
        otio.adapters.write_to_file(timeline, tmp)
        in_memory = otio.adapters.write_to_string(timeline, 'otio_json')
        with open(tmp, 'r') as f:
            on_disk = f.read()

        self.assertEqual(in_memory, on_disk)

    def test_adapters_fetch(self):
        """ Test the dynamic string based adapter fetching """
        self.assertEqual(
            otio.adapters.from_name('otio_json').module(),
            otio_json
        )


class HLSPlaylistAdapterTest(unittest.TestCase):

    def test_hls_attribute_list(self):
        """ Test the HLS adapter's attribute list parser """
        attribute_list_string = 'HEXTHING=0xFAF,FIRST-NEGFLOAT=-1.25,'\
                'STRTHING="foo, bar",DECIMALTHING=123456,FLOATTHING=1.233,'\
                'ENUMTHING=0xeS1,NEGFLOAT=-3.14'
        attribute_list_dictionary = {
                "HEXTHING": 0xFAF,
                "FIRST-NEGFLOAT": -1.25,
                "STRTHING": "foo, bar",
                "DECIMALTHING": 123456,
                "FLOATTHING": 1.233,
                "ENUMTHING": "0xeS1",
                "NEGFLOAT": -3.14
                }
        attr_list = hls_playlist._parse_attribute_list(attribute_list_string)

        self.assertEquals(len(attr_list), len(attribute_list_dictionary))
        for attrName, attrValue in attr_list:
            self.assertEquals(attrValue, attribute_list_dictionary[attrName])
    
    def test_playlist_tag_exclusivity(self):
        """ Test that mutually-exclusive tag types don't overlap """
        # see sections 4.3.2, 4.3.3, and 4.3.4 of 
        # draft-pantos-http-live-streaming for more information about these
        # constraints

        non_master_tags = hls_playlist.MEDIA_SEGMENT_TAGS.union(
                hls_playlist.MEDIA_PLAYLIST_TAGS)
        
        common_tags = non_master_tags.intersection(
                hls_playlist.MASTER_PLAYLIST_TAGS)
        self.assertEquals(len(common_tags), 0)

    def test_hls_playlist(self):
        hls_path = HLS_EXAMPLE_PATH
        timeline = otio.adapters.read_from_file(hls_path)

if __name__ == '__main__':
    unittest.main()
