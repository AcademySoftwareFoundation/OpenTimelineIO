# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

import os
import unittest

import opentimelineio as otio

import tempfile

# Reference data
SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
HLS_EXAMPLE_PATH = os.path.join(SAMPLE_DATA_DIR, "v1_prog_index.m3u8")

# Load the adapter module using otio
hls_playlist = otio.adapters.from_name("hls_playlist").module()

MEM_PLAYLIST_REF_VALUE = """#EXTM3U
#EXT-X-VERSION:7
#EXT-X-INDEPENDENT-SEGMENTS
#EXT-X-MEDIA-SEQUENCE:1
#EXT-X-PLAYLIST-TYPE:VOD
#EXT-X-TARGETDURATION:2
#EXT-X-MAP:BYTERANGE="729@0",URI="media-video-1.mp4"
#EXTINF:2.00200,
#EXT-X-BYTERANGE:534220@1361
video1.mp4
#EXT-X-ENDLIST"""

MEM_MASTER_PLAYLIST_REF_VALUE = """#EXTM3U
#EXT-X-VERSION:6
#EXT-X-MEDIA:GROUP-ID="aud1",NAME="a1",TYPE=AUDIO,URI="a1/prog_index.m3u8"
#EXT-X-STREAM-INF:AUDIO="aud1",BANDWIDTH=135801,CODECS="avc.test,aac.test",FRAME-RATE=23.976,RESOLUTION=1920x1080
v1/prog_index.m3u8"""

MEM_IFRAME_MASTER_PLAYLIST_REF_VALUE = """#EXTM3U
#EXT-X-VERSION:6
#EXT-X-MEDIA:GROUP-ID="aud1",NAME="a1",TYPE=AUDIO,URI="a1/prog_index.m3u8"
#EXT-X-I-FRAME-STREAM-INF:BANDWIDTH=123456,CODECS="avc.test",RESOLUTION=1920x1080,URI="v1/iframe_index.m3u8"
#EXT-X-STREAM-INF:AUDIO="aud1",BANDWIDTH=135801,CODECS="avc.test,aac.test",FRAME-RATE=23.976,RESOLUTION=1920x1080
v1/prog_index.m3u8"""

MEM_COMPLEX_MASTER_PLAYLIST_REF_VALUE = """#EXTM3U
#EXT-X-VERSION:6
#EXT-X-MEDIA:GROUP-ID="aud1",NAME="a1",TYPE=AUDIO,URI="a1/prog_index.m3u8"
#EXT-X-I-FRAME-STREAM-INF:BANDWIDTH=123456,CODECS="avc.test",RESOLUTION=1920x1080,URI="v1/iframe_index.m3u8"
#EXT-X-I-FRAME-STREAM-INF:BANDWIDTH=12345,CODECS="avc.test",RESOLUTION=720x480,URI="v2/iframe_index.m3u8"
#EXT-X-STREAM-INF:AUDIO="aud1",BANDWIDTH=135801,CODECS="avc.test,aac.test",FRAME-RATE=23.976,RESOLUTION=1920x1080
v1/prog_index.m3u8
#EXT-X-STREAM-INF:AUDIO="aud1",BANDWIDTH=24690,CODECS="avc.test,aac.test",FRAME-RATE=23.976,RESOLUTION=720x480
v2/prog_index.m3u8"""

MEM_SINGLE_TRACK_MASTER_PLAYLIST_REF_VALUE = """#EXTM3U
#EXT-X-VERSION:6
#EXT-X-I-FRAME-STREAM-INF:BANDWIDTH=123456,CODECS="avc.test",RESOLUTION=1920x1080,URI="v1/iframe_index.m3u8"
#EXT-X-STREAM-INF:BANDWIDTH=123456,CODECS="avc.test",FRAME-RATE=23.976,RESOLUTION=1920x1080
v1/prog_index.m3u8"""


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


class HLSPMedialaylistAdapterTest(unittest.TestCase):
    """ Test the HLS Playlist adapter media playlist functionality """

    def test_media_pl_from_mem(self):
        t = otio.schema.Timeline()
        track = otio.schema.Track("v1")
        track.metadata['HLS'] = {
            "EXT-X-INDEPENDENT-SEGMENTS": None,
            "EXT-X-PLAYLIST-TYPE": "VOD"
        }
        t.tracks.append(track)

        # Make a prototype media ref with the segment's initialization metadata
        segmented_media_ref = otio.schema.ExternalReference(
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
        media_ref1 = segmented_media_ref.deepcopy()
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
        with tempfile.TemporaryDirectory() as temp_dir:
            media_pl_tmp_path = os.path.join(
                temp_dir,
                "test_media_pl_from_mem.m3u8"
            )
            otio.adapters.write_to_file(t, media_pl_tmp_path)

            with open(media_pl_tmp_path) as f:
                pl_string = f.read()

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
        with tempfile.TemporaryDirectory() as temp_dir:
            media_pl_tmp_path = os.path.join(
                temp_dir,
                "test_media_roundtrip.m3u8"
            )
            otio.adapters.write_to_file(timeline, media_pl_tmp_path)

            # Read in both playlists
            with open(hls_path) as f:
                reference_lines = f.readlines()

            with open(media_pl_tmp_path) as f:
                adapter_out_lines = f.readlines()

            # Using otio as well
            in_timeline = otio.adapters.read_from_file(media_pl_tmp_path)

        # Strip newline chars
        reference_lines = [line.strip('\n') for line in reference_lines]
        adapter_out_lines = [line.strip('\n') for line in adapter_out_lines]

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
        timeline_streaming_md = timeline.metadata.setdefault('streaming', {})
        seg_min_duration = otio.opentime.RationalTime(6, 1)
        timeline_streaming_md['min_segment_duration'] = seg_min_duration
        seg_max_duration = otio.opentime.RationalTime(
            (60 * 60 * 24),
            1
        )
        timeline_streaming_md['max_segment_duration'] = seg_max_duration

        # Write out the playlist
        with tempfile.TemporaryDirectory() as temp_dir:
            media_pl_tmp_path = os.path.join(
                temp_dir,
                "test_media_segment_size.m3u8"
            )
            otio.adapters.write_to_file(timeline, media_pl_tmp_path)

            # Read in the playlist
            in_timeline = otio.adapters.read_from_file(media_pl_tmp_path)

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
        timeline_streaming_md = timeline.metadata.setdefault('streaming', {})
        seg_min_duration = otio.opentime.RationalTime(6, 1)
        timeline_streaming_md['min_segment_duration'] = seg_min_duration
        seg_max_duration = otio.opentime.RationalTime(
            (60 * 60 * 24),
            1
        )
        timeline_streaming_md['max_segment_duration'] = seg_max_duration

        # Configure the playlist to be an iframe list
        track_hls_metadata = timeline.tracks[0].metadata['HLS']
        del track_hls_metadata['EXT-X-INDEPENDENT-SEGMENTS']
        track_hls_metadata['EXT-X-I-FRAMES-ONLY'] = None

        # Write out the playlist
        with tempfile.TemporaryDirectory() as temp_dir:
            media_pl_tmp_path = os.path.join(
                temp_dir,
                "test_iframe_segment_size.m3u8"
            )
            otio.adapters.write_to_file(timeline, media_pl_tmp_path)

            # Read in the playlist
            in_timeline = otio.adapters.read_from_file(media_pl_tmp_path)
            with open(media_pl_tmp_path) as f:
                pl_lines = f.readlines()
            pl_lines = [line.strip('\n') for line in pl_lines]

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


class HLSPMasterPlaylistAdapterTest(unittest.TestCase):
    """ Test the HLS Playlist adapter master playlist functionality """

    def test_simple_master_pl_from_mem(self):
        t = otio.schema.Timeline()

        # add a video track
        vtrack = otio.schema.Track(
            "v1",
            kind=otio.schema.TrackKind.Video
        )
        vtrack.metadata.update(
            {
                'streaming': {
                    'bandwidth': 123456,
                    'codec': 'avc.test',
                    'width': 1920,
                    'height': 1080,
                    'frame_rate': 23.976,
                },
                'HLS': {
                    'uri': 'v1/prog_index.m3u8'
                }
            }
        )
        t.tracks.append(vtrack)

        # add an audio track
        atrack = otio.schema.Track(
            "a1",
            kind=otio.schema.TrackKind.Audio
        )
        atrack.metadata.update(
            {
                'linked_tracks': [vtrack.name],
                'streaming': {
                    'bandwidth': 12345,
                    'codec': 'aac.test',
                    'group_id': 'aud1',
                },
                'HLS': {
                    'uri': 'a1/prog_index.m3u8'
                }
            }
        )
        t.tracks.append(atrack)

        # Write out and validate the playlist
        with tempfile.TemporaryDirectory() as temp_dir:
            media_pl_tmp_path = os.path.join(
                temp_dir,
                "master.m3u8"
            )
            otio.adapters.write_to_file(t, media_pl_tmp_path)

            with open(media_pl_tmp_path) as f:
                pl_string = f.read()

        # Drop blank lines before comparing
        pl_string = '\n'.join(line for line in pl_string.split('\n') if line)

        # Compare against the reference value
        self.assertEqual(pl_string, MEM_MASTER_PLAYLIST_REF_VALUE)

    def test_master_pl_with_iframe_pl_from_mem(self):
        t = otio.schema.Timeline()

        # add a video track
        vtrack = otio.schema.Track(
            "v1",
            kind=otio.schema.TrackKind.Video
        )
        vtrack.metadata.update(
            {
                'streaming': {
                    'bandwidth': 123456,
                    'codec': 'avc.test',
                    'width': 1920,
                    'height': 1080,
                    'frame_rate': 23.976,
                },
                'HLS': {
                    'uri': 'v1/prog_index.m3u8',
                    'iframe_uri': 'v1/iframe_index.m3u8'
                }
            }
        )
        t.tracks.append(vtrack)

        # add an audio track
        atrack = otio.schema.Track(
            "a1",
            kind=otio.schema.TrackKind.Audio
        )
        atrack.metadata.update(
            {
                'linked_tracks': [vtrack.name],
                'streaming': {
                    'bandwidth': 12345,
                    'codec': 'aac.test',
                    'group_id': 'aud1',
                },
                'HLS': {
                    'uri': 'a1/prog_index.m3u8'
                }
            }
        )
        t.tracks.append(atrack)

        # Write out and validate the playlist
        with tempfile.TemporaryDirectory() as temp_dir:
            media_pl_tmp_path = os.path.join(
                temp_dir,
                "master.m3u8"
            )
            otio.adapters.write_to_file(t, media_pl_tmp_path)

            with open(media_pl_tmp_path) as f:
                pl_string = f.read()

        # Drop blank lines before comparing
        pl_string = '\n'.join(line for line in pl_string.split('\n') if line)

        # Compare against the reference value
        self.assertEqual(pl_string, MEM_IFRAME_MASTER_PLAYLIST_REF_VALUE)

    def test_master_pl_complex_from_mem(self):
        t = otio.schema.Timeline()

        # add a video track
        vtrack = otio.schema.Track(
            "v1",
            kind=otio.schema.TrackKind.Video
        )
        vtrack.metadata.update(
            {
                'streaming': {
                    'bandwidth': 123456,
                    'codec': 'avc.test',
                    'width': 1920,
                    'height': 1080,
                    'frame_rate': 23.976,
                },
                'HLS': {
                    'uri': 'v1/prog_index.m3u8',
                    'iframe_uri': 'v1/iframe_index.m3u8'
                }
            }
        )
        t.tracks.append(vtrack)

        # add an alternate video track rep
        v2track = otio.schema.Track(
            "v2",
            kind=otio.schema.TrackKind.Video
        )
        v2track.metadata.update(
            {
                'streaming': {
                    'bandwidth': 12345,
                    'codec': 'avc.test',
                    'width': 720,
                    'height': 480,
                    'frame_rate': 23.976,
                },
                'HLS': {
                    'uri': 'v2/prog_index.m3u8',
                    'iframe_uri': 'v2/iframe_index.m3u8'
                }
            }
        )
        t.tracks.append(v2track)

        # add an audio track
        atrack = otio.schema.Track(
            "a1",
            kind=otio.schema.TrackKind.Audio
        )
        atrack.metadata.update(
            {
                'linked_tracks': [vtrack.name, v2track.name],
                'streaming': {
                    'bandwidth': 12345,
                    'codec': 'aac.test',
                    'group_id': 'aud1',
                },
                'HLS': {
                    'uri': 'a1/prog_index.m3u8'
                }
            }
        )
        t.tracks.append(atrack)

        # Write out and validate the playlist
        with tempfile.TemporaryDirectory() as temp_dir:
            media_pl_tmp_path = os.path.join(
                temp_dir,
                "master.m3u8"
            )
            otio.adapters.write_to_file(t, media_pl_tmp_path)

            with open(media_pl_tmp_path) as f:
                pl_string = f.read()

        # Drop blank lines before comparing
        pl_string = '\n'.join(line for line in pl_string.split('\n') if line)

        # Compare against the reference value
        self.assertEqual(pl_string, MEM_COMPLEX_MASTER_PLAYLIST_REF_VALUE)

    def test_master_playlist_hint_metadata(self):
        """
        Test that URL hints for master playlists don't leak out to media
        playlsits.
        """
        # Start with the reference playlist
        hls_path = HLS_EXAMPLE_PATH
        timeline = otio.adapters.read_from_file(hls_path)

        # add master playlist metadata to the track
        timeline.tracks[0].metadata.update(
            {
                'bandwidth': 123456,
                'codec': 'avc.test',
                'width': 1920,
                'height': 1080,
                'frame_rate': 23.976,
                'HLS': {
                    'uri': 'v1/prog_index.m3u8',
                    'iframe_uri': 'v1/iframe_index.m3u8'
                }
            }
        )

        # Write out and validate the playlist
        with tempfile.TemporaryDirectory() as temp_dir:
            media_pl_tmp_path = os.path.join(
                temp_dir,
                "test_media_pl_from_mem.m3u8"
            )
            otio.adapters.write_to_file(timeline, media_pl_tmp_path)

            with open(media_pl_tmp_path) as f:
                pl_string = f.read()

        # ensure metadata that wasn't supposed to didn't leak out
        for line in pl_string.split('\n'):
            self.assertFalse(line.startswith('#uri:'))
            self.assertFalse(line.startswith('#iframe_uri:'))

    def test_explicit_master_pl_from_mem(self):
        """Test that forcing a master playlist for a single track timeline
        works.
        """
        t = otio.schema.Timeline()
        # Set the master playlist flag
        t.metadata.update(
            {
                'HLS': {
                    'master_playlist': True
                }
            }
        )

        # build a track
        track = otio.schema.Track('v1')
        track.metadata.update(
            {
                'streaming': {
                    'bandwidth': 123456,
                    'codec': 'avc.test',
                    'width': 1920,
                    'height': 1080,
                    'frame_rate': 23.976,
                },
                'HLS': {
                    'EXT-X-INDEPENDENT-SEGMENTS': None,
                    'EXT-X-PLAYLIST-TYPE': 'VOD',
                    'uri': 'v1/prog_index.m3u8',
                    'iframe_uri': 'v1/iframe_index.m3u8'
                }
            }
        )
        t.tracks.append(track)

        # Make a prototype media ref with the segment's initialization metadata
        segmented_media_ref = otio.schema.ExternalReference(
            target_url='video1.mp4',
            metadata={
                'streaming': {
                    'init_byterange': {
                        'byte_count': 729,
                        'byte_offset': 0
                    },
                    'init_uri': 'media-video-1.mp4'
                }
            }
        )

        # Make a copy of the media ref specifying the byte range for the
        # segment
        media_ref1 = segmented_media_ref.deepcopy()
        media_ref1.available_range = otio.opentime.TimeRange(
            otio.opentime.RationalTime(0, 1),
            otio.opentime.RationalTime(2.002, 1)
        )
        media_ref1.metadata.update(
            {
                'streaming': {
                    'byte_count': 534220,
                    'byte_offset': 1361
                }
            }
        )

        # make the segment and append it
        segment1 = otio.schema.Clip(media_reference=media_ref1)
        track.append(segment1)

        # Write out and validate the playlist
        with tempfile.TemporaryDirectory() as temp_dir:
            master_pl_tmp_path = os.path.join(
                temp_dir,
                "master.m3u8"
            )
            otio.adapters.write_to_file(t, master_pl_tmp_path)

            with open(master_pl_tmp_path) as f:
                pl_string = f.read()

        # Drop blank lines before comparing
        pl_string = '\n'.join(line for line in pl_string.split('\n') if line)

        # Compare against the reference value
        self.assertEqual(pl_string, MEM_SINGLE_TRACK_MASTER_PLAYLIST_REF_VALUE)


if __name__ == '__main__':
    unittest.main()
