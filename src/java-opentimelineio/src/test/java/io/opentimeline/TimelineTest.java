package io.opentimeline;

import io.opentimeline.opentime.RationalTime;
import io.opentimeline.opentime.TimeRange;
import io.opentimeline.opentimelineio.*;
import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

public class TimelineTest {

    @Test
    public void testInit() {
        RationalTime rt = new RationalTime(12, 24);
        Timeline tl = new Timeline.TimelineBuilder()
                .setName("test_timeline")
                .setGlobalStartTime(rt)
                .build();
        assertEquals(tl.getName(), "test_timeline");
        assertEquals(tl.getGlobalStartTime(), rt);
        try {
            tl.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testStr() {
        RationalTime rt = new RationalTime(12, 24);
        Timeline tl = new Timeline.TimelineBuilder()
                .setName("test_timeline")
                .setGlobalStartTime(rt)
                .build();
        assertEquals(tl.toString(),
                "io.opentimeline.opentimelineio.Timeline(" +
                        "name=test_timeline, " +
                        "tracks=io.opentimeline.opentimelineio.Stack(" +
                        "name=tracks, " +
                        "children=[], " +
                        "sourceRange=null, " +
                        "metadata=io.opentimeline.opentimelineio.AnyDictionary{}))");
        try {
            tl.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testMetadata() {
        RationalTime rt = new RationalTime(12, 24);
        AnyDictionary metadata = new AnyDictionary();
        metadata.put("foo", new Any("bar"));
        Timeline tl = new Timeline.TimelineBuilder()
                .setName("test_timeline")
                .setGlobalStartTime(rt)
                .setMetadata(metadata)
                .build();
        assertEquals(tl.getMetadata().get("foo").safelyCastString(), "bar");

        ErrorStatus errorStatus = new ErrorStatus();
        String encoded = tl.toJSONString(errorStatus);
        Timeline decoded = (Timeline) SerializableObject.fromJSONString(encoded, errorStatus);
        assertEquals(decoded, tl);
        assertEquals(tl.getMetadata(), decoded.getMetadata());
        try {
            tl.close();
            decoded.close();
            metadata.close();
            errorStatus.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testRange() {
        Track track = new Track.TrackBuilder().build();
        Stack stack = new Stack.StackBuilder().build();
        RationalTime rt = new RationalTime(5, 24);
        ErrorStatus errorStatus = new ErrorStatus();
        assertTrue(stack.appendChild(track, errorStatus));
        Timeline timeline = new Timeline.TimelineBuilder().build();
        timeline.setTracks(stack);

        ExternalReference mr = new ExternalReference.ExternalReferenceBuilder()
                .setAvailableRange(TimeRange.rangeFromStartEndTime(
                        new RationalTime(5, 24),
                        new RationalTime(15, 24)))
                .setTargetURL("/var/tmp/test.mov")
                .build();
        Clip cl = new Clip.ClipBuilder()
                .setName("test clip1")
                .setMediaReference(mr)
                .setSourceRange(new TimeRange.TimeRangeBuilder().setDuration(rt).build())
                .build();
        Clip cl2 = new Clip.ClipBuilder()
                .setName("test clip2")
                .setMediaReference(mr)
                .setSourceRange(new TimeRange.TimeRangeBuilder().setDuration(rt).build())
                .build();
        Clip cl3 = new Clip.ClipBuilder()
                .setName("test clip3")
                .setMediaReference(mr)
                .setSourceRange(new TimeRange.TimeRangeBuilder().setDuration(rt).build())
                .build();
        assertTrue(track.appendChild(cl, errorStatus));
        assertTrue(track.appendChild(cl2, errorStatus));
        assertTrue(track.appendChild(cl3, errorStatus));

        assertTrue(timeline.getDuration(errorStatus).equals(rt.add(rt).add(rt)));
        assertEquals(timeline.getRangeOfChild(cl, errorStatus),
                ((Track) timeline.getTracks().getChildren().get(0))
                        .getRangeOfChildAtIndex(0, errorStatus));
        try {
            timeline.close();
            errorStatus.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testSerialize() {
        Clip clip = new Clip.ClipBuilder()
                .setName("test_clip")
                .setMediaReference(new MissingReference.MissingReferenceBuilder().build())
                .build();
        Track track = new Track.TrackBuilder().build();
        Stack stack = new Stack.StackBuilder().build();
        ErrorStatus errorStatus = new ErrorStatus();
        assertTrue(stack.appendChild(track, errorStatus));
        Timeline timeline = new Timeline.TimelineBuilder().build();
        timeline.setTracks(stack);
        assertTrue(track.appendChild(clip, errorStatus));
        String encoded = timeline.toJSONString(errorStatus);
        Timeline decoded = (Timeline) SerializableObject.fromJSONString(encoded, errorStatus);
        assertEquals(decoded, timeline);
        String encoded2 = decoded.toJSONString(errorStatus);
        assertEquals(encoded, encoded2);
        try {
            timeline.close();
            errorStatus.close();
            decoded.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testSerializeOfSubclasses() {
        Clip clip1 = new Clip.ClipBuilder()
                .setName("Test Clip")
                .setMediaReference(new ExternalReference.ExternalReferenceBuilder()
                        .setTargetURL("/tmp/foo.mov")
                        .build())
                .build();
        Track track = new Track.TrackBuilder().build();
        Stack stack = new Stack.StackBuilder().build();
        ErrorStatus errorStatus = new ErrorStatus();
        assertTrue(stack.appendChild(track, errorStatus));
        Timeline tl1 = new Timeline.TimelineBuilder()
                .setName("Testing Serialization")
                .build();
        tl1.setTracks(stack);
        assertTrue(track.appendChild(clip1, errorStatus));
        String serialized = tl1.toJSONString(errorStatus);
        assertNotNull(serialized);
        Timeline tl2 = (Timeline) SerializableObject.fromJSONString(serialized, errorStatus);
        assertEquals(tl2, tl1);
        assertEquals(tl1.getName(), tl2.getName());
        assertEquals(tl1.getTracks().getChildren().size(), 1);
        assertEquals(tl2.getTracks().getChildren().size(), 1);
        Track track1 = (Track) tl1.getTracks().getChildren().get(0);
        Track track2 = (Track) tl2.getTracks().getChildren().get(0);
        assertEquals(track1, track2);
        assertEquals(track1.getChildren().size(), 1);
        assertEquals(track2.getChildren().size(), 1);
        Clip clip2 = (Clip) ((Track) tl2.getTracks().getChildren().get(0)).getChildren().get(0);
        assertEquals(clip1.getName(), clip2.getName());
        assertEquals(clip1.getMediaReference(), clip2.getMediaReference());
        assertEquals(((ExternalReference) clip1.getMediaReference()).getTargetURL(),
                ((ExternalReference) clip2.getMediaReference()).getTargetURL());

        try {
            tl1.close();
            tl2.close();
            clip1.close();
            clip2.close();
            errorStatus.close();
            track.close();
            stack.close();
            track1.close();
            track2.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testTracks() {
        Track V1 = new Track.TrackBuilder()
                .setName("V1")
                .setKind(Track.Kind.video)
                .build();
        Track V2 = new Track.TrackBuilder()
                .setName("V2")
                .setKind(Track.Kind.video)
                .build();
        Track A1 = new Track.TrackBuilder()
                .setName("A1")
                .setKind(Track.Kind.audio)
                .build();
        Track A2 = new Track.TrackBuilder()
                .setName("A2")
                .setKind(Track.Kind.audio)
                .build();
        Stack stack = new Stack.StackBuilder().build();
        ErrorStatus errorStatus = new ErrorStatus();
        assertTrue(stack.appendChild(V1, errorStatus));
        assertTrue(stack.appendChild(V2, errorStatus));
        assertTrue(stack.appendChild(A1, errorStatus));
        assertTrue(stack.appendChild(A2, errorStatus));
        Timeline tl = new Timeline.TimelineBuilder().build();
        tl.setTracks(stack);
        ArrayList<String> videoTrackNames = new ArrayList<>();
        List<Track> videoTracks = tl.getVideoTracks();
        for (Track t : videoTracks) {
            videoTrackNames.add(t.getName());
        }
        assertEquals(videoTrackNames, new ArrayList<>(Arrays.asList("V1", "V2")));
        ArrayList<String> audioTrackNames = new ArrayList<>();
        List<Track> audioTracks = tl.getAudioTracks();
        for (Track t : audioTracks) {
            audioTrackNames.add(t.getName());
        }
        assertEquals(audioTrackNames, new ArrayList<>(Arrays.asList("A1", "A2")));
        try {
            tl.close();
            A1.close();
            A2.close();
            V1.close();
            V2.close();
            stack.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
