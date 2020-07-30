package io.opentimeline;

import io.opentimeline.opentime.RationalTime;
import io.opentimeline.opentime.TimeRange;
import io.opentimeline.opentimelineio.*;
import org.junit.jupiter.api.Test;

import java.util.ArrayList;

public class DummyTest {

    @Test
    public void test() {
        try {
//            UnknownSchema unknownSchema = new UnknownSchema.UnknownSchemaBuilder().build();
            UnknownSchema unknownSchema = new UnknownSchema("Hello", 2);
            ErrorStatus errorStatus = new ErrorStatus();
//            System.out.println(unknownSchema.toJSONString(errorStatus));
//            System.out.println(unknownSchema.getOriginalSchemaName());
//            System.out.println(unknownSchema.getOriginalSchemaVersion());
//            System.out.println(unknownSchema.isUnknownSchema());
//            System.out.println(unknownSchema.currentRefCount());
//            System.out.println(unknownSchema.getNativeManager().className);
            errorStatus.getNativeManager().close();
            unknownSchema.getNativeManager().close();
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
