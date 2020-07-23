package io.opentimeline.opentimelineio;

public class LinearTimeWarp extends TimeEffect {

    protected LinearTimeWarp() {
    }

    public LinearTimeWarp(long nativeHandle) {
        this.nativeHandle = nativeHandle;
    }

    public LinearTimeWarp(
            String name,
            String effectName,
            double timeScalar,
            AnyDictionary metadata) {
        this.initObject(name, effectName, timeScalar, metadata);
    }

    public LinearTimeWarp(LinearTimeWarp.LinearTimeWarpBuilder builder) {
        this.initObject(builder.name, builder.effectName, builder.timeScalar, builder.metadata);
    }

    private void initObject(
            String name,
            String effectName,
            double timeScalar,
            AnyDictionary metadata) {
        this.className = this.getClass().getCanonicalName();
        this.initialize(name, effectName, timeScalar, metadata);
    }

    private native void initialize(
            String name,
            String effectName,
            double timeScalar,
            AnyDictionary metadata);

    public static class LinearTimeWarpBuilder {
        private String name = "";
        private String effectName = "";
        private double timeScalar = 1;
        private AnyDictionary metadata = new AnyDictionary();

        public LinearTimeWarpBuilder() {
        }

        public LinearTimeWarp.LinearTimeWarpBuilder setName(String name) {
            this.name = name;
            return this;
        }

        public LinearTimeWarp.LinearTimeWarpBuilder setEffectName(String effectName) {
            this.effectName = effectName;
            return this;
        }

        public LinearTimeWarp.LinearTimeWarpBuilder setTimeScalar(double timeScalar) {
            this.timeScalar = timeScalar;
            return this;
        }

        public LinearTimeWarp.LinearTimeWarpBuilder setMetadata(AnyDictionary metadata) {
            this.metadata = metadata;
            return this;
        }

        public LinearTimeWarp build() {
            return new LinearTimeWarp(this);
        }
    }

    public native double getTimeScalar();

    public native void setTimeScalar(double timeScalar);

}
