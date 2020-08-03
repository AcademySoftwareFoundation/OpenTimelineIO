package io.opentimeline;

import io.opentimeline.opentime.RationalTime;
import io.opentimeline.opentime.TimeRange;
import io.opentimeline.opentime.TimeTransform;
import io.opentimeline.opentimelineio.*;
import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.function.BiConsumer;
import java.util.function.Consumer;

public class DummyTest {

    @Test
    public void test() {
        try {
//            AnyDictionary anyDictionary = new AnyDictionary();
//            anyDictionary.put("foo1", new Any("bar1"));
//            anyDictionary.put("foo2", new Any("bar2"));
//            anyDictionary.forEach((s, any) -> System.out.println(s + " " + any.safelyCastString()));
//            SerializableObjectWithMetadata so =
//                    new SerializableObjectWithMetadata.SerializableObjectWithMetadataBuilder()
//                            .setName("Hello1")
//                            .setMetadata(anyDictionary)
//                            .build();
//            SerializableObjectWithMetadata so2 =
//                    new SerializableObjectWithMetadata.SerializableObjectWithMetadataBuilder()
//                            .setName("Hello2")
//                            .setMetadata(anyDictionary)
//                            .build();
            Any any1 = new Any("soo1");
            Any any2 = new Any("soo2");
            Any any3 = new Any("soo3");
            Any any4 = new Any("soo4");

            AnyVector anyVector = new AnyVector();
            anyVector.add(any1);
            anyVector.add(any2);
            AnyVector anyVector2 = new AnyVector();
            anyVector.add(any3);
            anyVector.add(any4);
            anyVector2.add(any3);
            anyVector2.add(any4);

            anyVector.forEach(any -> System.out.println(any.safelyCastString()));
            anyVector.retainAll(anyVector2); // getting random crashes. Failure in equating two Anys
            System.out.println();
            for (Any any : anyVector) {
                System.out.println(any.safelyCastString());
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
