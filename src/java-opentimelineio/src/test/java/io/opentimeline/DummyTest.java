package io.opentimeline;

import io.opentimeline.opentimelineio.Any;
import io.opentimeline.opentimelineio.ErrorStatus;
import org.junit.jupiter.api.Test;

public class DummyTest {

    @Test
    public void test() {
        ErrorStatus e = new ErrorStatus();
        System.out.println(e.className);
    }

    @Test
    public void test2() {
        Any any = OTIOFactory.getInstance().getAnyString("x".repeat(5000000));
        any = null;
        try {
            Thread.sleep(10000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        System.gc();
        try {
            Thread.sleep(10000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        OTIOFactory.getInstance().cleanUp();
        System.out.println("Hola");
    }

}
