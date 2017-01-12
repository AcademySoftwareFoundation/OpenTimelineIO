import json
import os
import tempfile
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

MEM_PLAYLIST_REF_VALUE = '''#EXTM3U
#EXT-X-VERSION:7
#EXT-X-TARGETDURATION:2
#EXT-X-PLAYLIST-TYPE:VOD
#EXT-X-INDEPENDENT-SEGMENTS
#EXT-X-MEDIA-SEQUENCE:1
#EXT-X-MAP:BYTERANGE="729@0",URI="media-video-1.mp4"
#EXTINF:2.00200,
#EXT-X-BYTERANGE:534220@1361
video1.mp4
#EXT-X-ENDLIST'''


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

    def test_media_pl_from_mem(self):
        t = otio.schema.Timeline()
        track = otio.schema.Sequence("v1")
        track.metadata['HLS'] = {
            "EXT-X-INDEPENDENT-SEGMENTS": None,
            "EXT-X-PLAYLIST-TYPE": "VOD"
        }
        t.tracks.append(track)

        # Make a prototype media ref with the segment's initialization metadata
        segmented_media_ref = otio.media_reference.External(
            target_url='video1.mp4',
            metadata={
                "init_byterange": {
                    "byte_count": 729,
                    "byte_offset": 0
                },
                "init_uri": "media-video-1.mp4"
            }
        )

        # Make a copy of the media ref specifying the byte range for the
        # segment
        media_ref1 = segmented_media_ref.copy()
        media_ref1.available_range = otio.opentime.TimeRange(
            otio.opentime.RationalTime(0, 1),
            otio.opentime.RationalTime(2.002, 1)
        )
        media_ref1.metadata.update(
            {
                "byte_count": 534220,
                "byte_offset": 1361
            }
        )

        # make the segment and append it
        segment1 = otio.schema.Clip(media_reference=media_ref1)
        track.append(segment1)

        # Write out and validate the playlist
        media_pl_tmp_path = tempfile.mkstemp(suffix=".m3u8", text=True)[1]
        otio.adapters.write_to_file(t, media_pl_tmp_path)

        with open(media_pl_tmp_path) as f:
            pl_string = f.read()

        os.remove(media_pl_tmp_path)

        self.assertEqual(pl_string, MEM_PLAYLIST_REF_VALUE)

    def _validate_sample_playlist(self, timeline):
        # Validate the track count
        self.assertEqual(len(timeline.tracks), 1)
        track = timeline.tracks[0]

        # Validate the track global metadata
        self.assertNotEqual(track.metadata['HLS'], {})
        track_metadata = track.metadata['HLS']
        self.assertEqual(track_metadata, {
            'EXT-X-INDEPENDENT-SEGMENTS': None,
            'EXT-X-VERSION': '7',
            'EXT-X-PLAYLIST-TYPE': 'VOD'}
        )

        # There are 50 segments (clips)
        # Validate the count, "sequence_num", and durations
        self.assertEqual(len(track), 50)
        start_seq_num = int(track[0].metadata['sequence_num'])
        segment_durations = otio.opentime.RationalTime(1.001, 1)
        for seq_num, clip in enumerate(track, start_seq_num):
            self.assertEqual(clip.metadata['sequence_num'], seq_num)
            if seq_num < 50:
                self.assertEqual(clip.duration(), segment_durations)
            else:
                # The last segment has a shorter duration
                self.assertEqual(
                    clip.duration(),
                    otio.opentime.RationalTime(0.83417, 1)
                )

        # Spot-check a segment
        segment_5 = track[4]
        segment_5_media_ref = segment_5.media_reference
        self.assertEqual(
            segment_5_media_ref.metadata['byte_count'],
            593718
        )
        self.assertEqual(
            segment_5_media_ref.metadata['byte_offset'],
            2430668
        )
        self.assertEqual(
            segment_5_media_ref.metadata['init_byterange']['byte_count'],
            729
        )
        self.assertEqual(
            segment_5_media_ref.metadata['init_byterange']['byte_offset'],
            0
        )
        self.assertEqual(
            segment_5_media_ref.metadata['init_uri'],
            "media-video-1.mp4"
        )
        self.assertEqual(
            segment_5_media_ref.target_url,
            "media-video-1.mp4"
        )

    def test_media_roundtrip(self):
        hls_path = HLS_EXAMPLE_PATH
        timeline = otio.adapters.read_from_file(hls_path)

        # validate the read-in playlist matches reference data
        self._validate_sample_playlist(timeline)

        # Write out and validate both playlists have the same lines
        media_pl_tmp_path = tempfile.mkstemp(suffix=".m3u8", text=True)[1]
        otio.adapters.write_to_file(timeline, media_pl_tmp_path)

        # Read in both playlists
        with open(hls_path) as f:
            reference_lines = f.readlines()

        with open(media_pl_tmp_path) as f:
            adapter_out_lines = f.readlines()

        # Using otio as well
        in_timeline = otio.adapters.read_from_file(media_pl_tmp_path)

        # Remove the temp out file
        os.remove(media_pl_tmp_path)

        # Strip newline chars
        reference_lines = [l.strip('\n') for l in reference_lines]
        adapter_out_lines = [l.strip('\n') for l in adapter_out_lines]

        # while imperfect, do a superficial comparison
        self.assertEqual(len(reference_lines), len(adapter_out_lines))
        diff_lines = set(reference_lines).symmetric_difference(
            adapter_out_lines
        )
        # ignore the EXT-X-MAP entry because attribute order is
        # non-deterministic
        diff_lines = [l for l in diff_lines if not l.startswith('#EXT-X-MAP')]
        self.assertEqual(len(diff_lines), 0)

        # validate the otio of the playlist we wrote
        self._validate_sample_playlist(in_timeline)

if __name__ == '__main__':
    unittest.main()
