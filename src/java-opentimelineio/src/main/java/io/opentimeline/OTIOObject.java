package io.opentimeline;

public class OTIOObject implements AutoCloseable {
    public OTIONative nativeManager;

    public OTIONative getNativeManager() {
        return nativeManager;
    }

    static {
        if (!LibraryLoader.load(OTIOObject.class, "jotio"))
            System.loadLibrary("jotio");
    }

    @Override
    public void close() throws Exception {
        this.getNativeManager().close();
    }

    @Override
    public int hashCode() {
        return Long.hashCode(nativeManager.getOTIOObjectNativeHandle());
    }
}
