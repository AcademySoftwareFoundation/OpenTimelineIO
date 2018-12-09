cmake_minimum_required(VERSION 2.8.12)
# project(app_project)

set(PYBIND11_CPP_STANDARD -std=c++11)
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_FLAGS "-std=c++11 -Wall -Wno-deprecated-register")

# set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/lib)

# add_subdirectory("../pybind11" "${CMAKE_CURRENT_BINARY_DIR}/pybind11_build")
add_subdirectory(deps/pybind11)
add_subdirectory(opentime)
add_subdirectory(opentimelineio)
add_subdirectory(py-opentimelineio)






