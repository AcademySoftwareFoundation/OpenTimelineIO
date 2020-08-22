#import "errorStruct.h"

typedef struct CxxRationalTime {
    double value, rate;
} CxxRationalTime;

typedef struct CxxTimeRange {
    CxxRationalTime start_time;
    CxxRationalTime duration;
} CxxTimeRange;

typedef struct CxxTimeTransform {
    CxxRationalTime offset;
    double scale;
    double rate;
} CxxTimeTransform;

typedef struct CxxNonsense {
    int statusCode;
    NSString* details;
} CxxNonsense;

#if defined(__cplusplus)
#import <opentime/rationalTime.h>
#import <opentime/timeRange.h>
#import <opentime/timeTransform.h>

namespace ot = opentime::OPENTIME_VERSION;

inline ot::RationalTime const& otioRationalTime(CxxRationalTime const& rt) {
    return *((ot::RationalTime const*)(&rt));
}

inline ot::TimeRange const& otioTimeRange(CxxTimeRange const& tr) {
    return *((ot::TimeRange const*)(&tr));
}

inline ot::TimeTransform const& otioTimeTransform(CxxTimeTransform const& tt) {
    return *((ot::TimeTransform const*)(&tt));
}

inline CxxRationalTime cxxRationalTime(ot::RationalTime const& rt) {
    return CxxRationalTime { rt.value(), rt.rate() };
}

inline CxxTimeRange cxxTimeRange(ot::TimeRange const& tr) {
    return CxxTimeRange { cxxRationalTime(tr.start_time()), cxxRationalTime(tr.duration()) };
}

inline CxxTimeTransform cxxTimeTransform(ot::TimeTransform const& tt) {
    return CxxTimeTransform { cxxRationalTime(tt.offset()), tt.scale(), tt.rate() };
}
#endif

#if defined(__cplusplus)
extern "C" {
#endif


    
double rational_time_value_rescaled_to(CxxRationalTime const*, double new_rate);
double rational_time_value_rescaled_to_copy(CxxRationalTime, double new_rate);
CxxRationalTime rational_time_rescaled_to(CxxRationalTime const* rt, double new_rate);
bool rational_time_almost_equal(CxxRationalTime, CxxRationalTime, double);

CxxRationalTime rational_time_duration_from_start_end_time(CxxRationalTime, CxxRationalTime);
bool rational_time_is_valid_timecode_rate(double);

CxxRationalTime rational_time_from_timecode(NSString* timecode, double rate, CxxErrorStruct* err);
CxxRationalTime rational_time_from_timestring(NSString* timestring, double rate, CxxErrorStruct* err);
NSString* rational_time_to_timecode(CxxRationalTime, double rate, CxxErrorStruct* err);
NSString* rational_time_to_timestring(CxxRationalTime);
CxxRationalTime rational_time_add(CxxRationalTime, CxxRationalTime);
CxxRationalTime rational_time_subtract(CxxRationalTime, CxxRationalTime);

CxxRationalTime time_range_end_time_inclusive(CxxTimeRange const*);
CxxRationalTime time_range_end_time_exclusive(CxxTimeRange const*);
CxxTimeRange time_range_duration_extended_by(CxxTimeRange const*, CxxRationalTime);
CxxTimeRange time_range_extended_by(CxxTimeRange const*, CxxTimeRange const*);

CxxTimeRange time_range_clamped_range(CxxTimeRange const*, CxxTimeRange const*);
CxxRationalTime time_range_clamped_time(CxxTimeRange const*, CxxRationalTime);

bool time_range_contains_time(CxxTimeRange const*, CxxRationalTime);
bool time_range_contains_range(CxxTimeRange const*, CxxTimeRange const*);
bool time_range_overlaps_time(CxxTimeRange const*, CxxRationalTime);
bool time_range_overlaps_range(CxxTimeRange const*, CxxTimeRange const*);
bool time_range_equals(CxxTimeRange const*, CxxTimeRange const*);
CxxTimeRange time_range_range_from_start_end_time(CxxRationalTime, CxxRationalTime);

bool time_transform_equals(CxxTimeTransform const*, CxxTimeTransform const*);
CxxTimeRange time_transform_applied_to_timerange(CxxTimeTransform const*, CxxTimeRange const*);
CxxTimeTransform time_transform_applied_to_timetransform(CxxTimeTransform const*, CxxTimeTransform const*);
CxxRationalTime time_transform_applied_to_time(CxxTimeTransform const*, CxxRationalTime);

#if defined(__cplusplus)
}
#endif
