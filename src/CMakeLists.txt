cmake_minimum_required(VERSION 2.8.12)

option(CXX_COVERAGE "CXX_COVERAGE" OFF)

set(PYBIND11_CPP_STANDARD -std=c++11)
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_FLAGS "-std=c++11 -Wall -Wno-deprecated-register")

if(CXX_COVERAGE)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fprofile-arcs -ftest-coverage --coverage")
    set(CMAKE_CXX_OUTPUT_EXTENSION_REPLACE 1)
endif()

add_subdirectory(deps)
add_subdirectory(opentime)
add_subdirectory(opentimelineio)

if (OTIO_PYTHON_INSTALL)
    add_subdirectory(py-opentimelineio)
endif (OTIO_PYTHON_INSTALL)








