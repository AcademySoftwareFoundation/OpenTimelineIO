package io.opentimeline.opentimelineio;

public class Deserialization {

    public static native boolean deserializeJSONFromString(
            String input, Any destination, ErrorStatus errorStatus);

    public static native boolean deserializeJSONFromFile(
            String fileName, Any destination, ErrorStatus errorStatus);

}
