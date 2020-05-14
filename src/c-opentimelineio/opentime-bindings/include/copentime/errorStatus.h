#ifdef __cplusplus
extern "C" {
#endif
#include <stdbool.h>
struct ErrorStatus;
typedef struct ErrorStatus ErrorStatus;


typedef enum {
    OK = 0,
    INVALID_TIMECODE_RATE = 1,
    NON_DROPFRAME_RATE = 2,
    INVALID_TIMECODE_STRING = 3,
    INVALID_TIME_STRING = 4,
    TIMECODE_RATE_MISMATCH = 5,
    NEGATIVE_VALUE = 6,
    INVALID_RATE_FOR_DROP_FRAME_TIMECODE = 7,
} Outcome_;
typedef int Outcome;
ErrorStatus *ErrorStatus_create();
ErrorStatus *ErrorStatus_create_1(Outcome in_outcome);
ErrorStatus *ErrorStatus_create_2(Outcome in_outcome, const char *in_details);
const char *ErrorStatus_outcome_to_string(ErrorStatus *self, Outcome var1);
void ErrorStatus_destroy(ErrorStatus *self);
#ifdef __cplusplus
}
#endif
