#ifdef __cplusplus
extern "C"{
#endif
#include <stdbool.h>
struct      Rational_Time;
typedef     struct RationalTime RationalTime;
enum IsDropFrameRate{
    InferFromRate = -1,
    ForceNo = 0,
    ForceYes = 1,
};
RationalTime* RationalTime_create(double value, double rate);
_Bool RationalTime_is_invalid_time(RationalTime* self);
double RationalTime_value(RationalTime* self);
double RationalTime_rate(RationalTime* self);
RationalTime* RationalTime_rescaled_to(RationalTime* self, double new_rate);
RationalTime* RationalTime_rescaled_to_1(RationalTime* self, RationalTime* rt);
double RationalTime_value_rescaled_to(RationalTime* self, double new_rate);
double RationalTime_value_rescaled_to_1(RationalTime* self, RationalTime* rt);
_Bool RationalTime_almost_equal(RationalTime* self, RationalTime* other, double delta);
RationalTime* RationalTime_duration_from_start_end_time(RationalTime* self, RationalTime* start_time, RationalTime* end_time_exclusive);
_Bool RationalTime_is_valid_timecode_rate(RationalTime* self, double rate);
RationalTime* RationalTime_from_frames(RationalTime* self, double frame, double rate);
RationalTime* RationalTime_from_seconds(RationalTime* self, double seconds);
/*RationalTime* RationalTime_from_timecode(RationalTime* self,  timecode, double rate, ErrorStatus* error_status);*/
/*RationalTime* RationalTime_from_time_string(RationalTime* self,  time_string, double rate, ErrorStatus* error_status);*/
int RationalTime_to_frames(RationalTime* self);
int RationalTime_to_frames_1(RationalTime* self, double rate);
double RationalTime_to_seconds(RationalTime* self);
/*int RationalTime_to_timecode(RationalTime* self, double rate,  drop_frame, ErrorStatus* error_status);*/
/*int RationalTime_to_timecode_1(RationalTime* self, ErrorStatus* error_status);*/
/*int RationalTime_to_time_string(RationalTime* self);*/
void RationalTime_destroy(RationalTime* self);
#ifdef __cplusplus
}
#endif
