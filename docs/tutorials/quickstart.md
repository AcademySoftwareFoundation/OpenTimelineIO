# Quickstart

This is for users who wish to get started using the "OTIOView" application to inspect the contents of editorial timelines.

**Note** This guide assumes that you are working inside a [virtualenv](https://virtualenv.pypa.io/en/latest/).

## Install Prerequisites

OTIOView has an additional prerequisite to OTIO:

- Try `python -m pip install PySide2` or `python -m pip install PySide6`
- If difficulties are encountered, please file an issue on OpenTimelineIO's github for assistance.

## Install OTIO

- `python -m pip install opentimelineio`

## Setup Any Additional Adapters You May Want

A default OTIO installation includes only the "Core" adapters, which include the native OTIO JSON format (`.otio`), OpenTimelineIO directory bundles (`.otiod`), and OpenTimelineIO ZIP bundles (`.otiod`).

A curated list of adapters for popular file formats like EDL, AAF, ALE, and FCP XML can be installed using the [OpenTimelineIO Plugins package in PyPI](https://pypi.org/project/OpenTimelineIO-Plugins/). These plugins can also be individually installed from their PyPI packages.

For mor information, see the [Adapters](./adapters) section.


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
the C++ binding and the pure python code. We use [scikit-build-core](https://scikit-build-core.readthedocs.io/)
as our python build backend, which means `pip` or [build](https://pypi.org/project/build/)
must be used to build the python package. `scikit-build-core` will take care
of automatically installing the required dependencies (cmake, ninja, etc).

By default, `scikit-build-core` will build the project in a temporary directory and will
not use caching. This can be changed by setting [`build-dir` in `pyproject.toml`](https://scikit-build-core.readthedocs.io/en/stable/configuration.html#other-options). Alternatively, you can also set `build-dir` via a command line
argument: `pip install --config-settings=build-dir=<path> .` or
`python -m build --config-settings=build-dir=<path> --wheel .`.

**Note** Any CMake arguments can be passed to `cmake` by using the `CMAKE_ARGS`
environment variable when building from source. *nix Example:

```bash
env CMAKE_ARGS="-DCMAKE_VAR=VALUE1 -DCMAKE_VAR_2=VALUE2" python -m pip install .
```

Additionally, `scikit-build-core` supports [editable installs](https://scikit-build-core.readthedocs.io/en/stable/configuration.html#editable-installs).
You can use this to speed up your development.

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
