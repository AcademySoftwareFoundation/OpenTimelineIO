package io.opentimeline.opentimelineio;

public class Deserialization {

    public native boolean deserializeJSONFromString(
            String input, Any destination, ErrorStatus errorStatus);

    public native boolean deserializeJSONFromFile(
            String fileName, Any destination, ErrorStatus errorStatus);

}
