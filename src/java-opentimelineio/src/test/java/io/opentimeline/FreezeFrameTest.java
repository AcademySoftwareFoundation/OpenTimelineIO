//package io.opentimeline;
//
//import io.opentimeline.opentimelineio.Any;
//import io.opentimeline.opentimelineio.AnyDictionary;
//import io.opentimeline.opentimelineio.FreezeFrame;
//import org.junit.jupiter.api.Test;
//
//import static org.junit.jupiter.api.Assertions.*;
//
//public class FreezeFrameTest {
//
//    @Test
//    public void testConstructor() {
//        try {
//            AnyDictionary metadata = new AnyDictionary();
//            metadata.put("foo", new Any("bar"));
//            FreezeFrame freezeFrame = new FreezeFrame("Foo", metadata);
//            assertEquals(freezeFrame.getEffectName(), "FreezeFrame");
//            assertEquals(freezeFrame.getName(), "Foo");
//            assertEquals(freezeFrame.getTimeScalar(), 0);
//            AnyDictionary effectMetadata = freezeFrame.getMetadata();
//            assertEquals(effectMetadata.size(), 1);
//            assertEquals(effectMetadata.get("foo").safelyCastString(), "bar");
//        } catch (Exception e) {
//            e.printStackTrace();
//        }
//    }
//
//}
