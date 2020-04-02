#include <pybind11/pybind11.h>
#include <pybind11/operators.h>

#include "opentime_bindings.h"
#include "opentime/timeTransform.h"
#include "opentimelineio/stringUtils.h"

namespace py = pybind11;
using namespace pybind11::literals;
using namespace opentime;

void opentime_timeTransform_bindings(py::module m) {
    py::class_<TimeTransform>(m, "TimeTransform")
        .def(py::init<RationalTime, double, double>(),
             "offset"_a = RationalTime(), "scale"_a = 1, "rate"_a = -1)
        .def_property_readonly("offset", &TimeTransform::offset)
        .def_property_readonly("scale", &TimeTransform::scale)
        .def_property_readonly("rate", &TimeTransform::rate)
        .def("applied_to", (TimeRange (TimeTransform::*)(TimeRange) const) &TimeTransform::applied_to, "other"_a)
        .def("applied_to", (TimeTransform (TimeTransform::*)(TimeTransform) const) &TimeTransform::applied_to, "other"_a)
        .def("applied_to", (RationalTime (TimeTransform::*)(RationalTime) const) &TimeTransform::applied_to, "other"_a)
        .def("__copy__", [](TimeTransform const& tt) {
                return tt;
            })
        .def("__deepcopy__", [](TimeTransform const& tt) {
                return tt;
            })
        .def(py::self == py::self)
        .def(py::self != py::self)
        .def("__str__", [](TimeTransform tt) {
                return string_printf("TimeTransform(%s, %g, %g)",
                                     opentime_python_str(tt.offset()).c_str(),
                                     tt.scale(), tt.rate());

            })
        .def("__repr__", [](TimeTransform tt) {
            return string_printf("otio.opentime.TimeTransform(offset=%s, scale=%g, rate=%g)",
                                 opentime_python_repr(tt.offset()).c_str(), tt.scale(), tt.rate());
            })
        ;
}

        
