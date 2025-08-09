// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include <pybind11/pybind11.h>

void otio_exception_bindings(pybind11::module);
void otio_any_dictionary_bindings(pybind11::module);
void otio_any_vector_bindings(pybind11::module);
void otio_imath_bindings(pybind11::module);
void otio_serializable_object_bindings(pybind11::module);
void otio_tests_bindings(pybind11::module);
void otio_bundle_bindings(pybind11::module);
