package io.opentimeline;

public class OTIONative implements AutoCloseable {

    public long nativeHandle;

    public String className;

    public OTIONative(long nativeHandle) {
        this.nativeHandle = nativeHandle;
    }

    @Override
    public native void close() throws Exception;

}
