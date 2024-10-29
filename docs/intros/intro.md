# Introduction

OpenTimelineIO provises tools for different types of users. This intro doc is to help understand the various facects of the OTIO.


## Software Integrations

The majority of users will interact with OpenTimelineIO by importing or exporting `.otio`, `.otiod` or `.otioz` files via software integration. [Learn more about available software integrations](integrations.md) and [OTIO supported features](/fundamentals/feature-matrix.rst). At the integration level, all you need are OTIO project files and compatible software, and feel free to get started with sample media and tutorials covering a variety of topics.


## Project Adaptors

While OpenTimelineIO favors the .otio JSON format, Python OpenTimelineIO supports many additional file formats via adapter plugins. Adaptors are community developed project conversion software. Adaptors aim to provide OTIO support when an native integration does not exist. To make use of an existing adaptor, see [OTIO Convert Quickstart documentation](otio_convert_quickstart.md). 

## APIs

OpentimelineIO provides a wide set of APIs for a variety of use cases.  

### Core C++ API

OTIO Core is implemented in C++ and provides cross platform APIs, and is hosted by the Academy Software Foundation.

The OTIO Community provides language bindings The OpenTimelineIO Python API provides a friendly API for interacting with OTIO objects as well as the Project Adaptor Interface. OTIO Also provides language bindings for 

### Python API

### Additional Language Bindings 

* [C Bindings](https://github.com/OpenTimelineIO/OpenTimelineIO-C-Bindings)
* [Java Bindings](https://github.com/OpenTimelineIO/OpenTimelineIO-Java-Bindings)
* [Swift Bindings](https://github.com/OpenTimelineIO/OpenTimelineIO-Swift-Bindings)


## Utility Software 

The OTIO project and wider community provides various additional software:

* OTIO Viewer
* OTIO Util
* Raven


