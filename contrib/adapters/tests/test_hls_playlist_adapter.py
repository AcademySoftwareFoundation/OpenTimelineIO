import json
import os
import unittest

import opentimelineio as otio

from opentimelineio.adapters.otio_json import (
    read_from_string
)

# Reference data
SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
HLS_EXAMPLE_PATH = os.path.join(SAMPLE_DATA_DIR, "v1_prog_index.m3u8")

ADAPTERS_DIR = os.path.dirname(os.path.dirname(__file__))
HLS_ADAPTER_PATH = os.path.join(ADAPTERS_DIR, "hls_playlist.py")
HLS_ADAPTER_MANIFEST_ENTRY = {
    "OTIO_SCHEMA": "Adapter.1",
    "name": "hls_playlist",
    "execution_scope": "in process",
    "filepath": HLS_ADAPTER_PATH,
    "suffixes": ["m3u8"]
}


# Add the HLS adapter at runtime
otio.adapters.MANIFEST.adapters.append(
    read_from_string(
        json.dumps(HLS_ADAPTER_MANIFEST_ENTRY)
    )
)

# Load the adapter module using otio
hls_playlist = otio.adapters.from_name("hls_playlist").module()


class HLSPlaylistDataStructuresTest(unittest.TestCase):
    """ Test the lower-level HLS Data structures """

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
        attr_list = hls_playlist.AttributeList.from_string(
            attribute_list_string
        )

        self.assertEquals(len(attr_list), len(attribute_list_dictionary))
        for attrName, attrValue in attr_list.items():
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


class HLSPlaylistAdapterTest(unittest.TestCase):
    """ Test the HLS Playlist adapter itself """

    def test_hls_playlist(self):
        hls_path = HLS_EXAMPLE_PATH
        timeline = otio.adapters.read_from_file(hls_path)

if __name__ == '__main__':
    unittest.main()
