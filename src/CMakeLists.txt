cmake_minimum_required(VERSION 2.8.12)

set(PYBIND11_CPP_STANDARD -std=c++11)
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_FLAGS "-std=c++11 -Wall -Wno-deprecated-register")

# make sure that git submodules are up to date when building
find_package(Git QUIET)
# XXX this is broken for travis builds
if (GIT_FOUND AND NOT DEFINED ENV{TRAVIS})
    # you might want to turn this off if you're working in one of the submodules
    # or trying it out with a different version of the submodule
    option(GIT_UPDATE_SUBMODULES "Update submodules each build" ON)
    if (GIT_UPDATE_SUBMODULES)
        message(
            STATUS "Updating git submodules to make sure they are up to date"
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

option(CXX_COVERAGE "CXX_COVERAGE" OFF)
if(CXX_COVERAGE)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} --coverage")
    # this makes it so cmake produces file.gcno instead of file.cpp.gcno
    set(CMAKE_CXX_OUTPUT_EXTENSION_REPLACE 1)
endif()

add_subdirectory(deps)
add_subdirectory(opentime)
add_subdirectory(opentimelineio)

if (OTIO_PYTHON_INSTALL)
    add_subdirectory(py-opentimelineio)
endif (OTIO_PYTHON_INSTALL)
