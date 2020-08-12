package io.opentimeline;

import io.opentimeline.opentime.RationalTime;
import io.opentimeline.opentime.TimeRange;
import io.opentimeline.opentimelineio.*;
import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

public class ItemTest {

    @Test
    public void testConstructor() {
        TimeRange tr = new TimeRange(
                new RationalTime(0, 1),
                new RationalTime(10, 1));
        Item it = new Item.ItemBuilder()
                .setName("foo")
                .setSourceRange(tr)
                .build();
        assertEquals(it.getSourceRange(), tr);
        assertEquals(it.getName(), "foo");
        ErrorStatus errorStatus = new ErrorStatus();
        String encoded = it.toJSONString(errorStatus);
        Item decoded = (Item) SerializableObject.fromJSONString(encoded, errorStatus);
        assertEquals(it, decoded);
        try {
            it.close();
            errorStatus.close();
            decoded.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testCopyArguments() {
        // make sure all the arguments are copied and not referenced
        TimeRange tr = new TimeRange(
                new RationalTime(0, 1),
                new RationalTime(10, 1));
        String name = "foobar";
        ArrayList<Effect> effects = new ArrayList<>();
        ArrayList<Marker> markers = new ArrayList<>();
        AnyDictionary metadata = new AnyDictionary();
        Item it = new Item.ItemBuilder()
                .setName(name)
                .setSourceRange(tr)
                .setEffects(effects)
                .setMarkers(markers)
                .setMetadata(metadata)
                .build();
        name = "foobaz";
        assertNotEquals(name, it.getName());

        tr = new TimeRange(
                new RationalTime(1, tr.getStartTime().getRate()),
                tr.getDuration());
        assertNotEquals(it.getSourceRange().getStartTime(), tr.getStartTime());
        markers.add(new Marker.MarkerBuilder().build());
        assertNotEquals(markers, it.getMarkers());
        metadata.put("foo", new Any("bar"));
        assertNotEquals(metadata, it.getMetadata());
        try {
            it.close();
            metadata.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testDuration() {
        TimeRange tr = new TimeRange(
                new RationalTime(0, 1),
                new RationalTime(10, 1));
        Item it = new Item.ItemBuilder()
                .setSourceRange(tr)
                .build();
        ErrorStatus errorStatus = new ErrorStatus();
        assertEquals(it.getDuration(errorStatus), tr.getDuration());
        try {
            it.close();
            errorStatus.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testAvailableRange() {
        Item it = new Item.ItemBuilder().build();
        ErrorStatus errorStatus = new ErrorStatus();
        it.getAvailableRange(errorStatus);
        assertEquals(errorStatus.getOutcome(), ErrorStatus.Outcome.NOT_IMPLEMENTED);
        try {
            it.close();
            errorStatus.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testDurationAndSourceRange() {
        Item it = new Item.ItemBuilder().build();
        ErrorStatus errorStatus = new ErrorStatus();
        it.getDuration(errorStatus);
        assertEquals(errorStatus.getOutcome(), ErrorStatus.Outcome.NOT_IMPLEMENTED);
        try {
            errorStatus.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
        errorStatus = new ErrorStatus();
        assertNull(it.getSourceRange());
        TimeRange tr = new TimeRange(
                new RationalTime(1, 1),
                new RationalTime(10, 1));
        Item it2 = new Item.ItemBuilder()
                .setSourceRange(tr)
                .build();
        assertEquals(tr, it2.getSourceRange());
        assertEquals(it2.getDuration(errorStatus), tr.getDuration());
        try {
            it.close();
            it2.close();
            errorStatus.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testTrimmedRange() {
        Item it = new Item.ItemBuilder().build();
        ErrorStatus errorStatus = new ErrorStatus();
        it.getTrimmedRange(errorStatus);
        assertEquals(errorStatus.getOutcome(), ErrorStatus.Outcome.NOT_IMPLEMENTED);
        try {
            errorStatus.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
        errorStatus = new ErrorStatus();
        TimeRange tr = new TimeRange(
                new RationalTime(1, 1),
                new RationalTime(10, 1));
        Item it2 = new Item.ItemBuilder()
                .setSourceRange(tr)
                .build();
        assertEquals(it2.getTrimmedRange(errorStatus), tr);
        try {
            it.close();
            it2.close();
            errorStatus.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testSerialize() {
        TimeRange tr = new TimeRange(
                new RationalTime(0, 1),
                new RationalTime(10, 1));
        Item it = new Item.ItemBuilder()
                .setSourceRange(tr)
                .build();
        ErrorStatus errorStatus = new ErrorStatus();
        String encoded = it.toJSONString(errorStatus);
        Item decoded = (Item) SerializableObject.fromJSONString(encoded, errorStatus);
        assertEquals(it, decoded);
        try {
            it.close();
            decoded.close();
            errorStatus.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testMetadata() {
        TimeRange tr = new TimeRange(new RationalTime(10, 1));
        AnyDictionary metadata = new AnyDictionary();
        metadata.put("foo", new Any("bar"));
        Item it = new Item.ItemBuilder()
                .setSourceRange(tr)
                .setMetadata(metadata)
                .build();
        ErrorStatus errorStatus = new ErrorStatus();
        String encoded = it.toJSONString(errorStatus);
        Item decoded = (Item) SerializableObject.fromJSONString(encoded, errorStatus);
        assertEquals(it, decoded);
        assertEquals(it.getMetadata().size(),
                decoded.getMetadata().size());
        assertEquals(it.getMetadata().get("foo").safelyCastString(),
                decoded.getMetadata().get("foo").safelyCastString());
        try {
            it.close();
            metadata.close();
            decoded.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testAddEffect() {
        TimeRange tr = new TimeRange(new RationalTime(10, 1));
        AnyDictionary metadata = new AnyDictionary();
        metadata.put("amount", new Any("100"));
        Effect effect = new Effect.EffectBuilder()
                .setEffectName("blur")
                .setMetadata(metadata)
                .build();
        ArrayList<Effect> effects = new ArrayList<>();
        effects.add(effect);
        Item it = new Item.ItemBuilder()
                .setSourceRange(tr)
                .setEffects(effects)
                .build();
        ErrorStatus errorStatus = new ErrorStatus();
        String encoded = it.toJSONString(errorStatus);
        Item decoded = (Item) SerializableObject.fromJSONString(encoded, errorStatus);
        assertEquals(it, decoded);
        assertEquals(it.getEffects(), decoded.getEffects());
        try {
            metadata.close();
            it.close();
            effect.close();
            errorStatus.close();
            decoded.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testAddMarker() {
        TimeRange tr = new TimeRange(new RationalTime(10, 1));
        AnyDictionary metadata = new AnyDictionary();
        metadata.put("some stuff to mark", new Any("100"));
        Marker marker = new Marker.MarkerBuilder()
                .setName("test_marker")
                .setMarkedRange(tr)
                .setMetadata(metadata)
                .build();
        ArrayList<Marker> markers = new ArrayList<>();
        markers.add(marker);
        Item it = new Item.ItemBuilder()
                .setSourceRange(tr)
                .setMarkers(markers)
                .build();
        ErrorStatus errorStatus = new ErrorStatus();
        String encoded = it.toJSONString(errorStatus);
        Item decoded = (Item) SerializableObject.fromJSONString(encoded, errorStatus);
        assertEquals(it, decoded);
        assertEquals(it.getMarkers(), decoded.getMarkers());
        try {
            metadata.close();
            it.close();
            marker.close();
            errorStatus.close();
            decoded.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testVisibleRange() {
        Clip A = new Clip.ClipBuilder()
                .setName("A")
                .setSourceRange(new TimeRange(
                        new RationalTime(1, 30),
                        new RationalTime(50, 30)))
                .build();
        Clip B = new Clip.ClipBuilder()
                .setName("B")
                .setSourceRange(new TimeRange(
                        new RationalTime(100, 30),
                        new RationalTime(50, 30)))
                .build();
        Clip C = new Clip.ClipBuilder()
                .setName("C")
                .setSourceRange(new TimeRange(
                        new RationalTime(50, 30),
                        new RationalTime(50, 30)))
                .build();
        Clip D = new Clip.ClipBuilder()
                .setName("D")
                .setSourceRange(new TimeRange(
                        new RationalTime(1, 30),
                        new RationalTime(50, 30)))
                .build();
        Transition transition1 = new Transition.TransitionBuilder()
                .setInOffset(new RationalTime(7, 30))
                .setOutOffset(new RationalTime(10, 30))
                .build();
        Transition transition2 = new Transition.TransitionBuilder()
                .setInOffset(new RationalTime(17, 30))
                .setOutOffset(new RationalTime(15, 30))
                .build();
        Track track = new Track.TrackBuilder()
                .setName("V1")
                .build();
        ErrorStatus errorStatus = new ErrorStatus();
        assertTrue(track.appendChild(A, errorStatus));
        assertTrue(track.appendChild(transition1, errorStatus));
        assertTrue(track.appendChild(B, errorStatus));
        assertTrue(track.appendChild(transition2, errorStatus));
        assertTrue(track.appendChild(C, errorStatus));
        assertTrue(track.appendChild(D, errorStatus));
        Stack stack = new Stack.StackBuilder()
                .build();
        assertTrue(stack.appendChild(track, errorStatus));
        Timeline timeline = new Timeline.TimelineBuilder().build();
        timeline.setTracks(stack);

        List<Composable> trackChildren = track.getChildren();
        ArrayList<String> clipNames = new ArrayList<>();
        ArrayList<TimeRange> clipTrimmedRanges = new ArrayList<>();
        ArrayList<TimeRange> clipVisibleRanges = new ArrayList<>();
        for (Composable composable : trackChildren) {
            if (composable instanceof Clip) {
                clipNames.add(composable.getName());
                clipTrimmedRanges.add(((Clip) composable).getTrimmedRange(errorStatus));
                clipVisibleRanges.add(((Clip) composable).getVisibleRange(errorStatus));
            }
        }
        assertEquals(clipNames, new ArrayList<>(Arrays.asList("A", "B", "C", "D")));
        assertEquals(clipTrimmedRanges, new ArrayList<>(Arrays.asList(
                new TimeRange(
                        new RationalTime(1, 30),
                        new RationalTime(50, 30)),
                new TimeRange(
                        new RationalTime(100, 30),
                        new RationalTime(50, 30)),
                new TimeRange(
                        new RationalTime(50, 30),
                        new RationalTime(50, 30)),
                new TimeRange(
                        new RationalTime(1, 30),
                        new RationalTime(50, 30))
        )));
        assertEquals(clipVisibleRanges, new ArrayList<>(Arrays.asList(
                new TimeRange(
                        new RationalTime(1, 30),
                        new RationalTime(50 + 10, 30)),
                new TimeRange(
                        new RationalTime(100 - 7, 30),
                        new RationalTime(50 + 15 + 7, 30)),
                new TimeRange(
                        new RationalTime(33, 30),
                        new RationalTime(50 + 17, 30)),
                new TimeRange(
                        new RationalTime(1, 30),
                        new RationalTime(50, 30))
        )));
        try {
            timeline.close();
            errorStatus.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
