#ifndef OTIO_ANYVECTOR_H
#define OTIO_ANYVECTOR_H

#include "any.hpp"
#include <vector>
#include <assert.h>

/*
 * A AnyVector has exactly the same API as
 *    std::vector<any>
 *
 * except that it records a "time-stamp" that
 * lets external observers know when the map has been destroyed (which includes
 * the case of the map being relocated in memory).
 *
 * This allows us to hand out iterators that can be aware of moves
 * and take steps to safe-guard themselves from causing a crash.
 */

class AnyVector : private std::vector<any> {
public:
    /* A boat-load of "using" calls that expose the API of std::vector. */
    using map::map;
    ...
};

#endif
