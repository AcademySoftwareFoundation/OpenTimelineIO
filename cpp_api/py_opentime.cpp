#include <pybind11/pybind11.h>
#include <pybind11/operators.h>
#include "opentime.h"


PYBIND11_MODULE(opentime, m) {
    m.doc() = "C++ test of opentime"; // optional module docstring
    m.def("from_frames", opentime::from_frames);
    m.def(
            "to_frames",
            pybind11::overload_cast<const opentime::RationalTime&, opentime::rt_rate_t>(&opentime::to_frames)
    );
    m.def(
            "to_frames",
            pybind11::overload_cast<const opentime::RationalTime&>(&opentime::to_frames)
    );
    m.def("from_seconds", opentime::from_seconds);
    m.def("to_seconds", opentime::to_seconds);
    m.def("to_time_string", opentime::to_time_string);
    m.def("from_time_string", opentime::from_time_string);
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
            pybind11::overload_cast<const opentime::RationalTime&, opentime::rt_rate_t>(&opentime::to_timecode),
            pybind11::arg("time_obj"),
            pybind11::arg("rate")
     );
    m.def(
            "to_timecode",
            pybind11::overload_cast<const opentime::RationalTime&>(&opentime::to_timecode),
            pybind11::arg("time_obj")
     );
    m.def(
            "from_timecode", 
            opentime::from_timecode,
            pybind11::arg("timecode_str"),
            pybind11::arg("rate")

    );

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
        .def(
                "almost_equal",
                &opentime::RationalTime::almost_equal,
                pybind11::arg("other"),
                pybind11::arg("delta")

        )
        .def(pybind11::self < pybind11::self)
        .def(pybind11::self > pybind11::self)
        .def(pybind11::self <= pybind11::self)
        .def(pybind11::self >= pybind11::self)
        .def(pybind11::self == pybind11::self)
        .def(pybind11::self != pybind11::self)
        .def(pybind11::self - pybind11::self)
        .def(pybind11::self + pybind11::self)
        .def(pybind11::self += pybind11::self)
        .def(
                "__str__",
                [](const opentime::RationalTime& rt)
                {
                    return (
                            pybind11::str("RationalTime({}, {})" ).attr("format")(
                            pybind11::str(pybind11::float_(rt.value))
                            , pybind11::str(pybind11::float_(rt.rate))
                            )
                    );
                }
        )
        .def(
                "__repr__",
                [](const opentime::RationalTime& rt)
                {
                    return (
                            pybind11::str("otio.opentime.RationalTime(value={}, rate={})" ).attr("format")(
                            pybind11::str(pybind11::float_(rt.value))
                            , pybind11::str(pybind11::float_(rt.rate))
                            )
                    );
                }
        )
        .def("__hash__",  &opentime::RationalTime::hash )
        .def("__copy__", &opentime::RationalTime::copy)
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
        .def(
                "__str__",
                [](const opentime::TimeRange& tr)
                {
                    return (
                            pybind11::str("TimeRange({}, {})" ).attr("format")(
                            pybind11::str(pybind11::cast(tr.start_time))
                            , pybind11::str(pybind11::cast(tr.duration))
                            )
                    );
                }
        )
        .def(
                "__repr__",
                [](const opentime::TimeRange& tr)
                {
                    return (
                            pybind11::str("otio.opentime.TimeRange(start_time={}, duration={})" ).attr("format")(
                            pybind11::repr(pybind11::cast(tr.start_time))
                            , pybind11::repr(pybind11::cast(tr.duration))
                            )
                    );
                }
        )
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
        /* .def_readwrite("duration", &opentime::TimeRange::duration) */
        .def_property(
                "duration",
                [](const opentime::TimeRange& tr)
                {
                    return tr.duration;
                },
                [](opentime::TimeRange& tr, const opentime::RationalTime& dur)
                {
                    if (dur.value < 0.0)
                    {
                        throw pybind11::type_error("duration must be a RationalTime with value >= 0, not " + std::to_string(dur.value));
                    }
                    tr.duration = dur;    
                }
        )
        ;
}
