package io.opentimeline;

import io.opentimeline.opentime.RationalTime;
import io.opentimeline.opentime.TimeRange;
import io.opentimeline.opentimelineio.*;
import org.junit.jupiter.api.Test;

import java.util.ArrayList;

import static org.junit.jupiter.api.Assertions.*;

public class StackTest {

    @Test
    public void testConstructor() {
        Stack stack = new Stack.StackBuilder()
                .setName("test")
                .build();
        assertEquals(stack.getName(), "test");
    }

    @Test
    public void testSerialize() {
        Stack stack = new Stack.StackBuilder()
                .setName("test")
                .build();
        Clip clip = new Clip.ClipBuilder()
                .setName("testClip")
                .build();
        ErrorStatus errorStatus = new ErrorStatus();
        assertTrue(stack.appendChild(clip, errorStatus));

        String encoded = stack.toJSONString(errorStatus);
        SerializableObject decoded = SerializableObject.fromJSONString(encoded, errorStatus);
        assertTrue(decoded.isEquivalentTo(stack));
        Stack decodedStack = new Stack(decoded);
        assertNotNull(decodedStack.getChildren().get(0).parent());
    }

    @Test
    public void testTrimRangeChild() {

        Track track = new Track.TrackBuilder()
                .setName("foo")
                .build();
        Stack stack = new Stack.StackBuilder()
                .setName("foo")
                .build();

        Composition[] co = {track, stack};

        for (Composition st : co) {
            st.setSourceRange(
                    new TimeRange(
                            new RationalTime(100, 24),
                            new RationalTime(50, 24)));
            TimeRange r = new TimeRange(
                    new RationalTime(110, 24),
                    new RationalTime(30, 24));
            assertTrue(st.trimChildRange(r).equals(r));
            r = new TimeRange(
                    new RationalTime(0, 24),
                    new RationalTime(30, 24));
            assertNull(st.trimChildRange(r));
            r = new TimeRange(
                    new RationalTime(1000, 24),
                    new RationalTime(30, 24));
            assertNull(st.trimChildRange(r));
            r = new TimeRange(
                    new RationalTime(90, 24),
                    new RationalTime(30, 24));
            assertTrue(st.trimChildRange(r).equals(
                    new TimeRange(
                            new RationalTime(100, 24),
                            new RationalTime(20, 24))));
            r = new TimeRange(
                    new RationalTime(110, 24),
                    new RationalTime(50, 24));
            assertTrue(st.trimChildRange(r).equals(
                    new TimeRange(
                            new RationalTime(110, 24),
                            new RationalTime(40, 24))));
            r = new TimeRange(
                    new RationalTime(90, 24),
                    new RationalTime(1000, 24));
            assertTrue(st.trimChildRange(r).equals(st.getSourceRange()));
        }

    }

    @Test
    public void testRangeOfChild() {
        Clip clip1 = new Clip.ClipBuilder()
                .setName("clip1")
                .setSourceRange(
                        new TimeRange(
                                new RationalTime(100, 24),
                                new RationalTime(50, 24)
                        ))
                .build();
        Clip clip2 = new Clip.ClipBuilder()
                .setName("clip2")
                .setSourceRange(
                        new TimeRange(
                                new RationalTime(101, 24),
                                new RationalTime(50, 24)
                        ))
                .build();
        Clip clip3 = new Clip.ClipBuilder()
                .setName("clip3")
                .setSourceRange(
                        new TimeRange(
                                new RationalTime(102, 24),
                                new RationalTime(50, 24)
                        ))
                .build();
        ArrayList<Composable> children = new ArrayList<>();
        children.add(clip1);
        children.add(clip2);
        children.add(clip3);
        ErrorStatus errorStatus = new ErrorStatus();
        Stack stack = new Stack.StackBuilder()
                .setName("foo")
                .build();
        stack.setChildren(children, errorStatus);

        assertTrue(stack.getDuration(errorStatus).equals(new RationalTime(50, 24)));

        assertTrue(
                stack.rangeOfChildAtIndex(0, errorStatus)
                        .getStartTime().equals(new RationalTime()));
        assertTrue(
                stack.rangeOfChildAtIndex(1, errorStatus)
                        .getStartTime().equals(new RationalTime()));
        assertTrue(
                stack.rangeOfChildAtIndex(2, errorStatus)
                        .getStartTime().equals(new RationalTime()));

        assertTrue(
                stack.rangeOfChildAtIndex(0, errorStatus)
                        .getDuration().equals(new RationalTime(50, 24)));
        assertTrue(
                stack.rangeOfChildAtIndex(1, errorStatus)
                        .getDuration().equals(new RationalTime(50, 24)));
        assertTrue(
                stack.rangeOfChildAtIndex(2, errorStatus)
                        .getDuration().equals(new RationalTime(50, 24)));

        assertTrue(stack.rangeOfChildAtIndex(2, errorStatus)
                .equals(
                        stack.getRangeOfChild(
                                stack.getChildren().get(2), errorStatus)));
    }

    @Test
    public void testRangeOfChildWithDuration() {

        TimeRange stSourceRange = new TimeRange(
                new RationalTime(5, 24),
                new RationalTime(5, 24));

        Stack st = new Stack.StackBuilder()
                .setName("foo")
                .setSourceRange(stSourceRange)
                .build();
        Clip clip1 = new Clip.ClipBuilder()
                .setName("clip1")
                .setSourceRange(
                        new TimeRange(
                                new RationalTime(100, 24),
                                new RationalTime(50, 24)
                        ))
                .build();
        Clip clip2 = new Clip.ClipBuilder()
                .setName("clip2")
                .setSourceRange(
                        new TimeRange(
                                new RationalTime(101, 24),
                                new RationalTime(50, 24)
                        ))
                .build();
        Clip clip3 = new Clip.ClipBuilder()
                .setName("clip3")
                .setSourceRange(
                        new TimeRange(
                                new RationalTime(102, 24),
                                new RationalTime(50, 24)
                        ))
                .build();
        ArrayList<Composable> children = new ArrayList<>();
        children.add(clip1);
        children.add(clip2);
        children.add(clip3);
        ErrorStatus errorStatus = new ErrorStatus();
        st.setChildren(children, errorStatus);

        // getRangeOfChild always returns the pre-trimmed range
        // To get post-trim range call getTrimmedRangeOfChild
        assertTrue(st.getRangeOfChild(st.getChildren().get(0), errorStatus)
                .equals(new TimeRange(
                        new RationalTime(0, 24),
                        new RationalTime(50, 24))));

        assertTrue(st.getTransformedTime(
                new RationalTime(25, 24),
                new Item(st.getChildren().get(0)),
                errorStatus).equals(new RationalTime(125, 24)));
        assertTrue(
                (new Clip(st.getChildren().get(0))).getTransformedTime(
                        new RationalTime(125, 24),
                        st,
                        errorStatus).equals(new RationalTime(25, 24)));

        assertTrue(st.trimmedRangeOfChildAtIndex(0, errorStatus).equals(st.getSourceRange()));

        assertTrue(new Clip(st.getChildren().get(0))
                .getTrimmedRangeInParent(errorStatus)
                .equals(st.getTrimmedRangeOfChild(st.getChildren().get(0), errorStatus)));

        // same test but via iteration
        for (int i = 0; i < st.getChildren().size(); i++) {
            assertTrue(new Clip(st.getChildren().get(i))
                    .getTrimmedRangeInParent(errorStatus)
                    .equals(st.getTrimmedRangeOfChild(st.getChildren().get(i), errorStatus)));
        }
    }
}
