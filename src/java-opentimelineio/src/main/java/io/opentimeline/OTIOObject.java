package io.opentimeline;

public class OTIOObject implements AutoCloseable {
    public OTIONative nativeManager;

    public OTIONative getNativeManager() {
        return nativeManager;
    }

    static {
        LibraryLoader.load("jotio");
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
