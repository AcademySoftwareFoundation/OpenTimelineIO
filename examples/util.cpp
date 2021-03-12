#include "util.h"

#include <Python.h>

#include <sstream>
#include <vector>

#include <sys/stat.h>
#include <stdlib.h>
#include <unistd.h>

std::string get_temp_dir()
{
    std::string out;
    
#if defined(_WINDOWS)

    // TODO

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

void convert_to_json(const std::string& inFileName, const std::string& outFileName)
{
    PyObject* pInt = nullptr;
	Py_Initialize();

    std::string src;
    std::stringstream ss(src);
    ss << "import opentimelineio as otio\n";
    ss << "timeline = otio.adapters.read_from_file('" << inFileName << "')\n";
    ss << "otio.adapters.write_to_file(timeline, '" << outFileName << "')\n";
	PyRun_SimpleString(ss.str().c_str());

	Py_Finalize();
}

