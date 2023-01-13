# Quickstart

This is for users who wish to get started using the "OTIOView" application to inspect the contents of editorial timelines.

**Note** This guide assumes that you are working inside a [virtualenv](https://virtualenv.pypa.io/en/latest/).

## Install Prerequisites

OTIOView has an additional prerequisite to OTIO:

- Try `python -m pip install PySide2` or `python -m pip install PySide6`
- If difficulties are encountered, please file an issue on OpenTimelineIO's github for assistance.

## Install OTIO

- `python -m pip install opentimelineio`

## Configure Environment Variables for extra adapters

A default OTIO installation includes only the "Core" adapters, which include CMX EDL, Final Cut Pro 7 XML, and the built in JSON format.
In order to get access to the "contrib" adapters (which includes rv and others), please consult the
[Adapters documentation page for details](./adapters).

## Run OTIOView

Once you have pip installed OpenTimelineIO, you should be able to run:

+ `otioview path/to/your/file.edl`

# Developer Quickstart

Get the source and submodules:
+ `git clone git@github.com:AcademySoftwareFoundation/OpenTimelineIO.git`

Before reading further, it is good to note that there is two parts to the
C++ code: the OTIO C++ library that you can use in your C++ projects,
and the C++ Python bindings that makes the C++ library available in Python.

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

The `CMAKE_INSTALL_PREFIX` variable must be set to a path with no spaces in it,
because CMake's default install location is in `C:\Program Files`, which won't work
with OpenTimelineIO due to spaces in the path.

## To build OTIO for Python development:

+ `python -m pip install -e .`

## To build OTIO for both C++ and Python development:

The Python package is a mix of pure python and C++ code. Therefore, it is
recommended to use the python tooling (`python -m pip`) to develop both
the C++ binding and the pure python code. We use `setuptools` as our
python build backend, which means `pip` will call the `setup.py` in the root
of the directory to build both the pure python and the C++ bindings.
`setuptools` will take care of all the complexity of building a C++ Python
extension for you.

The first time `setup.py` is run, cmake scripts will be created, and the headers
and libraries will be installed where you specify. If the C++ or Python  sources
are subsequently modified, running this command again will build and update everything
appropriately.

**Note** Any CMake arguments can be passed through `pip` by using the `CMAKE_ARGS`
environment variable when building from source. *nix Example:

```bash
env CMAKE_ARGS="-DCMAKE_VAR=VALUE1 -DCMAKE_VAR_2=VALUE2" python -m pip install .
```

`python -m pip install .` adds some overhead that might be annoying or unwanted when
developing the python bindings. For that reason (and only that reason), if you want a faster
iteration process, you can use `setuptools` commands. For example you can use
`python setup.py build_ext` to only run the compilation step. Be aware that calling `setup.py`
directly is highly discouraged and should only be used when no of the other options
are viable. See https://blog.ganssle.io/articles/2021/10/setup-py-deprecated.html.

To compile your own C++ file referencing the OTIO headers from your C++ build using gcc or clang, add the following -I flags:

+ `c++ -c source.cpp -I/home/someone/cxx-otio-root/include -I/home/someone/cxx-otio-root/include/opentimelineio/deps`

To link your own program against your OTIO build using gcc or clang, add the following -L/-l flags:
+ `c++ ... -L/home/someone/cxx-otio-root/lib -lopentimelineio`

To use opentime without opentimelineio, link with -lopentime instead, and compile with:
+ `c++ -c source.cpp -I/home/someone/cxx-otio-root/include`

# Debugging Quickstart

## Linux / GDB / LLDB

To compile in debug mode, set the `OTIO_CXX_DEBUG_BUILD` environment variable to any value
and then `python -m pip install`.

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

# How to Generate the C++ Documentation:

## Mac / Linux

The doxygen docs can be generated with the following commands:

```
cd doxygen ; doxygen config/dox_config ; cd ..
```

Another option is to trigger the make target:

```
make doc-cpp
```
