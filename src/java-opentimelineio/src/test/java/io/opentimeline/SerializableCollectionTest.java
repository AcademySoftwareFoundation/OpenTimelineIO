package io.opentimeline;

import io.opentimeline.opentimelineio.*;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

public class SerializableCollectionTest {

    Clip clip;
    MissingReference missingReference;
    AnyDictionary metadata;
    SerializableCollection sc;
    ArrayList<SerializableObject> children;

    @BeforeEach
    public void setUp() {
        clip = new Clip.ClipBuilder()
                .setName("testClip")
                .build();
        missingReference = new MissingReference.MissingReferenceBuilder().build();
        children = new ArrayList<>();
        children.add(clip);
        children.add(missingReference);
        metadata = new AnyDictionary();
        metadata.put("foo", new Any("bar"));
        sc = new SerializableCollection.SerializableCollectionBuilder()
                .setName("test")
                .setChildren(children)
                .build();
    }

    @Test
    public void testConstructor() {
        assertEquals(sc.getName(), "test");
        List<SerializableObject> ch = sc.getChildren();
        assertEquals(ch.size(), children.size());
        for (int i = 0; i < ch.size(); i++) {
            SerializableObject child = children.get(i);
            SerializableObject childCompare = ch.get(i);
            assertTrue(child.isEquivalentTo(childCompare));
        }
    }

    @Test
    public void testStr() {
        assertEquals(sc.toString(),
                "io.opentimeline.opentimelineio.SerializableCollection(" +
                        "name=test, " +
                        "children=[" +
                        "io.opentimeline.opentimelineio.Clip(name=testClip, " +
                        "mediaReference=io.opentimeline.opentimelineio.MissingReference(name=, " +
                        "availableRange=null, " +
                        "metadata=io.opentimeline.opentimelineio.AnyDictionary{}), " +
                        "sourceRange=null, " +
                        "metadata=io.opentimeline.opentimelineio.AnyDictionary{}), " +
                        "io.opentimeline.opentimelineio.MissingReference(name=, " +
                        "availableRange=null, " +
                        "metadata=io.opentimeline.opentimelineio.AnyDictionary{})], " +
                        "metadata=io.opentimeline.opentimelineio.AnyDictionary{})");
    }

    @Test
    public void testSerialize() {
        Any scAny = new Any(sc);
        ErrorStatus errorStatus = new ErrorStatus();
        Serialization serialization = new Serialization();
        String encoded = serialization.serializeJSONToString(scAny, errorStatus);
        SerializableObject decoded = SerializableObject.fromJSONString(encoded, errorStatus);
        assertTrue(decoded.isEquivalentTo(sc));
        try {
            scAny.close();
            decoded.close();
            errorStatus.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @AfterEach
    public void tearDown() {
        try {
            clip.getNativeManager().close();
            missingReference.getNativeManager().close();
            metadata.getNativeManager().close();
            sc.getNativeManager().close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

}
