// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include <pybind11/pybind11.h>
#include <pybind11/operators.h>

namespace py = pybind11;
using namespace pybind11::literals;

#include "otio_bindings.h"
#include "otio_anyDictionary.h"
#include "otio_anyVector.h"
#include "opentime/rationalTime.h"
#include "opentime/timeRange.h"
#include "opentime/timeTransform.h"
#include "opentimelineio/serializableObject.h"
#include "opentimelineio/stringUtils.h"

// namespace pybind11 { namespace detail {
//     template<> struct type_caster<AnyDictionaryProxy> {
//     public:
//         /**
//          * This macro establishes the name 'AnyDictionaryProxy' in
//          * function signatures and declares a local variable
//          * 'value' of type inty
//          */
//         PYBIND11_TYPE_CASTER(AnyDictionaryProxy, const_name("AnyDictionaryProxy"));

//         /**
//          * Conversion part 1 (Python->C++): convert a PyObject into an AnyDictionaryProxy
//          * instance or return false upon failure. The second argument
//          * indicates whether implicit conversions should be applied.
//          */
//         bool load(handle src, bool) {
//             // Extract PyObject from handle
//             PyObject *source = src.ptr();

//             if (!PyDict_Check(source)) {
//                 return false;
//             }

//             // Now try to convert into a C++ int
//             // value.long_value = PyLong_AsLong(tmp);
//             PyObject *key, *value;
//             Py_ssize_t pos = 0;

//             while (PyDict_Next(source, &pos, &key, &value)) {
//                 long i = PyLong_AsLong(value);
//                 if (i == -1 && PyErr_Occurred()) {
//                     return -1;
//                 }

//                 PyObject *o = PyLong_FromLong(i + 1);
//                 if (o == NULL)
//                     return -1;

//                 if (PyDict_SetItem(source, key, o) < 0) {
//                     Py_DECREF(o);
//                     return -1;
//                 }

//                 Py_DECREF(o);
//             }

//             /// Ensure return code was OK (to avoid out-of-range errors etc)
//             return !PyErr_Occurred();
//         }

//         /**
//          * Conversion part 2 (C++ -> Python): convert an AnyDictionaryProxy instance into
//          * a Python object. The second and third arguments are used to
//          * indicate the return value policy and parent object (for
//          * ``return_value_policy::reference_internal``) and are generally
//          * ignored by implicit casters.
//          */
//         // static handle cast(AnyDictionaryProxy src, return_value_policy /* policy */, handle /* parent */) {
//         //     return PyLong_FromLong(src.long_value);
//     };
// }}

void otio_any_dictionary_bindings(py::module m) {
    py::class_<AnyDictionaryProxy::Iterator>(m, "AnyDictionaryIterator")
        .def("__iter__", &AnyDictionaryProxy::Iterator::iter)
        .def("__next__", &AnyDictionaryProxy::Iterator::next);

    py::class_<AnyDictionaryProxy>(m, "AnyDictionary")
        .def(py::init<>())
        .def("__getitem__", &AnyDictionaryProxy::get_item, "key"_a)
        .def("__internal_setitem__", &AnyDictionaryProxy::set_item, "key"_a, "item"_a)
        .def("__delitem__", &AnyDictionaryProxy::del_item, "key"_a)
        .def("__len__", &AnyDictionaryProxy::len)
        .def("__iter__", &AnyDictionaryProxy::iter, py::return_value_policy::reference_internal);
}
