package io.opentimeline;

import io.opentimeline.opentime.RationalTime;
import io.opentimeline.opentime.TimeRange;
import io.opentimeline.opentimelineio.*;
import io.opentimeline.util.Pair;
import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.stream.IntStream;

import static org.junit.jupiter.api.Assertions.*;

public class ImageSequenceReferenceTest {

    @Test
    public void testCreate() {
        AnyDictionary metadata = new AnyDictionary();
        AnyDictionary subMetadata = new AnyDictionary();
        subMetadata.put("foo", new Any("bar"));
        metadata.put("custom", new Any(subMetadata));
        ImageSequenceReference ref = new ImageSequenceReference.ImageSequenceReferenceBuilder()
                .setTargetURLBase("file:///show/seq/shot/rndr/")
                .setNamePrefix("show_shot.")
                .setNameSuffix("exr")
                .setFrameZeroPadding(5)
                .setAvailableRange(new TimeRange(
                        new RationalTime(0, 30),
                        new RationalTime(60, 30)))
                .setFrameStep(3)
                .setMissingFramePolicy(ImageSequenceReference.MissingFramePolicy.hold)
                .setRate(30)
                .setMetadata(metadata)
                .build();

        // check values
        assertEquals(ref.getTargetURLBase(), "file:///show/seq/shot/rndr/");
        assertEquals(ref.getNamePrefix(), "show_shot.");
        assertEquals(ref.getNameSuffix(), "exr");
        assertEquals(ref.getFrameZeroPadding(), 5);
        assertEquals(ref.getAvailableRange(), new TimeRange(
                new RationalTime(0, 30),
                new RationalTime(60, 30)));
        assertEquals(ref.getFrameStep(), 3);
        assertEquals(ref.getRate(), 30);
        assertEquals(ref.getMetadata(), metadata);
        assertEquals(ref.getMissingFramePolicy(), ImageSequenceReference.MissingFramePolicy.hold);
        try {
            ref.close();
            metadata.close();
            subMetadata.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testSerializeRoundtrip() {
        AnyDictionary metadata = new AnyDictionary();
        AnyDictionary subMetadata = new AnyDictionary();
        subMetadata.put("foo", new Any("bar"));
        metadata.put("custom", new Any(subMetadata));
        ImageSequenceReference ref = new ImageSequenceReference.ImageSequenceReferenceBuilder()
                .setTargetURLBase("file:///show/seq/shot/rndr/")
                .setNamePrefix("show_shot.")
                .setNameSuffix("exr")
                .setFrameZeroPadding(5)
                .setAvailableRange(new TimeRange(
                        new RationalTime(0, 30),
                        new RationalTime(60, 30)))
                .setFrameStep(3)
                .setMissingFramePolicy(ImageSequenceReference.MissingFramePolicy.hold)
                .setRate(30)
                .setMetadata(metadata)
                .build();

        ErrorStatus errorStatus = new ErrorStatus();
        String encoded = ref.toJSONString(errorStatus);
        ImageSequenceReference decoded = (ImageSequenceReference) SerializableObject.fromJSONString(encoded, errorStatus);
        assertEquals(ref, decoded);
        String encoded2 = decoded.toJSONString(errorStatus);
        assertEquals(encoded, encoded2);

        // check values
        assertEquals(decoded.getTargetURLBase(), "file:///show/seq/shot/rndr/");
        assertEquals(decoded.getNamePrefix(), "show_shot.");
        assertEquals(decoded.getNameSuffix(), "exr");
        assertEquals(decoded.getFrameZeroPadding(), 5);
        assertEquals(decoded.getAvailableRange(), new TimeRange(
                new RationalTime(0, 30),
                new RationalTime(60, 30)));
        assertEquals(decoded.getFrameStep(), 3);
        assertEquals(decoded.getRate(), 30);
        assertEquals(decoded.getMetadata(), metadata);
        assertEquals(decoded.getMissingFramePolicy(), ImageSequenceReference.MissingFramePolicy.hold);
        try {
            ref.close();
            decoded.close();
            metadata.close();
            subMetadata.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testStr() {
        AnyDictionary metadata = new AnyDictionary();
        AnyDictionary subMetadata = new AnyDictionary();
        subMetadata.put("foo", new Any("bar"));
        metadata.put("custom", new Any(subMetadata));
        ImageSequenceReference ref = new ImageSequenceReference.ImageSequenceReferenceBuilder()
                .setTargetURLBase("file:///show/seq/shot/rndr/")
                .setNamePrefix("show_shot.")
                .setNameSuffix("exr")
                .setFrameZeroPadding(5)
                .setAvailableRange(new TimeRange(
                        new RationalTime(0, 30),
                        new RationalTime(60, 30)))
                .setFrameStep(3)
                .setMissingFramePolicy(ImageSequenceReference.MissingFramePolicy.hold)
                .setRate(30)
                .setMetadata(metadata)
                .build();
        assertEquals(ref.toString(),
                "io.opentimeline.opentimelineio.ImageSequenceReference(" +
                        "targetURLBase=file:///show/seq/shot/rndr/, " +
                        "namePrefix=show_shot., " +
                        "nameSuffix=exr, " +
                        "startFrame=1, " +
                        "frameStep=3, " +
                        "rate=30.0, " +
                        "frameZeroPadding=5, " +
                        "missingFramePolicy=hold, " +
                        "availableRange=io.opentimeline.opentime.TimeRange(" +
                        "startTime=io.opentimeline.opentime.RationalTime(value=0.0, rate=30.0), " +
                        "duration=io.opentimeline.opentime.RationalTime(value=60.0, rate=30.0)), " +
                        "metadata=io.opentimeline.opentimelineio.AnyDictionary{" +
                        "custom=io.opentimeline.opentimelineio.Any(" +
                        "value=io.opentimeline.opentimelineio.AnyDictionary{" +
                        "foo=io.opentimeline.opentimelineio.Any(value=bar)})})");
        try {
            ref.close();
            metadata.close();
            subMetadata.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testDeserializeInvalidEnumValue() {
        String encoded = "{\n" +
                "            \"OTIO_SCHEMA\": \"ImageSequenceReference.1\",\n" +
                "            \"metadata\": {\n" +
                "                \"custom\": {\n" +
                "                    \"foo\": \"bar\"\n" +
                "                }\n" +
                "            },\n" +
                "            \"name\": \"\",\n" +
                "            \"available_range\": {\n" +
                "                \"OTIO_SCHEMA\": \"TimeRange.1\",\n" +
                "                \"duration\": {\n" +
                "                    \"OTIO_SCHEMA\": \"RationalTime.1\",\n" +
                "                    \"rate\": 30.0,\n" +
                "                    \"value\": 60.0\n" +
                "                },\n" +
                "                \"start_time\": {\n" +
                "                    \"OTIO_SCHEMA\": \"RationalTime.1\",\n" +
                "                    \"rate\": 30.0,\n" +
                "                    \"value\": 0.0\n" +
                "                }\n" +
                "            },\n" +
                "            \"target_url_base\": \"file:///show/seq/shot/rndr/\",\n" +
                "            \"name_prefix\": \"show_shot.\",\n" +
                "            \"name_suffix\": \".exr\",\n" +
                "            \"start_frame\": 1,\n" +
                "            \"frame_step\": 3,\n" +
                "            \"rate\": 30.0,\n" +
                "            \"frame_zero_padding\": 5,\n" +
                "            \"missing_frame_policy\": \"BOGUS\"\n" +
                "        }";
        ErrorStatus errorStatus = new ErrorStatus();
        SerializableObject decoded = SerializableObject.fromJSONString(encoded, errorStatus);
        assertEquals(errorStatus.getOutcome(), ErrorStatus.Outcome.JSON_PARSE_ERROR);
        assertNull(decoded);
    }

    @Test
    public void testNumberOfImagesInSequence() {
        ImageSequenceReference ref = new ImageSequenceReference.ImageSequenceReferenceBuilder()
                .setTargetURLBase("file:///show/seq/shot/rndr/")
                .setNamePrefix("show_shot.")
                .setNameSuffix("exr")
                .setAvailableRange(new TimeRange(
                        new RationalTime(0, 24),
                        new RationalTime(48, 24)))
                .setRate(24)
                .build();
        assertEquals(ref.getNumberOfImagesInSequence(), 48);
        try {
            ref.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testNumberOfImagesInSequenceWithSkip() {
        ImageSequenceReference ref = new ImageSequenceReference.ImageSequenceReferenceBuilder()
                .setTargetURLBase("file:///show/seq/shot/rndr/")
                .setNamePrefix("show_shot.")
                .setNameSuffix("exr")
                .setAvailableRange(new TimeRange(
                        new RationalTime(0, 24),
                        new RationalTime(48, 24)))
                .setRate(24)
                .setFrameStep(2)
                .build();
        assertEquals(ref.getNumberOfImagesInSequence(), 24);
        ref.setFrameStep(3);
        assertEquals(ref.getNumberOfImagesInSequence(), 16);
        try {
            ref.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testTargetURLForImageNumber() {
        ArrayList<String> allImagesURLs = new ArrayList<>();
        for (int i = 1; i < 49; i++) {
            allImagesURLs.add("file:///show/seq/shot/rndr/show_shot." + String.format("%04d", i) + ".exr");
        }
        ImageSequenceReference ref = new ImageSequenceReference.ImageSequenceReferenceBuilder()
                .setTargetURLBase("file:///show/seq/shot/rndr/")
                .setNamePrefix("show_shot.")
                .setNameSuffix(".exr")
                .setAvailableRange(new TimeRange(
                        new RationalTime(0, 24),
                        new RationalTime(48, 24)))
                .setRate(24)
                .setFrameZeroPadding(4)
                .setFrameStep(1)
                .setStartFrame(1)
                .build();
        ArrayList<String> generatedURLs = new ArrayList<>();
        ErrorStatus errorStatus = new ErrorStatus();
        IntStream.range(0, ref.getNumberOfImagesInSequence()).forEach(n -> {
            generatedURLs.add(ref.getTargetURLForImageNumber(n, errorStatus));
        });
        assertEquals(allImagesURLs, generatedURLs);
        try {
            ref.close();
            errorStatus.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testTargetURLForImageNumberSteps() {
        ArrayList<String> allImagesURLs = new ArrayList<>();
        for (int i = 1; i < 49; i += 2) {
            allImagesURLs.add("file:///show/seq/shot/rndr/show_shot." + String.format("%04d", i) + ".exr");
        }
        ImageSequenceReference ref = new ImageSequenceReference.ImageSequenceReferenceBuilder()
                .setTargetURLBase("file:///show/seq/shot/rndr/")
                .setNamePrefix("show_shot.")
                .setNameSuffix(".exr")
                .setAvailableRange(new TimeRange(
                        new RationalTime(0, 24),
                        new RationalTime(48, 24)))
                .setRate(24)
                .setFrameZeroPadding(4)
                .setFrameStep(2)
                .setStartFrame(1)
                .build();
        ArrayList<String> generatedURLs = new ArrayList<>();
        ErrorStatus errorStatus = new ErrorStatus();
        IntStream.range(0, ref.getNumberOfImagesInSequence()).forEach(n -> {
            generatedURLs.add(ref.getTargetURLForImageNumber(n, errorStatus));
        });
        assertEquals(allImagesURLs, generatedURLs);

        ref.setFrameStep(3);
        ArrayList<String> allImagesURLsThrees = new ArrayList<>();
        for (int i = 1; i < 49; i += 3) {
            allImagesURLsThrees.add("file:///show/seq/shot/rndr/show_shot." + String.format("%04d", i) + ".exr");
        }
        ArrayList<String> generatedURLsThrees = new ArrayList<>();
        IntStream.range(0, ref.getNumberOfImagesInSequence()).forEach(n -> {
            generatedURLsThrees.add(ref.getTargetURLForImageNumber(n, errorStatus));
        });
        assertEquals(allImagesURLsThrees, generatedURLsThrees);

        ref.setFrameStep(2);
        ref.setStartFrame(0);
        ArrayList<String> allImagesURLsZeroFirst = new ArrayList<>();
        for (int i = 0; i < 48; i += 2) {
            allImagesURLsZeroFirst.add("file:///show/seq/shot/rndr/show_shot." + String.format("%04d", i) + ".exr");
        }
        ArrayList<String> generatedURLsZeroFirst = new ArrayList<>();
        IntStream.range(0, ref.getNumberOfImagesInSequence()).forEach(n -> {
            generatedURLsZeroFirst.add(ref.getTargetURLForImageNumber(n, errorStatus));
        });
        assertEquals(allImagesURLsZeroFirst, generatedURLsZeroFirst);

        try {
            ref.close();
            errorStatus.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testTargetURLForImageNumberWithMissingSlash() {
        ImageSequenceReference ref = new ImageSequenceReference.ImageSequenceReferenceBuilder()
                .setTargetURLBase("file:///show/seq/shot/rndr")
                .setNamePrefix("show_shot.")
                .setNameSuffix(".exr")
                .setAvailableRange(new TimeRange(
                        new RationalTime(0, 24),
                        new RationalTime(48, 24)))
                .setRate(24)
                .setFrameZeroPadding(4)
                .setFrameStep(1)
                .setStartFrame(1)
                .build();
        ErrorStatus errorStatus = new ErrorStatus();
        assertEquals(ref.getTargetURLForImageNumber(0, errorStatus),
                "file:///show/seq/shot/rndr/show_shot.0001.exr");
        try {
            ref.close();
            errorStatus.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testAbstractTargetURL() {
        ImageSequenceReference ref = new ImageSequenceReference.ImageSequenceReferenceBuilder()
                .setTargetURLBase("file:///show/seq/shot/rndr/")
                .setNamePrefix("show_shot.")
                .setNameSuffix(".exr")
                .setAvailableRange(new TimeRange(
                        new RationalTime(0, 24),
                        new RationalTime(48, 24)))
                .setRate(24)
                .setFrameZeroPadding(4)
                .setFrameStep(1)
                .setStartFrame(1)
                .build();
        assertEquals(ref.getAbstractTargetURL("@@@@"),
                "file:///show/seq/shot/rndr/show_shot.@@@@.exr");
        try {
            ref.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testAbstractTargetURLWithMissingSlash() {
        ImageSequenceReference ref = new ImageSequenceReference.ImageSequenceReferenceBuilder()
                .setTargetURLBase("file:///show/seq/shot/rndr")
                .setNamePrefix("show_shot.")
                .setNameSuffix(".exr")
                .setAvailableRange(new TimeRange(
                        new RationalTime(0, 24),
                        new RationalTime(48, 24)))
                .setRate(24)
                .setFrameZeroPadding(4)
                .setFrameStep(1)
                .setStartFrame(1)
                .build();
        assertEquals(ref.getAbstractTargetURL("@@@@"),
                "file:///show/seq/shot/rndr/show_shot.@@@@.exr");
        try {
            ref.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testPresentationTimeForImageNumber() {
        ImageSequenceReference ref = new ImageSequenceReference.ImageSequenceReferenceBuilder()
                .setTargetURLBase("file:///show/seq/shot/rndr/")
                .setNamePrefix("show_shot.")
                .setNameSuffix(".exr")
                .setAvailableRange(new TimeRange(
                        new RationalTime(0, 24),
                        new RationalTime(48, 24)))
                .setRate(24)
                .setFrameZeroPadding(4)
                .setFrameStep(2)
                .setStartFrame(1)
                .build();
        ErrorStatus errorStatus = new ErrorStatus();
        ArrayList<RationalTime> referenceValues = new ArrayList<>();
        IntStream.range(0, 24).forEach(n -> {
            referenceValues.add(new RationalTime(n * 2, 24));
        });
        ArrayList<RationalTime> generatedValues = new ArrayList<>();
        IntStream.range(0, ref.getNumberOfImagesInSequence()).forEach(n -> {
            generatedValues.add(ref.presentationTimeForImageNumber(n, errorStatus));
        });
        assertEquals(generatedValues, referenceValues);
        try {
            ref.close();
            errorStatus.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testPresentationTimeForImageNumberWithOffset() {
        ImageSequenceReference ref = new ImageSequenceReference.ImageSequenceReferenceBuilder()
                .setTargetURLBase("file:///show/seq/shot/rndr/")
                .setNamePrefix("show_shot.")
                .setNameSuffix(".exr")
                .setAvailableRange(new TimeRange(
                        new RationalTime(12, 24),
                        new RationalTime(48, 24)))
                .setRate(24)
                .setFrameZeroPadding(4)
                .setFrameStep(2)
                .setStartFrame(1)
                .build();
        RationalTime firstFrameTime = new RationalTime(12, 24);
        ErrorStatus errorStatus = new ErrorStatus();
        ArrayList<RationalTime> referenceValues = new ArrayList<>();
        IntStream.range(0, 24).forEach(n -> {
            referenceValues.add(firstFrameTime.add(new RationalTime(n * 2, 24)));
        });
        ArrayList<RationalTime> generatedValues = new ArrayList<>();
        IntStream.range(0, ref.getNumberOfImagesInSequence()).forEach(n -> {
            generatedValues.add(ref.presentationTimeForImageNumber(n, errorStatus));
        });
        assertEquals(generatedValues, referenceValues);
        try {
            ref.close();
            errorStatus.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testEndFrame() {
        ImageSequenceReference ref = new ImageSequenceReference.ImageSequenceReferenceBuilder()
                .setTargetURLBase("file:///show/seq/shot/rndr/")
                .setNamePrefix("show_shot.")
                .setNameSuffix(".exr")
                .setAvailableRange(new TimeRange(
                        new RationalTime(12, 24),
                        new RationalTime(48, 24)))
                .setRate(24)
                .setFrameZeroPadding(4)
                .setFrameStep(1)
                .setStartFrame(1)
                .build();
        assertEquals(ref.getEndFrame(), 48);
        ref.setFrameStep(2);
        assertEquals(ref.getEndFrame(), 48);
        try {
            ref.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testEndFrameWithOffset() {
        ImageSequenceReference ref = new ImageSequenceReference.ImageSequenceReferenceBuilder()
                .setTargetURLBase("file:///show/seq/shot/rndr/")
                .setNamePrefix("show_shot.")
                .setNameSuffix(".exr")
                .setAvailableRange(new TimeRange(
                        new RationalTime(12, 24),
                        new RationalTime(48, 24)))
                .setRate(24)
                .setFrameZeroPadding(4)
                .setFrameStep(1)
                .setStartFrame(101)
                .build();
        assertEquals(ref.getEndFrame(), 148);
        ref.setFrameStep(2);
        assertEquals(ref.getEndFrame(), 148);
        try {
            ref.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testFrameForTime() {
        ImageSequenceReference ref = new ImageSequenceReference.ImageSequenceReferenceBuilder()
                .setTargetURLBase("file:///show/seq/shot/rndr/")
                .setNamePrefix("show_shot.")
                .setNameSuffix(".exr")
                .setAvailableRange(new TimeRange(
                        new RationalTime(12, 24),
                        new RationalTime(48, 24)))
                .setRate(24)
                .setFrameZeroPadding(4)
                .setFrameStep(1)
                .setStartFrame(1)
                .build();
        ErrorStatus errorStatus = new ErrorStatus();
        // start should be frame 1
        assertEquals(ref.getFrameForTime(ref.getAvailableRange().getStartTime(), errorStatus),
                1);
        // test a sample in the middle
        assertEquals(ref.getFrameForTime(new RationalTime(15, 24), errorStatus),
                4);
        // The end time (inclusive) should map to the last frame number
        assertEquals(ref.getFrameForTime(ref.getAvailableRange().endTimeInclusive(), errorStatus),
                48);
        // make sure frame step and RationalTime rate have no effect
        ref.setFrameStep(2);
        assertEquals(ref.getFrameForTime(new RationalTime(118, 48), errorStatus),
                48);
        try {
            ref.close();
            errorStatus.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testFrameForTimeOutOfRange() {
        ImageSequenceReference ref = new ImageSequenceReference.ImageSequenceReferenceBuilder()
                .setTargetURLBase("file:///show/seq/shot/rndr/")
                .setNamePrefix("show_shot.")
                .setNameSuffix(".exr")
                .setAvailableRange(new TimeRange(
                        new RationalTime(12, 30),
                        new RationalTime(60, 30)))
                .setRate(30)
                .setFrameZeroPadding(4)
                .setFrameStep(1)
                .setStartFrame(1)
                .build();
        ErrorStatus errorStatus = new ErrorStatus();
        ref.getFrameForTime(new RationalTime(73, 30), errorStatus);
        assertEquals(errorStatus.getOutcome(), ErrorStatus.Outcome.INVALID_TIME_RANGE);
        try {
            ref.close();
            errorStatus.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testFrameRangeForTimeRange() {
        ImageSequenceReference ref = new ImageSequenceReference.ImageSequenceReferenceBuilder()
                .setTargetURLBase("file:///show/seq/shot/rndr/")
                .setNamePrefix("show_shot.")
                .setNameSuffix(".exr")
                .setAvailableRange(new TimeRange(
                        new RationalTime(12, 24),
                        new RationalTime(60, 24)))
                .setRate(24)
                .setFrameZeroPadding(4)
                .setFrameStep(1)
                .setStartFrame(1)
                .build();
        TimeRange timeRange = new TimeRange(
                new RationalTime(24, 24),
                new RationalTime(17, 24));
        ErrorStatus errorStatus = new ErrorStatus();
        assertEquals(ref.getFrameRangeForTimeRange(timeRange, errorStatus), new Pair<>(13, 29));
        try {
            ref.close();
            errorStatus.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testFrameRangeForTimeRangeOutOfBounds() {
        ImageSequenceReference ref = new ImageSequenceReference.ImageSequenceReferenceBuilder()
                .setTargetURLBase("file:///show/seq/shot/rndr/")
                .setNamePrefix("show_shot.")
                .setNameSuffix(".exr")
                .setAvailableRange(new TimeRange(
                        new RationalTime(12, 24),
                        new RationalTime(60, 24)))
                .setRate(24)
                .setFrameZeroPadding(4)
                .setFrameStep(1)
                .setStartFrame(1)
                .build();
        TimeRange timeRange = new TimeRange(
                new RationalTime(24, 24),
                new RationalTime(60, 24));
        ErrorStatus errorStatus = new ErrorStatus();
        ref.getFrameRangeForTimeRange(timeRange, errorStatus);
        assertEquals(errorStatus.getOutcome(), ErrorStatus.Outcome.INVALID_TIME_RANGE);
        try {
            ref.close();
            errorStatus.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testNegativeFrameNumbers() {
        ImageSequenceReference ref = new ImageSequenceReference.ImageSequenceReferenceBuilder()
                .setTargetURLBase("file:///show/seq/shot/rndr/")
                .setNamePrefix("show_shot.")
                .setNameSuffix(".exr")
                .setAvailableRange(new TimeRange(
                        new RationalTime(12, 24),
                        new RationalTime(48, 24)))
                .setRate(24)
                .setFrameZeroPadding(4)
                .setFrameStep(2)
                .setStartFrame(-1)
                .build();
        ErrorStatus errorStatus = new ErrorStatus();

        assertEquals(ref.getNumberOfImagesInSequence(), 24);
        assertEquals(ref.presentationTimeForImageNumber(0, errorStatus),
                new RationalTime(12, 24));
        assertEquals(ref.presentationTimeForImageNumber(1, errorStatus),
                new RationalTime(14, 24));
        assertEquals(ref.presentationTimeForImageNumber(2, errorStatus),
                new RationalTime(16, 24));
        assertEquals(ref.presentationTimeForImageNumber(23, errorStatus),
                new RationalTime(58, 24));

        assertEquals(ref.getTargetURLForImageNumber(0, errorStatus),
                "file:///show/seq/shot/rndr/show_shot.-0001.exr");
        assertEquals(ref.getTargetURLForImageNumber(1, errorStatus),
                "file:///show/seq/shot/rndr/show_shot.0001.exr");
        assertEquals(ref.getTargetURLForImageNumber(2, errorStatus),
                "file:///show/seq/shot/rndr/show_shot.0003.exr");
        assertEquals(ref.getTargetURLForImageNumber(17, errorStatus),
                "file:///show/seq/shot/rndr/show_shot.0033.exr");
        assertEquals(ref.getTargetURLForImageNumber(23, errorStatus),
                "file:///show/seq/shot/rndr/show_shot.0045.exr");

        // check values by ones
        ref.setFrameStep(1);
        IntStream.range(1, ref.getNumberOfImagesInSequence()).forEach(n -> {
            assertEquals(ref.getTargetURLForImageNumber(n, errorStatus),
                    "file:///show/seq/shot/rndr/show_shot." + String.format("%04d", n - 1) + ".exr");
        });

        try {
            ref.close();
            errorStatus.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
