package io.opentimeline;

import io.opentimeline.opentimelineio.*;
import org.junit.jupiter.api.Test;

import java.util.ArrayList;

public class DummyTest {

    @Test
    public void test() {
        try {

            AnyDictionary anyDictionary = new AnyDictionary();
            anyDictionary.put("foo", new Any("bar"));
            anyDictionary.put("n", new Any(123));
            SerializableObject serializableObject = new SerializableObject();
            ArrayList<SerializableObject> serializableObjects = new ArrayList<>();
            serializableObjects.add(serializableObject);
            SerializableCollection serializableCollection =
                    new SerializableCollection.SerializableCollectionBuilder()
                            .setName("HelloCollection")
                            .setChildren(serializableObjects)
                            .setMetadata(anyDictionary)
                            .build();
            ErrorStatus errorStatus = new ErrorStatus();
            System.out.println(serializableCollection.toJSONString(errorStatus));

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void test2() {

//        for (int i = 0; i < 1000; i++) {
//            Any any = OTIOFactory.getInstance().createAny("x");
//            Thread.sleep(10);
//            if (i % 100 == 0) System.gc();
//        }
//        Thread.sleep(1000);
//        System.gc();
//        System.gc();
//        System.gc();
//        System.out.println("////////////////");
//        OTIOFactory.getInstance().cleanUp();
//        for (int i = 1000; i < 10000; i++) {
//            Any any = OTIOFactory.getInstance().createAny("x");
//            Thread.sleep(10);
//            if (i % 100 == 0) System.gc();
//        }
    }

}
