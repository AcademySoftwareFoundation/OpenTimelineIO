package io.opentimeline;

import io.opentimeline.opentimelineio.Any;

import java.lang.ref.ReferenceQueue;

public class OTIOFactory {

    private ReferenceQueue<OTIONative> otioNativeReferenceQueue = new ReferenceQueue<>();

    private static final OTIOFactory instance = new OTIOFactory();

    private OTIOFactory() {
    }

    public static OTIOFactory getInstance() {
        return instance;
    }

    public Any getAnyString(String string) {
        cleanUp();
        Any any = new Any(string);
        OTIOFinalizer finalizer = new OTIOFinalizer(any, otioNativeReferenceQueue);
        return any;
    }

    public void cleanUp() {
        OTIOFinalizer finalizer = (OTIOFinalizer) otioNativeReferenceQueue.poll();
        if (finalizer != null) {
            System.out.println("Here");
            finalizer.cleanUp();
        }
    }
}
