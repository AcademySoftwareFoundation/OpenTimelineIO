package io.opentimeline;

import io.opentimeline.opentime.RationalTime;
import io.opentimeline.opentime.TimeRange;
import io.opentimeline.opentimelineio.*;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

public class TrackAlgoTest {

    Track sampleTrack = null;

    @BeforeEach
    public void setup() {
        String sampleTrackStr = "{\n" +
                "            \"OTIO_SCHEMA\": \"Track.1\",\n" +
                "            \"children\": [\n" +
                "                {\n" +
                "                    \"OTIO_SCHEMA\": \"Clip.1\",\n" +
                "                    \"effects\": [],\n" +
                "                    \"markers\": [],\n" +
                "                    \"media_reference\": null,\n" +
                "                    \"metadata\": {},\n" +
                "                    \"name\": \"A\",\n" +
                "                    \"source_range\": {\n" +
                "                        \"OTIO_SCHEMA\": \"TimeRange.1\",\n" +
                "                        \"duration\": {\n" +
                "                            \"OTIO_SCHEMA\": \"RationalTime.1\",\n" +
                "                            \"rate\": 24,\n" +
                "                            \"value\": 50\n" +
                "                        },\n" +
                "                        \"start_time\": {\n" +
                "                            \"OTIO_SCHEMA\": \"RationalTime.1\",\n" +
                "                            \"rate\": 24,\n" +
                "                            \"value\": 0.0\n" +
                "                        }\n" +
                "                    }\n" +
                "                },\n" +
                "                {\n" +
                "                    \"OTIO_SCHEMA\": \"Clip.1\",\n" +
                "                    \"effects\": [],\n" +
                "                    \"markers\": [],\n" +
                "                    \"media_reference\": null,\n" +
                "                    \"metadata\": {},\n" +
                "                    \"name\": \"B\",\n" +
                "                    \"source_range\": {\n" +
                "                        \"OTIO_SCHEMA\": \"TimeRange.1\",\n" +
                "                        \"duration\": {\n" +
                "                            \"OTIO_SCHEMA\": \"RationalTime.1\",\n" +
                "                            \"rate\": 24,\n" +
                "                            \"value\": 50\n" +
                "                        },\n" +
                "                        \"start_time\": {\n" +
                "                            \"OTIO_SCHEMA\": \"RationalTime.1\",\n" +
                "                            \"rate\": 24,\n" +
                "                            \"value\": 0.0\n" +
                "                        }\n" +
                "                    }\n" +
                "                },\n" +
                "                {\n" +
                "                    \"OTIO_SCHEMA\": \"Clip.1\",\n" +
                "                    \"effects\": [],\n" +
                "                    \"markers\": [],\n" +
                "                    \"media_reference\": null,\n" +
                "                    \"metadata\": {},\n" +
                "                    \"name\": \"C\",\n" +
                "                    \"source_range\": {\n" +
                "                        \"OTIO_SCHEMA\": \"TimeRange.1\",\n" +
                "                        \"duration\": {\n" +
                "                            \"OTIO_SCHEMA\": \"RationalTime.1\",\n" +
                "                            \"rate\": 24,\n" +
                "                            \"value\": 50\n" +
                "                        },\n" +
                "                        \"start_time\": {\n" +
                "                            \"OTIO_SCHEMA\": \"RationalTime.1\",\n" +
                "                            \"rate\": 24,\n" +
                "                            \"value\": 0.0\n" +
                "                        }\n" +
                "                    }\n" +
                "                }\n" +
                "            ],\n" +
                "            \"effects\": [],\n" +
                "            \"kind\": \"Video\",\n" +
                "            \"markers\": [],\n" +
                "            \"metadata\": {},\n" +
                "            \"name\": \"Sequence1\",\n" +
                "            \"source_range\": null\n" +
                "        }";
        ErrorStatus errorStatus = new ErrorStatus();
        sampleTrack = (Track) SerializableObject.fromJSONString(sampleTrackStr, errorStatus);
        try {
            errorStatus.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testTrimToExistingRange() {
        ErrorStatus errorStatus = new ErrorStatus();
        assertEquals(sampleTrack.getTrimmedRange(errorStatus),
                new TimeRange(
                        new RationalTime(0, 24),
                        new RationalTime(150, 24)));

        // trim to the exact range it already has
        Track trimmed = new Algorithms().trackTrimmedToRange(
                sampleTrack,
                new TimeRange(
                        new RationalTime(0, 24),
                        new RationalTime(150, 24)), errorStatus);
        // it shouldn't have changed at all
        assertEquals(sampleTrack, trimmed);
        try {
            errorStatus.close();
            trimmed.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testTrimToLongerRange() {
        ErrorStatus errorStatus = new ErrorStatus();

        // trim to the exact range it already has
        Track trimmed = new Algorithms().trackTrimmedToRange(
                sampleTrack,
                new TimeRange(
                        new RationalTime(60, 24),
                        new RationalTime(90, 24)), errorStatus);
        assertNotEquals(sampleTrack, trimmed);
        assertEquals(trimmed.getChildren().size(), 2);
        assertEquals(trimmed.getTrimmedRange(errorStatus),
                new TimeRange(
                        new RationalTime(0, 24),
                        new RationalTime(90, 24)));

        // did clipB get trimmed?
        List<Composable> trimmedChildren = trimmed.getChildren();
        assertEquals(trimmedChildren.get(0).getName(), "B");
        assertEquals(((Clip) trimmedChildren.get(0)).getTrimmedRange(errorStatus),
                new TimeRange(
                        new RationalTime(10, 24),
                        new RationalTime(40, 24)));

        // clipC should have been left alone
        assertEquals(trimmedChildren.get(1), sampleTrack.getChildren().get(2));
        try {
            trimmed.close();
            errorStatus.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testTrimEnd() {
        ErrorStatus errorStatus = new ErrorStatus();

        // trim off the end (clip C and part of B)
        Track trimmed = new Algorithms().trackTrimmedToRange(
                sampleTrack,
                new TimeRange(
                        new RationalTime(0, 24),
                        new RationalTime(90, 24)), errorStatus);
        assertNotEquals(sampleTrack, trimmed);
        assertEquals(trimmed.getChildren().size(), 2);
        assertEquals(trimmed.getTrimmedRange(errorStatus),
                new TimeRange(
                        new RationalTime(0, 24),
                        new RationalTime(90, 24)));

        // clip A should have been left alone
        List<Composable> trimmedChildren = trimmed.getChildren();
        assertEquals(trimmedChildren.get(0), sampleTrack.getChildren().get(0));

        // did clip B get trimmed?
        assertEquals(trimmedChildren.get(1).getName(), "B");
        assertEquals(((Clip) trimmedChildren.get(1)).getTrimmedRange(errorStatus),
                new TimeRange(
                        new RationalTime(0, 24),
                        new RationalTime(40, 24)));
        try {
            trimmed.close();
            errorStatus.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testTrimWithTransitions() {
        ErrorStatus errorStatus = new ErrorStatus();
        assertEquals(sampleTrack.getDuration(errorStatus),
                new RationalTime(150, 24));
        assertEquals(sampleTrack.getChildren().size(), 3);

        // add a transition
        Transition transition = new Transition.TransitionBuilder()
                .setInOffset(new RationalTime(12, 24))
                .setOutOffset(new RationalTime(20, 24))
                .build();
        assertTrue(sampleTrack.insertChild(1, transition, errorStatus));
        assertEquals(sampleTrack.getChildren().size(), 4);
        assertEquals(sampleTrack.getDuration(errorStatus),
                new RationalTime(150, 24));

        // if you try to sever a Transition in the middle it should fail
        Track trimmed = new Algorithms().trackTrimmedToRange(
                sampleTrack,
                new TimeRange(
                        new RationalTime(5, 24),
                        new RationalTime(50, 24)), errorStatus);
        assertEquals(errorStatus.getOutcome(), ErrorStatus.Outcome.CANNOT_TRIM_TRANSITION);
        assertNull(trimmed);

        trimmed = new Algorithms().trackTrimmedToRange(
                sampleTrack,
                new TimeRange(
                        new RationalTime(45, 24),
                        new RationalTime(50, 24)), errorStatus);
        assertEquals(errorStatus.getOutcome(), ErrorStatus.Outcome.CANNOT_TRIM_TRANSITION);
        assertNull(trimmed);

        trimmed = new Algorithms().trackTrimmedToRange(
                sampleTrack,
                new TimeRange(
                        new RationalTime(25, 24),
                        new RationalTime(50, 24)), errorStatus);
        assertNotEquals(sampleTrack, trimmed);

        String expected = "{\n" +
                "            \"OTIO_SCHEMA\": \"Track.1\",\n" +
                "            \"children\": [\n" +
                "                {\n" +
                "                    \"OTIO_SCHEMA\": \"Clip.1\",\n" +
                "                    \"effects\": [],\n" +
                "                    \"markers\": [],\n" +
                "                    \"media_reference\": null,\n" +
                "                    \"metadata\": {},\n" +
                "                    \"name\": \"A\",\n" +
                "                    \"source_range\": {\n" +
                "                        \"OTIO_SCHEMA\": \"TimeRange.1\",\n" +
                "                        \"duration\": {\n" +
                "                            \"OTIO_SCHEMA\": \"RationalTime.1\",\n" +
                "                            \"rate\": 24,\n" +
                "                            \"value\": 25\n" +
                "                        },\n" +
                "                        \"start_time\": {\n" +
                "                            \"OTIO_SCHEMA\": \"RationalTime.1\",\n" +
                "                            \"rate\": 24,\n" +
                "                            \"value\": 25.0\n" +
                "                        }\n" +
                "                    }\n" +
                "                },\n" +
                "                {\n" +
                "                    \"OTIO_SCHEMA\": \"Transition.1\",\n" +
                "                    \"name\": \"\",\n" +
                "                    \"metadata\": {},\n" +
                "                    \"transition_type\": \"\",\n" +
                "                    \"in_offset\": {\n" +
                "                        \"OTIO_SCHEMA\": \"RationalTime.1\",\n" +
                "                        \"rate\": 24,\n" +
                "                        \"value\": 12\n" +
                "                    },\n" +
                "                    \"out_offset\": {\n" +
                "                        \"OTIO_SCHEMA\": \"RationalTime.1\",\n" +
                "                        \"rate\": 24,\n" +
                "                        \"value\": 20\n" +
                "                    }\n" +
                "                },\n" +
                "                {\n" +
                "                    \"OTIO_SCHEMA\": \"Clip.1\",\n" +
                "                    \"effects\": [],\n" +
                "                    \"markers\": [],\n" +
                "                    \"media_reference\": null,\n" +
                "                    \"metadata\": {},\n" +
                "                    \"name\": \"B\",\n" +
                "                    \"source_range\": {\n" +
                "                        \"OTIO_SCHEMA\": \"TimeRange.1\",\n" +
                "                        \"duration\": {\n" +
                "                            \"OTIO_SCHEMA\": \"RationalTime.1\",\n" +
                "                            \"rate\": 24,\n" +
                "                            \"value\": 25\n" +
                "                        },\n" +
                "                        \"start_time\": {\n" +
                "                            \"OTIO_SCHEMA\": \"RationalTime.1\",\n" +
                "                            \"rate\": 24,\n" +
                "                            \"value\": 0.0\n" +
                "                        }\n" +
                "                    }\n" +
                "                }\n" +
                "            ],\n" +
                "            \"effects\": [],\n" +
                "            \"kind\": \"Video\",\n" +
                "            \"markers\": [],\n" +
                "            \"metadata\": {},\n" +
                "            \"name\": \"Sequence1\",\n" +
                "            \"source_range\": null\n" +
                "        }";
        SerializableObject expectedObj = SerializableObject.fromJSONString(expected, errorStatus);
        assertEquals(expectedObj, trimmed);
        try {
            errorStatus.close();
            trimmed.close();
            expectedObj.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @AfterEach
    public void cleanup() {
        try {
            sampleTrack.close();
            sampleTrack = null;
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

}
