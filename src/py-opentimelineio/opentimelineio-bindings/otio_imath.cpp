// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include <pybind11/pybind11.h>
#include <pybind11/operators.h>

#include "otio_utils.h"

#include "Imath/ImathBox.h"
#include "Imath/ImathVec.h"

namespace py = pybind11;

template <typename CLASS>
CLASS _type_checked(py::object const& rhs, char const* op) {
    try {
        return py::cast<CLASS>(rhs);
    }
    catch (...) {
        std::string rhs_type = py::cast<std::string>(rhs.get_type().attr("__name__"));
        throw py::type_error(string_printf("Unsupported operand type(s) for %s: "
                                           "%s and %s", typeid(CLASS).name(), op, rhs_type.c_str()));
    }
}

static void define_imath_2d(py::module m) {
    // Note that module_local is used to avoid issues when
    // Imath classes are binded with Pybind11 more than once.
    // Using module_local will avoid conflicts in such cases.
    py::class_<IMATH_NAMESPACE::V2d>(m, "V2d", py::module_local())
        .def(py::init<>([]() { return IMATH_NAMESPACE::V2d(0.0, 0.0); }))
        .def(py::init<double>())
        .def(py::init<double, double>())
        .def_readwrite("x", &IMATH_NAMESPACE::V2d::x)
        .def_readwrite("y", &IMATH_NAMESPACE::V2d::y)
        .def("__getitem__", [](IMATH_NAMESPACE::V2d const &v, size_t i) {
                return v[i];
            })
        .def("__eq__", [](IMATH_NAMESPACE::V2d lhs, py::object const& rhs) {
                return lhs == _type_checked<IMATH_NAMESPACE::V2d>(rhs, "==");
            })
        .def("__ne__", [](IMATH_NAMESPACE::V2d lhs, py::object const& rhs) {
                return lhs != _type_checked<IMATH_NAMESPACE::V2d>(rhs, "!=");
            })
        .def("__xor__", [](IMATH_NAMESPACE::V2d lhs, py::object const& rhs) {
                return lhs ^ _type_checked<IMATH_NAMESPACE::V2d>(rhs, "^");
            })
        .def("__mod__", [](IMATH_NAMESPACE::V2d lhs, py::object const& rhs) {
                return lhs % _type_checked<IMATH_NAMESPACE::V2d>(rhs, "%");
            })
        .def("__iadd__", [](IMATH_NAMESPACE::V2d lhs, IMATH_NAMESPACE::V2d rhs) {
                return lhs += rhs;
            })
        .def("__isub__", [](IMATH_NAMESPACE::V2d lhs, IMATH_NAMESPACE::V2d rhs) {
                return lhs -= rhs;
            })
        .def("__imul__", [](IMATH_NAMESPACE::V2d lhs, IMATH_NAMESPACE::V2d rhs) {
                return lhs *= rhs;
            })
        .def("__idiv__", [](IMATH_NAMESPACE::V2d lhs, IMATH_NAMESPACE::V2d rhs) {
                return lhs /= rhs;
            })
        .def(py::self - py::self)
        .def(py::self + py::self)
        .def(py::self * py::self)
        .def(py::self / py::self)
        .def("equalWithAbsError", [](IMATH_NAMESPACE::V2d* v, IMATH_NAMESPACE::V2d const & v2, double e) {
                return v->equalWithAbsError(v2, e);
            })
        .def("equalWithRelError", [](IMATH_NAMESPACE::V2d* v, IMATH_NAMESPACE::V2d const & v2, double e) {
                return v->equalWithRelError(v2, e);
            })
        .def("dot", [](IMATH_NAMESPACE::V2d* v, IMATH_NAMESPACE::V2d const & v2) {
                return v->dot(v2);
            })
        .def("cross", [](IMATH_NAMESPACE::V2d* v, IMATH_NAMESPACE::V2d const & v2) {
                return v->cross(v2);
            })
        .def("length", &IMATH_NAMESPACE::V2d::length)
        .def("length2", &IMATH_NAMESPACE::V2d::length2)
        .def("normalize", &IMATH_NAMESPACE::V2d::normalize)
        .def("normalizeExc", &IMATH_NAMESPACE::V2d::normalizeExc)
        .def("normalizeNonNull", &IMATH_NAMESPACE::V2d::normalizeNonNull)
        .def("normalized", &IMATH_NAMESPACE::V2d::normalized)
        .def("normalizedExc", &IMATH_NAMESPACE::V2d::normalizedExc)
        .def("normalizedNonNull", &IMATH_NAMESPACE::V2d::normalizedNonNull)
        .def_static("baseTypeLowest", []() {
                return IMATH_NAMESPACE::V2d::baseTypeLowest();
            })
        .def_static("baseTypeMax", []() {
                return IMATH_NAMESPACE::V2d::baseTypeMax();
            })
        .def_static("baseTypeSmallest", []() {
                return IMATH_NAMESPACE::V2d::baseTypeSmallest();
            })
        .def_static("baseTypeEpsilon", []() {
                return IMATH_NAMESPACE::V2d::baseTypeEpsilon();
            })
        .def_static("dimensions", []() {
                return IMATH_NAMESPACE::V2d::dimensions();
            });

    py::class_<IMATH_NAMESPACE::Box2d>(m, "Box2d", py::module_local())
        .def(py::init<>([]() { return IMATH_NAMESPACE::Box2d(IMATH_NAMESPACE::V2d(0.0, 0.0)); }))
        .def(py::init<IMATH_NAMESPACE::V2d>())
        .def(py::init<IMATH_NAMESPACE::V2d, IMATH_NAMESPACE::V2d>())
        .def_readwrite("min", &IMATH_NAMESPACE::Box2d::min)
        .def_readwrite("max", &IMATH_NAMESPACE::Box2d::max)
        .def("__eq__", [](IMATH_NAMESPACE::Box2d lhs, py::object const& rhs) {
            return lhs == _type_checked<IMATH_NAMESPACE::Box2d>(rhs, "==");
        })
        .def("__ne__", [](IMATH_NAMESPACE::Box2d lhs, py::object const& rhs) {
            return lhs != _type_checked<IMATH_NAMESPACE::Box2d>(rhs, "!=");
        })
        .def("center", &IMATH_NAMESPACE::Box2d::center)
        .def("extendBy", [](IMATH_NAMESPACE::Box2d* box, IMATH_NAMESPACE::V2d const& point ) {
            return box->extendBy(point); 
        })
        .def("extendBy", [](IMATH_NAMESPACE::Box2d* box, IMATH_NAMESPACE::Box2d const& rhs ) {
            return box->extendBy(rhs); 
        })
        .def("intersects", [](IMATH_NAMESPACE::Box2d* box, IMATH_NAMESPACE::V2d const& point ) {
            return box->intersects(point); 
        })
        .def("intersects", [](IMATH_NAMESPACE::Box2d* box, IMATH_NAMESPACE::Box2d const& rhs ) {
            return box->intersects(rhs); 
        });
}

void otio_imath_bindings(py::module m) {
    define_imath_2d(m);
}
