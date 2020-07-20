package io.opentimeline.opentimelineio;

public class FreezeFrame extends LinearTimeWarp {

    protected FreezeFrame() {
    }

    public FreezeFrame(String name, AnyDictionary metadata) {
        this.initObject(name, metadata);
    }

    public FreezeFrame(FreezeFrame.FreezeFrameBuilder builder) {
        this.initObject(builder.name, builder.metadata);
    }

    private void initObject(String name, AnyDictionary metadata) {
        this.className = this.getClass().getCanonicalName();
        this.initialize(name, metadata);
    }

    private native void initialize(String name, AnyDictionary metadata);

    public static class FreezeFrameBuilder {
        private String name = "";
        private AnyDictionary metadata = new AnyDictionary();

        public FreezeFrameBuilder() {
        }

        public FreezeFrame.FreezeFrameBuilder setName(String name) {
            this.name = name;
            return this;
        }

        public FreezeFrame.FreezeFrameBuilder setMetadata(AnyDictionary metadata) {
            this.metadata = metadata;
            return this;
        }

        public FreezeFrame build() {
            return new FreezeFrame(this);
        }
    }

}
