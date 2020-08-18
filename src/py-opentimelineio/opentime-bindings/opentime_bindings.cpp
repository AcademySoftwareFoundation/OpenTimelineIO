#include <pybind11/pybind11.h>
#include "opentime_bindings.h"

PYBIND11_MODULE(_opentime, m) {
    m.doc() = "Bindings to C++ OTIO implementation";
    opentime_rationalTime_bindings(m);
    opentime_timeRange_bindings(m);
    opentime_timeTransform_bindings(m);
    opentime_point_bindings(m);
    opentime_box_bindings(m);
}
