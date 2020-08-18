#include <pybind11/pybind11.h>
#include <pybind11/operators.h>

#include "opentime_bindings.h"
#include "opentime/point.h"
#include "opentime/stringPrintf.h"

namespace py = pybind11;
using namespace pybind11::literals;
using namespace opentime;

void opentime_box_bindings(py::module m) {
    py::class_<Box>(m, "Box")
        .def(py::init<double, double, Point>(), "width"_a= 0, "height"_a = 0, "center"_a = Point())
        .def_property_readonly("width", &Box::width)
        .def_property_readonly("height", &Box::height)
        .def_property_readonly("center", &Box::center)
        .def("get_aspect_ratio", &Box::get_aspect_ratio)
        .def("contains", &Box::contains)
        .def("get_union", &Box::get_union)
        .def("__copy__", [](Box p) {
                return p;
            })
        .def("__deepcopy__", [](Box p, py::object memo) {
                return p;
            })
        .def(py::self == py::self)
        .def(py::self != py::self)
        .def("__str__", [](Box b) {
                return string_printf("Box(%g, %g, %s)",
                                     b.width(), b.height(),
                                     opentime_python_str(b.center()).c_str());
            })
        .def("__repr__", [](Box b) {
                return string_printf("otio.opentime.Box(width=%g, height=%g, center=%s)",
                                     b.width(), b.height(),
                                     opentime_python_repr(b.center()).c_str());
            })
        ;
}

