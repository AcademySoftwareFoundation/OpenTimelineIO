package io.opentimeline;

import io.opentimeline.opentimelineio.*;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

public class ComposableTest {
    @Test
    public void testConstructor() {

        try {

            AnyDictionary metadata = new AnyDictionary();
            Any bar = new Any("bar");
            metadata.put("foo", bar);
            Composable seqi = new Composable("test", metadata);
            assertEquals(seqi.getName(), "test");
            assertEquals(metadata.size(), 1);
            assertEquals(metadata.get("foo").safelyCastString(), "bar");

        } catch (Exception e) {
            e.printStackTrace();
        }

    }

    @Test
    public void testSerialize() {
        try {

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
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}