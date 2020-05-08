#include <stdlib.h>

#include <opentime/rationalTime.h>
#include "rationalTime.h"

struct rational_time {
    void *obj;
};

RationalTime *createRationalTime(double value, double rate) {
    RationalTime *rationalTime;
    opentime::RationalTime *obj;

    rationalTime = (typeof(rationalTime)) malloc(sizeof(*rationalTime));
    obj = new opentime::RationalTime(value, rate);
    rationalTime->obj = obj;
    return rationalTime;
}

void deleteRationalTime(RationalTime *rationalTime) {
    if (rationalTime == NULL) return;
    delete static_cast<RationalTime *>(rationalTime->obj);
    free(rationalTime);
    rationalTime = NULL;
}

bool is_invalid_time(RationalTime *rationalTime) {
    opentime::RationalTime *rationalTimeObj;
    if (rationalTime == NULL) return true;
    rationalTimeObj = static_cast<opentime::RationalTime *>(rationalTime->obj);
    return rationalTimeObj->is_invalid_time();
}

double get_value(RationalTime *rationalTime) {
    opentime::RationalTime *rationalTimeObj;
    if (rationalTime == NULL) return 0;
    rationalTimeObj = static_cast<opentime::RationalTime *>(rationalTime->obj);
    return rationalTimeObj->value();
}

double get_rate(RationalTime *rationalTime) {
    opentime::RationalTime *rationalTimeObj;
    if (rationalTime == NULL) return 0;
    rationalTimeObj = static_cast<opentime::RationalTime *>(rationalTime->obj);
    return rationalTimeObj->rate();
}

RationalTime *rescaled_to_rate(double new_rate, RationalTime *rationalTime) {
    opentime::RationalTime *rationalTimeObj;
    if (rationalTime == NULL) return NULL;
    rationalTimeObj = static_cast<opentime::RationalTime *>(rationalTime->obj);
    double rescaledValue = rationalTimeObj->value_rescaled_to(new_rate);
    RationalTime *rescaledRationalTime = createRationalTime(rescaledValue, new_rate);
    return rescaledRationalTime;
}

RationalTime *rescaled_to_rational_time(RationalTime *scaleRationalTime, RationalTime *rationalTime) {
    opentime::RationalTime *rationalTimeObj;
    opentime::RationalTime *scaleRationalTimeObj;
    if (rationalTime == NULL || scaleRationalTime == NULL) return NULL;
    rationalTimeObj = static_cast<opentime::RationalTime *>(rationalTime->obj);
    scaleRationalTimeObj = static_cast<opentime::RationalTime *>(scaleRationalTime->obj);
    opentime::RationalTime rescaledRationalTime = rationalTimeObj->rescaled_to(*scaleRationalTimeObj);
    return createRationalTime(rescaledRationalTime.value(), rescaledRationalTime.rate());
}

double value_rescaled_to_rate(double new_rate, RationalTime *rationalTime) {
    opentime::RationalTime *rationalTimeObj;
    if (rationalTime == NULL) return 0;
    rationalTimeObj = static_cast<opentime::RationalTime *>(rationalTime->obj);
    return rationalTimeObj->value_rescaled_to(new_rate);
}

double value_rescaled_to_rational_time(RationalTime *scaleRationalTime, RationalTime *rationalTime) {
    opentime::RationalTime *scaleRationalTimeObj;
    if (rationalTime == NULL || scaleRationalTime == NULL) return 0;
    scaleRationalTimeObj = static_cast<opentime::RationalTime *>(scaleRationalTime->obj);
    return value_rescaled_to_rate(scaleRationalTimeObj->rate(), rationalTime);
}

bool almost_equal(double delta, RationalTime *rationalTime, RationalTime *rationalTimeOther) {
    opentime::RationalTime *rationalTimeObj;
    opentime::RationalTime *rationalTimeOtherObj;
    if (rationalTime == NULL || rationalTimeOther == NULL) return false;
    rationalTimeObj = static_cast<opentime::RationalTime *>(rationalTime->obj);
    rationalTimeOtherObj = static_cast<opentime::RationalTime *>(rationalTimeOther->obj);
    return rationalTimeObj->almost_equal(*rationalTimeOtherObj, delta);
}

RationalTime *duration_from_start_end_time(RationalTime *start_time, RationalTime *end_time_exclusive) {
    opentime::RationalTime *startTimeObj;
    opentime::RationalTime *endTimeExclusiveObj;
    if (start_time == NULL || end_time_exclusive == NULL) return NULL;
    startTimeObj = static_cast<opentime::RationalTime *>(start_time->obj);
    endTimeExclusiveObj = static_cast<opentime::RationalTime *>(end_time_exclusive->obj);
    opentime::RationalTime newRationalTime = opentime::RationalTime::duration_from_start_end_time(*startTimeObj,
                                                                                        *endTimeExclusiveObj);
    return createRationalTime(newRationalTime.value(), newRationalTime.rate());
}

bool is_valid_timecode(double rate){
    return opentime::RationalTime::is_valid_timecode_rate(rate);
}

RationalTime *from_frames(double frame, double rate){
    opentime::RationalTime rationalTime = opentime::RationalTime::from_frames(frame, rate);
    return createRationalTime(rationalTime.value(), rationalTime.rate());
}

RationalTime *from_seconds(double seconds){
    opentime::RationalTime rationalTime = opentime::RationalTime::from_seconds(seconds);
    return createRationalTime(rationalTime.value(), rationalTime.rate());
}

int to_frames(RationalTime *rationalTime) {
    opentime::RationalTime *rationalTimeObj;
    if (rationalTime == NULL) return 0;
    rationalTimeObj = static_cast<opentime::RationalTime *>(rationalTime->obj);
    return rationalTimeObj->to_frames();
}

int to_frames_rescaled(double rate, RationalTime *rationalTime){
    opentime::RationalTime *rationalTimeObj;
    if (rationalTime == NULL) return 0;
    rationalTimeObj = static_cast<opentime::RationalTime *>(rationalTime->obj);
    return rationalTimeObj->to_frames(rate);
}

double to_seconds(RationalTime *rationalTime){
    opentime::RationalTime *rationalTimeObj;
    if (rationalTime == NULL) return 0;
    rationalTimeObj = static_cast<opentime::RationalTime *>(rationalTime->obj);
    return rationalTimeObj->to_seconds();
}

RationalTime *add_to_first(RationalTime *first, RationalTime *other){
    opentime::RationalTime *firstTimeObj;
    opentime::RationalTime *otherTimeObj;
    if (first == NULL || other == NULL) return NULL;
    firstTimeObj = static_cast<opentime::RationalTime *>(first->obj);
    otherTimeObj = static_cast<opentime::RationalTime *>(other->obj);
    *firstTimeObj += *otherTimeObj;
    return first;
}

RationalTime *subtract_from_first(RationalTime *first, RationalTime *other){
    opentime::RationalTime *firstTimeObj;
    opentime::RationalTime *otherTimeObj;
    if (first == NULL || other == NULL) return NULL;
    firstTimeObj = static_cast<opentime::RationalTime *>(first->obj);
    otherTimeObj = static_cast<opentime::RationalTime *>(other->obj);
    *firstTimeObj -= *otherTimeObj;
    return first;
}

RationalTime *add(RationalTime *first, RationalTime *second){
    opentime::RationalTime *firstTimeObj;
    opentime::RationalTime *secondTimeObj;
    if (first == NULL || second == NULL) return NULL;
    firstTimeObj = static_cast<opentime::RationalTime *>(first->obj);
    secondTimeObj = static_cast<opentime::RationalTime *>(second->obj);
    opentime::RationalTime result = *firstTimeObj + *secondTimeObj;
    return createRationalTime(result.value(), result.rate());
}

RationalTime *subtract(RationalTime *first, RationalTime *second){
    opentime::RationalTime *firstTimeObj;
    opentime::RationalTime *secondTimeObj;
    if (first == NULL || second == NULL) return NULL;
    firstTimeObj = static_cast<opentime::RationalTime *>(first->obj);
    secondTimeObj = static_cast<opentime::RationalTime *>(second->obj);
    opentime::RationalTime result = *firstTimeObj - *secondTimeObj;
    return createRationalTime(result.value(), result.rate());
}

bool greater_than(RationalTime *lhs, RationalTime *rhs){
    opentime::RationalTime *lhsTimeObj;
    opentime::RationalTime *rhsTimeObj;
    if (lhs == NULL || rhs == NULL) return false;
    lhsTimeObj = static_cast<opentime::RationalTime *>(lhs->obj);
    rhsTimeObj = static_cast<opentime::RationalTime *>(rhs->obj);
    return *lhsTimeObj > *rhsTimeObj;
}

bool greater_than_equals(RationalTime *lhs, RationalTime *rhs){
    opentime::RationalTime *lhsTimeObj;
    opentime::RationalTime *rhsTimeObj;
    if (lhs == NULL || rhs == NULL) return false;
    lhsTimeObj = static_cast<opentime::RationalTime *>(lhs->obj);
    rhsTimeObj = static_cast<opentime::RationalTime *>(rhs->obj);
    return *lhsTimeObj >= *rhsTimeObj;
}
bool lesser_than(RationalTime *lhs, RationalTime *rhs){
    opentime::RationalTime *lhsTimeObj;
    opentime::RationalTime *rhsTimeObj;
    if (lhs == NULL || rhs == NULL) return false;
    lhsTimeObj = static_cast<opentime::RationalTime *>(lhs->obj);
    rhsTimeObj = static_cast<opentime::RationalTime *>(rhs->obj);
    return *lhsTimeObj < *rhsTimeObj;
}
bool lesser_than_equals(RationalTime *lhs, RationalTime *rhs){
    opentime::RationalTime *lhsTimeObj;
    opentime::RationalTime *rhsTimeObj;
    if (lhs == NULL || rhs == NULL) return false;
    lhsTimeObj = static_cast<opentime::RationalTime *>(lhs->obj);
    rhsTimeObj = static_cast<opentime::RationalTime *>(rhs->obj);
    return *lhsTimeObj <= *rhsTimeObj;
}
bool equals(RationalTime *lhs, RationalTime *rhs){
    opentime::RationalTime *lhsTimeObj;
    opentime::RationalTime *rhsTimeObj;
    if (lhs == NULL || rhs == NULL) return false;
    lhsTimeObj = static_cast<opentime::RationalTime *>(lhs->obj);
    rhsTimeObj = static_cast<opentime::RationalTime *>(rhs->obj);
    return *lhsTimeObj == *rhsTimeObj;
}
bool not_equals(RationalTime *lhs, RationalTime *rhs){
    opentime::RationalTime *lhsTimeObj;
    opentime::RationalTime *rhsTimeObj;
    if (lhs == NULL || rhs == NULL) return false;
    lhsTimeObj = static_cast<opentime::RationalTime *>(lhs->obj);
    rhsTimeObj = static_cast<opentime::RationalTime *>(rhs->obj);
    return *lhsTimeObj != *rhsTimeObj;
}