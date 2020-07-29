package io.opentimeline.opentimelineio;

import io.opentimeline.OTIONative;
import io.opentimeline.opentime.RationalTime;
import io.opentimeline.opentime.TimeRange;

public class Transition extends Composable {

    public static class Type {
        public static String SMPTE_Dissolve = "SMPTE_Dissolve";
        public static String Custom = "Custom_Transition";
    }

    protected Transition() {
    }

    Transition(OTIONative otioNative) {
        this.nativeManager = otioNative;
    }

    public Transition(
            String name,
            String transitionType,
            RationalTime inOffset,
            RationalTime outOffset,
            AnyDictionary metadata) {
        this.initObject(
                name,
                transitionType,
                inOffset,
                outOffset,
                metadata);
    }

    public Transition(Transition.TransitionBuilder builder) {
        this.initObject(
                builder.name,
                builder.transitionType,
                builder.inOffset,
                builder.outOffset,
                builder.metadata);
    }

    private void initObject(String name,
                            String transitionType,
                            RationalTime inOffset,
                            RationalTime outOffset,
                            AnyDictionary metadata) {
        this.initialize(
                name,
                transitionType,
                inOffset,
                outOffset,
                metadata);
        this.nativeManager.className = this.getClass().getCanonicalName();
    }

    private native void initialize(String name,
                                   String transitionType,
                                   RationalTime inOffset,
                                   RationalTime outOffset,
                                   AnyDictionary metadata);

    public static class TransitionBuilder {
        private String name = "";
        private String transitionType = "";
        private RationalTime inOffset = new RationalTime();
        private RationalTime outOffset = new RationalTime();
        private AnyDictionary metadata = new AnyDictionary();

        public TransitionBuilder() {
        }

        public Transition.TransitionBuilder setName(String name) {
            this.name = name;
            return this;
        }

        public Transition.TransitionBuilder setTransitionType(String transitionType) {
            this.transitionType = transitionType;
            return this;
        }

        public Transition.TransitionBuilder setInOffset(RationalTime inOffset) {
            this.inOffset = inOffset;
            return this;
        }

        public Transition.TransitionBuilder setOutOffset(RationalTime outOffset) {
            this.outOffset = outOffset;
            return this;
        }

        public Transition.TransitionBuilder setMetadata(AnyDictionary metadata) {
            this.metadata = metadata;
            return this;
        }

        public Transition build() {
            return new Transition(this);
        }
    }

    public native boolean isOverlapping();

    public native String getTransitionType();

    public native void setTransitionType(String transitionType);

    public native RationalTime getInOffset();

    public native void setInOffset(RationalTime inOffset);

    public native RationalTime getOutOffset();

    public native void setOutOffset(RationalTime outOffset);

    public native RationalTime getDuration(ErrorStatus errorStatus);

    public native TimeRange getRangeInParent(ErrorStatus errorStatus);

    public native TimeRange getTrimmedRangeInParent(ErrorStatus errorStatus);

}
