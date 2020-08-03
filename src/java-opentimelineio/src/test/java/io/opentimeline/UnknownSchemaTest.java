package io.opentimeline;

import io.opentimeline.opentimelineio.Any;
import io.opentimeline.opentimelineio.Clip;
import io.opentimeline.opentimelineio.ErrorStatus;
import io.opentimeline.opentimelineio.SerializableObject;
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
    public void setUp(){
        ErrorStatus errorStatus = new ErrorStatus();
        orig = SerializableObject.fromJSONString(hasUnknownSchema,errorStatus);
    }

    @Test
    public void testSerialize(){
        ErrorStatus errorStatus = new ErrorStatus();
        String serialized = orig.toJSONString(errorStatus);
        SerializableObject testOTIO = SerializableObject.fromJSONString(serialized,errorStatus);
        assertTrue(testOTIO.isEquivalentTo(orig));
    }

    @Test
    public void testIsUnknownSchema(){
        assertFalse(orig.isUnknownSchema());
        Clip origClip = new Clip(orig);
        Any unknownAny = origClip.getMediaReference().getMetadata().get("stuff");
        SerializableObject unknown = unknownAny.safelyCastSerializableObject();
        assertTrue(unknown.isUnknownSchema());
    }

}
