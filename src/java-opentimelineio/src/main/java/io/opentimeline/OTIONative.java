package io.opentimeline;

public class OTIONative {
    static {
        if (!LibraryLoader.load(Library.class, "jotio"))
            System.loadLibrary("jotio");
    }
}
