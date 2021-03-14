#include "util.h"

#include <opentimelineio/timeline.h>

#include <Python.h>

#include <iostream>
#include <sstream>
#include <vector>

#if defined(_WINDOWS)
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif // WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <combaseapi.h>
#else // _WINDOWS
#include <sys/stat.h>
#include <stdlib.h>
#include <unistd.h>
#endif // _WINDOWS

namespace otio = opentimelineio::OPENTIMELINEIO_VERSION;

namespace {

#if defined(_WINDOWS)

    std::string create_temp_dir()
    {
        std::string out;

        // Get the temporary directory.
        char path[MAX_PATH];
        DWORD r = GetTempPath(MAX_PATH, path);
        if (r)
        {
            out = std::string(path);

            // Replace path separators.
            for (size_t i = 0; i < out.size(); ++i)
            {
                if ('\\' == out[i])
                {
                    out[i] = '/';
                }
            }

            // Create a unique name from a GUID.
            GUID guid;
            CoCreateGuid(&guid);
            const uint8_t* guidP = reinterpret_cast<const uint8_t*>(&guid);
            for (int i = 0; i < 16; ++i)
            {
                char buf[3] = "";
                sprintf_s(buf, 3, "%02x", guidP[i]);
                out += buf;
            }

            // Create a unique directory.
            CreateDirectory(out.c_str(), NULL);
        }

        return out;
    }

#else // _WINDOWS

    std::string create_temp_dir()
    {
        // Find the temporary directory.
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

        // Create a unique directory.
        path = path + "/XXXXXX";
        const size_t size = path.size();
        std::vector<char> buf(size + 1);
        memcpy(buf.data(), path.c_str(), size);
        buf[size] = 0;
        return mkdtemp(buf.data());
    }

#endif // _WINDOWS
    
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
    std::string src;
    std::stringstream ss(src);
    ss << "import opentimelineio as otio\n";
    ss << "timeline = otio.adapters.read_from_file('" << inFileName << "')\n";
    ss << "otio.adapters.write_to_file(timeline, '" << outFileName << "')\n";
    return 0 == PyRun_SimpleString(ss.str().c_str());
}

void print_error(otio::ErrorStatus const& error_status)
{
    std::cout << "ERROR: " <<
        otio::ErrorStatus::outcome_to_string(error_status.outcome) << ": " <<
        error_status.details << std::endl;
}

