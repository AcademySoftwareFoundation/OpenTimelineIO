if (WINDOWS)
cmake_minimum_required(VERSION 3.17)
else()
cmake_minimum_required(VERSION 3.12)
endif()

project(OpenTimelineIO)

#------------------------------------------------------------------------------
# Options

option(OTIO_CXX_COVERAGE "Invoke gcov if available" OFF)
option(OTIO_AUTOMATIC_SUBMODULES "Fetch submodules automatically" ON)
option(OTIO_CXX_INSTALL "Install the cpp bindings" ON)
option(OTIO_PYTHON_INSTALL "Install the python bindings" ON)
option(OTIO_DEPENDENCIES_INSTALL "Install OTIO's C++ header dependencies (any and nonstd)" ON)
option(OTIO_PYTHON_INSTALL_DIR "Python installation dir" "${CMAKE_INSTALL_PREFIX}/python/lib}")
option(OTIO_SHARED_LIBS "Build shared if ON, static otherwise", ON)

if(OTIO_SHARED_LIBS)
    message(INFO, "Building shared libs....")
    set(OTIO_SHARED_OR_STATIC_LIB "SHARED")
else()
    message(INFO, "Building static libs....")
    set(OTIO_SHARED_OR_STATIC_LIB "STATIC")
endif()
if(OTIO_CXX_INSTALL)
    message(INFO, "Install C++ bindings..... ON")
    if(OTIO_DEPENDENCIES_INSTALL)
        message(INFO, "Install any and nonstd for C++.. ON")
    else()
        message(INFO, "Install any and nonstd for C++.. OFF")
    endif()
else()
    message(INFO, "Install C++ bindings..... OFF")
endif()
if(OTIO_PYTHON_INSTALL)
    message(INFO, "Install Python bindings.. ON")
    message(INFO, "  Python install dir..... ", ${OTIO_PYTHON_INSTALL_DIR})
else()
    message(INFO, "Install Python bindings.. OFF")
endif()

#------------------------------------------------------------------------------
# Global language settings

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(MSVC)
	set(PYBIND11_CPP_STANDARD /std:c++11)
	set(CMAKE_CXX_FLAGS "/W4 /EHsc")
else()
	set(PYBIND11_CPP_STANDARD -std=c++11)
	set(CMAKE_CXX_FLAGS "-std=c++11 -Wall")
endif()

if(OTIO_CXX_COVERAGE AND NOT MSVC)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} --coverage")
    # this causes cmake to produce file.gcno instead of file.cpp.gcno
    set(CMAKE_CXX_OUTPUT_EXTENSION_REPLACE 1)
endif()

if (MSVC)
    # Python in debug mode on Windows requires a "d" suffix on the module name,
    # this is also useful for distinguishing libraries built for the debug CRT.
    set(OTIO_DEBUG_POSTFIX "d")
else()
    set(OTIO_DEBUG_POSTFIX "")
endif()

#------------------------------------------------------------------------------
# Fetch or refresh submodules if requested
#
# fetching submodules does not work in Travis, so override the OTIO_UPDATE_SUBMODULES option

if (OTIO_AUTOMATIC_SUBMODULES AND NOT DEFINED ENV{TRAVIS})
    # make sure that git submodules are up to date when building
    find_package(Git QUIET)
    if (GIT_FOUND)
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

