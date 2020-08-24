package io.opentimeline.opentimelineio;

import io.opentimeline.OTIONative;
import io.opentimeline.OTIOObject;

/**
 * Base object for things that can be [de]serialized to/from .otio files.
 */
public class SerializableObject extends OTIOObject {

    public SerializableObject() {
        this.initObject();
    }

    SerializableObject(OTIONative otioNative) {
        this.nativeManager = otioNative;
    }

    private void initObject() {
        if (this.getClass().getCanonicalName().equals("io.opentimeline.opentimelineio.SerializableObject"))
            this.initialize();
        if (this.nativeManager != null)
            this.nativeManager.className = this.getClass().getCanonicalName();
    }

    private native void initialize();

    public native boolean toJSONFile(String fileName, ErrorStatus errorStatus);

    public native boolean toJSONFile(String fileName, ErrorStatus errorStatus, int indent);

    public native String toJSONString(ErrorStatus errorStatus);

    public native String toJSONString(ErrorStatus errorStatus, int indent);

    public static native SerializableObject fromJSONFile(String fileName, ErrorStatus errorStatus);

    public static native SerializableObject fromJSONString(String input, ErrorStatus errorStatus);

    /**
     * Returns true if the contents of self and other match.
     *
     * @param serializableObject other SerializableObject
     * @return true if the contents of both match, otherwise false
     */
    public native boolean isEquivalentTo(SerializableObject serializableObject);

    /**
     * Create a deepcopy of the SerializableObject
     *
     * @param errorStatus errorStatus to report error while cloning
     * @return a deepcopy of the object
     */
    public native SerializableObject clone(ErrorStatus errorStatus);

    public native AnyDictionary dynamicFields();

    /**
     * In general, SerializableObject will have a known schema
     * but UnknownSchema subclass will redefine this property to be True
     *
     * @return true if schema is unknown, otherwise false
     */
    public native boolean isUnknownSchema();

    public native String schemaName();

    public native int schemaVersion();

    public native int currentRefCount();

    @Override
    public boolean equals(Object obj) {
        if (!(obj instanceof SerializableObject))
            return false;
        return this.isEquivalentTo((SerializableObject) obj);
    }

    @Override
    public String toString() {
        return this.getClass().getCanonicalName() + "()";
    }
}
