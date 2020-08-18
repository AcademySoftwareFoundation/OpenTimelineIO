#include <pybind11/pybind11.h>
#include <pybind11/operators.h>

#include "opentime_bindings.h"
#include "opentime/point.h"
#include "opentime/stringPrintf.h"

namespace py = pybind11;
using namespace pybind11::literals;
using namespace opentime;

std::string opentime_python_str(Point p) {
    return string_printf("Point(%g, %g)", p.x(), p.y());
}

std::string opentime_python_repr(Point p) {
    return string_printf("otio.opentime.Point(x=%g, y=%g)", p.x(), p.y());
}

void opentime_point_bindings(py::module m) {
    py::class_<Point>(m, "Point")
        .def(py::init<double, double>(), "x"_a= 0, "y"_a = 0)
        .def_property_readonly("x", &Point::x)
        .def_property_readonly("y", &Point::y)
        .def("__copy__", [](Point p) {
                return p;
            })
        .def("__deepcopy__", [](Point p, py::object memo) {
                return p;
            })
        .def(py::self == py::self)
        .def(py::self != py::self)
        .def("__str__", [](Point p ) {
            return opentime_python_str( p );
        } )
        .def("__repr__", [](Point p ) {
            return opentime_python_repr( p );
        } )
        ;
}


