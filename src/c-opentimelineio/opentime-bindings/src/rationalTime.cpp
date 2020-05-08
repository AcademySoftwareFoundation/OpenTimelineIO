#include "rationalTime.h"
#include <opentime/rationalTime.h>

#ifdef __cplusplus
extern "C"{
#endif
RationalTime* RationalTime_create(double value, double rate){
    return reinterpret_cast<RationalTime*>( new opentime::RationalTime(value, rate));
}
_Bool RationalTime_is_invalid_time(RationalTime* self){
    return reinterpret_cast<opentime::RationalTime*>(self)->is_invalid_time();
}
double RationalTime_value(RationalTime* self){
    return reinterpret_cast<opentime::RationalTime*>(self)->value();
}
double RationalTime_rate(RationalTime* self){
    return reinterpret_cast<opentime::RationalTime*>(self)->rate();
}
RationalTime* RationalTime_rescaled_to(RationalTime* self, double new_rate){
    opentime::RationalTime obj = reinterpret_cast<opentime::RationalTime*>(self)->rescaled_to(new_rate);
    return reinterpret_cast<RationalTime*>(new opentime::RationalTime(obj));
}
RationalTime* RationalTime_rescaled_to_1(RationalTime* self, RationalTime* rt){
    opentime::RationalTime obj = reinterpret_cast<opentime::RationalTime*>(self)->rescaled_to(*reinterpret_cast<opentime::RationalTime*>(rt));
    return reinterpret_cast<RationalTime*>(new opentime::RationalTime(obj));
}
double RationalTime_value_rescaled_to(RationalTime* self, double new_rate){
    return reinterpret_cast<opentime::RationalTime*>(self)->value_rescaled_to(new_rate);
}
double RationalTime_value_rescaled_to_1(RationalTime* self, RationalTime* rt){
    return reinterpret_cast<opentime::RationalTime*>(self)->value_rescaled_to(*reinterpret_cast<opentime::RationalTime*>(rt));
}
_Bool RationalTime_almost_equal(RationalTime* self, RationalTime* other, double delta){
    return reinterpret_cast<opentime::RationalTime*>(self)->almost_equal(*reinterpret_cast<opentime::RationalTime*>(other), delta);
}
RationalTime* RationalTime_duration_from_start_end_time(RationalTime* self, RationalTime* start_time, RationalTime* end_time_exclusive){
    opentime::RationalTime obj = reinterpret_cast<opentime::RationalTime*>(self)->duration_from_start_end_time(*reinterpret_cast<opentime::RationalTime*>(start_time), *reinterpret_cast<opentime::RationalTime*>(end_time_exclusive));
    return reinterpret_cast<RationalTime*>(new opentime::RationalTime(obj));
}
_Bool RationalTime_is_valid_timecode_rate(RationalTime* self, double rate){
    return opentime::RationalTime::is_valid_timecode_rate(rate);
}
RationalTime* RationalTime_from_frames(RationalTime* self, double frame, double rate){
    opentime::RationalTime obj = reinterpret_cast<opentime::RationalTime*>(self)->from_frames(frame, rate);
    return reinterpret_cast<RationalTime*>(new opentime::RationalTime(obj));
}
RationalTime* RationalTime_from_seconds(RationalTime* self, double seconds){
    opentime::RationalTime obj = reinterpret_cast<opentime::RationalTime*>(self)->from_seconds(seconds);
    return reinterpret_cast<RationalTime*>(new opentime::RationalTime(obj));
}
/*RationalTime* RationalTime_from_timecode(RationalTime* self, const char* timecode, double rate, ErrorStatus* error_status){
    opentime::RationalTime obj = reinterpret_cast<opentime::RationalTime*>(self)->from_timecode(timecode, rate, error_status);
    return reinterpret_cast<RationalTime*>(new opentime::RationalTime(obj));
}*/
/*RationalTime* RationalTime_from_time_string(RationalTime* self, const char* time_string, double rate, ErrorStatus* error_status){
    opentime::RationalTime obj = reinterpret_cast<opentime::RationalTime*>(self)->from_time_string(time_string, rate, error_status);
    return reinterpret_cast<RationalTime*>(new opentime::RationalTime(obj));
}*/
int RationalTime_to_frames(RationalTime* self){
    return reinterpret_cast<opentime::RationalTime*>(self)->to_frames();
}
int RationalTime_to_frames_1(RationalTime* self, double rate){
    return reinterpret_cast<opentime::RationalTime*>(self)->to_frames(rate);
}
double RationalTime_to_seconds(RationalTime* self){
    return reinterpret_cast<opentime::RationalTime*>(self)->to_seconds();
}
/*const char* RationalTime_to_timecode(RationalTime* self, double rate,  drop_frame, ErrorStatus* error_status){
    return reinterpret_cast<const char*>(reinterpret_cast<opentime::RationalTime*>(self)->to_timecode(rate, drop_frame, error_status));
}*/
/*const char* RationalTime_to_timecode_1(RationalTime* self, ErrorStatus* error_status){
    return reinterpret_cast<const char*>(reinterpret_cast<opentime::RationalTime*>(self)->to_timecode(error_status));
}*/
/*const char* RationalTime_to_time_string(RationalTime* self){
    return reinterpret_cast<const char*>(reinterpret_cast<opentime::RationalTime*>(self)->to_time_string());
}*/
void RationalTime_destroy(RationalTime* self){
     delete reinterpret_cast<opentime::RationalTime*>(self);
}
#ifdef __cplusplus
}
#endif
