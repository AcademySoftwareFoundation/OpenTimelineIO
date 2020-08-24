package io.opentimeline;

/**
 * A class that holds the native handle and class name of an OTIO object.
 * It implements the AutoCloseable interface which adds the close() method.
 * This method can be called to free the native memory and is called automatically
 * on exit from scope when this object will be declared in a try-with-resources block.
 */
public class OTIONative implements AutoCloseable {

    public long nativeHandle;

    public String className;

    public OTIONative(long nativeHandle) {
        this.nativeHandle = nativeHandle;
    }

    /**
     * This method returns the native handle of the actual native object.
     * It can be used to check if two different Java objects hold reference to the same native object.
     * This is used to generate hash codes for OTIO objects so that they can be added to HashMaps.
     *
     * @return native handle of the actual native object
     */
    public native long getOTIOObjectNativeHandle();

    @Override
    public native void close() throws Exception;

}
