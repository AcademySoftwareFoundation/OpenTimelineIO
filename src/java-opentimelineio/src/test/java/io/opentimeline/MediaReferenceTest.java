package io.opentimeline;

import io.opentimeline.opentime.RationalTime;
import io.opentimeline.opentime.TimeRange;
import io.opentimeline.opentimelineio.*;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

public class MediaReferenceTest {

    @Test
    public void testConstructor() {
        try {
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
            mr.getNativeManager().close();
            mr = new MissingReference.MissingReferenceBuilder().build();
            assertNull(mr.getAvailableRange());
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testSerialization() {

        try {
            MissingReference mr = new MissingReference.MissingReferenceBuilder().build();
            Any mrAny = new Any(mr);
            ErrorStatus errorStatus = new ErrorStatus();
            Serialization serialization = new Serialization();
            String encoded = serialization.serializeJSONToString(mrAny, errorStatus);
            SerializableObject decoded = SerializableObject.fromJSONString(encoded, errorStatus);
            assertTrue(decoded.isEquivalentTo(mr));
        } catch (Exception e) {
            e.printStackTrace();
        }

    }

    @Test
    public void testFilepath() {
        try {
            ExternalReference mr = new ExternalReference.ExternalReferenceBuilder()
                    .setTargetURL("/var/tmp/foo.mov")
                    .build();
            Any mrAny = new Any(mr);
            ErrorStatus errorStatus = new ErrorStatus();
            Serialization serialization = new Serialization();
            String encoded = serialization.serializeJSONToString(mrAny, errorStatus);
            SerializableObject decoded = SerializableObject.fromJSONString(encoded, errorStatus);
            assertTrue(decoded.isEquivalentTo(mr));
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testEq() {
        try {
            ExternalReference mr1 = new ExternalReference.ExternalReferenceBuilder()
                    .setTargetURL("/var/tmp/foo.mov")
                    .build();
            ExternalReference mr2 = new ExternalReference.ExternalReferenceBuilder()
                    .setTargetURL("/var/tmp/foo.mov")
                    .build();
            assertTrue(mr1.isEquivalentTo(mr2));

            MissingReference bl = new MissingReference.MissingReferenceBuilder().build();
            assertFalse(bl.isEquivalentTo(mr1));
            mr2.getNativeManager().close(); //segfault
            mr2 = new ExternalReference.ExternalReferenceBuilder()
                    .setTargetURL("/var/tmp/foo2.mov")
                    .build();
            mr1 = new ExternalReference.ExternalReferenceBuilder()
                    .setTargetURL("/var/tmp/foo.mov")
                    .build();
            assertFalse(mr1.isEquivalentTo(mr2));
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testIsMissing() {
        try {
            ExternalReference mr = new ExternalReference.ExternalReferenceBuilder()
                    .setTargetURL("/var/tmp/foo.mov")
                    .build();
            assertFalse(mr.isMissingReference());
            MissingReference mr2 = new MissingReference.MissingReferenceBuilder()
                    .build();
            assertTrue(mr2.isMissingReference());
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
