# Quickstart

This is for users who wish to get started using the "OTIOView" application to inspect the contents of editorial timelines.

## Install Prerequisites

OTIOView has an additional prerequisite to OTIO:

- Try `pip install PySide2`
- If that doesn't work, try downloading PySide2 here: <a href="https://wiki.qt.io/Qt_for_Python" target="_blank">https://wiki.qt.io/Qt_for_Python</a>

You probably want the prebuilt binary for your platform.  PySide2 generally includes a link to the appropriate version of Qt as well.

## Install OTIO

- `pip install opentimelineio`

## Configure Environment Variables for extra adapters

By default, when you install OTIO you will only get the "Core" adapters, which include CMX EDL, Final Cut Pro 7 XML, and the built in JSON format.  In order to get access to the "contrib" adapters (which includes the maya sequencer, rv and others) you'll need to set some environment variables.  If you need support for these formats, please consult the 
<a href="adapters.html" target="_blank"> Adapters documentation page for details</a>

## Run OTIOView

Once you have pip installed OpenTimelineIO, you should be able to run:

+ `otioview path/to/your/file.edl`

# Developer Quickstart

Get the source and submodules:
+ `git clone git@github.com:PixarAnimationStudios/OpenTimelineIO.git`

## To build OTIO for C++ development:

### Linux/Mac

```bash
    mkdir build
    cd build
    cmake .. { options }
    make install
```

### Windows - in an "x64 Native Tools Command Prompt" for Visual Studio

```bash
    mkdir build
    cd build
    cmake .. -DCMAKE_INSTALL_PREFIX={path/to/install/location} { options }
    cmake --build . --target install --config Release
```

The CMAKE_INSTALL_PREFIX variable must be set to a path with no spaces in it, because CMake's default install location is in C:\Program Files, which won't work with OpenTimelineIO due to spaces in the path.

## To build OTIO for Python development:

### Linux

+ `python setup.py install`

### Mac

+ `python setup.py install --user`

The `--user` option is not necessary if the build is done within a virtualenv.

### Windows - in an "x64 Native Tools Command Prompt" for Visual Studio

+ `python setup.py install --cxx-install-root=C:/path/to/install/cpp`

## To build OTIO for both C++ and Python development:

The first time setup.py is run, cmake scripts will be created, and the headers and libraries will be installed where you specify. If the C++ or Python  sources are subsequently modified, running this command again will build and update everything appropriately.

### Linux

+ `python setup.py install --cxx-install-root=/home/someone/cxx-otio-root`

### Mac

+ `python setup.py install --cxx-install-root=/home/someone/cxx-otio-root --user`

The `--user` option is not necessary if the build is done within a virtualenv.

### Windows - in an "x64 Native Tools Command Prompt" for Visual Studio

+ `python setup.py install --cxx-install-root=C:/path/to/install/cpp`

To compile your own C++ file referencing the OTIO headers from your C++ build using gcc or clang, add the following -I flags:

+ `c++ -c source.cpp -I/home/someone/cxx-otio-root/include -I/home/someone/cxx-otio-root/include/opentimelineio/deps`

To link your own program against your OTIO build using gcc or clang, add the following -L/-l flags:
+ `c++ ... -L/home/someone/cxx-otio-root/lib -lopentimelineio`

To use opentime without opentimelineio, link with -lopentime instead, and compile with:
+ `c++ -c source.cpp -I/home/someone/cxx-otio-root/include`

# Debugging Quickstart

### Linux / GDB / LLDB

From your virtual environment, compile with debug flags:

+ `env OTIO_CXX_DEBUG_BUILD=1 python setup.py install`

You can then attach GDB to python and run your program:

+ `gdb --args python script_you_want_to_debug.py`

Or LLDB:

+ `lldb -- python script_you_want_to_debug.py`

One handy tip is that you can trigger a breakpoint in gdb by inserting a SIGINT:

```c++
        #include <csignal>
        // ...
        std::raise(SIGINT);
```

GDB will automatically break when it hits the SIGINT line.
