package io.opentimeline;

import io.opentimeline.opentimelineio.*;
import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

public class CompositionTest {

    @Test
    public void testConstructor() {
        Item item = new Item.ItemBuilder().build();
        Composition composition = new Composition.CompositionBuilder()
                .setName("test")
                .build();
        ErrorStatus errorStatus = new ErrorStatus();
        assertTrue(composition.appendChild(item, errorStatus));
        assertEquals(composition.getName(), "test");
        assertTrue(composition.getChildren().get(0).isEquivalentTo(item));
        assertEquals(composition.getCompositionKind(), "Composition");
        try {
            item.close();
            composition.close();
            errorStatus.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testStr() {
        Composition composition = new Composition.CompositionBuilder()
                .build();
        assertEquals(composition.toString(),
                "io.opentimeline.opentimelineio.Composition(" +
                        "name=, " +
                        "children=[], " +
                        "sourceRange=null, " +
                        "metadata=io.opentimeline.opentimelineio.AnyDictionary{})");
        try {
            composition.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testEquality() {
        Composition c0 = new Composition.CompositionBuilder().build();
        Composition c00 = new Composition.CompositionBuilder().build();
        assertTrue(c0.isEquivalentTo(c00));

        Item a = new Item.ItemBuilder()
                .setName("A")
                .build();
        Item b = new Item.ItemBuilder()
                .setName("B")
                .build();
        Item c = new Item.ItemBuilder()
                .setName("C")
                .build();

        ErrorStatus errorStatus = new ErrorStatus();

        Composition co1 = new Composition.CompositionBuilder().build();
        assertTrue(co1.appendChild(a, errorStatus));
        assertTrue(co1.appendChild(b, errorStatus));
        assertTrue(co1.appendChild(c, errorStatus));

        Item x = new Item.ItemBuilder()
                .setName("X")
                .build();
        Item y = new Item.ItemBuilder()
                .setName("Y")
                .build();
        Item z = new Item.ItemBuilder()
                .setName("Z")
                .build();

        Composition co2 = new Composition.CompositionBuilder().build();
        assertTrue(co2.appendChild(x, errorStatus));
        assertTrue(co2.appendChild(y, errorStatus));
        assertTrue(co2.appendChild(z, errorStatus));

        Item a2 = new Item.ItemBuilder()
                .setName("A")
                .build();
        Item b2 = new Item.ItemBuilder()
                .setName("B")
                .build();
        Item c2 = new Item.ItemBuilder()
                .setName("C")
                .build();

        Composition co3 = new Composition.CompositionBuilder().build();
        assertTrue(co2.appendChild(a2, errorStatus));
        assertTrue(co2.appendChild(b2, errorStatus));
        assertTrue(co2.appendChild(c2, errorStatus));

        assertNotEquals(co1.getNativeManager().nativeHandle, co2.getNativeManager().nativeHandle);
        assertFalse(co1.isEquivalentTo(co2));

        assertNotEquals(co1.getNativeManager().nativeHandle, co3.getNativeManager().nativeHandle);
        assertFalse(co1.isEquivalentTo(co3));

        try {
            c0.close();
            c00.close();
            c.close();
            b.close();
            a.close();
            errorStatus.close();
            co1.close();
            z.close();
            y.close();
            x.close();
            co2.close();
            c2.close();
            b2.close();
            a2.close();
            co3.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testReplacingChildren() {
        Item a = new Item.ItemBuilder()
                .setName("A")
                .build();
        Item b = new Item.ItemBuilder()
                .setName("B")
                .build();
        Item c = new Item.ItemBuilder()
                .setName("C")
                .build();
        Composition co = new Composition.CompositionBuilder().build();
        ErrorStatus errorStatus = new ErrorStatus();
        assertTrue(co.appendChild(a, errorStatus));
        assertTrue(co.appendChild(b, errorStatus));
        List<Composable> children = co.getChildren();
        assertEquals(children.size(), 2);
        assertTrue(children.get(0).isEquivalentTo(a));
        assertTrue(children.get(1).isEquivalentTo(b));
        assertTrue(co.removeChild(1, errorStatus));
        children = co.getChildren();
        assertEquals(children.size(), 1);
        assertTrue(co.setChild(0, c, errorStatus));
        children = co.getChildren();
        assertEquals(children.size(), 1);
        assertTrue(children.get(0).isEquivalentTo(c));

        co.clearChildren();

        children = new ArrayList<>();
        children.add(a);
        children.add(b);
        co.setChildren(children, errorStatus);
        children = co.getChildren();
        assertEquals(children.size(), 2);
        assertTrue(children.get(0).isEquivalentTo(a));
        assertTrue(children.get(1).isEquivalentTo(b));

        co.clearChildren();//need to clear children because setChildren does not clear parent of previous children

        children = co.getChildren();
        assertEquals(children.size(), 0);
        children = new ArrayList<>();
        children.add(c);
        children.add(b);
        children.add(a);
        co.setChildren(children, errorStatus);
        children = co.getChildren();
        assertEquals(children.size(), 3);
        assertTrue(children.get(0).isEquivalentTo(c));
        assertTrue(children.get(1).isEquivalentTo(b));
        assertTrue(children.get(2).isEquivalentTo(a));

        try {
            a.close();
            b.close();
            c.close();
            co.close();
            errorStatus.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testIsParentOf() {
        Composition co = new Composition.CompositionBuilder().build();
        Composition co2 = new Composition.CompositionBuilder().build();
        assertFalse(co.isParentOf(co2));
        ErrorStatus errorStatus = new ErrorStatus();
        assertTrue(co.appendChild(co2, errorStatus));
        assertTrue(co.isParentOf(co2));
        try {
            co.close();
            co2.close();
            errorStatus.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testParentManip() {
        Item it = new Item.ItemBuilder().build();
        Composition co = new Composition.CompositionBuilder().build();
        ErrorStatus errorStatus = new ErrorStatus();
        assertTrue(co.appendChild(it, errorStatus));
        assertTrue(it.parent().isEquivalentTo(co));
        try {
            it.close();
            co.close();
            errorStatus.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testMoveChild() {
        Item it = new Item.ItemBuilder().build();
        Composition co = new Composition.CompositionBuilder().build();
        ErrorStatus errorStatus = new ErrorStatus();
        assertTrue(co.appendChild(it, errorStatus));
        assertTrue(it.parent().isEquivalentTo(co));

        Composition co2 = new Composition.CompositionBuilder().build();
        assertFalse(co2.appendChild(it, errorStatus));
        assertEquals(errorStatus.getOutcome(), ErrorStatus.Outcome.CHILD_ALREADY_PARENTED);
        try {
            errorStatus.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
        errorStatus = new ErrorStatus();
        assertTrue(co.removeChild(0, errorStatus));
        assertTrue(co2.appendChild(it, errorStatus));
        assertTrue(it.parent().isEquivalentTo(co2));
        try {
            it.close();
            co.close();
            errorStatus.close();
            co2.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testRemoveActuallyRemoves() {
        Track track = new Track.TrackBuilder().build();
        Clip clip = new Clip.ClipBuilder().build();
        ErrorStatus errorStatus = new ErrorStatus();
        assertTrue(track.appendChild(clip, errorStatus));
        assertTrue(track.getChildren().get(0).isEquivalentTo(clip));
        // delete by index
        assertTrue(track.removeChild(0, errorStatus));
        assertEquals(track.getChildren().size(), 0);
        assertTrue(track.appendChild(clip, errorStatus));
        Clip clip2 = new Clip.ClipBuilder()
                .setName("test")
                .build();
        assertTrue(track.setChild(0, clip2, errorStatus));
        assertTrue(track.getChildren().get(0).isEquivalentTo(clip2));
        assertFalse(track.getChildren().get(0).isEquivalentTo(clip));
        try {
            track.close();
            clip.close();
            errorStatus.close();
            clip2.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
