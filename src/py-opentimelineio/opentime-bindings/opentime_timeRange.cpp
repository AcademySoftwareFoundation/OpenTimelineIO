#include <pybind11/pybind11.h>
#include <pybind11/operators.h>

#include "opentime_bindings.h"
#include "opentime/timeRange.h"
#include "opentime/stringPrintf.h"

namespace py = pybind11;
using namespace pybind11::literals;
using namespace opentime;

void opentime_timeRange_bindings(py::module m) {
    py::class_<TimeRange>(m, "TimeRange")
        .def(py::init<>())
        .def(py::init<RationalTime>(), "start_time"_a)
        .def(py::init<RationalTime, RationalTime>(),
             "start_time"_a = RationalTime(), "duration"_a)
        .def_property_readonly("start_time", &TimeRange::start_time)
        .def_property_readonly("duration", &TimeRange::duration)
        .def("end_time_inclusive", &TimeRange::end_time_inclusive)
        .def("end_time_exclusive", &TimeRange::end_time_exclusive)
        .def("extended_by", &TimeRange::extended_by, "other"_a)
        .def("clamped", (RationalTime (TimeRange::*)(RationalTime) const) &TimeRange::clamped, "other"_a)
        .def("clamped", (TimeRange (TimeRange::*)(TimeRange) const) &TimeRange::clamped, "other"_a)
        .def("contains", (bool (TimeRange::*)(RationalTime) const) &TimeRange::contains, "other"_a)
        .def("contains", (bool (TimeRange::*)(TimeRange) const) &TimeRange::contains, "other"_a)
        .def("overlaps", (bool (TimeRange::*)(RationalTime) const) &TimeRange::overlaps, "other"_a)
        .def("overlaps", (bool (TimeRange::*)(TimeRange) const) &TimeRange::overlaps, "other"_a)
        .def_static("range_from_start_end_time", &TimeRange::range_from_start_end_time,
                    "start_time"_a, "end_time_exclusive"_a)
        .def(py::self == py::self)
        .def(py::self != py::self)        
        .def("__str__", [](TimeRange tr) {
                return string_printf("TimeRange(%s, %s)",
                                     opentime_python_str(tr.start_time()).c_str(),
                                     opentime_python_str(tr.duration()).c_str());

            })
        .def("__repr__", [](TimeRange tr) {
            return string_printf("otio.opentime.TimeRange(start_time=%s, duration=%s)",
                                     opentime_python_repr(tr.start_time()).c_str(),
                                 opentime_python_repr(tr.duration()).c_str());
            })
        ;
}

        
