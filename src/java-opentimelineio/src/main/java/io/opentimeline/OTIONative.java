package io.opentimeline;

public class OTIONative {
    static {
        if (!LibraryLoader.load(OTIONative.class, "jotio"))
            System.loadLibrary("jotio");
    }
}
