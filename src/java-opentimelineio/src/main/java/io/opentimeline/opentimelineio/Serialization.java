package io.opentimeline.opentimelineio;

public class Serialization {

    public static String serializeJSONToString(Any value, ErrorStatus errorStatus, int indent) {
        return serializeJSONToStringNative(value, errorStatus, indent);
    }

    public static String serializeJSONToString(Any value, ErrorStatus errorStatus) {
        return serializeJSONToStringNative(value, errorStatus, 4);
    }

    private static native String serializeJSONToStringNative(
            Any value, ErrorStatus errorStatus, int indent);

    public static boolean serializeJSONToFile(
            Any value, String fileName, ErrorStatus errorStatus, int indent) {
        return serializeJSONToFileNative(value, fileName, errorStatus, indent);
    }

    public static boolean serializeJSONToFile(
            Any value, String fileName, ErrorStatus errorStatus) {
        return serializeJSONToFileNative(value, fileName, errorStatus, 4);
    }

    private static native boolean serializeJSONToFileNative(
            Any value, String fileName, ErrorStatus errorStatus, int indent);

}
