package io.opentimeline;

import io.opentimeline.opentime.RationalTime;
import io.opentimeline.opentime.TimeRange;
import io.opentimeline.opentimelineio.*;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

public class EdgeCases {

    @Test
    public void testEmptyCompositions() {
        Timeline timeline = new Timeline.TimelineBuilder().build();
        Stack stack = timeline.getTracks();
        List<Composable> tracks = stack.getChildren();
        assertEquals(tracks.size(), 0);
        ErrorStatus errorStatus = new ErrorStatus();
        assertEquals(stack.getDuration(errorStatus), new RationalTime(0, 24));
        try {
            timeline.close();
            errorStatus.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testIteratingOverDupes() {
        Timeline timeline = new Timeline.TimelineBuilder().build();
        Track track = new Track.TrackBuilder().build();
        Clip clip = new Clip.ClipBuilder()
                .setName("Dupe")
                .setSourceRange(new TimeRange(
                        new RationalTime(10, 30),
                        new RationalTime(15, 30)))
                .build();
        ErrorStatus errorStatus = new ErrorStatus();
        for (int i = 0; i < 10; i++) {
            Clip dupe = (Clip) clip.clone(errorStatus);
            assertTrue(track.appendChild(dupe, errorStatus));
        }
        Stack stack = new Stack.StackBuilder().build();
        assertTrue(stack.appendChild(track, errorStatus));
        timeline.setTracks(stack);
        assertEquals(track.getChildren().size(), 10);
        assertEquals(track.getTrimmedRange(errorStatus),
                new TimeRange(
                        new RationalTime(0, 30),
                        new RationalTime(150, 30)));

        List<Composable> trackChildren = track.getChildren();
        TimeRange previous = null;
        // test normal iteration
        for (Composable child : trackChildren) {
            Clip childClip = (Clip) child;
            assertEquals(track.getRangeOfChild(childClip, errorStatus),
                    childClip.getRangeInParent(errorStatus));
            assertNotEquals(childClip.getRangeInParent(errorStatus), previous);
            previous = childClip.getRangeInParent(errorStatus);
        }

        previous = null;
        // compare to iteration by index
        for (int i = 0; i < trackChildren.size(); i++) {
            Clip childClip = (Clip) trackChildren.get(i);
            assertEquals(track.getRangeOfChild(childClip, errorStatus),
                    track.rangeOfChildAtIndex(i, errorStatus));
            assertEquals(track.getRangeOfChild(childClip, errorStatus),
                    childClip.getRangeInParent(errorStatus));
            assertNotEquals(childClip.getRangeInParent(errorStatus), previous);
            previous = childClip.getRangeInParent(errorStatus);
        }
    }

}
