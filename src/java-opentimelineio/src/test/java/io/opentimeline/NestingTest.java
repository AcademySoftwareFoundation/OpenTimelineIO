package io.opentimeline;

import io.opentimeline.opentime.RationalTime;
import io.opentimeline.opentime.TimeRange;
import io.opentimeline.opentimelineio.*;
import io.opentimeline.util.Pair;
import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

import static org.junit.jupiter.api.Assertions.*;

public class NestingTest {

    interface Nester {
        Stack nest(Clip item, int index);
    }

    @Test
    public void testDeeplyNested() {
        // Take a single clip of media (frames 100-200) and nest it into a bunch
        // of layers
        // Nesting it should not shift the media at all.
        // At one level:
        // Timeline:
        //  Stack: [0-99]
        //   Track: [0-99]
        //    Clip: [100-199]
        //     Media Reference: [100-199]

        // here are some times in the top-level coordinate system
        RationalTime zero = new RationalTime(0, 24);
        RationalTime one = new RationalTime(1, 24);
        RationalTime fifty = new RationalTime(50, 24);
        RationalTime ninetynine = new RationalTime(99, 24);
        RationalTime onehundred = new RationalTime(100, 24);
        TimeRange topLevelRange = new TimeRange(zero, onehundred);

        // here are some times in the media-level coordinate system
        RationalTime firstFrame = new RationalTime(100, 24);
        RationalTime middle = new RationalTime(150, 24);
        RationalTime last = new RationalTime(199, 24);
        TimeRange mediaRange = new TimeRange(firstFrame, onehundred);

        Timeline timeline = new Timeline.TimelineBuilder().build();
        MediaReference media = new MissingReference.MissingReferenceBuilder()
                .setAvailableRange(mediaRange)
                .build();
        Clip clip = new Clip.ClipBuilder()
                .setMediaReference(media)
                .build();
        Track track = new Track.TrackBuilder().build();
        ErrorStatus errorStatus = new ErrorStatus();
        assertTrue(track.appendChild(clip, errorStatus));
        Stack stack = new Stack.StackBuilder().build();
        assertTrue(stack.appendChild(track, errorStatus));
        timeline.setTracks(stack);
        assertEquals(track.getNativeManager().getOTIOObjectNativeHandle(),
                clip.parent().getNativeManager().getOTIOObjectNativeHandle());
        assertEquals(stack.getNativeManager().getOTIOObjectNativeHandle(),
                track.parent().getNativeManager().getOTIOObjectNativeHandle());

        // the clip and track should auto-size to fit the media, since we
        // haven't trimmed anything
        assertEquals(clip.getDuration(errorStatus), onehundred);
        assertEquals(track.getDuration(errorStatus), onehundred);
        assertEquals(stack.getDuration(errorStatus), onehundred);

        // the ranges should match our expectations...
        assertEquals(clip.getTrimmedRange(errorStatus), mediaRange);
        assertEquals(track.getTrimmedRange(errorStatus), topLevelRange);
        assertEquals(stack.getTrimmedRange(errorStatus), topLevelRange);

        // verify that the media is where we expect
        assertEquals(stack.getTransformedTime(zero, clip, errorStatus), firstFrame);
        assertEquals(stack.getTransformedTime(fifty, clip, errorStatus), middle);
        assertEquals(stack.getTransformedTime(ninetynine, clip, errorStatus), last);

        Nester nester = (Clip item, int index) -> {
            assertNotNull(item);
            assertNotNull(item.parent());

            Composition parent = item.parent();
            Stack wrapper = new Stack.StackBuilder().build();
            assertEquals(parent.getChildren().get(index), item);
            ErrorStatus errorStatus1 = new ErrorStatus();
            assertTrue(parent.setChild(index, wrapper, errorStatus1));
            assertEquals(parent.getChildren().get(index), wrapper);
            assertNotEquals(parent.getChildren().get(index), item);
            assertTrue(wrapper.appendChild(item, errorStatus1));
            assertEquals(item.parent(), wrapper);
            return wrapper;
        };

        // now nest it many layers deeper
        ArrayList<Stack> wrappers = new ArrayList<>();
        int numWrappers = 10;
        for (int i = 0; i < numWrappers; i++) {
            Stack wrapper = nester.nest(clip, 0);
            wrappers.add(wrapper);
        }
        // nothing should have shifted at all
//        System.out.println(timeline.toJSONString(errorStatus));

        // the clip and track should auto-size to fit the media, since we
        // haven't trimmed anything
        assertEquals(clip.getDuration(errorStatus), onehundred);
        assertEquals(track.getDuration(errorStatus), onehundred);
        assertEquals(stack.getDuration(errorStatus), onehundred);

        // the ranges should match our expectations...
        assertEquals(clip.getTrimmedRange(errorStatus), mediaRange);
        assertEquals(track.getTrimmedRange(errorStatus), topLevelRange);
        assertEquals(stack.getTrimmedRange(errorStatus), topLevelRange);

        // verify that the media is where we expect
        assertEquals(stack.getTransformedTime(zero, clip, errorStatus), firstFrame);
        assertEquals(stack.getTransformedTime(fifty, clip, errorStatus), middle);
        assertEquals(stack.getTransformedTime(ninetynine, clip, errorStatus), last);

        // now trim them all by one frame at each end
        assertEquals(ninetynine.add(one), onehundred);
        TimeRange trim = new TimeRange(one, ninetynine.subtract(one));
        assertEquals(trim.getDuration(), new RationalTime(98, 24));
        for (Stack wrapper : wrappers) {
            wrapper.setSourceRange(trim);
        }
//        System.out.println(timeline.toJSONString(errorStatus));

        // the clip should be the same
        assertEquals(clip.getDuration(errorStatus), onehundred);

        // the parents should have shrunk by only 2 frames
        assertEquals(track.getDuration(errorStatus), new RationalTime(98, 24));
        assertEquals(stack.getDuration(errorStatus), new RationalTime(98, 24));

        // but the media should have shifted over by 1 one frame for each level
        // of nesting
        RationalTime ten = new RationalTime(numWrappers, 24);
        assertEquals(stack.getTransformedTime(zero, clip, errorStatus), firstFrame.add(ten));
        assertEquals(stack.getTransformedTime(fifty, clip, errorStatus), middle.add(ten));
        assertEquals(stack.getTransformedTime(ninetynine, clip, errorStatus), last.add(ten));

        try {
            timeline.close();
            media.close();
            clip.close();
            track.close();
            errorStatus.close();
            stack.close();
            for (Stack wrapper : wrappers) {
                wrapper.close();
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testChildAtTimeWithChildren() {
        Clip leader = new Clip.ClipBuilder()
                .setName("leader")
                .setSourceRange(new TimeRange(
                        new RationalTime(100, 24),
                        new RationalTime(10, 24)))
                .build();
        Clip clip1 = new Clip.ClipBuilder()
                .setName("clip1")
                .setSourceRange(new TimeRange(
                        new RationalTime(100, 24),
                        new RationalTime(10, 24)))
                .build();
        Clip clip2 = new Clip.ClipBuilder()
                .setName("clip2")
                .setSourceRange(new TimeRange(
                        new RationalTime(101, 24),
                        new RationalTime(10, 24)))
                .build();
        Clip clip3 = new Clip.ClipBuilder()
                .setName("clip3")
                .setSourceRange(new TimeRange(
                        new RationalTime(102, 24),
                        new RationalTime(10, 24)))
                .build();
        Clip credits = new Clip.ClipBuilder()
                .setName("credits")
                .setSourceRange(new TimeRange(
                        new RationalTime(102, 24),
                        new RationalTime(10, 24)))
                .build();
        Track body = new Track.TrackBuilder()
                .setName("body")
                .setSourceRange(new TimeRange(
                        new RationalTime(9, 24),
                        new RationalTime(12, 24)))
                .build();

        ErrorStatus errorStatus = new ErrorStatus();

        assertTrue(body.appendChild(clip1, errorStatus));
        assertTrue(body.appendChild(clip2, errorStatus));
        assertTrue(body.appendChild(clip3, errorStatus));

        Track sq = new Track.TrackBuilder()
                .setName("foo")
                .setSourceRange(new TimeRange(
                        new RationalTime(9, 24),
                        new RationalTime(12, 24)))
                .build();
        assertTrue(sq.appendChild(leader, errorStatus));
        assertTrue(sq.appendChild(body, errorStatus));
        assertTrue(sq.appendChild(credits, errorStatus));

        // Looks like this:
        // [ leader ][ body ][ credits ]
        // 10 f       12f     10f
        //
        // body: (source range starts: 9f duration: 12f)
        // [ clip1 ][ clip2 ][ clip 3]
        // 1f       11f

        List<Composable> sqChildren = sq.getChildren();
        leader = (Clip) sqChildren.get(0);
        body = (Track) sqChildren.get(1);
        credits = (Clip) sqChildren.get(2);
        List<Composable> bodyChildren = body.getChildren();
        clip1 = (Clip) bodyChildren.get(0);
        clip2 = (Clip) bodyChildren.get(1);
        clip3 = (Clip) bodyChildren.get(2);
        assertEquals(leader.getName(), "leader");
        assertEquals(body.getName(), "body");
        assertEquals(credits.getName(), "credits");
        assertEquals(clip1.getName(), "clip1");
        assertEquals(clip2.getName(), "clip2");
        assertEquals(clip3.getName(), "clip3");

        List<Pair<String, Integer>> expected = Arrays.asList(
                new Pair<>("leader", 100),
                new Pair<>("leader", 101),
                new Pair<>("leader", 102),
                new Pair<>("leader", 103),
                new Pair<>("leader", 104),
                new Pair<>("leader", 105),
                new Pair<>("leader", 106),
                new Pair<>("leader", 107),
                new Pair<>("leader", 108),
                new Pair<>("leader", 109),
                new Pair<>("clip1", 109),
                new Pair<>("clip2", 101),
                new Pair<>("clip2", 102),
                new Pair<>("clip2", 103),
                new Pair<>("clip2", 104),
                new Pair<>("clip2", 105),
                new Pair<>("clip2", 106),
                new Pair<>("clip2", 107),
                new Pair<>("clip2", 108),
                new Pair<>("clip2", 109),
                new Pair<>("clip2", 110),
                new Pair<>("clip3", 102),
                new Pair<>("credits", 102),
                new Pair<>("credits", 103),
                new Pair<>("credits", 104),
                new Pair<>("credits", 105),
                new Pair<>("credits", 106),
                new Pair<>("credits", 107),
                new Pair<>("credits", 108),
                new Pair<>("credits", 109),
                new Pair<>("credits", 110),
                new Pair<>("credits", 111)
        );

        for (int frame = 0; frame < expected.size(); frame++) {
            // first test child_at_time
            RationalTime playhead = new RationalTime(frame, 24);
            Composable item = sq.getChildAtTime(playhead, errorStatus);
            RationalTime mediaframe = sq.getTransformedTime(playhead, (Item) item, errorStatus);
            Pair<String, Integer> measuredVal = new Pair<>(item.getName(), mediaframe.toFrames(24));

            assertEquals(measuredVal, expected.get(frame));

            // then test eachChild
            TimeRange searchRange = new TimeRange(
                    new RationalTime(frame, 24),
                    new RationalTime());
            // with a 0 duration, should have the same result as above
            item = sq.eachClip(searchRange, errorStatus).collect(Collectors.toList()).get(0);
            mediaframe = sq.getTransformedTime(playhead, (Item) item, errorStatus);
            measuredVal = new Pair<>(item.getName(), mediaframe.toFrames(24));
            assertEquals(measuredVal, expected.get(frame));
        }

        try {
            sq.close();
            leader.close();
            body.close();
            credits.close();
            clip1.close();
            clip2.close();
            clip3.close();
            errorStatus.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
