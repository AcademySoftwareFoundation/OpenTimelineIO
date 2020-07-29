package io.opentimeline.opentimelineio;

import io.opentimeline.OTIONative;

public class Effect extends SerializableObjectWithMetadata {

    protected Effect() {
    }

    Effect(OTIONative otioNative) {
        this.nativeManager = otioNative;
    }

    public Effect(SerializableObject serializableObject) {
        this.nativeManager = serializableObject.getNativeManager();
    }

    public Effect(String name, String effectName, AnyDictionary metadata) {
        this.initObject(name, effectName, metadata);
    }

    public Effect(Effect.EffectBuilder builder) {
        this.initObject(builder.name, builder.effectName, builder.metadata);
    }

    private void initObject(String name, String effectName, AnyDictionary metadata) {
        this.initialize(name, effectName, metadata);
        this.nativeManager.className = this.getClass().getCanonicalName();
    }

    private native void initialize(String name, String effectName, AnyDictionary metadata);

    public static class EffectBuilder {
        private String name = "";
        private String effectName = "";
        private AnyDictionary metadata = new AnyDictionary();

        public EffectBuilder() {
        }

        public Effect.EffectBuilder setName(String name) {
            this.name = name;
            return this;
        }

        public Effect.EffectBuilder setEffectName(String effectName) {
            this.effectName = effectName;
            return this;
        }

        public Effect.EffectBuilder setMetadata(AnyDictionary metadata) {
            this.metadata = metadata;
            return this;
        }

        public Effect build() {
            return new Effect(this);
        }
    }

    public native String getEffectName();

    public native void setEffectName(String effectName);

}
