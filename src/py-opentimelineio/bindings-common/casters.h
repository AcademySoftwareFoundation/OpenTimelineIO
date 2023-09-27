#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "nonstd/optional.hpp"

using nonstd::optional;
using nonstd::nullopt_t;

#if __cplusplus < 201703L
namespace pybind11 { namespace detail {
    // Caster for converting to/from nonstd::optional.
    // Pybind11 supports optional types when C++17 is used.
    // So for now we have to create the casters manually. See
    // https://pybind11.readthedocs.io/en/stable/advanced/cast/stl.html#c-17-library-containers
    // ...however, if this is present AFTER c++17, because nonstd::optional
    // becomes std::optional starting in C++17, and Pybind11 already defines
    // casters for std::optional, this becomes a duplicate (and therefore build
    // error).
    // The casters can be removed when C++ versions less than 17 are no longer
    // supported by OTIO.
    template<typename T> struct type_caster<optional<T>>
        : public optional_caster<optional<T>> {};

    template<> struct type_caster<nullopt_t>
        : public void_caster<nullopt_t> {};
}}
#endif
