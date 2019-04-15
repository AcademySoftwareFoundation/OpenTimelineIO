//
//  tryme.m
//  libotio-macos
//
//  Created by David Baraff on 12/28/18.
//

#import <Foundation/Foundation.h>
#import <opentime/rationalTime.h>
#import <opentimelineio/clip.h>
#import "opentime.h"

namespace otio = opentimelineio::OPENTIMELINEIO_VERSION;

static inline otio::RationalTime const* otioRationalTime(CxxRationalTime const* rt) {
    return (otio::RationalTime const*)(rt);
}

static inline otio::TimeRange const* otioTR(CxxTimeRange const* tr) {
    return (otio::TimeRange const*)(tr);
}

static inline otio::TimeTransform const* otioTT(CxxTimeTransform const* tt) {
    return (otio::TimeTransform const*)(tt);
}

double rational_time_value_rescaled_to(CxxRationalTime const* rt, double rate) {
    return otioRationalTime(rt)->value_rescaled_to(rate);
}

CxxRationalTime rational_time_rescaled_to(CxxRationalTime const* rt, double new_rate) {
    return cxxRationalTime(otioRationalTime(rt)->rescaled_to(new_rate));
}

bool rational_time_almost_equal(CxxRationalTime lhs, CxxRationalTime rhs, double delta) {
    return otioRationalTime(lhs).almost_equal(otioRationalTime(rhs), delta);
}

CxxRationalTime rational_time_duration_from_start_end_time(CxxRationalTime s, CxxRationalTime e) {
    return cxxRationalTime(otio::RationalTime::duration_from_start_end_time(otioRationalTime(s),
                                                                            otioRationalTime(e)));
}

bool rational_time_is_valid_timecode_rate(double rate) {
    return otio::RationalTime::is_valid_timecode_rate(rate);
}

static inline void deal_with_error(opentime::ErrorStatus const& error_status, CxxErrorStruct* err) {
    if (error_status.outcome != error_status.OK) {
        err->statusCode = error_status.outcome;
        err->details = CFBridgingRetain([NSString stringWithUTF8String: error_status.details.c_str()]);
    }
}

CxxRationalTime rational_time_from_timecode(NSString* timecode, double rate, CxxErrorStruct* err) {
    opentime::ErrorStatus error_status;
    auto result = cxxRationalTime(opentime::RationalTime::from_timecode([timecode UTF8String], rate, &error_status));
    deal_with_error(error_status, err);
    return result;
}

CxxRationalTime rational_time_from_timestring(NSString* timestring, double rate, CxxErrorStruct* err) {
    opentime::ErrorStatus error_status;
    auto result = cxxRationalTime(otio::RationalTime::from_time_string([timestring UTF8String], rate, &error_status));
    deal_with_error(error_status, err);
    return result;
}

NSString* rational_time_to_timecode(CxxRationalTime rt, double rate, CxxErrorStruct* err) {
    opentime::ErrorStatus error_status;
    std::string result = otioRationalTime(rt).to_timecode(rate, &error_status);
    deal_with_error(error_status, err);
    return [NSString stringWithUTF8String: result.c_str()];
}

NSString* rational_time_to_timestring(CxxRationalTime rt) {
    std::string result = otioRationalTime(rt).to_time_string();
    return [NSString stringWithUTF8String: result.c_str()];
}

CxxRationalTime rational_time_add(CxxRationalTime lhs, CxxRationalTime rhs) {
    return cxxRationalTime(otioRationalTime(lhs) + otioRationalTime(rhs));
}

CxxRationalTime rational_time_subtract(CxxRationalTime lhs, CxxRationalTime rhs) {
    return cxxRationalTime(otioRationalTime(lhs) - otioRationalTime(rhs));
}

CxxRationalTime time_range_end_time_inclusive(CxxTimeRange const* tr) {
    return cxxRationalTime(otioTR(tr)->end_time_inclusive());
}

CxxRationalTime time_range_end_time_exclusive(CxxTimeRange const* tr) {
    return cxxRationalTime(otioTR(tr)->end_time_exclusive());
}

CxxTimeRange time_range_duration_extended_by(CxxTimeRange const* tr, CxxRationalTime rt) {
    return cxxTimeRange(otioTR(tr)->duration_extended_by(otioRationalTime(rt)));
}

CxxTimeRange time_range_extended_by(CxxTimeRange const* r1, CxxTimeRange const* r2) {
    return cxxTimeRange(otioTR(r1)->extended_by(*otioTR(r2)));
}

CxxTimeRange time_range_clamped_range(CxxTimeRange const* r1, CxxTimeRange const* r2) {
    return cxxTimeRange(otioTR(r1)->clamped(*otioTR(r2)));
}

CxxRationalTime time_range_clamped_time(CxxTimeRange const* r, CxxRationalTime t) {
    return cxxRationalTime(otioTR(r)->clamped(otioRationalTime(t)));
}

bool time_range_contains_time(CxxTimeRange const* r, CxxRationalTime t) {
    return otioTR(r)->contains(otioRationalTime(t));
}

bool time_range_contains_range(CxxTimeRange const* r1, CxxTimeRange const* r2) {
    return otioTR(r1)->contains(*otioTR(r2));
}

bool time_range_overlaps_time(CxxTimeRange const* r, CxxRationalTime t) {
    return otioTR(r)->overlaps(otioRationalTime(t));
}

bool time_range_overlaps_range(CxxTimeRange const* r1, CxxTimeRange const* r2) {
    return otioTR(r1)->overlaps(*otioTR(r2));
}

bool time_range_equals(CxxTimeRange const* r1, CxxTimeRange const* r2) {
    return *otioTR(r1) == *otioTR(r2);
}

CxxTimeRange time_range_range_from_start_end_time(CxxRationalTime s, CxxRationalTime e) {
    return cxxTimeRange(otio::TimeRange::range_from_start_end_time(otioRationalTime(s), otioRationalTime(e)));
}

bool time_transform_equals(CxxTimeTransform const* lhs, CxxTimeTransform const* rhs) {
    return *otioTT(lhs) == *otioTT(rhs);
}

CxxTimeRange time_transform_applied_to_timerange(CxxTimeTransform const* tt, CxxTimeRange const* tr) {
    return cxxTimeRange(otioTT(tt)->applied_to(*otioTR(tr)));
}

CxxTimeTransform time_transform_applied_to_timetransform(CxxTimeTransform const* tt, CxxTimeTransform const* other) {
    return cxxTimeTransform(otioTT(tt)->applied_to(*otioTT(other)));
}

CxxRationalTime time_transform_applied_to_time(CxxTimeTransform const* tt, CxxRationalTime t) {
    return cxxRationalTime(otioTT(tt)->applied_to(otioRationalTime(t)));
}
