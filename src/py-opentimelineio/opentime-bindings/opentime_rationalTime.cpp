#include <pybind11/pybind11.h>
#include <pybind11/operators.h>

#include "opentime/rationalTime.h"
#include "opentimelineio/stringUtils.h"

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
        if (error_status) {
            throw py::value_error(error_status.details);
        }
    }

    ErrorStatus error_status;
};

IsDropFrameRate df_enum_converter(py::object& df) {
    if (df.is(py::none())) {
        return IsDropFrameRate::InferFromRate;
    } else if (py::cast<bool>(py::bool_(df))) {
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
        std::string rhs_type = py::cast<std::string>(rhs.get_type().attr("__name__"));
        throw py::type_error(string_printf("unsupported operand type(s) for %s: "
                                           "RationalTime and %s", op, rhs_type.c_str()));
    }
}

void opentime_rationalTime_bindings(py::module m) {
    py::class_<RationalTime>(m, "RationalTime")
        .def(py::init<double, double>(), "value"_a = 0, "rate"_a = 1)
        .def("is_invalid_time", &RationalTime::is_invalid_time)
        .def_property_readonly("value", &RationalTime::value)
        .def_property_readonly("rate", &RationalTime::rate)
        .def("rescaled_to", (RationalTime (RationalTime::*)(double) const) &RationalTime::rescaled_to,
             "new_rate"_a)
        .def("rescaled_to", (RationalTime (RationalTime::*)(RationalTime) const) &RationalTime::rescaled_to,
             "other"_a)
        .def("value_rescaled_to", (double (RationalTime::*)(double) const) &RationalTime::value_rescaled_to,
             "new_rate"_a)
        .def("value_rescaled_to", (double (RationalTime::*)(RationalTime) const) &RationalTime::value_rescaled_to,
             "other"_a)
        .def("almost_equal", &RationalTime::almost_equal, "other"_a, "delta"_a = 0)
        .def("__copy__", [](RationalTime rt, py::object) {
                return rt;
            }, "copier"_a = py::none())
        .def("__deepcopy__", [](RationalTime rt, py::object) {
                return rt;
            }, "copier"_a = py::none())
        .def_static("duration_from_start_end_time", &RationalTime::duration_from_start_end_time,
                    "start_time"_a, "end_time_exclusive"_a)
        .def_static("is_valid_timecode_rate", &RationalTime::is_valid_timecode_rate, "rate"_a)
        .def_static("from_frames", &RationalTime::from_frames, "frame"_a, "rate"_a)
        .def_static("from_seconds", &RationalTime::from_seconds, "seconds"_a)
        .def("to_frames", (int (RationalTime::*)() const) &RationalTime::to_frames)
        .def("to_frames", (int (RationalTime::*)(double) const) &RationalTime::to_frames, "rate"_a)
        .def("to_seconds", &RationalTime::to_seconds)
        .def("to_timecode", [](RationalTime rt, double rate, py::object drop_frame) { 
                return rt.to_timecode(
                        rate, 
                        df_enum_converter(drop_frame),
                        ErrorStatusConverter()
                ); 
        }, "rate"_a, "drop_frame"_a)
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
            }, "timecode"_a, "rate"_a)
        .def_static("from_time_string", [](std::string s, double rate) {
                return RationalTime::from_time_string(s, rate, ErrorStatusConverter());
            }, "time_string"_a, "rate"_a)
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
