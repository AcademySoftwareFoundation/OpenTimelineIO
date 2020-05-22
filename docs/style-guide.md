
### OpenTimelineIO Style Guide

## Directory Structure

```
opentimelineio
│   Top level information
│   CMakeLists.txt
│
└───contrib
│   │
│   └───opentimelineio_contrib
│       └───adapters
│       └───application_plugins
│
└───docs 
└───examples 
└───maintainers
└───srcs
└───test
```

## Source and Header Naming

C and C++ header files are within their library name, and includes must reference the scoping library. For example, ```opentime/version.h```

File names are lowerCamelCase.

## Library Naming

Library names follow semantic versioning conventions.

Libraries compiled for debug are suffixed with _d. For example, opentime_d.lib indicates that the opentime library has been compiled with debug options enabled.

Libraries compiled for Microsoft Multithreaded are suffixed with mt. For example opentime_mt.lib indicates a release build for the mt runtime, wherase opentime_mtd.lib indicates the debug variant of the mt runtime.

Libraries compiled for static linking are suffixed with s. opentime_s.lib indicates a static version of the opentime library, whereas optime_sd.lib indicates a static debug variant.

## Python Module Naming




## Notation

#General Form

C++
---

- Typenames are CamelCase
- enum class is used, enums are UPPER_SNAKE_CASE
- member function names are lower_snake_case
- Macros are prefixed with library name and UPPER_SNAKE_CASE, for example, OPENTIME_VERSION

C
-

XXX

______
Python: PEP8

## Namespaces

All public API will be wrapped in a versioned opentime namespace as follows:

```cpp

namespace opentime
{ namespace OPENTIME_VERSION {
    ... code ...
}}

```

and similarly for opentimelineio.

Deprecated functionality will be further enclosed in a deprecated namespace as follows:

```cpp
namespace opentime
{ namespace OPENTIME_VERSION {
    ... code ...
    namespace deprecated {
        ... deprecated code ...
    }
    ... more code ...
}}

During a deprecation period, a deprecation header may be included to normalize deprecated names temporarily. For example, if there was a deprecated function in opentime/rationalTime.h, opentime/rationalTimeDeprecations.h might appear as:

```cpp
namespace opentime
{ namespace OPENTIME_VERSION {
    using deprecated::poorUnfortunateSoul;
}}
```


# Environment Variables

No runtime behavior of OpenTimelineIO is modified by the settings of environment variables.



