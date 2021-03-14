#include "util.h"

#include <opentimelineio/timeline.h>

#include <Python.h>

#include <iostream>
#include <sstream>
#include <vector>

#include <sys/stat.h>
#include <stdlib.h>
#include <unistd.h>

namespace otio = opentimelineio::OPENTIMELINEIO_VERSION;

namespace {

std::string get_temp_dir()
{
    std::string out;
    
#if defined(_WINDOWS)

    // TODO: Windows implementation

#else // _WINDOWS

    std::string path;
    char* env = nullptr;
    if ((env = getenv("TEMP"))) path = env;
    else if ((env = getenv("TMP"))) path = env;
    else if ((env = getenv("TMPDIR"))) path = env;
    else
    {
        for (const auto& i : { "/tmp", "/var/tmp", "/usr/tmp" })
        {
            struct stat buffer;   
            if (0 == stat(i, &buffer))
            {
                path = i;
                break;
            }
        }
    }
    path = path + "/XXXXXX";
    const size_t size = path.size();
    std::vector<char> buf(size + 1);
    memcpy(buf.data(), path.c_str(), size);
    buf[size] = 0;
    out = mkdtemp(buf.data());

#endif // _WINDOWS
    
    return out;
}

}

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
    const std::string temp_file_name = get_temp_dir() + "/temp.otio";
    _convert(file_name, temp_file_name);
    
    // Read the timeline from the temporary JSON file.
    return dynamic_cast<otio::Timeline*>(otio::Timeline::from_json_file(temp_file_name, error_status));
}

bool PythonAdapters::write_to_file(
    otio::SerializableObject::Retainer<otio::Timeline> const& timeline,
    std::string const& file_name,
    otio::ErrorStatus* error_status)
{
    // Write the timeline to a temporary JSON file.
    const std::string temp_file_name = get_temp_dir() + "/temp.otio";
    if (!timeline.value->to_json_file(temp_file_name, error_status))
    {
        return false;
    }
    
    // Convert the temporary JSON file to the output file.
    _convert(temp_file_name, file_name);
    
    return true;
}

void PythonAdapters::_convert(const std::string& inFileName, const std::string& outFileName)
{
    std::string src;
    std::stringstream ss(src);
    ss << "import opentimelineio as otio\n";
    ss << "timeline = otio.adapters.read_from_file('" << inFileName << "')\n";
    ss << "otio.adapters.write_to_file(timeline, '" << outFileName << "')\n";
    // TODO: Exception handling
    PyRun_SimpleString(ss.str().c_str());
}

void print_error(otio::ErrorStatus const& error_status)
{
    std::cout << "Error: " <<
        otio::ErrorStatus::outcome_to_string(error_status.outcome) << ": " <<
        error_status.details << std::endl;
}

