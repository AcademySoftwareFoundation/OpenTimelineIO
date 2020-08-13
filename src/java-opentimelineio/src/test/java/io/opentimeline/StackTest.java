package io.opentimeline;

import io.opentimeline.opentime.RationalTime;
import io.opentimeline.opentime.TimeRange;
import io.opentimeline.opentimelineio.*;
import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.List;

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
        assertEquals(decoded, stack);
        Stack decodedStack = (Stack) decoded;
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
            assertEquals(st.trimChildRange(r), r);
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
            assertEquals(st.trimChildRange(r),
                    new TimeRange(
                            new RationalTime(100, 24),
                            new RationalTime(20, 24)));
            r = new TimeRange(
                    new RationalTime(110, 24),
                    new RationalTime(50, 24));
            assertEquals(st.trimChildRange(r),
                    new TimeRange(
                            new RationalTime(110, 24),
                            new RationalTime(40, 24)));
            r = new TimeRange(
                    new RationalTime(90, 24),
                    new RationalTime(1000, 24));
            assertEquals(st.trimChildRange(r), st.getSourceRange());
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

        assertEquals(stack.getDuration(errorStatus), new RationalTime(50, 24));

        assertEquals(
                stack.rangeOfChildAtIndex(0, errorStatus)
                        .getStartTime(), new RationalTime());
        assertEquals(
                stack.rangeOfChildAtIndex(1, errorStatus)
                        .getStartTime(), new RationalTime());
        assertEquals(
                stack.rangeOfChildAtIndex(2, errorStatus)
                        .getStartTime(), new RationalTime());

        assertEquals(
                stack.rangeOfChildAtIndex(0, errorStatus)
                        .getDuration(), new RationalTime(50, 24));
        assertEquals(
                stack.rangeOfChildAtIndex(1, errorStatus)
                        .getDuration(), new RationalTime(50, 24));
        assertEquals(
                stack.rangeOfChildAtIndex(2, errorStatus)
                        .getDuration(), new RationalTime(50, 24));

        assertEquals(stack.rangeOfChildAtIndex(2, errorStatus)
                , stack.getRangeOfChild(
                        stack.getChildren().get(2), errorStatus));
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
        assertEquals(st.getRangeOfChild(st.getChildren().get(0), errorStatus)
                , new TimeRange(
                        new RationalTime(0, 24),
                        new RationalTime(50, 24)));

        assertEquals(st.getTransformedTime(
                new RationalTime(25, 24),
                (Item) st.getChildren().get(0),
                errorStatus), new RationalTime(125, 24));
        assertEquals(
                (((Clip) st.getChildren().get(0)).getTransformedTime(
                        new RationalTime(125, 24),
                        st,
                        errorStatus)), new RationalTime(25, 24));

        assertEquals(st.trimmedRangeOfChildAtIndex(0, errorStatus), st.getSourceRange());

        assertEquals(((Clip) st.getChildren().get(0))
                        .getTrimmedRangeInParent(errorStatus),
                st.getTrimmedRangeOfChild(st.getChildren().get(0), errorStatus));

        // same test but via iteration
        for (int i = 0; i < st.getChildren().size(); i++) {
            assertEquals(
                    ((Clip) st.getChildren().get(i))
                            .getTrimmedRangeInParent(errorStatus),
                    st.getTrimmedRangeOfChild(st.getChildren().get(i), errorStatus));
        }
    }

    @Test
    public void testTransformedTime() {

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
        List<Composable> children = new ArrayList<>();
        children.add(clip1);
        children.add(clip2);
        children.add(clip3);
        ErrorStatus errorStatus = new ErrorStatus();
        st.setChildren(children, errorStatus);
        children = st.getChildren();
        assertEquals(children.get(0).getName(), "clip1");
        assertEquals(children.get(1).getName(), "clip2");
        assertEquals(children.get(2).getName(), "clip3");

        RationalTime testTime = new RationalTime(0, 24);
        assertEquals(
                st.getTransformedTime(testTime, clip1, errorStatus),
                new RationalTime(100, 24));

        // ensure that transformed_time does not edit in place
        assertEquals(testTime, new RationalTime(0, 24));

        assertEquals(
                st.getTransformedTime(new RationalTime(0, 24), clip2, errorStatus),
                new RationalTime(101, 24));
        assertEquals(
                st.getTransformedTime(new RationalTime(0, 24), clip3, errorStatus),
                new RationalTime(102, 24));

        assertEquals(
                st.getTransformedTime(new RationalTime(50, 24), clip1, errorStatus),
                new RationalTime(150, 24));
        assertEquals(
                st.getTransformedTime(new RationalTime(50, 24), clip2, errorStatus),
                new RationalTime(151, 24));
        assertEquals(
                st.getTransformedTime(new RationalTime(50, 24), clip3, errorStatus),
                new RationalTime(152, 24));

        assertEquals(
                clip1.getTransformedTime(new RationalTime(100, 24), st, errorStatus),
                new RationalTime(0, 24));
        assertEquals(
                clip2.getTransformedTime(new RationalTime(101, 24), st, errorStatus),
                new RationalTime(0, 24));
        assertEquals(
                clip3.getTransformedTime(new RationalTime(102, 24), st, errorStatus),
                new RationalTime(0, 24));

        assertEquals(
                clip1.getTransformedTime(new RationalTime(150, 24), st, errorStatus),
                new RationalTime(50, 24));
        assertEquals(
                clip2.getTransformedTime(new RationalTime(151, 24), st, errorStatus),
                new RationalTime(50, 24));
        assertEquals(
                clip3.getTransformedTime(new RationalTime(152, 24), st, errorStatus),
                new RationalTime(50, 24));
    }
}
