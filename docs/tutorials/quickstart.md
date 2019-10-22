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

    otioview path/to/your/file.edl


# Developer Quickstart

0.  Get the source and submodules:
    + `git clone --recursive git@github.com:PixarAnimationStudios/OpenTimelineIO.git`

1. To build OTIO only for C++ development (i.e. produce the OTIO C++ libraries and header files), then use cmake:
    + `mkdir build`
    + `cd build`
    + `cmake .. {options}`
    + `make install`
    For {options} configure the variables PYTHON_EXECUTABLE, PYTHON_LIBRARY, and CMAKE_INSTALL_PREFIX appropriately.

2. To build OTIO only for Python development in a virtualenv run:
    + `python setup.py install`

    Currently the install script must be run in a virtualenv.

3. To build OTIO for Python in a virtualenv and also install the OTIO C++ headers and libraries, run the following command:
    + `python setup.py install --cxx-install-root=/home/someone/cxx-otio-root`

    Currently the install script must be run in a virtualenv.

    The first time setup.py is run, cmake scripts will be created, and the headers and libraries will be installed where you specify. If the C++ or Python  sources are subsequently modified, running this command again will build and update everything appropriately.

To compile your own C++ file referencing the OTIO headers from your C++ build using gcc or clang, add the following -I flags:
+ `c++ -c source.cpp -I/home/someone/cxx-otio-root/include -I/home/someone/cxx-otio-root/include/opentimelineio/deps`

To link your own program against your OTIO build using gcc or clang, add the following -L/-l flags:
+ `c++ ... -L/home/someone/cxx-otio-root/lib -lopentimelineio`

To use opentime without opentimelineio, link with -lopentime instead, and compile with:
+ `c++ -c source.cpp -I/home/someone/cxx-otio-root/include`
