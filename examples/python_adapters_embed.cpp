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

namespace otio = opentimelineio::OPENTIMELINEIO_VERSION;

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

private:
    bool _convert(std::string const& in_file_name, std::string const& out_file_name);
};

PythonAdapters::PythonAdapters()
{
    Py_Initialize();
}

PythonAdapters::~PythonAdapters()
{
    Py_Finalize();
}

otio::SerializableObject::Retainer<otio::Timeline> PythonAdapters::read_from_file(
    std::string const& file_name,
    otio::ErrorStatus* error_status)
{
    // Convert the input file to a temporary JSON file.
    const std::string temp_file_name = create_temp_dir() + "/temp.otio";
    if (!_convert(file_name, temp_file_name))
    {
        error_status->outcome = otio::ErrorStatus::Outcome::FILE_OPEN_FAILED;
        error_status->details = "cannot read file: " + file_name;
        return nullptr;
    }

    // Read the timeline from the temporary JSON file.
    return dynamic_cast<otio::Timeline*>(otio::Timeline::from_json_file(temp_file_name, error_status));
}

bool PythonAdapters::write_to_file(
    otio::SerializableObject::Retainer<otio::Timeline> const& timeline,
    std::string const& file_name,
    otio::ErrorStatus* error_status)
{
    // Write the timeline to a temporary JSON file.
    const std::string temp_file_name = create_temp_dir() + "/temp.otio";
    if (!timeline.value->to_json_file(temp_file_name, error_status))
    {
        return false;
    }

    // Convert the temporary JSON file to the output file.
    if (!_convert(temp_file_name, file_name))
    {
        error_status->outcome = otio::ErrorStatus::Outcome::FILE_WRITE_FAILED;
        error_status->details = "cannot write file: " + file_name;
        return false;
    }

    return true;
}

bool PythonAdapters::_convert(const std::string& inFileName, const std::string& outFileName)
{
    std::stringstream ss;
    ss << "import opentimelineio as otio\n";
    ss << "timeline = otio.adapters.read_from_file('" << normalize_path(inFileName) << "')\n";
    ss << "otio.adapters.write_to_file(timeline, '" << normalize_path(outFileName) << "')\n";
    return 0 == PyRun_SimpleString(ss.str().c_str());
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
        print_error(error_status);
        return 1;
    }

    std::cout << "Video tracks: " << timeline.value->video_tracks().size() << std::endl;
    std::cout << "Audio tracks: " << timeline.value->audio_tracks().size() << std::endl;

    if (!adapters.write_to_file(timeline, argv[2], &error_status))
    {
        print_error(error_status);
        return 1;
    }

    return 0;
}
