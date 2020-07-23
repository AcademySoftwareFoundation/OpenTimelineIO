package io.opentimeline;

import io.opentimeline.opentimelineio.*;
import org.junit.jupiter.api.Test;

import java.util.ArrayList;

public class DummyTest {

    @Test
    public void test() {
//        AnyDictionary anyDictionary = new AnyDictionary();
//        SerializableObject serializableObject = new SerializableObject();
//        ArrayList<SerializableObject> arrayList = new ArrayList<>();
//        arrayList.add(serializableObject);
//        SerializableCollection serializableCollection = new SerializableCollection("", arrayList, anyDictionary);
        UnknownSchema unknownSchema = new UnknownSchema("", 1);
        System.out.println(unknownSchema.className);
    }

    @Test
    public void test2() throws InterruptedException {

        for (int i = 0; i < 1000; i++) {
            Any any = OTIOFactory.getInstance().createAnyString("x");
            Thread.sleep(10);
            if (i % 100 == 0) System.gc();
        }
        Thread.sleep(1000);
        System.gc();
        System.gc();
        System.gc();
        System.out.println("////////////////");
        OTIOFactory.getInstance().cleanUp();
        for (int i = 1000; i < 10000; i++) {
            Any any = OTIOFactory.getInstance().createAnyString("x");
            Thread.sleep(10);
            if (i % 100 == 0) System.gc();
        }
    }

}
