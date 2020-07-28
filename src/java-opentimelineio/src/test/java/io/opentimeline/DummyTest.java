package io.opentimeline;

import io.opentimeline.opentime.ErrorStatus;
import io.opentimeline.opentimelineio.Any;
import io.opentimeline.opentimelineio.SerializableObject;
import io.opentimeline.opentimelineio.UnknownSchema;
import org.junit.jupiter.api.Test;

public class DummyTest {

    @Test
    public void test() {
//        ErrorStatus errorStatus = new ErrorStatus();
        SerializableObject serializableObject = new SerializableObject();
        System.out.println(serializableObject.schemaName());
        try {
            serializableObject.getNativeManager().close();
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
