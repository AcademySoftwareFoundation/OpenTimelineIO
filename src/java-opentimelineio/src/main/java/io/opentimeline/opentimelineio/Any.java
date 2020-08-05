package io.opentimeline.opentimelineio;

import io.opentimeline.OTIONative;
import io.opentimeline.OTIOObject;
import io.opentimeline.opentime.RationalTime;
import io.opentimeline.opentime.TimeRange;
import io.opentimeline.opentime.TimeTransform;

public class Any extends OTIOObject {

    private String anyTypeClass = "";

    Any(OTIONative otioNative) {
        this.nativeManager = otioNative;
    }

    public <T> Any(T value) {

        if (value instanceof Boolean) {
            this.initBool((Boolean) value);
            anyTypeClass = Boolean.class.getCanonicalName();
        } else if (value instanceof Integer) {
            this.initInt((Integer) value);
            anyTypeClass = Integer.class.getCanonicalName();
        } else if (value instanceof Long) {
            this.initLong((Long) value);
            anyTypeClass = Long.class.getCanonicalName();
        } else if (value instanceof Double) {
            this.initDouble((Double) value);
            anyTypeClass = Double.class.getCanonicalName();
        } else if (value instanceof String) {
            this.initString((String) value);
            anyTypeClass = String.class.getCanonicalName();
        } else if (value instanceof RationalTime) {
            this.initRationalTime((RationalTime) value);
            anyTypeClass = RationalTime.class.getCanonicalName();
        } else if (value instanceof TimeRange) {
            this.initTimeRange((TimeRange) value);
            anyTypeClass = TimeRange.class.getCanonicalName();
        } else if (value instanceof TimeTransform) {
            this.initTimeTransform((TimeTransform) value);
            anyTypeClass = TimeTransform.class.getCanonicalName();
        } else if (value instanceof AnyDictionary) {
            this.initAnyDictionary((AnyDictionary) value);
            anyTypeClass = AnyDictionary.class.getCanonicalName();
        } else if (value instanceof AnyVector) {
            this.initAnyVector((AnyVector) value);
            anyTypeClass = AnyVector.class.getCanonicalName();
        } else if (value instanceof SerializableObject) {
            this.initSerializableObject((SerializableObject) value);
            anyTypeClass = SerializableObject.class.getCanonicalName();
        } else throw new RuntimeException("Any: Type not supported.");
    }

    private void initBool(boolean b) {
        this.initializeBool(b);
        this.nativeManager.className = this.getClass().getCanonicalName();
    }

    private void initInt(int i) {
        this.initializeInt(i);
        this.nativeManager.className = this.getClass().getCanonicalName();
    }

    private void initLong(long a) {
        this.initializeLong(a);
        this.nativeManager.className = this.getClass().getCanonicalName();
    }

    private void initDouble(double d) {
        this.initializeDouble(d);
        this.nativeManager.className = this.getClass().getCanonicalName();
    }

    private void initString(String string) {
        this.initializeString(string);
        this.nativeManager.className = this.getClass().getCanonicalName();
    }

    private void initRationalTime(RationalTime rationalTime) {
        this.initializeRationalTime(rationalTime);
        this.nativeManager.className = this.getClass().getCanonicalName();
    }

    private void initTimeRange(TimeRange timeRange) {
        this.initializeTimeRange(timeRange);
        this.nativeManager.className = this.getClass().getCanonicalName();
    }

    private void initTimeTransform(TimeTransform timeTransform) {
        this.initializeTimeTransform(timeTransform);
        this.nativeManager.className = this.getClass().getCanonicalName();
    }

    private void initAnyVector(AnyVector anyVector) {
        this.initializeAnyVector(anyVector);
        this.nativeManager.className = this.getClass().getCanonicalName();
    }

    private void initAnyDictionary(AnyDictionary anyDictionary) {
        this.initializeAnyDictionary(anyDictionary);
        this.nativeManager.className = this.getClass().getCanonicalName();
    }

    private void initSerializableObject(SerializableObject serializableObject) {
        this.initializeSerializableObject(serializableObject);
        this.nativeManager.className = this.getClass().getCanonicalName();
    }

    private native void initializeBool(boolean a);

    private native void initializeInt(int a);

    private native void initializeLong(long a);

    private native void initializeDouble(double a);

    private native void initializeString(String a);

    private native void initializeRationalTime(RationalTime rationalTime);

    private native void initializeTimeRange(TimeRange timeRange);

    private native void initializeTimeTransform(TimeTransform timeTransform);

    private native void initializeAnyVector(AnyVector anyVector);

    private native void initializeAnyDictionary(AnyDictionary anyDictionary);

    private native void initializeSerializableObject(SerializableObject serializableObject);

    public native boolean safelyCastBoolean();

    public native int safelyCastInt();

    public native long safelyCastLong();

    public native double safelyCastDouble();

    public native String safelyCastString();

    public native RationalTime safelyCastRationalTime();

    public native TimeRange safelyCastTimeRange();

    public native TimeTransform safelyCastTimeTransform();

    public native SerializableObject safelyCastSerializableObject();

    public native AnyDictionary safelyCastAnyDictionary();

    public native AnyVector safelyCastAnyVector();

    public String getAnyTypeClass() {
        return anyTypeClass;
    }

    public boolean equals(Any any) {
        if (!anyTypeClass.equals(any.getAnyTypeClass())) {
            return false;
        }
        switch (anyTypeClass) {
            case "java.lang.Boolean":
                return safelyCastBoolean() == any.safelyCastBoolean();
            case "java.lang.Integer":
                return safelyCastInt() == any.safelyCastInt();
            case "java.lang.Long":
                return safelyCastLong() == any.safelyCastLong();
            case "java.lang.Double":
                return safelyCastDouble() == any.safelyCastDouble();
            case "java.lang.String":
                return safelyCastString().equals(any.safelyCastString());
            case "io.opentimeline.opentime.RationalTime":
                return safelyCastRationalTime().equals(any.safelyCastRationalTime());
            case "io.opentimeline.opentime.TimeRange":
                return safelyCastTimeRange().equals(any.safelyCastTimeRange());
            case "io.opentimeline.opentime.TimeTransform":
                return safelyCastTimeTransform().equals(any.safelyCastTimeTransform());
            case "io.opentimeline.opentimelineio.AnyDictionary":
                return safelyCastAnyDictionary().equals(any.safelyCastAnyDictionary());
            case "io.opentimeline.opentimelineio.AnyVector":
                return safelyCastAnyVector().equals(any.safelyCastAnyVector());
            case "io.opentimeline.opentimelineio.SerializableObject":
                return safelyCastSerializableObject().isEquivalentTo(any.safelyCastSerializableObject());
            default:
                throw new RuntimeException("Any: Type not supported.");
        }
    }

    @Override
    public boolean equals(Object obj) {
        if (!(obj instanceof Any))
            return false;
        return equals((Any) obj);
    }
}
