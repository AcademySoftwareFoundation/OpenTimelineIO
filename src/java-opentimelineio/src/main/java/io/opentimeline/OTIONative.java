package io.opentimeline;

public class OTIONative {
    public long nativeHandle;
    static {
        if (!LibraryLoader.load(OTIONative.class, "jotio"))
            System.loadLibrary("jotio");
    }
}
