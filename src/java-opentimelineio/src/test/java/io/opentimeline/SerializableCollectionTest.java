//package io.opentimeline;
//
//import io.opentimeline.opentimelineio.*;
//import org.junit.jupiter.api.AfterEach;
//import org.junit.jupiter.api.BeforeEach;
//import org.junit.jupiter.api.Test;
//
//import java.util.ArrayList;
//import java.util.List;
//
//import static org.junit.jupiter.api.Assertions.*;
//
//public class SerializableCollectionTest {
//
//    Clip clip;
//    MissingReference missingReference;
//    AnyDictionary metadata;
//    SerializableCollection sc;
//    ArrayList<SerializableObject> children;
//
//    @BeforeEach
//    public void setUp() {
//        clip = new Clip.ClipBuilder()
//                .setName("testClip")
//                .build();
//        missingReference = new MissingReference.MissingReferenceBuilder().build();
//        children = new ArrayList<>();
//        children.add(clip);
//        children.add(missingReference);
//        metadata = new AnyDictionary();
//        metadata.put("foo", new Any("bar"));
//        sc = new SerializableCollection.SerializableCollectionBuilder()
//                .setName("test")
//                .setChildren(children)
//                .build();
//    }
//
//    @Test
//    public void testConstructor() {
//        assertEquals(sc.getName(), "test");
//        List<SerializableObject.Retainer<SerializableObject>> ch = sc.getChildren();
//        assertEquals(ch.size(), children.size());
//        for (int i = 0; i < ch.size(); i++) {
//            SerializableObject child = children.get(i);
//            SerializableObject childCompare = ch.get(i).value();
//            assertTrue(child.isEquivalentTo(childCompare));
//        }
//    }
//
//    @Test
//    public void testSerialize() {
//        Any scAny = new Any(sc);
//        ErrorStatus errorStatus = new ErrorStatus();
//        String encoded = Serialization.serializeJSONToString(scAny, errorStatus);
//        SerializableObject decoded = SerializableObject.fromJSONString(encoded, errorStatus);
//        assertTrue(decoded.isEquivalentTo(sc));
//    }
//
//    @AfterEach
//    public void tearDown() {
//        try {
//            clip.close();
//            missingReference.close();
//            metadata.close();
//            sc.close();
//        } catch (Exception e) {
//            e.printStackTrace();
//        }
//    }
//
//}
