from . _opentime import *
from . _opentime import _testing

from_frames = RationalTime.from_frames
from_timecode = RationalTime.from_timecode
from_time_string = RationalTime.from_time_string
from_seconds = RationalTime.from_seconds

range_from_start_end_time = TimeRange.range_from_start_end_time
duration_from_start_end_time = RationalTime.duration_from_start_end_time

def to_timecode(rt, rate=None):
    return rt.to_timecode() if rate is None else rt.to_timecode(rate)

def to_frames(rt, rate=None):
    return rt.to_frames() if rate is None else rt.to_frames(rate)

def to_seconds(rt):
    return rt.to_seconds()

def to_time_string(rt):
    return rt.to_time_string()




