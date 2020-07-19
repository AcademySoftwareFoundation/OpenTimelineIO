package io.opentimeline;

import java.lang.ref.PhantomReference;
import java.lang.ref.ReferenceQueue;

public class OTIOFinalizer extends PhantomReference<OTIONative> {

    String nativeClassName;
    long nativeHandle;

    public OTIOFinalizer(OTIONative referent, ReferenceQueue<? super OTIONative> q) {
        super(referent, q);
        this.nativeHandle = referent.nativeHandle;
        this.nativeClassName = referent.className;
    }

    private native void disposeNativeObject(long nativeHandle, String nativeClassName);

    public void cleanUp() {
        try {
            System.out.println("native cleanup for " + nativeClassName + " " + nativeHandle);
            disposeNativeObject(nativeHandle, nativeClassName);
        } catch (Exception e) {
            System.out.println("Couldn't dispose native object.");
        }
        clear();
    }
}
