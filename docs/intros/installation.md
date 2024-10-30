# Installation

There are various ways of working with OpenTimelineIO, from simply importing and exporting otio files in supported software, using the OpenTimelineIO Python API to automate workflows and writing custom project adapators, to native application integration and working with the core C++ library or language bindings. 


## Software Integrations

For most users, there is nothing to install to use OpenTimelineIO. OpenTimelineIO is available in many video software packages today, allowing for importing or exporting `.otio`, `.otiod` or `.otioz` files with no additional requirements. 

[See a list available software integrations](integrations.md).


## Project Adaptors

While OpenTimelineIO prefers native integration to support `otio` file formats, not all software has been updated. To that end, OpenTimelineIO supports additional project formats via [Adapter Plugins](/adaptors.md). 

Adaptors are community developed project converters. Adaptors provide OTIO support when an native integration does not exist. To make use of an existing adaptor, see [OTIO Convert Quickstart documentation](otio_convert_quickstart.md). 

For developers, [learn how to write your own adaptors](/tutorials/write-an-adapter.html).

## Python API

The python API is the preferred API to create and manupulate Timelines, Tracks, Edits, and core schema objects. With the Python API developers can adjust timing, replace media, write adaptors, media linkers, create custom schema additions, and more. 

## Core C++ API

The OTIO Core library is implemented in C++ and provides a cross platform APIs for loading OTIO files, creating Timelines and other core schema objects. 

Developers can interface directly with OTIO and write native cross platform integrations using the C++ API, or use the C++ Api to brige to new languages.

The C++ API can be found at the Core OpenTimelineIO Github hosted by the Academy Software Foundation.


## Additional Language Bindings 

The OTIO Community provides language bindings The OpenTimelineIO Python API provides a friendly API for interacting with OTIO objects as well as the Project Adaptor Interface. OTIO Also provides language bindings for 

* [C Bindings](https://github.com/OpenTimelineIO/OpenTimelineIO-C-Bindings)
* [Java Bindings](https://github.com/OpenTimelineIO/OpenTimelineIO-Java-Bindings)
* [Swift Bindings](https://github.com/OpenTimelineIO/OpenTimelineIO-Swift-Bindings)


## Utility Software 

The OTIO project and wider community provides various additional software:

* OTIO Viewer
* OTIO Util
* Raven


