#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/operators.h>
#include "nonstd/optional.hpp"

using nonstd::optional;
using nonstd::nullopt_t;

namespace pybind11 { namespace detail {
    template<typename T> struct type_caster<optional<T>>
        : public optional_caster<optional<T>> {};

    template<> struct type_caster<nullopt_t>
        : public void_caster<nullopt_t> {};
}}
