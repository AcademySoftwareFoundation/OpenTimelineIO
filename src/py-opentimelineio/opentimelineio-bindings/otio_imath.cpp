// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include <pybind11/pybind11.h>
#include <pybind11/operators.h>

#include "otio_utils.h"

#include "ImathBox.h"
#include "ImathVec.h"

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
    py::class_<Imath::V2d>(m, "V2d", py::module_local())
        .def(py::init<>())
        .def(py::init<double>())
        .def(py::init<double, double>())
        .def_readwrite("x", &Imath::V2d::x)
        .def_readwrite("y", &Imath::V2d::y)
        .def("__getitem__", [](Imath::V2d const &v, size_t i) {
                return v[i];
            })
        .def("__eq__", [](Imath::V2d lhs, py::object const& rhs) {
                return lhs == _type_checked<Imath::V2d>(rhs, "==");
            })
        .def("__ne__", [](Imath::V2d lhs, py::object const& rhs) {
                return lhs != _type_checked<Imath::V2d>(rhs, "!=");
            })
        .def("__xor__", [](Imath::V2d lhs, py::object const& rhs) {
                return lhs ^ _type_checked<Imath::V2d>(rhs, "^");
            })
        .def("__mod__", [](Imath::V2d lhs, py::object const& rhs) {
                return lhs % _type_checked<Imath::V2d>(rhs, "%");
            })
        .def("__iadd__", [](Imath::V2d lhs, Imath::V2d rhs) {
                return lhs += rhs;
            })
        .def("__isub__", [](Imath::V2d lhs, Imath::V2d rhs) {
                return lhs -= rhs;
            })
        .def("__imul__", [](Imath::V2d lhs, Imath::V2d rhs) {
                return lhs *= rhs;
            })
        .def("__idiv__", [](Imath::V2d lhs, Imath::V2d rhs) {
                return lhs /= rhs;
            })
        .def(py::self - py::self)
        .def(py::self + py::self)
        .def(py::self * py::self)
        .def(py::self / py::self)
        .def("equalWithAbsError", [](Imath::V2d* v, Imath::V2d const & v2, double e) {
                return v->equalWithAbsError(v2, e);
            })
        .def("equalWithRelError", [](Imath::V2d* v, Imath::V2d const & v2, double e) {
                return v->equalWithRelError(v2, e);
            })
        .def("dot", [](Imath::V2d* v, Imath::V2d const & v2) {
                return v->dot(v2);
            })
        .def("cross", [](Imath::V2d* v, Imath::V2d const & v2) {
                return v->cross(v2);
            })
        .def("length", &Imath::V2d::length)
        .def("length2", &Imath::V2d::length2)
        .def("normalize", &Imath::V2d::normalize)
        .def("normalizeExc", &Imath::V2d::normalizeExc)
        .def("normalizeNonNull", &Imath::V2d::normalizeNonNull)
        .def("normalized", &Imath::V2d::normalized)
        .def("normalizedExc", &Imath::V2d::normalizedExc)
        .def("normalizedNonNull", &Imath::V2d::normalizedNonNull)
        .def_static("baseTypeLowest", []() {
                return Imath::V2d::baseTypeLowest();
            })
        .def_static("baseTypeMax", []() {
                return Imath::V2d::baseTypeMax();
            })
        .def_static("baseTypeSmallest", []() {
                return Imath::V2d::baseTypeSmallest();
            })
        .def_static("baseTypeEpsilon", []() {
                return Imath::V2d::baseTypeEpsilon();
            })
        .def_static("dimensions", []() {
                return Imath::V2d::dimensions();
            });

    py::class_<Imath::Box2d>(m, "Box2d", py::module_local())
        .def(py::init<>())
        .def(py::init<Imath::V2d>())
        .def(py::init<Imath::V2d, Imath::V2d>())
        .def_readwrite("min", &Imath::Box2d::min)
        .def_readwrite("max", &Imath::Box2d::max)
        .def("__eq__", [](Imath::Box2d lhs, py::object const& rhs) {
            return lhs == _type_checked<Imath::Box2d>(rhs, "==");
        })
        .def("__ne__", [](Imath::Box2d lhs, py::object const& rhs) {
            return lhs != _type_checked<Imath::Box2d>(rhs, "!=");
        })
        .def("center", &Imath::Box2d::center)
        .def("extendBy", [](Imath::Box2d* box, Imath::V2d const& point ) {
            return box->extendBy(point); 
        })
        .def("extendBy", [](Imath::Box2d* box, Imath::Box2d const& rhs ) {
            return box->extendBy(rhs); 
        })
        .def("intersects", [](Imath::Box2d* box, Imath::V2d const& point ) {
            return box->intersects(point); 
        })
        .def("intersects", [](Imath::Box2d* box, Imath::Box2d const& rhs ) {
            return box->intersects(rhs); 
        });
}

void otio_imath_bindings(py::module m) {
    define_imath_2d(m);
}
