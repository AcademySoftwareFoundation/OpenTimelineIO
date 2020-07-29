package io.opentimeline.opentimelineio;

import io.opentimeline.OTIONative;
import io.opentimeline.OTIOObject;
import io.opentimeline.opentime.RationalTime;
import io.opentimeline.opentime.TimeRange;
import io.opentimeline.opentime.TimeTransform;

public class Any extends OTIOObject {

    Any(OTIONative otioNative) {
        this.nativeManager = otioNative;
    }

    public Any(boolean b) {
        this.initBool(b);
    }

    public Any(int i) {
        this.initInt(i);
    }

    public Any(long l) {
        this.initLong(l);
    }

    public Any(double d) {
        this.initDouble(d);
    }

    public Any(String string) {
        this.initString(string);
    }

    public Any(RationalTime rationalTime) {
        this.initRationalTime(rationalTime);
    }

    public Any(TimeRange timeRange) {
        this.initTimeRange(timeRange);
    }

    public Any(TimeTransform timeTransform) {
        this.initTimeTransform(timeTransform);
    }

    public Any(AnyDictionary anyDictionary) {
        this.initAnyDictionary(anyDictionary);
    }

    public Any(AnyVector anyVector) {
        this.initAnyVector(anyVector);
    }

    public Any(SerializableObject serializableObject) {
        this.initSerializableObject(serializableObject);
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
        this.initializeRationalTime(RationalTime.rationalTimeToArray(rationalTime));
        this.nativeManager.className = this.getClass().getCanonicalName();
    }

    private void initTimeRange(TimeRange timeRange) {
        this.initializeTimeRange(TimeRange.timeRangeToArray(timeRange));
        this.nativeManager.className = this.getClass().getCanonicalName();
    }

    private void initTimeTransform(TimeTransform timeTransform) {
        this.initializeTimeTransform(TimeTransform.timeTransformToArray(timeTransform));
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

    private native void initializeRationalTime(double[] rationalTime);

    private native void initializeTimeRange(double[] timeRange);

    private native void initializeTimeTransform(double[] timeTransform);

    private native void initializeAnyVector(AnyVector anyVector);

    private native void initializeAnyDictionary(AnyDictionary anyDictionary);

    private native void initializeSerializableObject(SerializableObject serializableObject);

    public native boolean safelyCastBoolean();

    public native int safelyCastInt();

    public native int safelyCastLong();

    public native double safelyCastDouble();

    public native String safelyCastString();

    public RationalTime safelyCastRationalTime() {
        return RationalTime.rationalTimeFromArray(safelyCastRationalTimeNative());
    }

    private native double[] safelyCastRationalTimeNative();

    public TimeRange safelyCastTimeRange() {
        return TimeRange.timeRangeFromArray(safelyCastTimeRangeNative());
    }

    private native double[] safelyCastTimeRangeNative();

    public TimeTransform safelyCastTimeTransform() {
        return TimeTransform.timeTransformFromArray(safelyCastTimeTransformNative());
    }

    private native double[] safelyCastTimeTransformNative();

    public native SerializableObject safelyCastSerializableObject();

    public native AnyDictionary safelyCastAnyDictionary();

    public native AnyVector safelyCastAnyVector();

}
