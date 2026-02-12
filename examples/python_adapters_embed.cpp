// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

// Example OTIO C++ code for reading and writing files supported by the OTIO
// Python adapters.
//
// This example uses an embedded Python interpreter to convert between
// input/output files and JSON that can be used from C++ code.
//
// To run this example make sure the environment variable PYTHONPATH is set
// correctly.

#include "util.h"

#include <opentimelineio/timeline.h>

#include <Python.h>

#include <iostream>
#include <sstream>

#if defined(_WINDOWS)
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif // WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <combaseapi.h>
#endif // _WINDOWS

namespace otio = opentimelineio::OPENTIMELINEIO_VERSION_NS;

class PythonAdapters
{
public:
    PythonAdapters();
    ~PythonAdapters();

    otio::SerializableObject::Retainer<otio::Timeline> read_from_file(
        std::string const&,
        otio::ErrorStatus*);

    bool write_to_file(
        otio::SerializableObject::Retainer<otio::Timeline> const&,
        std::string const&,
        otio::ErrorStatus*);
};

PythonAdapters::PythonAdapters()
{
    Py_Initialize();
}

PythonAdapters::~PythonAdapters()
{
    Py_Finalize();
}

class PyObjectRef
{
public:
    PyObjectRef(PyObject* o) :
        o(o)
    {
        if (!o)
        {
            throw std::runtime_error("Python error");
        }
    }

    ~PyObjectRef()
    {
        Py_XDECREF(o);
    }

    PyObject* o = nullptr;

    operator PyObject* () const { return o; }
};

otio::SerializableObject::Retainer<otio::Timeline> PythonAdapters::read_from_file(
    std::string const& file_name,
    otio::ErrorStatus* error_status)
{
    otio::SerializableObject::Retainer<otio::Timeline> timeline;
    try
    {
        // Import the OTIO Python module.
        auto p_module = PyObjectRef(PyImport_ImportModule("opentimelineio.adapters"));
        
        // Read the timeline into Python.
        auto p_read_from_file = PyObjectRef(PyObject_GetAttrString(p_module, "read_from_file"));
        auto p_read_from_file_args = PyObjectRef(PyTuple_New(1));
        const std::string file_name_normalized = examples::normalize_path(file_name);
        auto p_read_from_file_arg = PyUnicode_FromStringAndSize(file_name_normalized.c_str(), file_name_normalized.size());
        if (!p_read_from_file_arg)
        {
            throw std::runtime_error("cannot create arg");
        }
        PyTuple_SetItem(p_read_from_file_args, 0, p_read_from_file_arg);
        auto p_timeline = PyObjectRef(PyObject_CallObject(p_read_from_file, p_read_from_file_args));

        // Convert the Python timeline into a string and use that to create a C++ timeline.
        auto p_to_json_string = PyObjectRef(PyObject_GetAttrString(p_timeline, "to_json_string"));
        auto p_json_string = PyObjectRef(PyObject_CallObject(p_to_json_string, NULL));
        timeline = otio::SerializableObject::Retainer<otio::Timeline>(
            dynamic_cast<otio::Timeline*>(otio::Timeline::from_json_string(
                PyUnicode_AsUTF8AndSize(p_json_string, NULL),
                error_status)));
    }
    catch (const std::exception& e)
    {
        error_status->outcome = otio::ErrorStatus::Outcome::FILE_OPEN_FAILED;
        error_status->details = e.what();
    }
    if (PyErr_Occurred())
    {
        PyErr_Print();
    }
    return timeline;
}

bool PythonAdapters::write_to_file(
    otio::SerializableObject::Retainer<otio::Timeline> const& timeline,
    std::string const& file_name,
    otio::ErrorStatus* error_status)
{
    bool r = false;
    try
    {
        // Import the OTIO Python module.
        auto p_module = PyObjectRef(PyImport_ImportModule("opentimelineio.adapters"));

        // Convert the C++ timeline to a string and pass that to Python.
        const auto string = timeline.value->to_json_string(error_status);
        if (otio::is_error(error_status))
        {
            throw std::runtime_error("cannot convert to string");
        }
        auto p_read_from_string = PyObjectRef(PyObject_GetAttrString(p_module, "read_from_string"));
        auto p_read_from_string_args = PyObjectRef(PyTuple_New(1));
        auto p_read_from_string_arg = PyUnicode_FromStringAndSize(string.c_str(), string.size());
        if (!p_read_from_string_arg)
        {
            throw std::runtime_error("cannot create arg");
        }
        PyTuple_SetItem(p_read_from_string_args, 0, p_read_from_string_arg);
        auto p_timeline = PyObjectRef(PyObject_CallObject(p_read_from_string, p_read_from_string_args));

        // Write the Python timeline.
        auto p_write_to_file = PyObjectRef(PyObject_GetAttrString(p_module, "write_to_file"));
        auto p_write_to_file_args = PyObjectRef(PyTuple_New(2));
        const std::string file_name_normalized = examples::normalize_path(file_name);
        auto p_write_to_file_arg = PyUnicode_FromStringAndSize(file_name_normalized.c_str(), file_name_normalized.size());
        if (!p_write_to_file_arg)
        {
            throw std::runtime_error("cannot create arg");
        }
        PyTuple_SetItem(p_write_to_file_args, 0, p_timeline);
        PyTuple_SetItem(p_write_to_file_args, 1, p_write_to_file_arg);
        PyObjectRef(PyObject_CallObject(p_write_to_file, p_write_to_file_args));

        r = true;
    }
    catch (const std::exception& e)
    {
        error_status->outcome = otio::ErrorStatus::Outcome::FILE_WRITE_FAILED;
        error_status->details = e.what();
    }
    if (PyErr_Occurred())
    {
        PyErr_Print();
    }
    return r;
}

int main(int argc, char** argv)
{
    if (argc != 3)
    {
        std::cout << "Usage: python_adapters_embed (inputpath) (outputpath)" << std::endl;
        return 1;
    }

    PythonAdapters adapters;
    otio::ErrorStatus error_status;
    auto timeline = adapters.read_from_file(argv[1], &error_status);
    if (!timeline)
    {
        examples::print_error(error_status);
        return 1;
    }

    std::cout << "Video tracks: " << timeline.value->video_tracks().size() << std::endl;
    std::cout << "Audio tracks: " << timeline.value->audio_tracks().size() << std::endl;

    if (!adapters.write_to_file(timeline, argv[2], &error_status))
    {
        examples::print_error(error_status);
        return 1;
    }

    return 0;
}
