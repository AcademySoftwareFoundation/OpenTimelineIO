package io.opentimeline;

import io.opentimeline.opentimelineio.OTIOTest;
import io.opentimeline.opentimelineio.SerializableCollection;
import io.opentimeline.opentimelineio.SerializableObject;
import org.junit.jupiter.api.Test;

import java.util.ArrayList;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class MultithreadingTest {

    @Test
    public void test1() {
        SerializableObject child = new SerializableObject();
        SerializableCollection serializableCollection
                = new SerializableCollection.SerializableCollectionBuilder().build();
        serializableCollection.insertChild(0, child);
        try {
            child.close();
            child = null;
        } catch (Exception e) {
            e.printStackTrace();
        }
        ArrayList<Thread> threads = new ArrayList<>();
        for (int i = 0; i < 5; i++) {
            Thread thread = new Thread(() -> assertEquals(OTIOTest.testRetainers1(serializableCollection), 1024 * 10));
            thread.start();
            threads.add(thread);
        }
        for (Thread thread : threads) {
            try {
                thread.join();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
}
