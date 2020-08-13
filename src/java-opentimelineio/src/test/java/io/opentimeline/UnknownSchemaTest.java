package io.opentimeline;

import io.opentimeline.opentimelineio.*;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

public class UnknownSchemaTest {

    String hasUnknownSchema =
            "{\n" +
                    "    \"OTIO_SCHEMA\": \"Clip.1\",\n" +
                    "    \"effects\": [],\n" +
                    "    \"markers\": [],\n" +
                    "    \"media_reference\": {\n" +
                    "        \"OTIO_SCHEMA\": \"ExternalReference.1\",\n" +
                    "        \"available_range\": {\n" +
                    "            \"OTIO_SCHEMA\": \"TimeRange.1\",\n" +
                    "            \"duration\": {\n" +
                    "                \"OTIO_SCHEMA\": \"RationalTime.1\",\n" +
                    "                \"rate\": 24,\n" +
                    "                \"value\": 140\n" +
                    "            },\n" +
                    "            \"start_time\": {\n" +
                    "                \"OTIO_SCHEMA\": \"RationalTime.1\",\n" +
                    "                \"rate\": 24,\n" +
                    "                \"value\": 91\n" +
                    "            }\n" +
                    "        },\n" +
                    "        \"metadata\": {\n" +
                    "            \"stuff\": {\n" +
                    "                \"OTIO_SCHEMA\": \"MyOwnDangSchema.3\",\n" +
                    "                \"some_data\": 895,\n" +
                    "                \"howlongami\": {\n" +
                    "                     \"OTIO_SCHEMA\": \"RationalTime.1\",\n" +
                    "                      \"rate\": 30,\n" +
                    "                      \"value\": 100\n" +
                    "                   }\n" +
                    "            }\n" +
                    "        },\n" +
                    "        \"name\": null,\n" +
                    "        \"target_url\": \"/usr/tmp/some_media.mov\"\n" +
                    "    },\n" +
                    "    \"metadata\": {},\n" +
                    "    \"name\": null,\n" +
                    "    \"source_range\": null\n" +
                    "}";

    SerializableObject orig;

    @BeforeEach
    public void setUp() {
        ErrorStatus errorStatus = new ErrorStatus();
        orig = SerializableObject.fromJSONString(hasUnknownSchema, errorStatus);
    }

    @Test
    public void testStr() {
        UnknownSchema unknownSchema = new UnknownSchema.UnknownSchemaBuilder().build();
        assertEquals(unknownSchema.toString(),
                "io.opentimeline.opentimelineio.UnknownSchema(" +
                        "originalSchemaName=UnknownSchema, originalSchemaVersion=1)");
        try {
            unknownSchema.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testSerialize() {
        ErrorStatus errorStatus = new ErrorStatus();
        String serialized = orig.toJSONString(errorStatus);
        SerializableObject testOTIO = SerializableObject.fromJSONString(serialized, errorStatus);
        assertTrue(testOTIO.isEquivalentTo(orig));
        try {
            errorStatus.close();
            testOTIO.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testIsUnknownSchema() {
        assertFalse(orig.isUnknownSchema());
        Clip origClip = (Clip) orig;
        Any unknownAny = origClip.getMediaReference().getMetadata().get("stuff");
        SerializableObject unknown = unknownAny.safelyCastSerializableObject();
        assertTrue(unknown.isUnknownSchema());
        try {
            unknownAny.close();
            unknown.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @AfterEach
    public void cleanup() {
        try {
            orig.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

}
