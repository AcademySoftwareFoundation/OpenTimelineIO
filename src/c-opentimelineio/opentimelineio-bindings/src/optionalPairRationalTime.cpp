#include "copentimelineio/optionalPairRationalTime.h"
#include <opentime/rationalTime.h>
#include <opentimelineio/optional.h>
#include <utility>

typedef std::pair<
    nonstd::optional<opentime::RationalTime>,
    nonstd::optional<opentime::RationalTime>>
    PairDef;

#ifdef __cplusplus
extern "C"
{
#endif
    OptionalPairRationalTime*
    OptionalPairRationalTime_create(RationalTime* first, RationalTime* second)
    {
        nonstd::optional<opentime::RationalTime> firstRationalTimeOptional =
            nonstd::nullopt;
        nonstd::optional<opentime::RationalTime> secondRationalTimeOptional =
            nonstd::nullopt;
        if(first != NULL)
        {
            firstRationalTimeOptional =
                nonstd::optional<opentime::RationalTime>(
                    *reinterpret_cast<opentime::RationalTime*>(first));
        }
        if(second != NULL)
        {
            secondRationalTimeOptional =
                nonstd::optional<opentime::RationalTime>(
                    *reinterpret_cast<opentime::RationalTime*>(second));
        }
        return reinterpret_cast<OptionalPairRationalTime*>(
            new std::pair<
                nonstd::optional<opentime::RationalTime>,
                nonstd::optional<opentime::RationalTime>>(
                firstRationalTimeOptional, secondRationalTimeOptional));
    }
    RationalTime* OptionalPairRationalTime_first(OptionalPairRationalTime* self)
    {
        nonstd::optional<opentime::RationalTime> rationalTimeOptional =
            reinterpret_cast<PairDef*>(self)->first;
        if(rationalTimeOptional == nonstd::nullopt) return NULL;
        return reinterpret_cast<RationalTime*>(
            new opentime::RationalTime(rationalTimeOptional.value()));
    }
    RationalTime*
    OptionalPairRationalTime_second(OptionalPairRationalTime* self)
    {
        nonstd::optional<opentime::RationalTime> rationalTimeOptional =
            reinterpret_cast<PairDef*>(self)->second;
        if(rationalTimeOptional == nonstd::nullopt) return NULL;
        return reinterpret_cast<RationalTime*>(
            new opentime::RationalTime(rationalTimeOptional.value()));
    }
    void OptionalPairRationalTime_destroy(OptionalPairRationalTime* self)
    {
        delete reinterpret_cast<PairDef*>(self);
    }

#ifdef __cplusplus
}
#endif