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
#EXT-X-INDEPENDENT-SEGMENTS
#EXT-X-MEDIA-SEQUENCE:1
#EXT-X-PLAYLIST-TYPE:VOD
#EXT-X-TARGETDURATION:2
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

        self.assertEqual(len(attr_list), len(attribute_list_dictionary))
        for attrName, attrValue in attr_list.items():
            self.assertEqual(attrValue, attribute_list_dictionary[attrName])

    def test_playlist_tag_exclusivity(self):
        """ Test that mutually-exclusive tag types don't overlap """
        # see sections 4.3.2, 4.3.3, and 4.3.4 of
        # draft-pantos-http-live-streaming for more information about these
        # constraints

        non_master_tags = hls_playlist.MEDIA_SEGMENT_TAGS.union(
            hls_playlist.MEDIA_PLAYLIST_TAGS)

        common_tags = non_master_tags.intersection(
            hls_playlist.MASTER_PLAYLIST_TAGS)
        self.assertEqual(len(common_tags), 0)


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
                "streaming": {
                    "init_byterange": {
                        "byte_count": 729,
                        "byte_offset": 0
                    },
                    "init_uri": "media-video-1.mp4"
                }
            }
        )

        # Make a copy of the media ref specifying the byte range for the
        # segment
        media_ref1 = segmented_media_ref.copy()
        media_ref1.available_range = otio.opentime.TimeRange(
            otio.opentime.RationalTime(0, 1),
            otio.opentime.RationalTime(2.002, 1)
        )
        media_ref1.metadata['streaming'].update(
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

        # Compare against the reference value
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
        start_seq_num = int(track[0].metadata['streaming']['sequence_num'])
        segment_durations = otio.opentime.RationalTime(1.001, 1)
        for seq_num, clip in enumerate(track, start_seq_num):
            self.assertEqual(
                clip.metadata['streaming']['sequence_num'],
                seq_num
            )
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
        seg_5_media_ref = segment_5.media_reference
        seg_5_ref_streaming_metadata = seg_5_media_ref.metadata['streaming']
        self.assertEqual(
            seg_5_ref_streaming_metadata['byte_count'],
            593718
        )
        self.assertEqual(
            seg_5_ref_streaming_metadata['byte_offset'],
            2430668
        )
        self.assertEqual(
            seg_5_ref_streaming_metadata['init_byterange']['byte_count'],
            729
        )
        self.assertEqual(
            seg_5_ref_streaming_metadata['init_byterange']['byte_offset'],
            0
        )
        self.assertEqual(
            seg_5_ref_streaming_metadata['init_uri'],
            "media-video-1.mp4"
        )
        self.assertEqual(
            seg_5_media_ref.target_url,
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

        # Compare the lines
        self.assertEqual(reference_lines, adapter_out_lines)

        # validate the otio of the playlist we wrote
        self._validate_sample_playlist(in_timeline)

    def test_media_segment_size(self):
        hls_path = HLS_EXAMPLE_PATH
        timeline = otio.adapters.read_from_file(hls_path)

        # validate the read-in playlist matches reference data
        self._validate_sample_playlist(timeline)

        # Set the sement size to ~six seconds
        seg_min_duration = otio.opentime.RationalTime(6, 1)
        timeline.metadata['min_segment_duration'] = seg_min_duration
        timeline.metadata['max_segment_duration'] = otio.opentime.RationalTime(
            (60 * 60 * 24),
            1
        )

        # Write out the playlist
        media_pl_tmp_path = tempfile.mkstemp(suffix=".m3u8", text=True)[1]
        otio.adapters.write_to_file(timeline, media_pl_tmp_path)

        # Read in the playlist
        in_timeline = otio.adapters.read_from_file(media_pl_tmp_path)
        os.remove(media_pl_tmp_path)

        # Pick a duration that segments won't exceed but is less than max
        seg_upper_duration = otio.opentime.RationalTime(7, 1)

        # When reading an HLS playlist, segments become clips. Check clip
        # durations (except the last one since it's the leftover)
        for clip in in_timeline.tracks[0][:-1]:
            self.assertTrue(clip.duration() >= seg_min_duration)
            self.assertTrue(clip.duration() < seg_upper_duration)

        # Check the last segment duration
        last_clip = in_timeline.tracks[0][-1]
        self.assertTrue(last_clip.duration() < seg_min_duration)
        self.assertTrue(
            last_clip.duration() > otio.opentime.RationalTime(
                0, 1
            )
        )

    def test_iframe_segment_size(self):
        hls_path = HLS_EXAMPLE_PATH
        timeline = otio.adapters.read_from_file(hls_path)

        # the reference playlist is one segment per keyframe, pluck the first
        # segment duration as reference for keyframe duration
        keyframe_duration = timeline.tracks[0][0].duration()

        # validate the read-in playlist matches reference data
        self._validate_sample_playlist(timeline)

        # Set the sement size to ~six seconds
        seg_min_duration = otio.opentime.RationalTime(6, 1)
        timeline.metadata['min_segment_duration'] = seg_min_duration
        timeline.metadata['max_segment_duration'] = otio.opentime.RationalTime(
            (60 * 60 * 24),
            1
        )

        # Configure the playlist to be an iframe list
        track_hls_metadata = timeline.tracks[0].metadata['HLS']
        del(track_hls_metadata['EXT-X-INDEPENDENT-SEGMENTS'])
        track_hls_metadata['EXT-X-I-FRAMES-ONLY'] = None

        # Write out the playlist
        media_pl_tmp_path = tempfile.mkstemp(suffix=".m3u8", text=True)[1]
        otio.adapters.write_to_file(timeline, media_pl_tmp_path)

        # Read in the playlist
        in_timeline = otio.adapters.read_from_file(media_pl_tmp_path)
        with open(media_pl_tmp_path) as f:
            pl_lines = f.readlines()
        pl_lines = [l.strip('\n') for l in pl_lines]
        os.remove(media_pl_tmp_path)

        # validate the TARGETDURATION value is correct
        self.assertTrue('#EXT-X-TARGETDURATION:6' in pl_lines)
        self.assertTrue('#EXT-X-MEDIA-SEQUENCE:0' in pl_lines)
        self.assertEqual(len(timeline.tracks), len(in_timeline.tracks))
        self.assertEqual(len(timeline.tracks[0]), len(in_timeline.tracks[0]))

        # The segments should all be 1.001 seconds like the original input
        seg_upper_duration = otio.opentime.RationalTime(1.1, 1)

        # When reading an HLS playlist, segments become clips. Check clip
        # durations (except the last one since it's the leftover)
        for clip in in_timeline.tracks[0][:-1]:
            self.assertTrue(clip.duration() == keyframe_duration)
            self.assertTrue(clip.duration() < seg_upper_duration)

        # Check the last segment duration
        last_clip = in_timeline.tracks[0][-1]
        self.assertTrue(last_clip.duration() < seg_min_duration)
        self.assertTrue(
            last_clip.duration() > otio.opentime.RationalTime(0, 1)
        )


if __name__ == '__main__':
    unittest.main()
