if (WINDOWS)
    cmake_minimum_required(VERSION 3.17)
else()
    cmake_minimum_required(VERSION 3.12)
endif()

#------------------------------------------------------------------------------
# Project Meta data
# TODO: read this information from a configuration file, here, and in setup.py

set(OTIO_VERSION_MAJOR "0")
set(OTIO_VERSION_MINOR "14")
set(OTIO_VERSION_PATCH "0")
set(OTIO_VERSION ${OTIO_VERSION_MAJOR}.${OTIO_VERSION_MINOR}.${OTIO_VERSION_PATCH})

set(OTIO_AUTHOR       "Contributors to the OpenTimelineIO project")
set(OTIO_AUTHOR_EMAIL "opentimelineio@pixar.com")
set(OTIO_LICENSE      "Modified Apache 2.0 License")

project(OpenTimelineIO VERSION ${OTIO_VERSION} LANGUAGES C CXX)

#------------------------------------------------------------------------------
# Options
# Add all options and settings here for all subprojects to aid in project
# maintenance and troubleshooting

# Installation options
option(OTIO_CXX_INSTALL    "Install the cpp bindings" ON)
option(OTIO_PYTHON_INSTALL "Install the python bindings" ON)
option(OTIO_DEPENDENCIES_INSTALL "Install OTIO's C++ header dependencies (any and nonstd)" ON)
option(OTIO_INSTALL_COMMANDLINE_TOOLS "Install the OTIO command line tools" ON)
set(OTIO_PYTHON_INSTALL_DIR "" CACHE STRING "Python installation dir (such as the site-packages dir)")

# Build options
option(OTIO_SHARED_LIBS  "Build shared if ON, static if OFF" ON)
option(OTIO_CXX_COVERAGE "Invoke code coverage if gcov is available" OFF)
option(OTIO_AUTOMATIC_SUBMODULES "Fetch submodules automatically" ON)

#------------------------------------------------------------------------------
# Set option dependent variables

if(OTIO_PYTHON_INSTALL)
    # reconcile install directories for builds incorporating python in order
    # that default behaviors match a reasonable expectation, as follows:
    #
    # if nothing has been set, 
    #   Python: ${OTIO_RESOLVED_PYTHON_INSTALL_DIR}/opentimelineio
    #   C++:    ${OTIO_RESOLVED_PYTHON_INSTALL_DIR}/opentimelineio/cxx-libs
    # if only CMAKE_INSTALL_PREFIX has been set,
    #   Python: ${CMAKE_INSTALL_PREFIX}/opentimelineio/python
    #   C++:    ${CMAKE_INSTALL_PREFIX}/opentimelineio
    # if only OTIO_PYTHON_INSTALL_DIR has been set,
    #   Python: ${OTIO_PYTHON_INSTALL_DIR}/opentimelineio
    #   C++:    ${OTIO_PYTHON_INSTALL_DIR}/opentimelineio/cxx-libs
    #
    # In a python install, the dylibs/dlls need to be installed where __init.py
    # can find them, rather as part of the C++ sdk package; so the variable 
    # OTIO_RESOLVED_CXX_DYLIB_INSTALL_DIR indicates where that is.
    #
    if(OTIO_PYTHON_INSTALL_DIR STREQUAL "" AND CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)
        # neither install directory supplied from the command line
        find_package(Python REQUIRED COMPONENTS Interpreter Development)
        set(OTIO_RESOLVED_PYTHON_INSTALL_DIR "${OTIO_RESOLVED_PYTHON_INSTALL_DIR}")
        set(OTIO_RESOLVED_CXX_INSTALL_DIR "${OTIO_RESOLVED_PYTHON_INSTALL_DIR}/opentimelineio/cxx-libs")
        set(OTIO_RESOLVED_CXX_DYLIB_INSTALL_DIR "${OTIO_RESOLVED_PYTHON_INSTALL_DIR}/opentimelineio")
        message(INFO, "OTIO Defaulting both Python and C++ install to ${OTIO_RESOLVED_PYTHON_INSTALL_DIR}")
    else()
        # either python_install or install_prefix have been set
        if(OTIO_PYTHON_INSTALL_DIR_INITIALIZED_TO_DEFAULT)
            # CMAKE_INSTALL_PREFIX was set, so install the python components there
            set(OTIO_RESOLVED_PYTHON_INSTALL_DIR "${CMAKE_INSTALL_PREFIX}/python")
            set(OTIO_RESOLVED_CXX_INSTALL_DIR "${CMAKE_INSTALL_PREFIX}")

            # In order to not require setting $PYTHONPATH to point at the .so,
            # the shared libraries are installed into the python library 
            # location.
            set(OTIO_RESOLVED_CXX_DYLIB_INSTALL_DIR "${OTIO_RESOLVED_PYTHON_INSTALL_DIR}/opentimelineio")
            message(INFO, "OTIO Defaulting Python install to ${OTIO_RESOLVED_PYTHON_INSTALL_DIR}")
            message(INFO, "Note: C++ linkable-shared libraries can be found: ${CMAKE_INSTALL_PREFIX}/opentimelineio")
        else()
            # OTIO_PYTHON_INSTALL_DIR was set, so install everything into the python package
            set(OTIO_RESOLVED_PYTHON_INSTALL_DIR "${OTIO_PYTHON_INSTALL_DIR}")
            set(OTIO_RESOLVED_CXX_INSTALL_DIR "${OTIO_PYTHON_INSTALL_DIR}/opentimelineio/cxx-sdk")
            set(OTIO_RESOLVED_CXX_DYLIB_INSTALL_DIR "${OTIO_PYTHON_INSTALL_DIR}/opentimelineio")
            message(INFO, "OTIO Defaulting C++ install to ${OTIO_PYTHON_INSTALL_DIR}")
        endif()
    endif()
else()
    set(OTIO_RESOLVED_CXX_INSTALL_DIR "${CMAKE_INSTALL_PREFIX}")
    set(OTIO_RESOLVED_CXX_DYLIB_INSTALL_DIR "${CMAKE_INSTALL_PREFIX}/lib")
    message(INFO, "OTIO C++ installing to ${CMAKE_INSTALL_PREFIX}")
endif()

set(CMAKE_INSTALL_INCLUDEDIR "${OTIO_RESOLVED_CXX_INSTALL_DIR}/include")

if(OTIO_SHARED_LIBS)
    message(INFO, "Building shared libs.")
    set(OTIO_SHARED_OR_STATIC_LIB "SHARED")
else()
    message(INFO, "Building static libs.")
    set(OTIO_SHARED_OR_STATIC_LIB "STATIC")
    if (OTIO_PYTHON_INSTALL AND NOT MSVC)
        # TODO: add explicit visibility decorations for OpenTime and OpentimelineIO to resolve
        # this issue. For reference, there is discussion here: https://gist.github.com/ax3l/ba17f4bb1edb5885a6bd01f58de4d542
        message(WARNING, "pybind11 forces visibility flags, used shared libraries instead.")
    endif()
endif()

if(OTIO_CXX_INSTALL)
    message(INFO, "Installing C++ bindings to: ${OTIO_RESOLVED_CXX_INSTALL_DIR}")
    message(INFO, "Installing C++ dynamic libraries to: ${OTIO_RESOLVED_CXX_DYLIB_INSTALL_DIR}")

    if(OTIO_DEPENDENCIES_INSTALL)
        message(INFO, "  Installing 'any' and 'nonstd' for C++.. (OTIO_DEPENDENCIES_INSTALL:ON)")
    else()
        message(INFO, "  Not installing any and nonstd for C++.. (OTIO_DEPENDENCIES_INSTALL:OFF)")
    endif()
else()
    message(INFO, "Install C++ bindings..... OFF")
endif()

if(OTIO_PYTHON_INSTALL)
    message(INFO, "Installing Python bindings to: ${OTIO_RESOLVED_PYTHON_INSTALL_DIR}")
else()
    message(INFO, "Install Python bindings.. OFF")
endif()

#------------------------------------------------------------------------------
# Global language settings

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(MSVC)
	set(PYBIND11_CPP_STANDARD /std:c++11)
else()
	set(PYBIND11_CPP_STANDARD -std=c++11)
endif()

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
        message(INFO, "Checking git repo is available:")
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
# Build the dependencies and components

add_subdirectory(src/deps)
add_subdirectory(src/opentime)
add_subdirectory(src/opentimelineio)

if(OTIO_PYTHON_INSTALL)
    add_subdirectory(src/py-opentimelineio)
endif()
