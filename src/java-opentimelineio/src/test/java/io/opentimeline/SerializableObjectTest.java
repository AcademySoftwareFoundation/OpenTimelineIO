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
        AnyDictionary metadata = new AnyDictionary();
        metadata.put("foo", new Any("bar"));
        SerializableObjectWithMetadata so = new SerializableObjectWithMetadata(metadata);
        assertEquals(so.getMetadata().size(), 1);
        assertEquals(so.getMetadata().get("foo").safelyCastString(), "bar");
        try {
            metadata.close();
            so.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testStr() {
        AnyDictionary metadata = new AnyDictionary();
        metadata.put("foo", new Any("bar"));
        SerializableObjectWithMetadata so = new SerializableObjectWithMetadata(metadata);
        assertEquals(so.toString(),
                "io.opentimeline.opentimelineio.SerializableObjectWithMetadata(" +
                        "name=, " +
                        "metadata=io.opentimeline.opentimelineio.AnyDictionary{" +
                        "foo=io.opentimeline.opentimelineio.Any(value=bar)})");
        SerializableObject serializableObject = new SerializableObject();
        assertEquals(serializableObject.toString(),
                "io.opentimeline.opentimelineio.SerializableObject()");
        try {
            metadata.close();
            so.close();
            serializableObject.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testUpdate() {
        SerializableObjectWithMetadata so =
                new SerializableObjectWithMetadata.SerializableObjectWithMetadataBuilder().build();
        AnyDictionary metadata = so.getMetadata();
        metadata.put("foo", new Any("bar"));
        so.setMetadata(metadata);
        assertEquals(so.getMetadata().size(), 1);
        assertEquals(so.getMetadata().get("foo").safelyCastString(), "bar");
        SerializableObjectWithMetadata so2 =
                new SerializableObjectWithMetadata.SerializableObjectWithMetadataBuilder().build();
        metadata = so2.getMetadata();
        metadata.put("foo", new Any("not bar"));
        so2.setMetadata(metadata);
        assertEquals(so2.getMetadata().size(), 1);
        assertEquals(so2.getMetadata().get("foo").safelyCastString(), "not bar");
        so.setMetadata(so2.getMetadata());
        assertEquals(so.getMetadata().size(), 1);
        assertEquals(so.getMetadata().get("foo").safelyCastString(), "not bar");
        try {
            so.close();
            metadata.close();
            so2.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testEq() {
        SerializableObject so = new SerializableObject();
        SerializableObject so2 = new SerializableObject();
        assertNotEquals(so.getNativeManager().nativeHandle, so2.getNativeManager().nativeHandle);
        assertTrue(so.isEquivalentTo(so2));
        try {
            so.close();
            so2.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
