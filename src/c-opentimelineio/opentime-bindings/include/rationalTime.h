#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

struct rational_time;
typedef struct rational_time RationalTime;

RationalTime *createRationalTime(double value, double rate);
void deleteRationalTime(RationalTime *rationalTime);
bool is_invalid_time(RationalTime *rationalTime);
double get_value(RationalTime *rationalTime);
double get_rate(RationalTime *rationalTime);
RationalTime *rescaled_to_rate(double new_rate, RationalTime *rationalTime);
RationalTime *rescaled_to_rational_time(RationalTime *scaleRationalTime,
                                        RationalTime *rationalTime);
double value_rescaled_to_rate(double new_rate, RationalTime *rationalTime);
double value_rescaled_to_rational_time(RationalTime *scaleRationalTime,
                                       RationalTime *rationalTime);
bool almost_equal(double delta, RationalTime *rationalTime,
                  RationalTime *rationalTimeOther);
RationalTime *duration_from_start_end_time(RationalTime *start_time,
                                           RationalTime *end_time_exclusive);
bool is_valid_timecode_rate(double rate);
RationalTime *from_frames(double frame, double rate);
RationalTime *from_seconds(double seconds);
/*RationalTime *from_timecode(char *timecode, int timecode_str_length, double rate);*/
/*RationalTime *from_time_string*/
int to_frames(RationalTime *rationalTime);
int to_frames_rescaled(double rate, RationalTime *rationalTime);
double to_seconds(RationalTime *rationalTime);
/*char *to_timecode*/
/*char *to_time_string*/
RationalTime *add_to_first(RationalTime *first, RationalTime *other);
RationalTime *subtract_from_first(RationalTime *first, RationalTime *other);
RationalTime *add(RationalTime *first, RationalTime *second);
RationalTime *subtract(RationalTime *first, RationalTime *second);
bool greater_than(RationalTime *lhs, RationalTime *rhs);
bool greater_than_equals(RationalTime *lhs, RationalTime *rhs);
bool lesser_than(RationalTime *lhs, RationalTime *rhs);
bool lesser_than_equals(RationalTime *lhs, RationalTime *rhs);
bool equals(RationalTime *lhs, RationalTime *rhs);
bool not_equals(RationalTime *lhs, RationalTime *rhs);

#ifdef __cplusplus
}
#endif
