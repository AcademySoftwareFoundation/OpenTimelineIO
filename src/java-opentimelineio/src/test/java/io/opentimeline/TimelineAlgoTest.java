package io.opentimeline;

import io.opentimeline.opentime.RationalTime;
import io.opentimeline.opentime.TimeRange;
import io.opentimeline.opentimelineio.*;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

public class TimelineAlgoTest {

    Timeline timeline = null;

    @BeforeEach
    public void setup() {
        String tlString = "{\n" +
                "                \"OTIO_SCHEMA\": \"Timeline.1\",\n" +
                "                \"metadata\": {},\n" +
                "                \"name\": null,\n" +
                "                \"tracks\": {\n" +
                "                    \"OTIO_SCHEMA\": \"Stack.1\",\n" +
                "                    \"children\": [\n" +
                "                        {\n" +
                "                            \"OTIO_SCHEMA\": \"Track.1\",\n" +
                "                            \"children\": [\n" +
                "                                {\n" +
                "                                    \"OTIO_SCHEMA\": \"Clip.1\",\n" +
                "                                    \"effects\": [],\n" +
                "                                    \"markers\": [],\n" +
                "                                    \"media_reference\": null,\n" +
                "                                    \"metadata\": {},\n" +
                "                                    \"name\": \"A\",\n" +
                "                                    \"source_range\": {\n" +
                "                                        \"OTIO_SCHEMA\": \"TimeRange.1\",\n" +
                "                                        \"duration\": {\n" +
                "                                            \"OTIO_SCHEMA\": \"RationalTime.1\",\n" +
                "                                            \"rate\": 24,\n" +
                "                                            \"value\": 50\n" +
                "                                        },\n" +
                "                                        \"start_time\": {\n" +
                "                                            \"OTIO_SCHEMA\": \"RationalTime.1\",\n" +
                "                                            \"rate\": 24,\n" +
                "                                            \"value\": 0.0\n" +
                "                                        }\n" +
                "                                    }\n" +
                "                                },\n" +
                "                                {\n" +
                "                                    \"OTIO_SCHEMA\": \"Clip.1\",\n" +
                "                                    \"effects\": [],\n" +
                "                                    \"markers\": [],\n" +
                "                                    \"media_reference\": null,\n" +
                "                                    \"metadata\": {},\n" +
                "                                    \"name\": \"B\",\n" +
                "                                    \"source_range\": {\n" +
                "                                        \"OTIO_SCHEMA\": \"TimeRange.1\",\n" +
                "                                        \"duration\": {\n" +
                "                                            \"OTIO_SCHEMA\": \"RationalTime.1\",\n" +
                "                                            \"rate\": 24,\n" +
                "                                            \"value\": 50\n" +
                "                                        },\n" +
                "                                        \"start_time\": {\n" +
                "                                            \"OTIO_SCHEMA\": \"RationalTime.1\",\n" +
                "                                            \"rate\": 24,\n" +
                "                                            \"value\": 0.0\n" +
                "                                        }\n" +
                "                                    }\n" +
                "                                },\n" +
                "                                {\n" +
                "                                    \"OTIO_SCHEMA\": \"Clip.1\",\n" +
                "                                    \"effects\": [],\n" +
                "                                    \"markers\": [],\n" +
                "                                    \"media_reference\": null,\n" +
                "                                    \"metadata\": {},\n" +
                "                                    \"name\": \"C\",\n" +
                "                                    \"source_range\": {\n" +
                "                                        \"OTIO_SCHEMA\": \"TimeRange.1\",\n" +
                "                                        \"duration\": {\n" +
                "                                            \"OTIO_SCHEMA\": \"RationalTime.1\",\n" +
                "                                            \"rate\": 24,\n" +
                "                                            \"value\": 50\n" +
                "                                        },\n" +
                "                                        \"start_time\": {\n" +
                "                                            \"OTIO_SCHEMA\": \"RationalTime.1\",\n" +
                "                                            \"rate\": 24,\n" +
                "                                            \"value\": 0.0\n" +
                "                                        }\n" +
                "                                    }\n" +
                "                                }\n" +
                "                            ],\n" +
                "                            \"effects\": [],\n" +
                "                            \"kind\": \"Video\",\n" +
                "                            \"markers\": [],\n" +
                "                            \"metadata\": {},\n" +
                "                            \"name\": \"Sequence1\",\n" +
                "                            \"source_range\": null\n" +
                "                        }\n" +
                "                    ],\n" +
                "                    \"effects\": [],\n" +
                "                    \"markers\": [],\n" +
                "                    \"metadata\": {},\n" +
                "                    \"name\": \"tracks\",\n" +
                "                    \"source_range\": null\n" +
                "                }\n" +
                "            }";
        ErrorStatus errorStatus = new ErrorStatus();
        timeline = (Timeline) SerializableObject.fromJSONString(tlString, errorStatus);
        try {
            errorStatus.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testTrimToExistingRange() {
        ErrorStatus errorStatus = new ErrorStatus();
        Stack stack = timeline.getTracks();
        List<Composable> tracks = stack.getChildren();
        Track originalTrack = (Track) tracks.get(0);
        assertEquals(originalTrack.getTrimmedRange(errorStatus),
                new TimeRange(
                        new RationalTime(0, 24),
                        new RationalTime(150, 24)));

        // trim to the exact range it already has
        Timeline trimmed = new Algorithms().timelineTrimmedToRange(timeline,
                new TimeRange(
                        new RationalTime(0, 24),
                        new RationalTime(150, 24)),
                errorStatus);

        // it shouldn't have changes at all
        assertEquals(timeline, trimmed);

        try {
            trimmed.close();
            errorStatus.close();
            originalTrack.close();
            stack.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testTrimToLongerRange() {
        ErrorStatus errorStatus = new ErrorStatus();

        // trim to a larger range
        Timeline trimmed = new Algorithms().timelineTrimmedToRange(timeline,
                new TimeRange(
                        new RationalTime(-10, 24),
                        new RationalTime(160, 24)),
                errorStatus);

        // it shouldn't have changes at all
        assertEquals(timeline, trimmed);

        try {
            trimmed.close();
            errorStatus.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testTrimFront() {
        ErrorStatus errorStatus = new ErrorStatus();
        Stack stack = timeline.getTracks();
        List<Composable> tracks = stack.getChildren();
        Track originalTrack = (Track) tracks.get(0);

        // trim off the front (clip A and part of B)
        Timeline trimmed = new Algorithms().timelineTrimmedToRange(timeline,
                new TimeRange(
                        new RationalTime(60, 24),
                        new RationalTime(90, 24)),
                errorStatus);
        // it shouldn't have changes at all
        assertNotEquals(timeline, trimmed);
        try {
            stack.close();
        } catch (Exception e) {
            e.printStackTrace();
        }

        stack = trimmed.getTracks();
        tracks = stack.getChildren();
        Track trimmedTrack = (Track) tracks.get(0);
        assertEquals(trimmedTrack.getChildren().size(), 2);
        assertEquals(trimmedTrack.getTrimmedRange(errorStatus),
                new TimeRange(
                        new RationalTime(0, 24),
                        new RationalTime(90, 24)));

        // did clip B get trimmed?
        assertEquals(trimmedTrack.getChildren().get(0).getName(), "B");
        assertEquals(((Clip) trimmedTrack.getChildren().get(0)).getTrimmedRange(errorStatus),
                new TimeRange(
                        new RationalTime(10, 24),
                        new RationalTime(40, 24)));

        // clip C should have been left alone
        assertEquals(trimmedTrack.getChildren().get(1), originalTrack.getChildren().get(2));

        try {
            trimmed.close();
            trimmedTrack.close();
            errorStatus.close();
            originalTrack.close();
            stack.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testTrimWithTransitions() {
        ErrorStatus errorStatus = new ErrorStatus();
        Stack stack = timeline.getTracks();
        List<Composable> tracks = stack.getChildren();
        Track originalTrack = (Track) tracks.get(0);

        assertEquals(timeline.getDuration(errorStatus), new RationalTime(150, 24));
        assertEquals(originalTrack.getChildren().size(), 3);

        Transition tr = new Transition.TransitionBuilder()
                .setInOffset(new RationalTime(12, 24))
                .setOutOffset(new RationalTime(20, 24))
                .build();
        assertTrue(originalTrack.insertChild(1, tr, errorStatus));
        assertEquals(originalTrack.getChildren().size(), 4);
        assertEquals(timeline.getDuration(errorStatus), new RationalTime(150, 24));

        // if you try to sever a Transition in the middle it should fail
        Timeline trimmed = new Algorithms().timelineTrimmedToRange(timeline,
                new TimeRange(
                        new RationalTime(5, 24),
                        new RationalTime(50, 24)),
                errorStatus);
        assertEquals(errorStatus.getOutcome(), ErrorStatus.Outcome.CANNOT_TRIM_TRANSITION);
        try {
            errorStatus.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
        errorStatus = new ErrorStatus();
        trimmed = new Algorithms().timelineTrimmedToRange(timeline,
                new TimeRange(
                        new RationalTime(45, 24),
                        new RationalTime(50, 24)),
                errorStatus);
        assertEquals(errorStatus.getOutcome(), ErrorStatus.Outcome.CANNOT_TRIM_TRANSITION);
        try {
            errorStatus.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
        errorStatus = new ErrorStatus();
        trimmed = new Algorithms().timelineTrimmedToRange(timeline,
                new TimeRange(
                        new RationalTime(25, 24),
                        new RationalTime(50, 24)),
                errorStatus);
        assertNotEquals(timeline, trimmed);

        String expectedStr = "{\n" +
                "                \"OTIO_SCHEMA\": \"Timeline.1\",\n" +
                "                \"metadata\": {},\n" +
                "                \"name\": null,\n" +
                "                \"tracks\": {\n" +
                "                    \"OTIO_SCHEMA\": \"Stack.1\",\n" +
                "                    \"children\": [\n" +
                "                        {\n" +
                "                            \"OTIO_SCHEMA\": \"Track.1\",\n" +
                "                            \"children\": [\n" +
                "                                {\n" +
                "                                    \"OTIO_SCHEMA\": \"Clip.1\",\n" +
                "                                    \"effects\": [],\n" +
                "                                    \"markers\": [],\n" +
                "                                    \"media_reference\": null,\n" +
                "                                    \"metadata\": {},\n" +
                "                                    \"name\": \"A\",\n" +
                "                                    \"source_range\": {\n" +
                "                                        \"OTIO_SCHEMA\": \"TimeRange.1\",\n" +
                "                                        \"duration\": {\n" +
                "                                            \"OTIO_SCHEMA\": \"RationalTime.1\",\n" +
                "                                            \"rate\": 24,\n" +
                "                                            \"value\": 25\n" +
                "                                        },\n" +
                "                                        \"start_time\": {\n" +
                "                                            \"OTIO_SCHEMA\": \"RationalTime.1\",\n" +
                "                                            \"rate\": 24,\n" +
                "                                            \"value\": 25.0\n" +
                "                                        }\n" +
                "                                    }\n" +
                "                                },\n" +
                "                                {\n" +
                "                                    \"OTIO_SCHEMA\": \"Transition.1\",\n" +
                "                                    \"in_offset\": {\n" +
                "                                        \"OTIO_SCHEMA\": \"RationalTime.1\",\n" +
                "                                        \"rate\": 24,\n" +
                "                                        \"value\": 12\n" +
                "                                    },\n" +
                "                                    \"metadata\": {},\n" +
                "                                    \"name\": null,\n" +
                "                                    \"out_offset\": {\n" +
                "                                        \"OTIO_SCHEMA\": \"RationalTime.1\",\n" +
                "                                        \"rate\": 24,\n" +
                "                                        \"value\": 20\n" +
                "                                    },\n" +
                "                                    \"transition_type\": null\n" +
                "                                },\n" +
                "                                {\n" +
                "                                    \"OTIO_SCHEMA\": \"Clip.1\",\n" +
                "                                    \"effects\": [],\n" +
                "                                    \"markers\": [],\n" +
                "                                    \"media_reference\": null,\n" +
                "                                    \"metadata\": {},\n" +
                "                                    \"name\": \"B\",\n" +
                "                                    \"source_range\": {\n" +
                "                                        \"OTIO_SCHEMA\": \"TimeRange.1\",\n" +
                "                                        \"duration\": {\n" +
                "                                            \"OTIO_SCHEMA\": \"RationalTime.1\",\n" +
                "                                            \"rate\": 24,\n" +
                "                                            \"value\": 25\n" +
                "                                        },\n" +
                "                                        \"start_time\": {\n" +
                "                                            \"OTIO_SCHEMA\": \"RationalTime.1\",\n" +
                "                                            \"rate\": 24,\n" +
                "                                            \"value\": 0.0\n" +
                "                                        }\n" +
                "                                    }\n" +
                "                                }\n" +
                "                            ],\n" +
                "                            \"effects\": [],\n" +
                "                            \"kind\": \"Video\",\n" +
                "                            \"markers\": [],\n" +
                "                            \"metadata\": {},\n" +
                "                            \"name\": \"Sequence1\",\n" +
                "                            \"source_range\": null\n" +
                "                        }\n" +
                "                    ],\n" +
                "                    \"effects\": [],\n" +
                "                    \"markers\": [],\n" +
                "                    \"metadata\": {},\n" +
                "                    \"name\": \"tracks\",\n" +
                "                    \"source_range\": null\n" +
                "                }\n" +
                "            }";

        Timeline expected = (Timeline) SerializableObject.fromJSONString(expectedStr, errorStatus);

        assertEquals(expected, trimmed);

        try {
            trimmed.close();
            expected.close();
            errorStatus.close();
            originalTrack.close();
            stack.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @AfterEach
    public void cleanUp() {
        try {
            timeline.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
        timeline = null;
    }

}
