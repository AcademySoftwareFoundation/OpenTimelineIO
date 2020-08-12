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

import static org.junit.jupiter.api.Assertions.*;

public class StackAlgoTest {

    Track trackZ = null;
    Track trackABC = null;
    Track trackDgE = null;
    Track trackgFg = null;

    @BeforeEach
    public void setup() {

        ErrorStatus errorStatus = new ErrorStatus();

        trackZ = (Track) SerializableObject.fromJSONString("" +
                        "{\n" +
                        "            \"OTIO_SCHEMA\": \"Track.1\",\n" +
                        "            \"children\": [\n" +
                        "                {\n" +
                        "                    \"OTIO_SCHEMA\": \"Clip.1\",\n" +
                        "                    \"effects\": [],\n" +
                        "                    \"markers\": [],\n" +
                        "                    \"media_reference\": null,\n" +
                        "                    \"metadata\": {},\n" +
                        "                    \"name\": \"Z\",\n" +
                        "                    \"source_range\": {\n" +
                        "                        \"OTIO_SCHEMA\": \"TimeRange.1\",\n" +
                        "                        \"duration\": {\n" +
                        "                            \"OTIO_SCHEMA\": \"RationalTime.1\",\n" +
                        "                            \"rate\": 24,\n" +
                        "                            \"value\": 150\n" +
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
                        "        }",
                errorStatus);

        trackABC = (Track) SerializableObject.fromJSONString("" +
                        "{\n" +
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
                        "        }",
                errorStatus);

        trackDgE = (Track) SerializableObject.fromJSONString("" +
                        "{\n" +
                        "            \"OTIO_SCHEMA\": \"Track.1\",\n" +
                        "            \"children\": [\n" +
                        "                {\n" +
                        "                    \"OTIO_SCHEMA\": \"Clip.1\",\n" +
                        "                    \"effects\": [],\n" +
                        "                    \"markers\": [],\n" +
                        "                    \"media_reference\": null,\n" +
                        "                    \"metadata\": {},\n" +
                        "                    \"name\": \"D\",\n" +
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
                        "                    \"OTIO_SCHEMA\": \"Gap.1\",\n" +
                        "                    \"effects\": [],\n" +
                        "                    \"markers\": [],\n" +
                        "                    \"media_reference\": null,\n" +
                        "                    \"metadata\": {},\n" +
                        "                    \"name\": \"g\",\n" +
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
                        "                    \"name\": \"E\",\n" +
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
                        "        }",
                errorStatus);

        trackgFg = (Track) SerializableObject.fromJSONString("" +
                        "{\n" +
                        "            \"OTIO_SCHEMA\": \"Track.1\",\n" +
                        "            \"children\": [\n" +
                        "                {\n" +
                        "                    \"OTIO_SCHEMA\": \"Gap.1\",\n" +
                        "                    \"effects\": [],\n" +
                        "                    \"markers\": [],\n" +
                        "                    \"media_reference\": null,\n" +
                        "                    \"metadata\": {},\n" +
                        "                    \"name\": \"g1\",\n" +
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
                        "                    \"name\": \"F\",\n" +
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
                        "                    \"OTIO_SCHEMA\": \"Gap.1\",\n" +
                        "                    \"effects\": [],\n" +
                        "                    \"markers\": [],\n" +
                        "                    \"media_reference\": null,\n" +
                        "                    \"metadata\": {},\n" +
                        "                    \"name\": \"g2\",\n" +
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
                        "        }",
                errorStatus);

        try {
            errorStatus.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testFlattenSingleTrack() {
        Stack stack = new Stack.StackBuilder().build();
        ErrorStatus errorStatus = new ErrorStatus();
        assertTrue(stack.appendChild(trackABC, errorStatus));
        Track flatTrack = new Algorithms().flattenStack(stack, errorStatus);
        // the result should be equivalent
        List<Composable> flatTrackChildren = flatTrack.getChildren();
        List<Composable> trackABCChildren = trackABC.getChildren();
        assertEquals(flatTrackChildren, trackABCChildren);
        // but not the same actual objects
        assertNotEquals(flatTrackChildren.get(0).getNativeManager().getOTIOObjectNativeHandle(),
                trackABCChildren.get(0).getNativeManager().getOTIOObjectNativeHandle());
        assertNotEquals(flatTrackChildren.get(1).getNativeManager().getOTIOObjectNativeHandle(),
                trackABCChildren.get(1).getNativeManager().getOTIOObjectNativeHandle());
        assertNotEquals(flatTrackChildren.get(2).getNativeManager().getOTIOObjectNativeHandle(),
                trackABCChildren.get(2).getNativeManager().getOTIOObjectNativeHandle());
        try {
            stack.close();
            errorStatus.close();
            flatTrack.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testFlattenObscureTrack() {
        Stack stack = new Stack.StackBuilder().build();
        ErrorStatus errorStatus = new ErrorStatus();
        assertTrue(stack.appendChild(trackABC, errorStatus));
        assertTrue(stack.appendChild(trackZ, errorStatus));
        Track flatTrack = new Algorithms().flattenStack(stack, errorStatus);
        List<Composable> flatTrackChildren = flatTrack.getChildren();
        List<Composable> trackZChildren = trackZ.getChildren();
        assertEquals(flatTrackChildren, trackZChildren);

        // It is an error to add an item to composition if it is already in
        // another composition.  This clears out the old test composition
        // (and also clears out its parent pointers).
        try {
            stack.close();
            flatTrack.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
        stack = new Stack.StackBuilder().build();
        assertTrue(stack.appendChild(trackZ, errorStatus));
        assertTrue(stack.appendChild(trackABC, errorStatus));
        flatTrack = new Algorithms().flattenStack(stack, errorStatus);
        flatTrackChildren = flatTrack.getChildren();
        List<Composable> trackABCChildren = trackABC.getChildren();
        assertEquals(flatTrackChildren, trackABCChildren);
        try {
            flatTrack.close();
            errorStatus.close();
            stack.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testFlattenGaps() {
        Stack stack = new Stack.StackBuilder().build();
        ErrorStatus errorStatus = new ErrorStatus();
        assertTrue(stack.appendChild(trackABC, errorStatus));
        assertTrue(stack.appendChild(trackDgE, errorStatus));
        Track flatTrack = new Algorithms().flattenStack(stack, errorStatus);
        List<Composable> flatTrackChildren = flatTrack.getChildren();
        List<Composable> trackABCChildren = trackABC.getChildren();
        List<Composable> trackDgEChildren = trackDgE.getChildren();
        List<Composable> trackgFgChildren = trackgFg.getChildren();
        assertEquals(flatTrackChildren.get(0), trackDgEChildren.get(0));
        assertEquals(flatTrackChildren.get(1), trackABCChildren.get(1));
        assertEquals(flatTrackChildren.get(2), trackDgEChildren.get(2));
        assertNotEquals(flatTrackChildren.get(0).getNativeManager().getOTIOObjectNativeHandle(),
                trackDgEChildren.get(0).getNativeManager().getOTIOObjectNativeHandle());
        assertNotEquals(flatTrackChildren.get(1).getNativeManager().getOTIOObjectNativeHandle(),
                trackABCChildren.get(1).getNativeManager().getOTIOObjectNativeHandle());
        assertNotEquals(flatTrackChildren.get(2).getNativeManager().getOTIOObjectNativeHandle(),
                trackDgEChildren.get(2).getNativeManager().getOTIOObjectNativeHandle());

        // create a new stack out of the old parts, delete the old stack first
        try {
            stack.close();
            flatTrack.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
        stack = new Stack.StackBuilder().build();
        assertTrue(stack.appendChild(trackABC, errorStatus));
        assertTrue(stack.appendChild(trackgFg, errorStatus));
        flatTrack = new Algorithms().flattenStack(stack, errorStatus);
        flatTrackChildren = flatTrack.getChildren();
        assertEquals(flatTrackChildren.get(0), trackABCChildren.get(0));
        assertEquals(flatTrackChildren.get(1), trackgFgChildren.get(1));
        assertEquals(flatTrackChildren.get(2), trackABCChildren.get(2));
        assertNotEquals(flatTrackChildren.get(0).getNativeManager().getOTIOObjectNativeHandle(),
                trackABCChildren.get(0).getNativeManager().getOTIOObjectNativeHandle());
        assertNotEquals(flatTrackChildren.get(1).getNativeManager().getOTIOObjectNativeHandle(),
                trackgFgChildren.get(1).getNativeManager().getOTIOObjectNativeHandle());
        assertNotEquals(flatTrackChildren.get(2).getNativeManager().getOTIOObjectNativeHandle(),
                trackABCChildren.get(2).getNativeManager().getOTIOObjectNativeHandle());
        try {
            stack.close();
            flatTrack.close();
            errorStatus.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testFlattenGapsWithTrims() {
        Stack stack = new Stack.StackBuilder().build();
        ErrorStatus errorStatus = new ErrorStatus();
        assertTrue(stack.appendChild(trackZ, errorStatus));
        assertTrue(stack.appendChild(trackDgE, errorStatus));
        Track flatTrack = new Algorithms().flattenStack(stack, errorStatus);
        List<Composable> flatTrackChildren = flatTrack.getChildren();
        assertEquals(flatTrackChildren.get(0), trackDgE.getChildren().get(0));
        assertEquals(flatTrackChildren.get(1).getName(), "Z");
        assertEquals(((Clip) flatTrackChildren.get(1)).getSourceRange(),
                new TimeRange(
                        new RationalTime(50, 24),
                        new RationalTime(50, 24)));
        assertEquals(flatTrackChildren.get(2), trackDgE.getChildren().get(2));

        try {
            stack.close();
            flatTrack.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
        stack = new Stack.StackBuilder().build();
        assertTrue(stack.appendChild(trackZ, errorStatus));
        assertTrue(stack.appendChild(trackgFg, errorStatus));
        flatTrack = new Algorithms().flattenStack(stack, errorStatus);
        flatTrackChildren = flatTrack.getChildren();
        assertEquals(flatTrackChildren.get(0).getName(), "Z");
        assertEquals(((Clip) flatTrackChildren.get(0)).getSourceRange(),
                new TimeRange(
                        new RationalTime(0, 24),
                        new RationalTime(50, 24)));
        assertEquals(flatTrackChildren.get(1), trackgFg.getChildren().get(1));
        assertEquals(flatTrackChildren.get(2).getName(), "Z");
        assertEquals(((Clip) flatTrackChildren.get(2)).getSourceRange(),
                new TimeRange(
                        new RationalTime(100, 24),
                        new RationalTime(50, 24)));
        try {
            stack.close();
            flatTrack.close();
            errorStatus.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testFlattenListOfTracks() {
        List<Track> tracks = new ArrayList<>();
        tracks.add(trackABC);
        tracks.add(trackDgE);
        ErrorStatus errorStatus = new ErrorStatus();
        Track flatTrack = new Algorithms().flattenStack(tracks, errorStatus);
        List<Composable> flatTrackChildren = flatTrack.getChildren();
        List<Composable> trackABCChildren = trackABC.getChildren();
        List<Composable> trackgFgChildren = trackgFg.getChildren();
        List<Composable> trackDgEChildren = trackDgE.getChildren();
        assertEquals(flatTrackChildren.get(0), trackDgEChildren.get(0));
        assertEquals(flatTrackChildren.get(1), trackABCChildren.get(1));
        assertEquals(flatTrackChildren.get(2), trackDgEChildren.get(2));

        try {
            flatTrack.close();
        } catch (Exception e) {
            e.printStackTrace();
        }

        tracks = new ArrayList<>();
        tracks.add(trackABC);
        tracks.add(trackgFg);
        flatTrack = new Algorithms().flattenStack(tracks, errorStatus);
        flatTrackChildren = flatTrack.getChildren();
        assertEquals(flatTrackChildren.get(0), trackABCChildren.get(0));
        assertEquals(flatTrackChildren.get(1), trackgFgChildren.get(1));
        assertEquals(flatTrackChildren.get(2), trackABCChildren.get(2));
        try {
            errorStatus.close();
            flatTrack.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testFlattenExampleCode() {
        String projectRootDir = System.getProperty("user.dir");
        String sampleDataDir = projectRootDir + File.separator +
                "src" + File.separator + "test" + File.separator + "sample_data";
        String multitrackTest = sampleDataDir + File.separator + "multitrack.otio";
        String preflattenedTest = sampleDataDir + File.separator + "preflattened.otio";
        File file = new File(multitrackTest);
        assertTrue(file.exists());
        file = new File(preflattenedTest);
        assertTrue(file.exists());
        ErrorStatus errorStatus = new ErrorStatus();

        Timeline timeline = (Timeline) SerializableObject.fromJSONFile(multitrackTest, errorStatus);
        Timeline preflattened = (Timeline) SerializableObject.fromJSONFile(preflattenedTest, errorStatus);
        Track preflattenedTrack = preflattened.getVideoTracks().get(0);
        Track flattenedTrack = new Algorithms().flattenStack(timeline.getVideoTracks(), errorStatus);
        // the names will be different, so clear them both
        preflattenedTrack.setName("");
        flattenedTrack.setName("");
        assertEquals(preflattenedTrack, flattenedTrack);
        try {
            timeline.close();
            preflattened.close();
            preflattenedTrack.close();
            flattenedTrack.close();
            errorStatus.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testFlattenWithTransition() {
        Stack stack = new Stack.StackBuilder().build();
        ErrorStatus errorStatus = new ErrorStatus();
        assertTrue(trackDgE.insertChild(1,
                new Transition.TransitionBuilder()
                        .setName("test_transition")
                        .setInOffset(new RationalTime(10, 24))
                        .setOutOffset(new RationalTime(15, 24))
                        .build(),
                errorStatus));
        assertTrue(stack.appendChild(trackABC, errorStatus));
        assertTrue(stack.appendChild(trackDgE, errorStatus));
        Track flatTrack = new Algorithms().flattenStack(stack, errorStatus);
        assertEquals(trackABC.getChildren().size(), 3);
        assertEquals(((Track) stack.getChildren().get(1)).getChildren().size(), 4);
        assertEquals(flatTrack.getChildren().size(), 4);
        assertEquals(flatTrack.getChildren().get(1).getName(), "test_transition");
        try {
            stack.close();
            errorStatus.close();
            flatTrack.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @AfterEach
    public void cleanup() {

        try {
            trackZ.close();
            trackgFg.close();
            trackDgE.close();
            trackABC.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
