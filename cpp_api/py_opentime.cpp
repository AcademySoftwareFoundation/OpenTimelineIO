#include <pybind11/pybind11.h>
#include <pybind11/operators.h>
#include "opentime.h"


PYBIND11_MODULE(opentime, m) {
    m.doc() = "C++ test of opentime"; // optional module docstring
    m.def("from_frames", opentime::from_frames);
    m.def("from_seconds", opentime::from_seconds);
    m.def("to_seconds", opentime::to_seconds);
    m.def(
            "range_from_start_end_time",
            opentime::range_from_start_end_time,
            pybind11::arg("start_time"),
            pybind11::arg("end_time_exclusive")
    );
    m.def(
            "duration_from_start_end_time",
            opentime::duration_from_start_end_time,
            pybind11::arg("start_time"),
            pybind11::arg("end_time_exclusive")
    );
    m.def(
            "to_timecode",
            opentime::to_timecode,
            pybind11::arg("time_obj"),
            pybind11::arg("rate")
     );
    m.def("from_timecode", opentime::from_timecode);

    pybind11::class_<opentime::RationalTime>(m, "RationalTime")
        .def(pybind11::init<opentime::rt_value_t, opentime::rt_rate_t>(),
                pybind11::arg("value"),
                pybind11::arg("rate")
        )
        .def(pybind11::init<opentime::rt_value_t>())
        .def(pybind11::init())
        .def(
                "rescaled_to",
                pybind11::overload_cast<opentime::rt_rate_t>(
                    &opentime::RationalTime::rescaled_to,
                    pybind11::const_))
        .def(
                "rescaled_to",
                pybind11::overload_cast<const opentime::RationalTime&>(
                    &opentime::RationalTime::rescaled_to,
                    pybind11::const_
                )
        )
        .def(pybind11::self < pybind11::self)
        .def(pybind11::self > pybind11::self)
        .def(pybind11::self <= pybind11::self)
        .def(pybind11::self >= pybind11::self)
        .def(pybind11::self == pybind11::self)
        .def(pybind11::self != pybind11::self)
        .def(pybind11::self - pybind11::self)
        .def(pybind11::self + pybind11::self)
        .def("__str__",  &opentime::RationalTime::to_string)
        .def("__repr__",  &opentime::RationalTime::repr)
        .def("__hash__",  &opentime::RationalTime::hash )
        .def_readwrite("value", &opentime::RationalTime::value)
        .def_readwrite("rate", &opentime::RationalTime::rate)
        ;
        // .def("setName", &Pet::setName)
        // .def("getName", &Pet::getName);
        //
    pybind11::class_<opentime::TimeRange>(m, "TimeRange")
        .def(
                pybind11::init<
                    const opentime::RationalTime&,
                    const opentime::RationalTime&
                >(),
                pybind11::arg("start_time"),
                pybind11::arg("duration")
        )
        .def(
                pybind11::init<const opentime::RationalTime&>(),
                pybind11::arg("start_time")
        )
        .def(pybind11::init())
        .def("__str__",  &opentime::TimeRange::to_string)
        .def("__repr__",  &opentime::TimeRange::repr)
        .def(
                "contains",
                pybind11::overload_cast<const opentime::RationalTime&>(
                    &opentime::TimeRange::contains, pybind11::const_
                )
        )
        .def(
                "contains",
                pybind11::overload_cast<const opentime::TimeRange&>(
                    &opentime::TimeRange::contains, pybind11::const_
                )
        )
        .def(
                "overlaps",
                pybind11::overload_cast<const opentime::RationalTime&>(
                    &opentime::TimeRange::overlaps, pybind11::const_
                )
        )
        .def(
                "overlaps",
                pybind11::overload_cast<const opentime::TimeRange&>(
                    &opentime::TimeRange::overlaps, pybind11::const_
                )
        )
        .def("end_time_exclusive", &opentime::TimeRange::end_time_exclusive)
        .def("end_time_inclusive", &opentime::TimeRange::end_time_inclusive)
        .def(pybind11::self == pybind11::self)
        .def(pybind11::self != pybind11::self)
        .def("__hash__",  &opentime::TimeRange::hash )
        .def_readwrite("start_time", &opentime::TimeRange::start_time)
        .def_readwrite("duration", &opentime::TimeRange::duration)
        ;
}
