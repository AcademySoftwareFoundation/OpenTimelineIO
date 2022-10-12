#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "nonstd/optional.hpp"

using nonstd::optional;
using nonstd::nullopt_t;

namespace pybind11 { namespace detail {
    // Caster for converting to/from nonstd::optional.
    // Pybind11 supports optional types when C++17 is used.
    // So for now we have to create the casters manually.
    // See https://pybind11.readthedocs.io/en/stable/advanced/cast/stl.html#c-17-library-containers
    template<typename T> struct type_caster<optional<T>>
        : public optional_caster<optional<T>> {};

    template<> struct type_caster<nullopt_t>
        : public void_caster<nullopt_t> {};
}}
