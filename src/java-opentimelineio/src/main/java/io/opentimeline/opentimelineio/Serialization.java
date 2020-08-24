package io.opentimeline.opentimelineio;

public class Serialization {

    /**
     * Serialize any OTIO object contained in an Any to a String.
     *
     * @param value       Any to be serialized
     * @param errorStatus errorStatus to report error during serialization
     * @param indent      number of spaces to use for indentation in JSON
     * @return serialized OTIO object
     */
    public String serializeJSONToString(Any value, ErrorStatus errorStatus, int indent) {
        return serializeJSONToStringNative(value, errorStatus, indent);
    }

    /**
     * Serialize any OTIO object contained in an Any to a String with a default indent of 4.
     *
     * @param value       Any to be serialized
     * @param errorStatus errorStatus to report error during serialization
     * @return serialized OTIO object
     */
    public String serializeJSONToString(Any value, ErrorStatus errorStatus) {
        return serializeJSONToStringNative(value, errorStatus, 4);
    }

    private native String serializeJSONToStringNative(
            Any value, ErrorStatus errorStatus, int indent);

    /**
     * Serialize any OTIO object contained in an Any to a file.
     *
     * @param value       Any to be serialized
     * @param fileName    path to file
     * @param errorStatus errorStatus to report error during serialization
     * @param indent      number of spaces to use for indentation in JSON
     * @return was the object serialized and was the file created successfully?
     */
    public boolean serializeJSONToFile(
            Any value, String fileName, ErrorStatus errorStatus, int indent) {
        return serializeJSONToFileNative(value, fileName, errorStatus, indent);
    }

    /**
     * Serialize any OTIO object contained in an Any to a file with a default indent of 4.
     *
     * @param value       Any to be serialized
     * @param fileName    path to file
     * @param errorStatus errorStatus to report error during serialization
     * @return was the object serialized and was the file created successfully?
     */
    public boolean serializeJSONToFile(
            Any value, String fileName, ErrorStatus errorStatus) {
        return serializeJSONToFileNative(value, fileName, errorStatus, 4);
    }

    private native boolean serializeJSONToFileNative(
            Any value, String fileName, ErrorStatus errorStatus, int indent);

}
