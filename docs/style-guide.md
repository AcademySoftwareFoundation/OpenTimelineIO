
### OpenTimelineIO Style Guide

As much as is practical the styles and conventions described in this document are facilitated by the use of tools such as clang-format, and by lint checks that run as part of the Pull Request workflow.

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
- If a named item has an SI unit, such as seconds, the name of the item should be suffixed with the unit, with propercase for the unit. For example, timeOffset_s, OPENTIME_ONE_MINUTE_s


C
-

XXX

______
Python: OpentimelineIO follows PEP8, as described at https://www.python.org/dev/peps/pep-0008/i8 

In the future a stronger style guide for python, such as black (https://github.com/psf/black) may be adopted, but that is contingent on moving completely to python3.

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

No runtime behavior of the OpenTimelineIO C++ runtime is modified by the settings of environment variables. This is because the C++ libraries must run in environments without environment variables, or that are sandboxed for security.



