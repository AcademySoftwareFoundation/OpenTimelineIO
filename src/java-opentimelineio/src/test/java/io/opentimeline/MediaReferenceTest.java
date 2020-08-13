package io.opentimeline;

import io.opentimeline.opentime.RationalTime;
import io.opentimeline.opentime.TimeRange;
import io.opentimeline.opentimelineio.*;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

public class MediaReferenceTest {

    @Test
    public void testConstructor() {
        TimeRange tr = new TimeRange(
                new RationalTime(5, 24),
                new RationalTime(10, 24));
        AnyDictionary metadata = new AnyDictionary();
        metadata.put("show", new Any("OTIOTheMovie"));
        MissingReference mr = new MissingReference.MissingReferenceBuilder()
                .setAvailableRange(tr)
                .setMetadata(metadata)
                .build();

        assertTrue(mr.getAvailableRange().equals(tr));
        try {
            mr.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
        mr = new MissingReference.MissingReferenceBuilder().build();
        assertNull(mr.getAvailableRange());
        try {
            metadata.close();
            mr.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testSerialization() {
        MissingReference mr = new MissingReference.MissingReferenceBuilder().build();
        Any mrAny = new Any(mr);
        ErrorStatus errorStatus = new ErrorStatus();
        Serialization serialization = new Serialization();
        String encoded = serialization.serializeJSONToString(mrAny, errorStatus);
        SerializableObject decoded = SerializableObject.fromJSONString(encoded, errorStatus);
        assertTrue(decoded.isEquivalentTo(mr));
        try {
            mr.close();
            mrAny.close();
            errorStatus.close();
            decoded.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testStr() {
        MediaReference mr = new MediaReference.MediaReferenceBuilder().build();
        assertEquals(mr.toString(),
                "io.opentimeline.opentimelineio.MediaReference(" +
                        "name=, " +
                        "availableRange=null, " +
                        "metadata=io.opentimeline.opentimelineio.AnyDictionary{})");
        try {
            mr.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testFilepath() {
        ExternalReference mr = new ExternalReference.ExternalReferenceBuilder()
                .setTargetURL("/var/tmp/foo.mov")
                .build();
        Any mrAny = new Any(mr);
        ErrorStatus errorStatus = new ErrorStatus();
        Serialization serialization = new Serialization();
        String encoded = serialization.serializeJSONToString(mrAny, errorStatus);
        SerializableObject decoded = SerializableObject.fromJSONString(encoded, errorStatus);
        assertTrue(decoded.isEquivalentTo(mr));
        try {
            mr.close();
            mrAny.close();
            errorStatus.close();
            decoded.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testEq() {
        ExternalReference mr1 = new ExternalReference.ExternalReferenceBuilder()
                .setTargetURL("/var/tmp/foo.mov")
                .build();
        ExternalReference mr2 = new ExternalReference.ExternalReferenceBuilder()
                .setTargetURL("/var/tmp/foo.mov")
                .build();
        assertTrue(mr1.isEquivalentTo(mr2));

        MissingReference bl = new MissingReference.MissingReferenceBuilder().build();
        assertFalse(bl.isEquivalentTo(mr1));
        try {
            mr1.close();
            mr2.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
        mr2 = new ExternalReference.ExternalReferenceBuilder()
                .setTargetURL("/var/tmp/foo2.mov")
                .build();
        mr1 = new ExternalReference.ExternalReferenceBuilder()
                .setTargetURL("/var/tmp/foo.mov")
                .build();
        assertFalse(mr1.isEquivalentTo(mr2));
        try {
            mr1.close();
            mr2.close();
            bl.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testIsMissing() {
        ExternalReference mr = new ExternalReference.ExternalReferenceBuilder()
                .setTargetURL("/var/tmp/foo.mov")
                .build();
        assertFalse(mr.isMissingReference());
        MissingReference mr2 = new MissingReference.MissingReferenceBuilder()
                .build();
        assertTrue(mr2.isMissingReference());
        try {
            mr.close();
            mr2.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
