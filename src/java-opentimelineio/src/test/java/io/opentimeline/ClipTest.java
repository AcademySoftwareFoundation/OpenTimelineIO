package io.opentimeline;

import io.opentimeline.opentime.RationalTime;
import io.opentimeline.opentime.TimeRange;
import io.opentimeline.opentimelineio.*;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

public class ClipTest {

    @Test
    public void testConstructor() {

        try {

            String name = "test";
            RationalTime rt = new RationalTime(5, 24);
            TimeRange tr = new TimeRange(rt, rt);
            ExternalReference mr = new ExternalReference.ExternalReferenceBuilder()
                    .setTargetURL("/var/tmp/test.mov")
                    .setAvailableRange(new TimeRange(rt, new RationalTime(10, 24)))
                    .build();
            Clip clip = new Clip.ClipBuilder()
                    .setName(name)
                    .setMediaReference(mr)
                    .setSourceRange(tr)
                    .build();

            assertEquals(clip.getName(), name);
            assertTrue(clip.getSourceRange().equals(tr));
            assertTrue(clip.getMediaReference().isEquivalentTo(mr));

            Any clipAny = new Any(clip);
            ErrorStatus errorStatus = new ErrorStatus();
            String encoded = Serialization.serializeJSONToString(clipAny, errorStatus);
            Any destination = new Any(new SerializableObject());
            assertTrue(Deserialization.deserializeJSONFromString(encoded, destination, errorStatus));
            assertTrue(clip.isEquivalentTo(destination.safelyCastSerializableObject()));
        } catch (Exception e) {
            e.printStackTrace();
        }

    }

    @Test
    public void testRanges() {

        try {

            TimeRange tr = new TimeRange(
                    new RationalTime(86400, 24),
                    new RationalTime(200, 24));

            Clip clip = new Clip.ClipBuilder()
                    .setName("test_clip")
                    .setMediaReference(
                            new ExternalReference(
                                    "var/tmp/foo.mov",
                                    tr, new AnyDictionary()))
                    .build();

            ErrorStatus errorStatus = new ErrorStatus();
            assertTrue(clip.getDuration(errorStatus).equals(clip.getTrimmedRange(errorStatus).getDuration()));
            assertTrue(clip.getDuration(errorStatus).equals(tr.getDuration()));
            assertTrue(clip.getTrimmedRange(errorStatus).equals(tr));
            assertTrue(clip.getAvailableRange(errorStatus).equals(tr));

        } catch (Exception e) {
            e.printStackTrace();
        }

    }

    @Test
    public void testRefDefault() {
        Clip clip = new Clip.ClipBuilder().build();
        MissingReference missingReference = new MissingReference.MissingReferenceBuilder().build();
        assertTrue(clip.getMediaReference().isEquivalentTo(missingReference));
        ExternalReference externalReference = new ExternalReference.ExternalReferenceBuilder().build();
        clip.setMediaReference(externalReference);
        assertTrue(clip.getMediaReference().isEquivalentTo(externalReference));
    }
}
