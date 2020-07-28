//package io.opentimeline;
//
//import io.opentimeline.opentimelineio.Any;
//import io.opentimeline.opentimelineio.AnyDictionary;
//import io.opentimeline.opentimelineio.LinearTimeWarp;
//import org.junit.jupiter.api.Test;
//
//import static org.junit.jupiter.api.Assertions.*;
//
//public class LinearTimeWarpTest {
//    @Test
//    public void testConstructor() {
//        try {
//            AnyDictionary metadata = new AnyDictionary();
//            metadata.put("foo", new Any("bar"));
//            LinearTimeWarp linearTimeWarp = new LinearTimeWarp.LinearTimeWarpBuilder()
//                    .setEffectName("Foo")
//                    .setTimeScalar(2.5)
//                    .setMetadata(metadata)
//                    .build();
//            assertEquals(linearTimeWarp.getEffectName(), "Foo");
//            assertEquals(linearTimeWarp.getTimeScalar(), 2.5);
//            AnyDictionary effectMetadata = linearTimeWarp.getMetadata();
//            assertEquals(effectMetadata.size(), 1);
//            assertEquals(effectMetadata.get("foo").safelyCastString(), "bar");
//        }catch (Exception e){
//            e.printStackTrace();
//        }
//    }
//}
