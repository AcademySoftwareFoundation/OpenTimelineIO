package io.opentimeline;

import io.opentimeline.opentime.RationalTime;
import io.opentimeline.opentime.TimeRange;
import io.opentimeline.opentimelineio.*;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

public class MarkerTest {

    @Test
    public void testConstructor() {
        TimeRange tr = new TimeRange(
                new RationalTime(5, 24),
                new RationalTime(10, 24));
        AnyDictionary metadata = new AnyDictionary();
        metadata.put("foo", new Any("bar"));
        Marker m = new Marker.MarkerBuilder()
                .setName("marker_1")
                .setMarkedRange(tr)
                .setColor(Marker.Color.green)
                .setMetadata(metadata)
                .build();

        assertEquals(m.getName(), "marker_1");
        assertEquals(m.getMetadata().size(), 1);
        assertEquals(m.getMetadata().get("foo").safelyCastString(), "bar");
        assertTrue(m.getMarkedRange().equals(tr));
        assertEquals(m.getColor(), Marker.Color.green);

        ErrorStatus errorStatus = new ErrorStatus(); //Fix segfault
        String encoded = m.toJSONString(errorStatus);
        SerializableObject decoded = SerializableObject.fromJSONString(encoded, errorStatus);
        assertTrue(decoded.isEquivalentTo(m));
        try {
            metadata.close();
            m.close();
            errorStatus.close();
            decoded.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testStr() {
        TimeRange tr = new TimeRange(
                new RationalTime(5, 24),
                new RationalTime(10, 24));
        AnyDictionary metadata = new AnyDictionary();
        metadata.put("foo", new Any("bar"));
        Marker m = new Marker.MarkerBuilder()
                .setName("marker_1")
                .setMarkedRange(tr)
                .setColor(Marker.Color.green)
                .setMetadata(metadata)
                .build();
        assertEquals(m.toString(),
                "io.opentimeline.opentimelineio.Marker(" +
                        "name=marker_1, " +
                        "markedRange=io.opentimeline.opentime.TimeRange(" +
                        "startTime=io.opentimeline.opentime.RationalTime(value=5.0, rate=24.0), " +
                        "duration=io.opentimeline.opentime.RationalTime(value=10.0, rate=24.0)), " +
                        "metadata=io.opentimeline.opentimelineio.AnyDictionary{" +
                        "foo=io.opentimeline.opentimelineio.Any(value=bar)})");
        try {
            m.close();
            metadata.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testUpgrade() {
        String src = "{\n" +
                "            \"OTIO_SCHEMA\" : \"Marker.1\",\n" +
                "            \"metadata\" : {},\n" +
                "            \"name\" : null,\n" +
                "            \"range\" : {\n" +
                "                \"OTIO_SCHEMA\" : \"TimeRange.1\",\n" +
                "                \"start_time\" : {\n" +
                "                    \"OTIO_SCHEMA\" : \"RationalTime.1\",\n" +
                "                    \"rate\" : 5,\n" +
                "                    \"value\" : 0\n" +
                "                },\n" +
                "                \"duration\" : {\n" +
                "                    \"OTIO_SCHEMA\" : \"RationalTime.1\",\n" +
                "                    \"rate\" : 5,\n" +
                "                    \"value\" : 0\n" +
                "                }\n" +
                "            }\n" +
                "\n" +
                "        }";

        ErrorStatus errorStatus = new ErrorStatus();
        Marker marker = (Marker) SerializableObject.fromJSONString(src, errorStatus);

        assertTrue(marker.getMarkedRange().equals(
                new TimeRange(
                        new RationalTime(0, 5),
                        new RationalTime(0, 5))));
        try {
            errorStatus.close();
            marker.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testEq() {
        Marker marker = new Marker.MarkerBuilder().build();
        Item item = new Item.ItemBuilder().build();
        assertFalse(marker.isEquivalentTo(item));
        try {
            marker.close();
            item.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

}
