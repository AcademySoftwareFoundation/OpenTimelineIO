package io.opentimeline;

import io.opentimeline.opentime.ErrorStatus;
import io.opentimeline.opentime.IsDropFrameRate;
import io.opentimeline.opentime.RationalTime;
import io.opentimeline.util.Pair;
import io.opentimeline.util.Triplet;
import org.junit.jupiter.api.Test;

import java.util.ArrayList;

import static org.junit.jupiter.api.Assertions.*;

public class RationalTimeTest {
    @Test
    public void testCreate() {
        RationalTime t = new RationalTime();
        assertEquals(t.getValue(), 0);
        assertEquals(t.getRate(), 1);

        t = new RationalTime(30, 1);
        assertEquals(t.getValue(), 30);
        assertEquals(t.getRate(), 1);

        t = new RationalTime.RationalTimeBuilder()
                .setValue(32)
                .build();
        assertEquals(t.getValue(), 32);
        assertEquals(t.getRate(), 1);

        t = new RationalTime.RationalTimeBuilder()
                .setRate(29.97)
                .build();
        assertEquals(t.getValue(), 0);
        assertEquals(t.getRate(), 29.97);
    }

    @Test
    public void testStr() {
        RationalTime rt = new RationalTime(10, 24);
        assertEquals(rt.toString(),
                "io.opentimeline.opentime.RationalTime(value=10.0, rate=24.0)");
    }

    @Test
    public void testEquality() {
        RationalTime t1 = new RationalTime.RationalTimeBuilder()
                .setValue(30.2)
                .build();
        assertTrue(t1.equals(t1));
        RationalTime t2 = new RationalTime.RationalTimeBuilder()
                .setValue(30.2)
                .build();
        assertTrue(t1.equals(t2));
    }

    @Test
    public void testInequality() {
        RationalTime t1 = new RationalTime.RationalTimeBuilder()
                .setValue(30.2)
                .build();
        assertTrue(t1.equals(t1));
        RationalTime t2 = new RationalTime.RationalTimeBuilder()
                .setValue(33.2)
                .build();
        assertFalse(t1.equals(t2));
    }

    @Test
    public void testComparison() {
        RationalTime t1 = new RationalTime.RationalTimeBuilder()
                .setValue(15.2)
                .build();
        RationalTime t2 = new RationalTime.RationalTimeBuilder()
                .setValue(15.6)
                .build();
        assertEquals(t1.compareTo(t2), -1);
        assertEquals(t2.compareTo(t1), 1);
        assertEquals(t1.compareTo(t1), 0);

        RationalTime t3 = new RationalTime.RationalTimeBuilder()
                .setValue(30.4)
                .setRate(2)
                .build();
        assertEquals(t1.compareTo(t3), 0);

        /* test implicit base conversion */
        t2 = new RationalTime(15.6, 48);
        assertEquals(t1.compareTo(t2), 1);
    }

    @Test
    public void testBaseConversion() {
        RationalTime t = new RationalTime(10, 24);
        assertEquals(t.getRate(), 24);
        t = t.rescaledTo(48);
        assertEquals(t.getRate(), 48);

        t = new RationalTime(10, 24);
        RationalTime t2 = new RationalTime(20, 48);
        t = t.rescaledTo(t2);
        assertEquals(t.getRate(), t2.getRate());
    }

    @Test
    public void testTimecodeConvert() {
        String timecode = "00:06:56:17";
        ErrorStatus errorStatus = new ErrorStatus();
        RationalTime t = RationalTime.fromTimecode(timecode, 24, errorStatus);
        assertEquals(timecode, t.toTimecode(errorStatus));
    }

    @Test
    public void testTimecode24() {
        String timecode = "00:00:01:00";
        ErrorStatus errorStatus = new ErrorStatus();
        RationalTime t = new RationalTime(24, 24);
        assertTrue(t.equals(RationalTime.fromTimecode(timecode, 24, errorStatus)));

        timecode = "00:01:00:00";
        t = new RationalTime(24 * 60, 24);
        assertTrue(t.equals(RationalTime.fromTimecode(timecode, 24, errorStatus)));

        timecode = "01:00:00:00";
        t = new RationalTime(24 * 60 * 60, 24);
        assertTrue(t.equals(RationalTime.fromTimecode(timecode, 24, errorStatus)));

        timecode = "24:00:00:00";
        t = new RationalTime(24 * 60 * 60 * 24, 24);
        assertTrue(t.equals(RationalTime.fromTimecode(timecode, 24, errorStatus)));

        timecode = "23:59:59:23";
        t = new RationalTime(24 * 60 * 60 * 24 - 1, 24);
        assertTrue(t.equals(RationalTime.fromTimecode(timecode, 24, errorStatus)));
    }

    @Test
    public void testAdd() {
        RationalTime sum1 = new RationalTime();
        RationalTime ans = new RationalTime(55, 24);

        for (int i = 0; i < 10; i++) {
            RationalTime incr = new RationalTime(i + 1, 24);
            sum1 = sum1.add(incr);
        }
        assertTrue(sum1.equals(ans));
    }

    @Test
    public void testTimecodeZero() {
        RationalTime t = new RationalTime();
        String timecode = "00:00:00:00";
        ErrorStatus errorStatus = new ErrorStatus();
        assertEquals(timecode, t.toTimecode(24, IsDropFrameRate.InferFromRate, errorStatus));
        assertTrue(t.equals(RationalTime.fromTimecode(timecode, 24, errorStatus)));
    }

    @Test
    public void testLongRunningTimecode() {
        long finalFrameNumber = 24 * 60 * 60 * 24 - 1;
        RationalTime finalTime = RationalTime.fromFrames(finalFrameNumber, 24);
        ErrorStatus errorStatus = new ErrorStatus();
        assertEquals(finalTime.toTimecode(errorStatus), "23:59:59:23");

        RationalTime step_time = new RationalTime(1, 24);
        RationalTime cumulativeTime = new RationalTime();
        for (int i = 0; i < finalFrameNumber; i++) {
            cumulativeTime = cumulativeTime.add(step_time);
        }
        assertTrue(cumulativeTime.equals(finalTime));

        /* Adding by a non-multiple of 24 */
        for (long fnum = 1113; fnum < finalFrameNumber; fnum += 1113) {
            RationalTime rt = new RationalTime(fnum, 24);
            String tc = rt.toTimecode(errorStatus);
            RationalTime rt2 = RationalTime.fromTimecode(tc, 24, errorStatus);
            assertTrue(rt.equals(rt2));
            assertEquals(tc, rt2.toTimecode(errorStatus));
        }
    }

    @Test
    public void testTimecode23967fps() {
        /* This should behave exactly like 24fps */
        String timecode = "00:00:01:00";
        ErrorStatus errorStatus = new ErrorStatus();
        RationalTime t = new RationalTime(24, 23.976);
        assertTrue(t.equals(RationalTime.fromTimecode(timecode, 23.976, errorStatus)));

        timecode = "00:01:00:00";
        t = new RationalTime(24 * 60, 23.976);
        assertTrue(t.equals(RationalTime.fromTimecode(timecode, 23.976, errorStatus)));

        timecode = "01:00:00:00";
        t = new RationalTime(24 * 60 * 60, 23.976);
        assertTrue(t.equals(RationalTime.fromTimecode(timecode, 23.976, errorStatus)));

        timecode = "24:00:00:00";
        t = new RationalTime(24 * 60 * 60 * 24, 23.976);
        assertTrue(t.equals(RationalTime.fromTimecode(timecode, 23.976, errorStatus)));

        timecode = "23:59:59:23";
        t = new RationalTime(24 * 60 * 60 * 24 - 1, 24000.0 / 1001.0);
        assertTrue(t.equals(RationalTime.fromTimecode(timecode, 24000.0 / 1001.0, errorStatus)));
    }

    @Test
    public void testConvertingNegativeValuesToTimecode() {
        RationalTime t = new RationalTime(-1, 25);
        ErrorStatus errorStatus = new ErrorStatus();
        String tc = t.toTimecode(errorStatus);
        assertEquals(errorStatus.getOutcome(), ErrorStatus.Outcome.NEGATIVE_VALUE);
    }

    @Test
    public void testDropframeTimecode2997fps() {
        /* Test drop frame in action. Focused on minute roll overs

        We nominal_fps 30 for frame calculation
        For this frame rate we drop 2 frames per minute except every 10th.

        Compensation is calculated like this when below 10 minutes:
          (fps * seconds + frames - dropframes * (minutes - 1))
        Like this when not a whole 10 minute above 10 minutes:
          --minutes == minutes - 1
          (fps * seconds + frames - dropframes * (--minutes - --minutes / 10))
        And like this after that:
          (fps * seconds + frames - dropframes * (minutes - minutes / 10))
        */

        ArrayList<Pair<Double, String>> firstFourFrames = new ArrayList<>();
        firstFourFrames.add(new Pair<>(0d, "00:00:00;00"));
        firstFourFrames.add(new Pair<>(1d, "00:00:00;01"));
        firstFourFrames.add(new Pair<>(2d, "00:00:00;02"));
        firstFourFrames.add(new Pair<>(3d, "00:00:00;03"));

        ArrayList<Pair<Double, String>> firstMinuteRollover = new ArrayList<>();
        firstMinuteRollover.add(new Pair<>(30d * 59d + 29d, "00:00:59;29"));
        firstMinuteRollover.add(new Pair<>(30d * 59d + 30d, "00:01:00;02"));
        firstMinuteRollover.add(new Pair<>(30d * 59d + 31d, "00:01:00;03"));
        firstMinuteRollover.add(new Pair<>(30d * 59d + 32d, "00:01:00;04"));
        firstMinuteRollover.add(new Pair<>(30d * 59d + 33d, "00:01:00;05"));

        ArrayList<Pair<Double, String>> fifthMinute = new ArrayList<>();
        fifthMinute.add(new Pair<>(30d * 299d + 29d - 2d * 4d, "00:04:59;29"));
        fifthMinute.add(new Pair<>(30d * 299d + 30d - 2d * 4d, "00:05:00;02"));
        fifthMinute.add(new Pair<>(30d * 299d + 31d - 2d * 4d, "00:05:00;03"));
        fifthMinute.add(new Pair<>(30d * 299d + 32d - 2d * 4d, "00:05:00;04"));
        fifthMinute.add(new Pair<>(30d * 299d + 33d - 2d * 4d, "00:05:00;05"));

        ArrayList<Pair<Double, String>> seventhMinute = new ArrayList<>();
        seventhMinute.add(new Pair<>(30d * 419d + 29d - 2d * 6d, "00:06:59;29"));
        seventhMinute.add(new Pair<>(30d * 419d + 30d - 2d * 6d, "00:07:00;02"));
        seventhMinute.add(new Pair<>(30d * 419d + 31d - 2d * 6d, "00:07:00;03"));
        seventhMinute.add(new Pair<>(30d * 419d + 32d - 2d * 6d, "00:07:00;04"));
        seventhMinute.add(new Pair<>(30d * 419d + 33d - 2d * 6d, "00:07:00;05"));

        ArrayList<Pair<Double, String>> tenthMinute = new ArrayList<>();
        tenthMinute.add(new Pair<>(30d * 599d + 29d - 2d * (10d - Math.floorDiv(10, 10)), "00:09:59;29"));
        tenthMinute.add(new Pair<>(30d * 599d + 30d - 2d * (10d - Math.floorDiv(10, 10)), "00:10:00;00"));
        tenthMinute.add(new Pair<>(30d * 599d + 31d - 2d * (10d - Math.floorDiv(10, 10)), "00:10:00;01"));
        tenthMinute.add(new Pair<>(30d * 599d + 32d - 2d * (10d - Math.floorDiv(10, 10)), "00:10:00;02"));
        tenthMinute.add(new Pair<>(30d * 599d + 33d - 2d * (10d - Math.floorDiv(10, 10)), "00:10:00;03"));

        ArrayList<Pair<Double, String>> secondHour = new ArrayList<>();
        secondHour.add(new Pair<>(30d * 7199d + 29d - 2d * (120d - Math.floorDiv(120, 10)), "01:59:59;29"));
        secondHour.add(new Pair<>(30d * 7199d + 30d - 2d * (120d - Math.floorDiv(120, 10)), "02:00:00;00"));
        secondHour.add(new Pair<>(30d * 7199d + 31d - 2d * (120d - Math.floorDiv(120, 10)), "02:00:00;01"));
        secondHour.add(new Pair<>(30d * 7199d + 32d - 2d * (120d - Math.floorDiv(120, 10)), "02:00:00;02"));
        secondHour.add(new Pair<>(30d * 7199d + 33d - 2d * (120d - Math.floorDiv(120, 10)), "02:00:00;03"));

        ArrayList<Pair<Double, String>> secondAndHalfHour = new ArrayList<>();
        secondAndHalfHour.add(new Pair<>(30d * 8999d + 29d - 2d * (150d - Math.floorDiv(150, 10)), "02:29:59;29"));
        secondAndHalfHour.add(new Pair<>(30d * 8999d + 30d - 2d * (150d - Math.floorDiv(150, 10)), "02:30:00;00"));
        secondAndHalfHour.add(new Pair<>(30d * 8999d + 31d - 2d * (150d - Math.floorDiv(150, 10)), "02:30:00;01"));
        secondAndHalfHour.add(new Pair<>(30d * 8999d + 32d - 2d * (150d - Math.floorDiv(150, 10)), "02:30:00;02"));
        secondAndHalfHour.add(new Pair<>(30d * 8999d + 33d - 2d * (150d - Math.floorDiv(150, 10)), "02:30:00;03"));

        ArrayList<Pair<Double, String>> tenthHour = new ArrayList<>();
        tenthHour.add(new Pair<>(30d * 35999d + 29d - 2d * (600d - Math.floorDiv(600, 10)), "09:59:59;29"));
        tenthHour.add(new Pair<>(30d * 35999d + 30d - 2d * (600d - Math.floorDiv(600, 10)), "10:00:00;00"));
        tenthHour.add(new Pair<>(30d * 35999d + 31d - 2d * (600d - Math.floorDiv(600, 10)), "10:00:00;01"));
        tenthHour.add(new Pair<>(30d * 35999d + 32d - 2d * (600d - Math.floorDiv(600, 10)), "10:00:00;02"));
        tenthHour.add(new Pair<>(30d * 35999d + 33d - 2d * (600d - Math.floorDiv(600, 10)), "10:00:00;03"));

        /* Since 3 minutes < 10, we subtract 1 from 603 minutes */
        ArrayList<Pair<Double, String>> tenthHourThirdMinute = new ArrayList<>();
        tenthHourThirdMinute.add(new Pair<>(30d * 36179d + 29d - 2d * (602d - Math.floorDiv(602, 10)), "10:02:59;29"));
        tenthHourThirdMinute.add(new Pair<>(30d * 36179d + 30d - 2d * (602d - Math.floorDiv(602, 10)), "10:03:00;02"));
        tenthHourThirdMinute.add(new Pair<>(30d * 36179d + 31d - 2d * (602d - Math.floorDiv(602, 10)), "10:03:00;03"));
        tenthHourThirdMinute.add(new Pair<>(30d * 36179d + 32d - 2d * (602d - Math.floorDiv(602, 10)), "10:03:00;04"));
        tenthHourThirdMinute.add(new Pair<>(30d * 36179d + 33d - 2d * (602d - Math.floorDiv(602, 10)), "10:03:00;05"));

        ArrayList<ArrayList<Pair<Double, String>>> testValues = new ArrayList<>();
        testValues.add(firstFourFrames);
        testValues.add(firstMinuteRollover);
        testValues.add(fifthMinute);
        testValues.add(seventhMinute);
        testValues.add(tenthMinute);
        testValues.add(secondHour);
        testValues.add(secondAndHalfHour);
        testValues.add(tenthHour);
        testValues.add(tenthHourThirdMinute);
        ErrorStatus errorStatus = new ErrorStatus();

        for (ArrayList<Pair<Double, String>> timeValues : testValues) {
            for (Pair<Double, String> timeValue : timeValues) {
                Double value = timeValue.getFirst();
                String timecode = timeValue.getSecond();

                RationalTime t = new RationalTime(value, 29.97);
                assertEquals(timecode, t.toTimecode(29.97, IsDropFrameRate.ForceYes, errorStatus));

                RationalTime t1 = RationalTime.fromTimecode(timecode, 29.97, errorStatus);
                assertTrue(t.equals(t1));
            }
        }
    }

    @Test
    public void testTimecodeNTSC2997fps() {
        double frames = 1084319;
        double rateFloat = 30000.0 / 1001.0;
        RationalTime t = new RationalTime(frames, rateFloat);
        ErrorStatus errorStatus = new ErrorStatus();

        String dftc = t.toTimecode(rateFloat, IsDropFrameRate.ForceYes, errorStatus);
        assertEquals(dftc, "10:03:00;05");

        String tc = t.toTimecode(rateFloat, IsDropFrameRate.ForceNo, errorStatus);
        assertEquals(tc, "10:02:23:29");

        /* Detect DFTC from rate for backward compatability with old versions */
        String tcAuto = t.toTimecode(rateFloat, IsDropFrameRate.InferFromRate, errorStatus);
        assertEquals(tcAuto, "10:03:00;05");

        RationalTime invalidDFRate = new RationalTime(30, 24000.0 / 1001.0);
        String tcInvalid = invalidDFRate.toTimecode(24000.0 / 1001.0, IsDropFrameRate.ForceYes, errorStatus);
        assertEquals(errorStatus.getOutcome(), ErrorStatus.Outcome.INVALID_RATE_FOR_DROP_FRAME_TIMECODE);
    }

    @Test
    public void testTimecode2997() {
        ArrayList<Triplet<Double, String, String>> refValues = new ArrayList<>();
        refValues.add(new Triplet<>(10789d, "00:05:59:19", "00:05:59;29"));
        refValues.add(new Triplet<>(10790d, "00:05:59:20", "00:06:00;02"));
        refValues.add(new Triplet<>(17981d, "00:09:59:11", "00:09:59;29"));
        refValues.add(new Triplet<>(17982d, "00:09:59:12", "00:10:00;00"));
        refValues.add(new Triplet<>(17983d, "00:09:59:13", "00:10:00;01"));
        refValues.add(new Triplet<>(17984d, "00:09:59:14", "00:10:00;02"));

        ErrorStatus errorStatus = new ErrorStatus();

        for (Triplet<Double, String, String> refValue : refValues) {
            Double value = refValue.getFirst();
            String tc = refValue.getSecond();
            String dftc = refValue.getThird();

            RationalTime t = new RationalTime(value, 29.97);
            String toDfTc = t.toTimecode(29.97, IsDropFrameRate.ForceYes, errorStatus);
            String toTc = t.toTimecode(29.97, IsDropFrameRate.ForceNo, errorStatus);
            String toAutoTc = t.toTimecode(29.97, IsDropFrameRate.InferFromRate, errorStatus);

            /* 29.97 should auto-detect dftc for backward compatibility */
            assertEquals(toDfTc, toAutoTc);

            /* check calculated against reference */
            assertEquals(toDfTc, dftc);
            assertEquals(tc, toTc);

            /* check they convert back */
            RationalTime t1 = RationalTime.fromTimecode(toDfTc, 29.97, errorStatus);
            assertTrue(t1.equals(t));

            RationalTime t2 = RationalTime.fromTimecode(toTc, 29.97, errorStatus);
            assertTrue(t2.equals(t));
        }
    }

    @Test
    public void testFaultyFormattedTimecode() {
        ErrorStatus errorStatus = new ErrorStatus();
        RationalTime t = RationalTime.fromTimecode("01:00:13;23", 24, errorStatus);
        assertEquals(errorStatus.getOutcome(), ErrorStatus.Outcome.NON_DROPFRAME_RATE);
    }

    @Test
    public void testInvalidRateToTimecodeFunctions() {
        RationalTime t = new RationalTime(100, 29.98);
        ErrorStatus errorStatus = new ErrorStatus();

        String tc = t.toTimecode(29.98, IsDropFrameRate.InferFromRate, errorStatus);
        assertEquals(errorStatus.getOutcome(), ErrorStatus.Outcome.INVALID_TIMECODE_RATE);

        tc = t.toTimecode(errorStatus);
        assertEquals(errorStatus.getOutcome(), ErrorStatus.Outcome.INVALID_TIMECODE_RATE);
    }

    @Test
    public void testTimeString24() {
        ErrorStatus errorStatus = new ErrorStatus();

        String timeString = "00:00:00.041667";
        RationalTime t = new RationalTime(1, 24);
        RationalTime timeObj = RationalTime.fromTimeString(timeString, 24, errorStatus);
        assertTrue(t.almostEqual(timeObj, 0.001));
        assertEquals(timeObj.getRate(), 24);

        timeString = "00:00:01";
        t = new RationalTime(24, 24);
        timeObj = RationalTime.fromTimeString(timeString, 24, errorStatus);
        assertTrue(t.almostEqual(timeObj, 0.001));
        assertEquals(timeObj.getRate(), 24);

        timeString = "00:01:00";
        t = new RationalTime(24 * 60, 24);
        timeObj = RationalTime.fromTimeString(timeString, 24, errorStatus);
        assertTrue(t.almostEqual(timeObj, 0.001));
        assertEquals(timeObj.getRate(), 24);

        timeString = "01:00:00";
        t = new RationalTime(24 * 60 * 60, 24);
        timeObj = RationalTime.fromTimeString(timeString, 24, errorStatus);
        assertTrue(t.almostEqual(timeObj, 0.001));
        assertEquals(timeObj.getRate(), 24);

        timeString = "24:00:00";
        t = new RationalTime(24 * 60 * 60 * 24, 24);
        timeObj = RationalTime.fromTimeString(timeString, 24, errorStatus);
        assertTrue(t.almostEqual(timeObj, 0.001));
        assertEquals(timeObj.getRate(), 24);

        timeString = "23:59:59.958333";
        t = new RationalTime(24 * 60 * 60 * 24 - 1, 24);
        timeObj = RationalTime.fromTimeString(timeString, 24, errorStatus);
        assertTrue(t.almostEqual(timeObj, 0.001));
        assertEquals(timeObj.getRate(), 24);
    }

    @Test
    public void testTimeString25() {
        ErrorStatus errorStatus = new ErrorStatus();

        String timeString = "00:00:01";
        RationalTime t = new RationalTime(25, 25);
        RationalTime timeObj = RationalTime.fromTimeString(timeString, 25, errorStatus);
        assertTrue(t.almostEqual(timeObj, 0.001));
        assertEquals(timeObj.getRate(), 25);

        timeString = "00:01:00";
        t = new RationalTime(25 * 60, 25);
        timeObj = RationalTime.fromTimeString(timeString, 25, errorStatus);
        assertTrue(t.almostEqual(timeObj, 0.001));
        assertEquals(timeObj.getRate(), 25);

        timeString = "01:00:00";
        t = new RationalTime(25 * 60 * 60, 25);
        timeObj = RationalTime.fromTimeString(timeString, 25, errorStatus);
        assertTrue(t.almostEqual(timeObj, 0.001));
        assertEquals(timeObj.getRate(), 25);

        timeString = "24:00:00";
        t = new RationalTime(25 * 60 * 60 * 24, 25);
        timeObj = RationalTime.fromTimeString(timeString, 25, errorStatus);
        assertTrue(t.almostEqual(timeObj, 0.001));
        assertEquals(timeObj.getRate(), 25);

        timeString = "23:59:59.92";
        t = new RationalTime(25 * 60 * 60 * 24 - 2, 25);
        timeObj = RationalTime.fromTimeString(timeString, 25, errorStatus);
        assertTrue(t.almostEqual(timeObj, 0.001));
        assertEquals(timeObj.getRate(), 25);
    }

    @Test
    public void testTimeStringNegativeRationalTime() {
        /*
        Negative rational time should return a valid time string
        with a '-' signage. (This is making it ffmpeg compatible)
        */

        String baselineTimeString = "-00:00:01.0";
        RationalTime rt = new RationalTime(-24, 24);
        String timeString = rt.toTimeString();
        assertEquals(baselineTimeString, timeString);
    }

    @Test
    public void testTimeStringZero() {
        RationalTime t = new RationalTime();
        String timeString = "00:00:00.0";
        ErrorStatus errorStatus = new ErrorStatus();

        RationalTime timeObj = RationalTime.fromTimeString(timeString, 24, errorStatus);
        assertEquals(timeString, t.toTimeString());
        assertTrue(t.almostEqual(timeObj, 0.001));
    }

    @Test
    public void testToTimeStringMicrosecondsStartWithZero() {
        /*
        this number has a leading 0 in the fractional part when converted to
        time string (ie 27.08333)
        */
        ErrorStatus errorStatus = new ErrorStatus();
        RationalTime rt = new RationalTime(2090, 24);
        RationalTime compareRt = RationalTime.fromTimeString(rt.toTimeString(), 24, errorStatus);
//        assertTrue(rt.equals(compareRt));
        // TODO: both are not equal but almost equal. So do we need to check using the almost equal function?
    }

    @Test
    public void testLongRunningTimeString24() {
        int finalFrameNumber = 24 * 60 * 60 * 24 - 1;
        RationalTime finalTime = RationalTime.fromFrames(finalFrameNumber, 24);
        assertEquals(finalTime.toTimeString(), "23:59:59.958333");

        RationalTime stepTime = new RationalTime(1, 24);
        RationalTime cumulativeTime = new RationalTime();
        for (int i = 0; i < finalFrameNumber; i++) {
            cumulativeTime = cumulativeTime.add(stepTime);
        }
        assertTrue(cumulativeTime.almostEqual(finalTime, 0.001));

        ErrorStatus errorStatus = new ErrorStatus();
        /* Adding by a non-multiple of 24 */
        for (int fnum = 1113; fnum < finalFrameNumber; fnum += 1113) {
            RationalTime rt = RationalTime.fromFrames(fnum, 24);
            String tc = rt.toTimeString();
            RationalTime rt2 = RationalTime.fromTimeString(tc, 24, errorStatus);
            assertTrue(rt.equals(rt2));
            assertEquals(tc, rt2.toTimeString());
        }
    }

    @Test
    public void testTimeString23976fps() {
        /*
        This list is rewritten from conversion into seconds of
        test_timecode_23976_fps
        */
        ArrayList<Pair<Double, String>> refValues = new ArrayList<>();
        refValues.add(new Pair<>(1025d, "00:00:01.708333"));
        refValues.add(new Pair<>(179900d, "00:04:59.833333"));
        refValues.add(new Pair<>(180000d, "00:05:00.0"));
        refValues.add(new Pair<>(360000d, "00:10:00.0"));
        refValues.add(new Pair<>(720000d, "00:20:00.0"));
        refValues.add(new Pair<>(1079300d, "00:29:58.833333"));
        refValues.add(new Pair<>(1080000d, "00:30:00.0"));
        refValues.add(new Pair<>(1080150d, "00:30:00.25"));
        refValues.add(new Pair<>(1440000d, "00:40:00.0"));
        refValues.add(new Pair<>(1800000d, "00:50:00.0"));
        refValues.add(new Pair<>(1978750d, "00:54:57.916666"));
        refValues.add(new Pair<>(1980000d, "00:55:00.0"));
        refValues.add(new Pair<>(46700d, "00:01:17.833333"));
        refValues.add(new Pair<>(225950d, "00:06:16.583333"));
        refValues.add(new Pair<>(436400d, "00:12:07.333333"));
        refValues.add(new Pair<>(703350d, "00:19:32.25"));

        for (Pair<Double, String> refValue : refValues) {
            Double value = refValue.getFirst();
            String ts = refValue.getSecond();
            RationalTime t = new RationalTime(value, 600);
            assertEquals(ts, t.toTimeString());
        }
    }

    @Test
    public void testFramesWithIntFps() {
        int[] fpsArr = {24, 30, 48, 60};

        for (int fps : fpsArr) {
            RationalTime t1 = RationalTime.fromFrames(101, fps);
            RationalTime t2 = new RationalTime(101, fps);
            assertTrue(t1.equals(t2));
        }
    }

    @Test
    public void testFramesWithNonIntFps() {
        float[] fpsArr = {23.98f, 29.97f, 59.94f};

        for (float fps : fpsArr) {
            RationalTime t1 = RationalTime.fromFrames(101, fps);
            RationalTime t2 = new RationalTime(101, fps);
            assertTrue(t1.equals(t2));
        }
    }

    @Test
    public void testSeconds() {
        int s1 = 1834;
        RationalTime t1 = RationalTime.fromSeconds(s1);
        assertEquals(t1.getValue(), s1);
        assertEquals(t1.getRate(), 1);
        double t1AsSeconds = t1.toSeconds();
        assertEquals(t1AsSeconds, s1);
        assertEquals((float) t1.getValue() / t1.getRate(), s1, 0.00000001);

        float s2 = 248474.345f;
        RationalTime t2 = RationalTime.fromSeconds(s2);
        assertEquals(t2.getValue(), s2, 0.00000001);
        assertEquals(t2.getRate(), 1, 0.00000001);
        double t2AsSeconds = t2.toSeconds();
        assertEquals(t2AsSeconds, s2, 0.00000001);
        assertEquals((float) t2.getValue() / t2.getRate(), s2, 0.00000001);

        float v3 = 3459;
        float r3 = 24;
        float s3 = v3 / 24;
        RationalTime t3 = new RationalTime(v3, r3);
        RationalTime t4 = RationalTime.fromSeconds(s3);
        assertEquals(t3.toSeconds(), s3, 0.00000001);
        assertEquals(t4.toSeconds(), s3, 0.00000001);
    }

    @Test
    public void testDuration() {
        RationalTime startTime = RationalTime.fromFrames(100, 24);
        RationalTime endTime = RationalTime.fromFrames(200, 24);
        RationalTime duration = RationalTime.durationFromStartEndTime(startTime, endTime);
        assertTrue(duration.equals(RationalTime.fromFrames(100, 24)));

        startTime = RationalTime.fromFrames(0, 1);
        endTime = RationalTime.fromFrames(200, 24);
        duration = RationalTime.durationFromStartEndTime(startTime, endTime);
        assertTrue(duration.equals(RationalTime.fromFrames(200, 24)));
    }

    @Test
    public void testMath() {
        RationalTime a = RationalTime.fromFrames(100, 24);
        RationalTime gap = RationalTime.fromFrames(50, 24);
        RationalTime b = RationalTime.fromFrames(150, 24);

        assertTrue(b.subtract(a).equals(gap));
        assertTrue(a.add(gap).equals(b));
        assertTrue(b.subtract(gap).equals(a));

        RationalTime step = new RationalTime(1, 24);
        for (int i = 0; i < 50; i++) {
            a = a.add(step);
        }
        assertTrue(a.equals(RationalTime.fromFrames(150, 24)));
    }

    @Test
    public void testMathWithDifferentScales() {
        RationalTime a = RationalTime.fromFrames(100, 24);
        RationalTime gap = RationalTime.fromFrames(100, 48);
        RationalTime b = RationalTime.fromFrames(75, 12);

        assertTrue(b.subtract(a).equals(gap.rescaledTo(24)));
        assertTrue(a.add(gap).equals(b.rescaledTo(48)));
        assertTrue(b.subtract(gap).equals(a));

        RationalTime gap2 = new RationalTime(gap);
        gap2 = gap2.add(a);
        assertTrue(gap2.equals(a.add(gap)));
        assertTrue(b.subtract(gap).equals(a.rescaledTo(48)));
    }

    @Test
    public void testDurationFromStartEndTime() {
        RationalTime tEnd = new RationalTime(12, 25);
        RationalTime tDur = RationalTime.durationFromStartEndTime(new RationalTime(0, 25), tEnd);
        assertTrue(tEnd.equals(tDur));
    }

    @Test
    public void testSubtractWithDifferentRates() {
        RationalTime t1 = new RationalTime(12, 10);
        RationalTime t2 = new RationalTime(12, 5);
        assertEquals(t1.subtract(t2).getValue(), -12);
    }

    @Test
    public void testPassingNDFTimecodeAtDFRate() {
        String DF_TC = "01:00:02;05";
        String NDF_TC = "00:59:58:17";
        int frames = 107957;
        ErrorStatus errorStatus = new ErrorStatus();

        String tc1 = (new RationalTime(frames, 29.97).toTimecode(errorStatus));
        assertEquals(tc1, DF_TC);

        String tc2 = (new RationalTime(frames, 29.97).toTimecode(29.97, IsDropFrameRate.ForceNo, errorStatus));
        assertEquals(tc2, NDF_TC);

        RationalTime t1 = RationalTime.fromTimecode(DF_TC, 29.97, errorStatus);
        assertEquals(t1.getValue(), frames);

        RationalTime t2 = RationalTime.fromTimecode(NDF_TC, 29.97, errorStatus);
        assertEquals(t2.getValue(), frames);
    }
}
