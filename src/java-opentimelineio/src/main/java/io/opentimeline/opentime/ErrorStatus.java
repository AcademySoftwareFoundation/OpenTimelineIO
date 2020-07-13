package io.opentimeline.opentime;

import io.opentimeline.OTIONative;

public class ErrorStatus extends OTIONative {

    public enum Outcome {
        OK,
        INVALID_TIMECODE_RATE,
        NON_DROPFRAME_RATE,
        INVALID_TIMECODE_STRING,
        INVALID_TIME_STRING,
        TIMECODE_RATE_MISMATCH,
        NEGATIVE_VALUE,
        INVALID_RATE_FOR_DROP_FRAME_TIMECODE,
    }

    public ErrorStatus() {
        this.initialize(Outcome.OK.ordinal(), outcomeToString(Outcome.OK));
    }

    public ErrorStatus(Outcome outcome) {
        if (outcome == null) {
            throw new NullPointerException();
        }
        this.initialize(outcome.ordinal(), outcomeToString(outcome));
    }

    public ErrorStatus(Outcome outcome, String details) {
        if (outcome == null || details == null) {
            throw new NullPointerException();
        }
        this.initialize(outcome.ordinal(), details);
    }

    public ErrorStatus(long nativeHandle) {
        this.nativeHandle = nativeHandle;
    }

    private native void initialize(int o, String outcomeDetails);

    public static String outcomeToString(Outcome o) {
        if (o == null) {
            throw new NullPointerException();
        }
        return outcomeToStringNative(o.ordinal());
    }

    public Outcome getOutcome() {
        return Outcome.values()[getOutcomeNative()];
    }

    private static native String outcomeToStringNative(int o);

    private native int getOutcomeNative();

    private native void dispose();

    @Override
    protected void finalize() throws Throwable {
        dispose();
    }
}
