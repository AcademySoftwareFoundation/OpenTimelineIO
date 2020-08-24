package io.opentimeline;

import java.lang.ref.PhantomReference;
import java.lang.ref.ReferenceQueue;

/**
 * A finalizer class for internal use of the library.
 * It extends PhantomReference&lt;&gt; and stores
 * the class name and native handle of the object whose reference it holds.
 * <p>
 * The OTIOFactory will call the cleanUp() method of this class to free native memory allocated
 * after the Java object is Garbage Collected.
 */
public class OTIOFinalizer extends PhantomReference<OTIONative> {

    String nativeClassName;
    long nativeHandle;

    public OTIOFinalizer(OTIONative referent, ReferenceQueue<OTIONative> q) {
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
