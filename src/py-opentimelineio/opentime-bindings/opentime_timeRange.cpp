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
        // matches the python constructor behavior
        .def(py::init(
                    [](RationalTime* start_time, RationalTime* duration) {
                    if (start_time == nullptr && duration == nullptr) {
                        return TimeRange();
                    } 
                    else if (start_time == nullptr) {
                        return TimeRange(
                            RationalTime(0.0, duration->rate()),
                            *duration
                        );
                    } 
                    // duration == nullptr
                    else if (duration == nullptr) {
                        return TimeRange(
                            *start_time,
                            RationalTime(0.0, start_time->rate())
                        );
                    }
                    else {
                        return TimeRange(*start_time, *duration);
                    }
        }), "start_time"_a=nullptr, "duration"_a=nullptr)
        .def_property_readonly("start_time", &TimeRange::start_time)
        .def_property_readonly("duration", &TimeRange::duration)
        .def("end_time_inclusive", &TimeRange::end_time_inclusive, R"docstring(
The time of the last sample containing data in the TimeRange.

If the TimeRange starts at (0,24) with duration (10,24), this will be 
(9,24)

If the TimeRange starts at (0,24) with duration (10.5, 24): 
(10, 24)

In other words, the last frame with data, even if the last frame is fractional.
)docstring")
        .def("end_time_exclusive", &TimeRange::end_time_exclusive, R"docstring(
Time of the first sample outside the time range.

If Start frame is 10 and duration is 5, then end_time_exclusive is 15,
because the last time with data in this range is 14.

If Start frame is 10 and duration is 5.5, then end_time_exclusive is 
15.5, because the last time with data in this range is 15.
)docstring")
        .def("duration_extended_by", &TimeRange::duration_extended_by, "other"_a)
        .def("extended_by", &TimeRange::extended_by, "other"_a, R"docstring(Construct a new TimeRange that is  this one extended by other.)docstring")
        .def("clamped", (RationalTime (TimeRange::*)(RationalTime) const) &TimeRange::clamped, "other"_a, R"docstring(
Clamp 'other' (RationalTime) according to 
self.start_time/end_time_exclusive and bound arguments.
)docstring")
        .def("clamped", (TimeRange (TimeRange::*)(TimeRange) const) &TimeRange::clamped, "other"_a, R"docstring(
Clamp 'other' (TimeRange) according to
self.start_time/end_time_exclusive and bound arguments.
)docstring")
        .def("contains", (bool (TimeRange::*)(RationalTime) const) &TimeRange::contains, "other"_a, R"docstring(
The start of `this` precedes `other`.
`other` precedes the end of `this`.
::
                    other
                      ↓
                      *
              [      this      ]

)docstring")
        .def("contains", (bool (TimeRange::*)(TimeRange, double) const) &TimeRange::contains, "other"_a, "epsilon_s"_a=opentime::DEFAULT_EPSILON_s, R"docstring(
The start of `this` precedes start of `other`.
The end of `this` antecedes end of `other`.
::

                  [ other ]
             [      this      ]

The converse would be ``other.contains(this)``
)docstring")
        .def("overlaps", (bool (TimeRange::*)(RationalTime) const) &TimeRange::overlaps, "other"_a, R"docstring(
`this` contains `other`.
::
                  other
                   ↓
                   *
             [    this    ]
)docstring")
        .def("overlaps", (bool (TimeRange::*)(TimeRange, double) const) &TimeRange::overlaps, "other"_a, "epsilon_s"_a=opentime::DEFAULT_EPSILON_s, R"docstring(
The start of `this` strictly precedes end of `other` by a value >= `epsilon_s`.
The end of `this` strictly antecedes start of `other` by a value >= `epsilon_s`.
::
             [ this ]
                 [ other ]
The converse would be ``other.overlaps(this)``
)docstring")
        .def("before", (bool (TimeRange::*)(RationalTime, double ) const) &TimeRange::before, "other"_a, "epsilon_s"_a=opentime::DEFAULT_EPSILON_s, R"docstring(
The end of `this` strictly precedes `other` by a value >= `epsilon_s`.
::
                       other
                         ↓
             [ this ]    *
)docstring")
        .def("before", (bool (TimeRange::*)(TimeRange, double) const) &TimeRange::before, "other"_a, "epsilon_s"_a=opentime::DEFAULT_EPSILON_s, R"docstring(
The end of `this` strictly equals the start of `other` and
the start of `this` strictly equals the end of `other`.
::
             [this][other]
The converse would be ``other.meets(this)``
)docstring")
        .def("meets", (bool (TimeRange::*)(TimeRange, double) const) &TimeRange::meets, "other"_a, "epsilon_s"_a=opentime::DEFAULT_EPSILON_s, R"docstring(
The end of `this` strictly equals the start of `other` and
the start of `this` strictly equals the end of `other`.
::
             [this][other]
The converse would be ``other.meets(this)``
)docstring")
        .def("begins", (bool (TimeRange::*)(RationalTime, double) const) &TimeRange::begins, "other"_a, "epsilon_s"_a=opentime::DEFAULT_EPSILON_s, R"docstring(
The start of `this` strictly equals `other`.
::
           other
             ↓
             *
             [ this ]
)docstring")
        .def("begins", (bool (TimeRange::*)(TimeRange, double) const) &TimeRange::begins, "other"_a, "epsilon_s"_a=opentime::DEFAULT_EPSILON_s, R"docstring(
The start of `this` strictly equals the start of `other`.
The end of `this` strictly precedes the end of `other` by a value >= `epsilon_s`.
::
             [ this ]
             [    other    ]
The converse would be ``other.begins(this)``
)docstring")
        .def("finishes", (bool (TimeRange::*)(RationalTime, double) const) &TimeRange::finishes, "other"_a, "epsilon_s"_a=opentime::DEFAULT_EPSILON_s, R"docstring(
The end of `this` strictly equals `other`.
::
                  other
                    ↓
                    *
             [ this ]
)docstring")
        .def("finishes", (bool (TimeRange::*)(TimeRange, double) const) &TimeRange::finishes, "other"_a, "epsilon_s"_a=opentime::DEFAULT_EPSILON_s, R"docstring(
The start of `this` strictly antecedes the start of `other` by a value >= `epsilon_s`.
The end of `this` strictly equals the end of `other`.
::
                     [ this ]
             [     other    ]
The converse would be ``other.finishes(this)``
)docstring")
        .def("intersects", (bool (TimeRange::*)(TimeRange, double) const) &TimeRange::intersects, "other"_a, "epsilon_s"_a=opentime::DEFAULT_EPSILON_s, R"docstring(
The start of `this` precedes or equals the end of `other` by a value >= `epsilon_s`.
The end of `this` antecedes or equals the start of `other` by a value >= `epsilon_s`.
::
        [    this    ]           OR      [    other    ]
             [     other    ]                    [     this    ]
The converse would be ``other.finishes(this)``
)docstring")
        .def("__copy__", [](TimeRange tr) {
                return tr;
            })
        .def("__deepcopy__", [](TimeRange tr, py::object memo) {
                return tr;
            })
        .def_static("range_from_start_end_time", &TimeRange::range_from_start_end_time,
                    "start_time"_a, "end_time_exclusive"_a)
        .def_static("range_from_start_end_time_inclusive", &TimeRange::range_from_start_end_time_inclusive,
                    "start_time"_a, "end_time_inclusive"_a)
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
