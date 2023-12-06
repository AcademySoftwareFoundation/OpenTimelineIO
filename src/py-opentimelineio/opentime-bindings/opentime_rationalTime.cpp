// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include <pybind11/pybind11.h>
#include <pybind11/operators.h>

#include "opentime/rationalTime.h"
#include "opentimelineio/stringUtils.h"
#include "opentimelineio/optional.h"
#include "py-opentimelineio/bindings-common/casters.h"

namespace py = pybind11;
using namespace pybind11::literals;

using namespace opentime;

namespace {
struct ErrorStatusConverter {
    operator ErrorStatus* () {
        return &error_status;
    }

    ~ErrorStatusConverter() noexcept(false) {
        namespace py = pybind11;
        if (is_error(error_status)) {
            throw py::value_error(error_status.details);
        }
    }

    ErrorStatus error_status;
};

IsDropFrameRate df_enum_converter(optional<bool>& df) {
    if (!df.has_value()) {
        return IsDropFrameRate::InferFromRate;
    } else if (df.value()) {
        return IsDropFrameRate::ForceYes;
    } else {
        return IsDropFrameRate::ForceNo;
    }
}
}

std::string opentime_python_str(RationalTime rt) {
    return string_printf("RationalTime(%g, %g)", rt.value(), rt.rate());
}

std::string opentime_python_repr(RationalTime rt) {
    return string_printf("otio.opentime.RationalTime(value=%g, rate=%g)", rt.value(), rt.rate());
}

RationalTime _type_checked(py::object const& rhs, char const* op) {
    try {
        return py::cast<RationalTime>(rhs);
    }
    catch (...) {
        std::string rhs_type = py::cast<std::string>(py::type::of(rhs).attr("__name__"));
        throw py::type_error(string_printf("unsupported operand type(s) for %s: "
                                           "RationalTime and %s", op, rhs_type.c_str()));
    }
}

void opentime_rationalTime_bindings(py::module m) {
    py::class_<RationalTime>(m, "RationalTime", R"docstring(
The RationalTime class represents a measure of time of :math:`rt.value/rt.rate` seconds.
It can be rescaled into another :class:`~RationalTime`'s rate.
)docstring")
        .def(py::init<double, double>(), "value"_a = 0, "rate"_a = 1)
        .def("is_invalid_time", &RationalTime::is_invalid_time, R"docstring(
Returns true if the time is invalid. The time is considered invalid if the value or the rate are a NaN value
or if the rate is less than or equal to zero.
)docstring")
        .def_property_readonly("value", &RationalTime::value)
        .def_property_readonly("rate", &RationalTime::rate)
        .def("rescaled_to", (RationalTime (RationalTime::*)(double) const) &RationalTime::rescaled_to,
             "new_rate"_a, R"docstring(Returns the time value for time converted to new_rate.)docstring")
        .def("rescaled_to", (RationalTime (RationalTime::*)(RationalTime) const) &RationalTime::rescaled_to,
             "other"_a, R"docstring(Returns the time for time converted to new_rate.)docstring")
        .def("value_rescaled_to", (double (RationalTime::*)(double) const) &RationalTime::value_rescaled_to,
             "new_rate"_a, R"docstring(Returns the time value for "self" converted to new_rate.)docstring")
        .def("value_rescaled_to", (double (RationalTime::*)(RationalTime) const) &RationalTime::value_rescaled_to,
             "other"_a)
        .def("almost_equal", &RationalTime::almost_equal, "other"_a, "delta"_a = 0)
        .def("strictly_equal", &RationalTime::strictly_equal, "other"_a)
        .def("floor", &RationalTime::floor)
        .def("ceil", &RationalTime::ceil)
        .def("round", &RationalTime::round)
        .def("__copy__", [](RationalTime rt) {
                return rt;
            })
        .def("__deepcopy__", [](RationalTime rt, py::object) {
                return rt;
            }, "copier"_a = py::none())
        .def_static("duration_from_start_end_time", &RationalTime::duration_from_start_end_time,
                    "start_time"_a, "end_time_exclusive"_a, R"docstring(
Compute the duration of samples from first to last (excluding last). This is not the same as distance.

For example, the duration of a clip from frame 10 to frame 15 is 5 frames. Result will be in the rate of start_time.
)docstring")
        .def_static("duration_from_start_end_time_inclusive", &RationalTime::duration_from_start_end_time_inclusive,
                    "start_time"_a, "end_time_inclusive"_a, R"docstring(
Compute the duration of samples from first to last (including last). This is not the same as distance.

For example, the duration of a clip from frame 10 to frame 15 is 6 frames. Result will be in the rate of start_time.
)docstring")
        .def_static("is_valid_timecode_rate", &RationalTime::is_valid_timecode_rate, "rate"_a, "Returns true if the rate is valid for use with timecode.")
        .def_static("nearest_valid_timecode_rate", &RationalTime::nearest_valid_timecode_rate, "rate"_a,
            "Returns the first valid timecode rate that has the least difference from the given value.")
        .def_static("from_frames", &RationalTime::from_frames, "frame"_a, "rate"_a, "Turn a frame number and rate into a :class:`~RationalTime` object.")
        .def_static("from_seconds", static_cast<RationalTime (*)(double, double)> (&RationalTime::from_seconds), "seconds"_a, "rate"_a)
        .def_static("from_seconds", static_cast<RationalTime (*)(double)> (&RationalTime::from_seconds), "seconds"_a)
        .def("to_frames", (int (RationalTime::*)() const) &RationalTime::to_frames, "Returns the frame number based on the current rate.")
        .def("to_frames", (int (RationalTime::*)(double) const) &RationalTime::to_frames, "rate"_a, "Returns the frame number based on the given rate.")
        .def("to_seconds", &RationalTime::to_seconds)
        .def("to_timecode", [](RationalTime rt, double rate, optional<bool> drop_frame) {
                return rt.to_timecode(
                        rate,
                        df_enum_converter(drop_frame),
                        ErrorStatusConverter()
                );
        }, "rate"_a, "drop_frame"_a, "Convert to timecode (``HH:MM:SS;FRAME``)")
        .def("to_timecode", [](RationalTime rt, double rate) {
                return rt.to_timecode(
                        rate,
                        IsDropFrameRate::InferFromRate,
                        ErrorStatusConverter()
                );
        }, "rate"_a)
        .def("to_timecode", [](RationalTime rt) {
                return rt.to_timecode(
                        rt.rate(),
                        IsDropFrameRate::InferFromRate,
                        ErrorStatusConverter());
                })
        .def("to_time_string", &RationalTime::to_time_string)
        .def_static("from_timecode", [](std::string s, double rate) {
                return RationalTime::from_timecode(s, rate, ErrorStatusConverter());
            }, "timecode"_a, "rate"_a, "Convert a timecode string (``HH:MM:SS;FRAME``) into a :class:`~RationalTime`.")
        .def_static("from_time_string", [](std::string s, double rate) {
                return RationalTime::from_time_string(s, rate, ErrorStatusConverter());
            }, "time_string"_a, "rate"_a, "Convert a time with microseconds string (``HH:MM:ss`` where ``ss`` is an integer or a decimal number) into a :class:`~RationalTime`.")
        .def("__str__", &opentime_python_str)
        .def("__repr__", &opentime_python_repr)
        .def(- py::self)
        .def("__lt__", [](RationalTime lhs, py::object const& rhs) {
                return lhs < _type_checked(rhs, "<");
            })
        .def("__gt__", [](RationalTime lhs, py::object const& rhs) {
                return lhs > _type_checked(rhs, ">");
            })
        .def("__le__", [](RationalTime lhs, py::object const& rhs) {
                return lhs <= _type_checked(rhs, "<=");
            })
        .def("__ge__", [](RationalTime lhs, py::object const& rhs) {
                return lhs >= _type_checked(rhs, ">=");
            })
        .def("__eq__", [](RationalTime lhs, py::object const& rhs) {
                return lhs == _type_checked(rhs, "==");
            })
        .def("__ne__", [](RationalTime lhs, py::object const& rhs) {
                return lhs != _type_checked(rhs, "!=");
            })
        .def(py::self - py::self)
        .def(py::self + py::self)
        // The simple "py::self += py::self" returns the original,
        // which is not what we want here: we need this to return a new copy
        // to avoid mutating any additional references, since this class has complete value semantics.

        .def("__iadd__", [](RationalTime lhs, RationalTime rhs) {
                return lhs += rhs;
            });

    py::module test = m.def_submodule("_testing", "Module for regression tests");
    test.def("add_many", [](RationalTime step_time, int final_frame_number) {
            RationalTime sum = step_time;
            for (int i = 1; i < final_frame_number; i++) {
                sum += step_time;
            }
            return sum;
        });
}
