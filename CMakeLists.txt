# FindPython's Development.Module component was added in 3.18.
# Require 3.18.2+ because pybind11 recommends it.
cmake_minimum_required(VERSION 3.18.2)

#------------------------------------------------------------------------------
# Project Meta data
# TODO: read this information from a configuration file, here, and in setup.py

set(OTIO_VERSION_MAJOR "0")
set(OTIO_VERSION_MINOR "16")
set(OTIO_VERSION_PATCH "0")
set(OTIO_VERSION ${OTIO_VERSION_MAJOR}.${OTIO_VERSION_MINOR}.${OTIO_VERSION_PATCH})

set(OTIO_AUTHOR       "Contributors to the OpenTimelineIO project")
set(OTIO_AUTHOR_EMAIL "otio-discussion@lists.aswf.io")
set(OTIO_LICENSE      "Modified Apache 2.0 License")

set(CMAKE_OSX_ARCHITECTURES "arm64;x86_64" CACHE STRING "")

project(OpenTimelineIO VERSION ${OTIO_VERSION} LANGUAGES C CXX)

#------------------------------------------------------------------------------
# Options
# Add all options and settings here for all subprojects to aid in project
# maintenance and troubleshooting

# Installation options
option(OTIO_CXX_INSTALL               "Install the C++ bindings" ON)
option(OTIO_PYTHON_INSTALL            "Install the Python bindings" OFF)
option(OTIO_DEPENDENCIES_INSTALL      "Install OTIO's C++ header dependencies (any and nonstd)" ON)
option(OTIO_INSTALL_PYTHON_MODULES    "Install OTIO pure Python modules/files" ON)
option(OTIO_INSTALL_COMMANDLINE_TOOLS "Install the OTIO command line tools" ON)
option(OTIO_INSTALL_CONTRIB           "Install the opentimelineio_contrib Python package" ON)
set(OTIO_IMATH_LIBS "" CACHE STRING   "Imath library overrides to use instead of src/deps or find_package")
option(OTIO_FIND_IMATH                "Find Imath using find_package, ignored if OTIO_IMATH_LIBS is set" OFF)
set(OTIO_PYTHON_INSTALL_DIR "" CACHE STRING "Python installation dir (such as the site-packages dir)")

# Build options
option(OTIO_SHARED_LIBS          "Build shared if ON, static if OFF" ON)
option(OTIO_CXX_COVERAGE         "Invoke code coverage if lcov/gcov is available" OFF)
option(OTIO_CXX_EXAMPLES         "Build CXX examples (also requires OTIO_PYTHON_INSTALL=ON)" OFF)
option(OTIO_AUTOMATIC_SUBMODULES "Fetch submodules automatically" ON)

#------------------------------------------------------------------------------
# Set option dependent variables

if(OTIO_PYTHON_INSTALL)
    # Find the python interpreter using FindPython module.
    # The Development.Module component is used instead of the Development one
    # because we don't need the libpython library since we don't link against it.
    # pybind11 will detect that we already found a python
    # interpreter and will use what was found previously (here).
    # See https://pybind11.readthedocs.io/en/stable/compiling.html#findpython-mode
    # Also, the "manylinux" docker images don't have libpython, so requiring the libraries is an issue there.
    find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)
    message(STATUS "Python_INCLUDE_DIRS: ${Python_INCLUDE_DIRS}")
    message(STATUS "Python_VERSION: ${Python_VERSION}")

    # reconcile install directories for builds incorporating Python in order
    # that default behaviors match a reasonable expectation, as follows:
    #

    # if nothing has been set,
    #   Python: ${Python_SITEARCH}/opentimelineio
    # if only CMAKE_INSTALL_PREFIX has been set,
    #   Python: ${CMAKE_INSTALL_PREFIX}/opentimelineio/python
    # if only OTIO_PYTHON_INSTALL_DIR has been set,
    #   Python: ${OTIO_PYTHON_INSTALL_DIR}/opentimelineio
    #
    # In a Python install, the dylibs/dlls need to be installed where __init__.py
    # can find them, rather as part of the C++ SDK package; so the variable
    # OTIO_RESOLVED_CXX_DYLIB_INSTALL_DIR indicates where that is.
    #
    if(OTIO_PYTHON_INSTALL_DIR STREQUAL "" AND CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)
        # neither install directory supplied from the command line
        set(OTIO_RESOLVED_PYTHON_INSTALL_DIR "${Python_SITEARCH}")
        set(OTIO_RESOLVED_CXX_DYLIB_INSTALL_DIR "${OTIO_RESOLVED_PYTHON_INSTALL_DIR}/opentimelineio")
        message(STATUS "OTIO Defaulting Python install to ${OTIO_RESOLVED_PYTHON_INSTALL_DIR}")
    else()
        # either python_install or install_prefix have been set
        if(NOT OTIO_PYTHON_INSTALL_DIR)
            # CMAKE_INSTALL_PREFIX was set, so install the python components there
            set(OTIO_RESOLVED_PYTHON_INSTALL_DIR "${CMAKE_INSTALL_PREFIX}/python")

            # In order to not require setting $PYTHONPATH to point at the .so,
            # the shared libraries are installed into the python library
            # location.
            set(OTIO_RESOLVED_CXX_DYLIB_INSTALL_DIR "${OTIO_RESOLVED_PYTHON_INSTALL_DIR}/opentimelineio")
            message(STATUS "OTIO Defaulting Python install to ${OTIO_RESOLVED_PYTHON_INSTALL_DIR}")
        else()
            # OTIO_PYTHON_INSTALL_DIR was set, so install everything into the python package
            set(OTIO_RESOLVED_PYTHON_INSTALL_DIR "${OTIO_PYTHON_INSTALL_DIR}")
            set(OTIO_RESOLVED_CXX_DYLIB_INSTALL_DIR "${OTIO_PYTHON_INSTALL_DIR}/opentimelineio")
        endif()
    endif()

    if (WIN32)
        string(REPLACE "\\" "/" OTIO_RESOLVED_PYTHON_INSTALL_DIR ${OTIO_RESOLVED_PYTHON_INSTALL_DIR})
    endif()

else()
    set(OTIO_RESOLVED_CXX_DYLIB_INSTALL_DIR "${CMAKE_INSTALL_PREFIX}/lib")
    message(STATUS "OTIO C++ installing to ${CMAKE_INSTALL_PREFIX}")
endif()

if(OTIO_SHARED_LIBS)
    message(STATUS "Building shared libs")
    set(OTIO_SHARED_OR_STATIC_LIB "SHARED")
else()
    message(STATUS "Building static libs")
    set(OTIO_SHARED_OR_STATIC_LIB "STATIC")
    if (OTIO_PYTHON_INSTALL)
        # If we're compiling for pybind, we can hide all our symbols, they'll only be called from pybind
        # Note that this has no effect on Windows.
        set(CMAKE_CXX_VISIBILITY_PRESET hidden)
        set(CMAKE_VISIBILITY_INLINES_HIDDEN 1)

        if(MSVC AND Python_VERSION_MAJOR VERSION_LESS 3)
            # Statically link run-time library (vcruntime and msvcp)
            # See https://docs.microsoft.com/en-us/cpp/build/reference/md-mt-ld-use-run-time-library?view=msvc-160
            # This allows us to compile OTIO bindings with a newer MSVC version
            # than the one used by the interpreter where OTIO will be installed.
            # This is only required for Python < 3 because only these are
            # compiled with an older compiler (9.0). CPython 3.5+ uses at least
            # Visual C++ 14.X.
            # See https://wiki.python.org/moin/WindowsCompilers#Which_Microsoft_Visual_C.2B-.2B-_compiler_to_use_with_a_specific_Python_version_.3F
            add_compile_options(/MT)
        endif()
    endif()
endif()

set(OTIO_RESOLVED_CXX_INSTALL_DIR "${CMAKE_INSTALL_PREFIX}")

if(OTIO_CXX_INSTALL)
    message(STATUS "Installing C++ bindings to: ${OTIO_RESOLVED_CXX_INSTALL_DIR}")
    message(STATUS "Installing C++ dynamic libraries to: ${OTIO_RESOLVED_CXX_DYLIB_INSTALL_DIR}")

    if(OTIO_DEPENDENCIES_INSTALL)
        message(STATUS "  Installing 'any' and 'nonstd' for C++ (OTIO_DEPENDENCIES_INSTALL=ON)")
    else()
        message(STATUS "  Not installing any and nonstd for C++ (OTIO_DEPENDENCIES_INSTALL=OFF)")
    endif()
else()
    message(STATUS "Install C++ bindings: OFF")
endif()

if(OTIO_PYTHON_INSTALL)
    message(STATUS "Installing Python bindings to: ${OTIO_RESOLVED_PYTHON_INSTALL_DIR}")
else()
    message(STATUS "Install Python bindings: OFF")
endif()

#------------------------------------------------------------------------------
# Global language settings

if (NOT CMAKE_CXX_STANDARD)
    set(CMAKE_CXX_STANDARD 14)
endif()

set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(OTIO_CXX_COVERAGE AND NOT MSVC)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} --coverage")
    # this causes cmake to produce file.gcno instead of file.cpp.gcno
    set(CMAKE_CXX_OUTPUT_EXTENSION_REPLACE 1)
    message(STATUS "Building C++ with Coverage: ON")
else()
    message(STATUS "Building C++ with Coverage: OFF")
endif()

if(WIN32)
    # Windows debug builds for Python require a d in order for the module to
    # load. This also helps ensure that debug builds in general are matched
    # to the Microsoft debug CRT.
    set(OTIO_DEBUG_POSTFIX "d")
endif()

set_property(GLOBAL PROPERTY USE_FOLDERS ON)

#------------------------------------------------------------------------------
# Fetch or refresh submodules if requested
#
# fetching submodules does not work in Travis, so override the OTIO_AUTOMATIC_SUBMODULES option
# TODO: Travis is no longer used for CI of OpenTimelineIO, so the ENV var that overrides
# the automatic submodule feature should be renamed.

if (OTIO_AUTOMATIC_SUBMODULES AND NOT DEFINED ENV{TRAVIS})
    # make sure that git submodules are up to date when building
    find_package(Git QUIET)
    if (GIT_FOUND)
        message(STATUS "Checking git repo is available:")
        execute_process(
            # the following command returns true if cwd is in the repo
            COMMAND ${GIT_EXECUTABLE} rev-parse --is-inside-work-tree
            WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
            RESULT_VARIABLE IN_A_GIT_REPO_RETCODE
        )
    endif()

    if (GIT_FOUND AND IN_A_GIT_REPO_RETCODE EQUAL 0)
        # you might want to turn this off if you're working in one of the submodules
        # or trying it out with a different version of the submodule
        option(GIT_UPDATE_SUBMODULES "Update submodules each build" ON)
        if (GIT_UPDATE_SUBMODULES)
            message(
                STATUS "root: Updating git submodules to make sure they are up to date"
            )
            execute_process(
                COMMAND ${GIT_EXECUTABLE} submodule update --init --recursive
                WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
                RESULT_VARIABLE GIT_UPDATE_SUBMODULES_RESULT
            )
            if (NOT GIT_UPDATE_SUBMODULES_RESULT EQUAL "0")
                message(
                    FATAL_ERROR
                    "git submodule update --init --recursive failed with \
                    ${GIT_UPDATE_SUBMODULES_RESULT}"
                )
            endif()
        endif()
    endif()
endif()

#------------------------------------------------------------------------------
# Setup tests

include(CTest)
set(CTEST_OUTPUT_ON_FAILURE ON)

#------------------------------------------------------------------------------
# Build the dependencies and components

#----- Imath
set(OTIO_RESOLVED_IMATH_LIBRARIES "")
if (NOT "${OTIO_IMATH_LIBS}" STREQUAL "")
    message(STATUS "Using Imath from OTIO_MATH_LIBS: ${OTIO_IMATH_LIBS}")
    set(OTIO_RESOLVED_IMATH_LIBRARIES "${OTIO_IMATH_LIBS}")
    set(USE_DEPS_IMATH OFF)
elseif(OTIO_FIND_IMATH)
    find_package(Imath QUIET)
    if (Imath_FOUND)
        message(STATUS "Found Imath 3 at ${Imath_CONFIG}")
        set(USE_DEPS_IMATH OFF)
    else()
        find_package(IlmBase QUIET)
        if (IlmBase_FOUND)
            message(STATUS "Imath 3 not found, found Imath 2 at ${IlmBase_CONFIG}")
            message(STATUS "You may need to point to the Imath headers by setting IMATH_INCLUDES")
            set(USE_DEPS_IMATH_OFF)
            set(OTIO_RESOLVED_IMATH_LIBRARIES "${IlmBase_LIBRARIES")
        else()
            message(STATUS "Imath 3 and 2 were not found, using src/deps/Imath")
            set(USE_DEPS_IMATH ON)
        endif()
    endif()
else()
    message(STATUS "Using src/deps/Imath by default")
    set(USE_DEPS_IMATH ON)
endif()

# set up the internally hosted dependencies
add_subdirectory(src/deps)

set (OTIO_IMATH_TARGETS
    # For OpenEXR/Imath 3.x:
    $<TARGET_NAME_IF_EXISTS:Imath::Imath>
    $<TARGET_NAME_IF_EXISTS:Imath::Half>
    # For OpenEXR >= 2.4/2.5 with reliable exported targets
    $<TARGET_NAME_IF_EXISTS:IlmBase::Imath>
    $<TARGET_NAME_IF_EXISTS:IlmBase::Half>
    $<TARGET_NAME_IF_EXISTS:IlmBase::Iex>
    # For OpenEXR <= 2.3:
    ${ILMBASE_LIBRARIES})

add_subdirectory(src/opentime)
add_subdirectory(src/opentimelineio)

if(BUILD_TESTING)
	add_subdirectory(tests)
endif()

if(OTIO_PYTHON_INSTALL)
    add_subdirectory(src/py-opentimelineio)
endif()

if(OTIO_CXX_EXAMPLES)
    add_subdirectory(examples)
endif()

