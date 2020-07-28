package io.opentimeline;

public class OTIOObject {
    public OTIONative nativeManager;

    public OTIONative getNativeManager() {
        return nativeManager;
    }

    static {
        if (!LibraryLoader.load(OTIOObject.class, "jotio"))
            System.loadLibrary("jotio");
    }
}
