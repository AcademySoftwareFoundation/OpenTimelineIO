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
