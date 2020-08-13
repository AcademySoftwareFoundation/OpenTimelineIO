package io.opentimeline;

import io.opentimeline.opentime.RationalTime;
import io.opentimeline.opentime.TimeRange;
import io.opentimeline.opentimelineio.*;
import org.junit.jupiter.api.Test;

import java.util.ArrayList;

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
}
