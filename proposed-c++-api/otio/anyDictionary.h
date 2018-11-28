#ifndef OTIO_ANYDICTIONARY_H
#define OTIO_ANYDICTIONARY_H

#include "any.hpp"
#include <map>
#include <string>

/*
 * A AnyDictionary has exactly the same API as
 *    std::map<std::string, any>
 *
 * except that it records a "time-stamp" that bumps monotonically every time an
 * operation that would invalidate iterators is performed.
 * (This happens for operator=, clear, erase, insert, swap).  The stamp also
 * lets external observers know when the map has been destroyed (which includes
 * the case of the map being relocated in memory).
 *
 * This allows us to hand out iterators that can be aware of mutation and moves
 * and take steps to safe-guard themselves from causing a crash.  (Yes,
 * I'm talking to you, Python...)
 */
class AnyDictionary : private std::map<std::string, any> {
public:
    /* A boat-load of "using" calls that expose the API of std::map. */
    using map::map;
    ...
};

#endif
