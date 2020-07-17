package io.opentimeline.opentimelineio;

import io.opentimeline.OTIONative;
import io.opentimeline.opentime.RationalTime;
import io.opentimeline.opentime.TimeRange;
import io.opentimeline.opentime.TimeTransform;

public class Any extends OTIONative {

    public Any(long nativeHandle) {
        this.nativeHandle = nativeHandle;
    }

    public Any(boolean a) {
        this.initialize(a);
    }

    public Any(int a) {
        this.initialize(a);
    }

    public Any(double a) {
        this.initialize(a);
    }

    public Any(String a) {
        this.initialize(a);
    }

//    public Any(RationalTime a) {
//        this.initialize(a);
//    }
//
//    public Any(TimeRange a) {
//        this.initialize(a);
//    }
//
//    public Any(TimeTransform a) {
//        this.initialize(a);
//    }

    private void initObject(boolean a) {
        this.className = this.getClass().getCanonicalName();
        this.initialize(a);
    }

    private void initObject(int a) {
        this.className = this.getClass().getCanonicalName();
        this.initialize(a);
    }

//    private void initObject(long a) {
//        this.className = this.getClass().getCanonicalName();
//        this.initialize(a);
//    }

    private void initObject(double a) {
        this.className = this.getClass().getCanonicalName();
        this.initialize(a);
    }

    private void initObject(String a) {
        this.className = this.getClass().getCanonicalName();
        this.initialize(a);
    }

//    private void initObject(RationalTime a) {
//        this.className = this.getClass().getCanonicalName();
//        this.initialize(a);
//    }
//
//    private void initObject(TimeRange a) {
//        this.className = this.getClass().getCanonicalName();
//        this.initialize(a);
//    }
//
//    private void initObject(TimeTransform a) {
//        this.className = this.getClass().getCanonicalName();
//        this.initialize(a);
//    }

//    private native void initObject(AnyVector a){
//        this.className = this.getClass().getCanonicalName();
//        this.initialize(a);
//    }
//    private native void initObject(AnyDictionary a){
//        this.className = this.getClass().getCanonicalName();
//        this.initialize(a);
//    }
//    private native void initObject(SerializableObject a){
//        this.className = this.getClass().getCanonicalName();
//        this.initialize(a);
//    }

    private native void initialize(boolean a);

    private native void initialize(int a);

//    private native void initialize(long a);

    private native void initialize(double a);

    private native void initialize(String a);

//    private native void initialize(RationalTime a);
//
//    private native void initialize(TimeRange a);
//
//    private native void initialize(TimeTransform a);

    //    private native void initialize(AnyVector a);
    //    private native void initialize(AnyDictionary a);
    //    private native void initialize(SerializableObject a);

    public native boolean safelyCastBoolean();

    public native int safelyCastInt();

    public native double safelyCastDouble();

    public native String safelyCastString();

//    public native RationalTime safelyCastRationalTime();
//
//    public native TimeRange safelyCastTimeRange();
//
//    public native TimeTransform safelyCastTimeTransform();

    //    public native SerializableObject safelyCastSerializableObject();
    //    public native AnyDictionary safelyCastAnyDictionary();
    //    public native AnyVector safelyCastAnyVector();

    private native void dispose();

    @Override
    public void close() throws Exception {
        dispose();
    }
}
