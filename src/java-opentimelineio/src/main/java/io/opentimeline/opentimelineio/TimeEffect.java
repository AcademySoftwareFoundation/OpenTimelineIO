package io.opentimeline.opentimelineio;

import io.opentimeline.OTIONative;

public class TimeEffect extends Effect {

    protected TimeEffect() {
    }

    TimeEffect(OTIONative otioNative) {
        this.nativeManager = otioNative;
    }

    public TimeEffect(String name, String effectName, AnyDictionary metadata) {
        this.initObject(name, effectName, metadata);
    }

    public TimeEffect(TimeEffect.TimeEffectBuilder builder) {
        this.initObject(builder.name, builder.effectName, builder.metadata);
    }

    private void initObject(String name, String effectName, AnyDictionary metadata) {
        this.initialize(name, effectName, metadata);
        this.nativeManager.className = this.getClass().getCanonicalName();
    }

    private native void initialize(String name, String effectName, AnyDictionary metadata);

    public static class TimeEffectBuilder {
        private String name = "";
        private String effectName = "";
        private AnyDictionary metadata = new AnyDictionary();

        public TimeEffectBuilder() {
        }

        public TimeEffect.TimeEffectBuilder setName(String name) {
            this.name = name;
            return this;
        }

        public TimeEffect.TimeEffectBuilder setEffectName(String effectName) {
            this.effectName = effectName;
            return this;
        }

        public TimeEffect.TimeEffectBuilder setMetadata(AnyDictionary metadata) {
            this.metadata = metadata;
            return this;
        }

        public TimeEffect build() {
            return new TimeEffect(this);
        }
    }

}
