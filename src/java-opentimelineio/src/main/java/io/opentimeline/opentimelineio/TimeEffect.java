package io.opentimeline.opentimelineio;

public class TimeEffect extends Effect {

    protected TimeEffect() {
    }

    public TimeEffect(String name, String effectName, AnyDictionary metadata) {
        this.initObject(name, effectName, metadata);
    }

    public TimeEffect(TimeEffect.TimeEffectBuilder builder) {
        this.initObject(builder.name, builder.effectName, builder.metadata);
    }

    private void initObject(String name, String effectName, AnyDictionary metadata) {
        this.className = this.getClass().getCanonicalName();
        this.initialize(name, effectName, metadata);
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

        public TimeEffect.TimeEffectBuilder setTimeEffectName(String effectName) {
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
