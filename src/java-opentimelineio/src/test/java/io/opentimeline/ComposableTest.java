package io.opentimeline;

import io.opentimeline.opentimelineio.*;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

public class ComposableTest {
    @Test
    public void testConstructor() {
        AnyDictionary metadata = new AnyDictionary();
        Any bar = new Any("bar");
        metadata.put("foo", bar);
        Composable seqi = new Composable("test", metadata);
        assertEquals(seqi.getName(), "test");
        assertEquals(metadata.size(), 1);
        assertEquals(metadata.get("foo").safelyCastString(), "bar");
        try {
            metadata.close();
            bar.close();
            seqi.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testStr() {
        Composable composable = new Composable.ComposableBuilder().build();
        assertEquals(composable.toString(),
                "io.opentimeline.opentimelineio.Composable(" +
                        "name=, metadata=io.opentimeline.opentimelineio.AnyDictionary{})");
        try {
            composable.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testSerialize() {
        AnyDictionary metadata = new AnyDictionary();
        Any bar = new Any("bar");
        metadata.put("foo", bar);
        Composable seqi = new Composable("test", metadata);
        ErrorStatus errorStatus = new ErrorStatus();
        Any seqiAny = new Any(seqi);
        Serialization serialization = new Serialization();
        String encoded = serialization.serializeJSONToString(seqiAny, errorStatus);
        SerializableObject decoded = SerializableObject.fromJSONString(encoded, errorStatus);
        assertTrue(seqi.isEquivalentTo(decoded));

        try {
            metadata.close();
            bar.close();
            seqi.close();
            errorStatus.close();
            seqiAny.close();
            decoded.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}