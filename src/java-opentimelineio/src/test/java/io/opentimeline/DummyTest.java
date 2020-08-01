package io.opentimeline;

import io.opentimeline.opentime.RationalTime;
import io.opentimeline.opentime.TimeRange;
import io.opentimeline.opentime.TimeTransform;
import io.opentimeline.opentimelineio.*;
import org.junit.jupiter.api.Test;

import java.util.ArrayList;

public class DummyTest {

    @Test
    public void test() {
        try {
            AnyDictionary anyDictionary = new AnyDictionary();
            anyDictionary.put("foo1", new Any("bar1"));
            anyDictionary.put("foo2", new Any("bar2"));
            SerializableObjectWithMetadata so =
                    new SerializableObjectWithMetadata.SerializableObjectWithMetadataBuilder()
                            .setName("Hello1")
                            .setMetadata(anyDictionary)
                            .build();
            SerializableObjectWithMetadata so2 =
                    new SerializableObjectWithMetadata.SerializableObjectWithMetadataBuilder()
                            .setName("Hello2")
                            .setMetadata(anyDictionary)
                            .build();
            Any any1 = new Any("so");
            Any any2 = new Any("so2");
            Any any3 = new Any("so3");
            Any any4 = new Any("so4");

            AnyVector anyVector = new AnyVector();
            anyVector.add(any1);
            anyVector.add(any2);
            AnyVector anyVector2 = new AnyVector();
            anyVector.add(any3);
            anyVector.add(any4);
            anyVector2.add(any3);
            anyVector2.add(any4);

            for (int i = 0; i < anyVector.size(); i++) {
                System.out.println(anyVector.get(i).safelyCastString());
            }
            anyVector.retainAll(anyVector2);
            System.out.println();
            for (int i = 0; i < anyVector.size(); i++) {
                System.out.println(anyVector.get(i).safelyCastString());
            }
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
