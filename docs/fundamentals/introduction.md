
# API Introduction

OpenTimelineIO is organized into a few components with separate concerns:

## Python API

The Python API is the preferred API to create and manupulate Timelines, Tracks, Edits, and core schema objects. With the Python API developers can adjust timing, replace media, write adaptors, media linkers, create custom schema additions, and more. 

## Core C++ API

The OTIO Core library is implemented in C++ and provides a cross platform APIs for loading OTIO files, creating Timelines and other core schema objects. 

Developers can interface directly with OTIO and write native cross platform integrations using the C++ API, or use the C++ Api to brige to new languages.

The C++ API can be found at the Core OpenTimelineIO Github hosted by the Academy Software Foundation.


## Additional Language Bindings 

The OTIO Community provides language bindings The OpenTimelineIO Python API provides a friendly API for interacting with OTIO objects as well as the Project Adaptor Interface. OTIO Also provides language bindings for 

* [C Bindings](https://github.com/OpenTimelineIO/OpenTimelineIO-C-Bindings)
* [Java Bindings](https://github.com/OpenTimelineIO/OpenTimelineIO-Java-Bindings)
* [Swift Bindings](https://github.com/OpenTimelineIO/OpenTimelineIO-Swift-Bindings)
