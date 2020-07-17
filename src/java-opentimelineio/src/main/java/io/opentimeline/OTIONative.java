package io.opentimeline;

public abstract class OTIONative implements AutoCloseable {
    public long nativeHandle;
    public String className;
    static {
        if (!LibraryLoader.load(OTIONative.class, "jotio"))
            System.loadLibrary("jotio");
    }

    @Override
    public abstract void close() throws Exception;
}
