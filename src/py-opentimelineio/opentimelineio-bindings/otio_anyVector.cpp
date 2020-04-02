#include <pybind11/pybind11.h>
#include <pybind11/operators.h>

namespace py = pybind11;
using namespace pybind11::literals;

#include "otio_utils.h"
#include "otio_anyVector.h"
#include "opentime/rationalTime.h"
#include "opentimelineio/stringUtils.h"

void otio_any_vector_bindings(py::module m) {
    py::class_<AnyVectorProxy::Iterator>(m, "AnyVectorIterator")
        .def("__iter__", &AnyVectorProxy::Iterator::iter)
    #if PY_MAJOR_VERSION >= 3
        .def("__next__", &AnyVectorProxy::Iterator::next);
    #else
        .def("next", &AnyVectorProxy::Iterator::next);
    #endif
    
    py::class_<AnyVectorProxy>(m, "AnyVector")
        .def(py::init<>())
        .def("__internal_getitem__", &AnyVectorProxy::get_item, "index"_a)
        .def("__internal_setitem__", &AnyVectorProxy::set_item, "index"_a, "item"_a)
        .def("__internal_delitem__", &AnyVectorProxy::del_item, "index"_a)
        .def("__len__", &AnyVectorProxy::len)
        .def("__internal_insert", &AnyVectorProxy::insert)
        .def("__iter__", &AnyVectorProxy::iter, py::return_value_policy::reference_internal);
}




