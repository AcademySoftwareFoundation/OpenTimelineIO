# Quickstart

**Note** Use a virtual environment for pip installations. The developer commands below use uv to manage one automatically.

## Install OTIO

- `python -m pip install opentimelineio`

## Setup Any Additional Adapters You May Want

A default OTIO installation includes only the "Core" adapters, which include the native OTIO JSON format (`.otio`), OpenTimelineIO directory bundles (`.otiod`), and OpenTimelineIO ZIP bundles (`.otiod`).

A curated list of adapters for popular file formats like EDL, AAF, ALE, and FCP XML can be installed using the [OpenTimelineIO Plugins package in PyPI](https://pypi.org/project/OpenTimelineIO-Plugins/). These plugins can also be individually installed from their PyPI packages.

For more information, see the [Adapters](./adapters) section.


## Timeline Viewers
OpenTimelineIO provides applications to view timelines in a graphical interface.

### Raven
[Raven](https://github.com/OpenTimelineIO/raven) is the preferred application and replaces OTIOView as the main 
application for viewing timelines.

### OTIOView
[OTIOView](https://github.com/OpenTimelineIO/otioview) has been moved to its own repository so those who rely on it 
still have access to it.

# Developer Quickstart

Get the source and submodules:
```sh
git clone --recursive git@github.com:AcademySoftwareFoundation/OpenTimelineIO.git
cd OpenTimelineIO
```

For an existing checkout, run `git submodule update --init --recursive` before
building. Source archives already include the required dependency sources.

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

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and run:

```sh
uv sync --locked
uv run python -m unittest discover -s tests
uv run ruff check .
```

This builds the native bindings and installs the package in editable mode,
alongside the locked development tools. Pure Python edits are immediately
available. After changing C++, rebuild with:

```sh
uv sync --locked --reinstall-package opentimelineio
```

`make format-python` runs Ruff formatting followed by quote, comma, and import
autofixes. `make format-check` checks that combined result without editing files.
Use these commands rather than running the formatter alone, since the final
comma fix is part of the project's style. `uv build` creates an sdist
and then builds a wheel from it. `uv sync --locked --group docs` installs the
documentation tools, which require Python 3.11 or newer.

## To build OTIO for both C++ and Python development:

The Python package combines pure Python with C++ extensions. scikit-build-core
invokes CMake to compile those extensions, while uv manages environments and
runs the PEP 517 build. Standard pip installs also work:

```sh
python -m pip install -e .
```

Use CMake configuration settings to customize the build:

```sh
uv sync --locked --reinstall-package opentimelineio -Ccmake.define.CMAKE_CXX_STANDARD=17
```

`CMAKE_ARGS` is supported for existing build environments. To install C++ SDK
headers and libraries for another C++ project, use the standalone CMake build
above, separately from the Python wheel build.

For VFX Reference Platform builds, use that platform's compiler, Python, and
library versions. In an ASWF container or studio environment, prevent uv from
selecting or downloading a different Python:

```sh
UV_NO_MANAGED_PYTHON=1 UV_PYTHON_DOWNLOADS=never uv sync --locked --python /path/to/platform/python
```

The CI matrix verifies CY2023–CY2027 against the corresponding ASWF containers.
The [VFX Reference Platform FAQ](https://vfxplatform.com/FAQ/) identifies those
containers as the reference for build recipes and compiler flags.

To compile your own C++ file referencing the OTIO headers from your C++ build using gcc or clang, add the following -I flags:

+ `c++ -c source.cpp -I/home/someone/cxx-otio-root/include -I/home/someone/cxx-otio-root/include/opentimelineio/deps`

To link your own program against your OTIO build using gcc or clang, add the following -L/-l flags:
+ `c++ ... -L/home/someone/cxx-otio-root/lib -lopentimelineio`

To use opentime without opentimelineio, link with -lopentime instead, and compile with:
+ `c++ -c source.cpp -I/home/someone/cxx-otio-root/include`

# Debugging Quickstart

## Linux / GDB / LLDB

To compile in debug mode with symbols, run:

```sh
uv sync --locked --reinstall-package opentimelineio -Ccmake.build-type=Debug -Cinstall.strip=false
```

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
