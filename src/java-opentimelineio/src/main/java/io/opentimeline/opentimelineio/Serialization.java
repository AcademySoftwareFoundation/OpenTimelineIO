package io.opentimeline.opentimelineio;

public class Serialization {

    public String serializeJSONToString(Any value, ErrorStatus errorStatus, int indent) {
        return serializeJSONToStringNative(value, errorStatus, indent);
    }

    public String serializeJSONToString(Any value, ErrorStatus errorStatus) {
        return serializeJSONToStringNative(value, errorStatus, 4);
    }

    private native String serializeJSONToStringNative(
            Any value, ErrorStatus errorStatus, int indent);

    public boolean serializeJSONToFile(
            Any value, String fileName, ErrorStatus errorStatus, int indent) {
        return serializeJSONToFileNative(value, fileName, errorStatus, indent);
    }

    public boolean serializeJSONToFile(
            Any value, String fileName, ErrorStatus errorStatus) {
        return serializeJSONToFileNative(value, fileName, errorStatus, 4);
    }

    private native boolean serializeJSONToFileNative(
            Any value, String fileName, ErrorStatus errorStatus, int indent);

}
