package io.opentimeline.opentimelineio;

public class Deserialization {

    /**
     * Deserialize an OTIO JSON String and get the result in an Any object.
     *
     * @param input       JSON String
     * @param destination JSON will be deserialized into this object
     * @param errorStatus errorStatus to report any error while deserialization
     * @return was the JSON deserialized successfully?
     */
    public native boolean deserializeJSONFromString(
            String input, Any destination, ErrorStatus errorStatus);

    /**
     * Deserialize an OTIO JSON file and get the result in an Any object.
     *
     * @param fileName    path to JSON file
     * @param destination JSON will be deserialized into this object
     * @param errorStatus errorStatus to report any error while deserialization
     * @return was the JSON deserialized successfully?
     */
    public native boolean deserializeJSONFromFile(
            String fileName, Any destination, ErrorStatus errorStatus);

}
