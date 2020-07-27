package io.opentimeline;

import io.opentimeline.opentime.RationalTime;
import io.opentimeline.opentime.TimeRange;
import io.opentimeline.opentimelineio.*;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

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
        try {
            Any refAny = new Any(generatorReference);
            ErrorStatus errorStatus = new ErrorStatus();
            String encoded = Serialization.serializeJSONToString(refAny, errorStatus);
            SerializableObject decoded = SerializableObject.fromJSONString(encoded, errorStatus);
            assertTrue(decoded.isEquivalentTo(generatorReference));
        } catch (Exception e) {
            e.printStackTrace();
        }

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
//        Any destination = new Any(new SerializableObject());
//        assertTrue(Deserialization.deserializeJSONFromFile(genRefTest, destination, errorStatus));
        SerializableObject serializableObject = SerializableObject.fromJSONFile(genRefTest, errorStatus);
        Timeline timeline = new Timeline(serializableObject);
        Stack stack = timeline.getTracks();
        List<SerializableObject.Retainer<Composable>> tracks = stack.getChildren();
        Track track = new Track(tracks.get(0).value());
        ArrayList<SerializableObject.Retainer<Composable>> track0Children = new ArrayList<>(track.getChildren());
        Clip clip = new Clip(track0Children.get(0).value());
        assertEquals((new GeneratorReference(clip.getMediaReference())).getGeneratorKind(), "SMPTEBars");
    }

    @AfterEach
    public void cleanUp() {
        try {
            metadata.close();
            parameters.close();
            generatorReference.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

}
