#ifndef OTIO_OPENTIME_BINDINGS_H
#define OTIO_OPENTIME_BINDINGS_H

#include "opentime/rationalTime.h"
#include <pybind11/pybind11.h>
#include <string>

void opentime_rationalTime_bindings(pybind11::module);
void opentime_timeRange_bindings(pybind11::module);
void opentime_timeTransform_bindings(pybind11::module);

std::string opentime_python_str(opentime::RationalTime rt);
std::string opentime_python_repr(opentime::RationalTime rt);

#endif
