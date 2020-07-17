package io.opentimeline.opentimelineio;

import io.opentimeline.OTIONative;

public class ErrorStatus extends OTIONative {

    public enum Outcome {
        OK,
        NOT_IMPLEMENTED,
        UNRESOLVED_OBJECT_REFERENCE,
        DUPLICATE_OBJECT_REFERENCE,
        MALFORMED_SCHEMA,
        JSON_PARSE_ERROR,
        CHILD_ALREADY_PARENTED,
        FILE_OPEN_FAILED,
        FILE_WRITE_FAILED,
        SCHEMA_ALREADY_REGISTERED,
        SCHEMA_NOT_REGISTERED,
        SCHEMA_VERSION_UNSUPPORTED,
        KEY_NOT_FOUND,
        ILLEGAL_INDEX,
        TYPE_MISMATCH,
        INTERNAL_ERROR,
        NOT_AN_ITEM,
        NOT_A_CHILD_OF,
        NOT_A_CHILD,
        NOT_DESCENDED_FROM,
        CANNOT_COMPUTE_AVAILABLE_RANGE,
        INVALID_TIME_RANGE,
        OBJECT_WITHOUT_DURATION,
        CANNOT_TRIM_TRANSITION
    }

    public ErrorStatus() {
        this.initObject();
    }

    public ErrorStatus(long nativeHandle) {
        this.nativeHandle = nativeHandle;
    }

    private void initObject() {
        this.className = this.getClass().getCanonicalName();
        this.initialize();
    }

    private native void initialize();

    public static String outcomeToString(Outcome o) {
        if (o == null) {
            throw new NullPointerException();
        }
        return outcomeToStringNative(o.ordinal());
    }

    private static native String outcomeToStringNative(int o);

    public Outcome getOutcome() {
        return Outcome.values()[getOutcomeNative()];
    }

    private native int getOutcomeNative();

    private native void dispose();

    @Override
    public void close() throws Exception {
        dispose();
    }
}
