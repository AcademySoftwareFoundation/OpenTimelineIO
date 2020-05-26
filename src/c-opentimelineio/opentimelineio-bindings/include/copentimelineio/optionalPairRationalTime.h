#pragma once

#include "copentime/rationalTime.h"

#ifdef __cplusplus
extern "C"
{
#endif
    struct OptionalPairRationalTime;
    typedef struct OptionalPairRationalTime OptionalPairRationalTime;

    OptionalPairRationalTime*
    OptionalPairRationalTime_create(RationalTime* first, RationalTime* second);
    RationalTime*
    OptionalPairRationalTime_first(OptionalPairRationalTime* self);
    RationalTime*
         OptionalPairRationalTime_second(OptionalPairRationalTime* self);
    void OptionalPairRationalTime_destroy(OptionalPairRationalTime* self);

#ifdef __cplusplus
}
#endif
