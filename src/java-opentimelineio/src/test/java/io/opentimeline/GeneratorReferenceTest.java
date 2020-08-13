package io.opentimeline;

import io.opentimeline.opentime.RationalTime;
import io.opentimeline.opentime.TimeRange;
import io.opentimeline.opentimelineio.*;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.io.File;
import java.util.ArrayList;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

public class GeneratorReferenceTest {

    GeneratorReference generatorReference;
    AnyDictionary metadata, parameters;

    @BeforeEach
    public void setUp() {
        metadata = new AnyDictionary();
        parameters = new AnyDictionary();
        parameters.put("test_param", new Any(5.0));
        metadata.put("foo", new Any("bar"));
        generatorReference = new GeneratorReference.GeneratorReferenceBuilder()
                .setName("SMPTEBars")
                .setGeneratorKind("SMPTEBars")
                .setAvailableRange(
                        new TimeRange(
                                new RationalTime(0, 24),
                                new RationalTime(100, 24)))
                .setParameters(parameters)
                .setMetadata(metadata)
                .build();
    }

    @Test
    public void testConstructor() {
        assertEquals(generatorReference.getGeneratorKind(), "SMPTEBars");
        assertEquals(generatorReference.getName(), "SMPTEBars");
        assertEquals(generatorReference.getParameters().get("test_param").safelyCastDouble(), 5.0);
        assertEquals(generatorReference.getParameters().size(), 1);
        assertEquals(generatorReference.getMetadata().get("foo").safelyCastString(), "bar");
        assertEquals(generatorReference.getMetadata().size(), 1);
        assertTrue(generatorReference.getAvailableRange()
                .equals(
                        new TimeRange(
                                new RationalTime(0, 24),
                                new RationalTime(100, 24))));
    }

    @Test
    public void testSerialize() {
        Any refAny = new Any(generatorReference);
        ErrorStatus errorStatus = new ErrorStatus();
        Serialization serialization = new Serialization();
        String encoded = serialization.serializeJSONToString(refAny, errorStatus);
        SerializableObject decoded = SerializableObject.fromJSONString(encoded, errorStatus);
        assertTrue(decoded.isEquivalentTo(generatorReference));
        try {
            refAny.close();
            errorStatus.close();
            decoded.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testStr() {
        assertEquals(generatorReference.toString(),
                "io.opentimeline.opentimelineio.GeneratorReference(" +
                        "name=SMPTEBars, " +
                        "generatorKind=SMPTEBars, " +
                        "parameters=io.opentimeline.opentimelineio.AnyDictionary{" +
                        "test_param=io.opentimeline.opentimelineio.Any(value=5.0)}, " +
                        "metadata=io.opentimeline.opentimelineio.AnyDictionary{" +
                        "foo=io.opentimeline.opentimelineio.Any(value=bar)})");
    }

    @Test
    public void testReadFile() {
        String projectRootDir = System.getProperty("user.dir");
        String sampleDataDir = projectRootDir + File.separator +
                "src" + File.separator + "test" + File.separator + "sample_data";
        String genRefTest = sampleDataDir + File.separator + "generator_reference_test.otio";
        File file = new File(genRefTest);
        assertTrue(file.exists());
        ErrorStatus errorStatus = new ErrorStatus();
//            Any destination = new Any(new SerializableObject()); // this gives JSON_PARSE_ERROR
//            Deserialization deserialization = new Deserialization();
//            assertTrue(deserialization.deserializeJSONFromFile(genRefTest, destination, errorStatus));
//            SerializableObject serializableObject = destination.safelyCastSerializableObject();
        Timeline timeline = (Timeline) SerializableObject.fromJSONFile(genRefTest, errorStatus);
        Stack stack = timeline.getTracks();
        List<Composable> tracks = stack.getChildren();
        Track track = (Track) tracks.get(0);
        ArrayList<Composable> track0Children = new ArrayList<>(track.getChildren());
        Clip clip = (Clip) track0Children.get(0);
        assertEquals(((GeneratorReference) clip.getMediaReference()).getGeneratorKind(), "SMPTEBars");
        try {
            errorStatus.close();
            timeline.close();
            stack.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @AfterEach
    public void cleanUp() {
        try {
            metadata.getNativeManager().close();
            parameters.getNativeManager().close();
            generatorReference.getNativeManager().close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

}
