package io.opentimeline;

import io.opentimeline.opentimelineio.Any;
import io.opentimeline.opentimelineio.AnyDictionary;
import io.opentimeline.opentimelineio.SerializableObject;
import io.opentimeline.opentimelineio.SerializableObjectWithMetadata;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

public class SerializableObjectTest {

    @Test
    public void testConstructor() {
        try {
            AnyDictionary metadata = new AnyDictionary();
            metadata.put("foo", new Any("bar"));
            SerializableObjectWithMetadata so = new SerializableObjectWithMetadata(metadata);
            assertEquals(so.getMetadata().size(), 1);
            assertEquals(so.getMetadata().get("foo").safelyCastString(), "bar");
        } catch (Exception e) {
            e.printStackTrace();
        }

    }

    @Test
    public void testUpdate() {
        try {
            SerializableObjectWithMetadata so =
                    new SerializableObjectWithMetadata.SerializableObjectWithMetadataBuilder().build();
            so.getMetadata().put("foo", new Any("bar"));
            assertEquals(so.getMetadata().size(), 1);
            assertEquals(so.getMetadata().get("foo").safelyCastString(), "bar");
            SerializableObjectWithMetadata so2 =
                    new SerializableObjectWithMetadata.SerializableObjectWithMetadataBuilder().build();
            so2.getMetadata().put("foo", new Any("not bar"));
            assertEquals(so2.getMetadata().size(), 1);
            assertEquals(so2.getMetadata().get("foo").safelyCastString(), "not bar");
            so.setMetadata(so2.getMetadata());
            assertEquals(so.getMetadata().size(), 1);
            assertEquals(so.getMetadata().get("foo").safelyCastString(), "not bar");
        } catch (Exception e) {
            e.printStackTrace();
        }

    }

    @Test
    public void testEq() {
        try {
            SerializableObject so = new SerializableObject();
            SerializableObject so2 = new SerializableObject();
            assertNotEquals(so.nativeHandle, so2.nativeHandle);
            assertTrue(so.isEquivalentTo(so2));
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
