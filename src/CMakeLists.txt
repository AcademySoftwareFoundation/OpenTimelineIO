cmake_minimum_required(VERSION 2.8.12)
# project(app_project)

set(PYBIND11_CPP_STANDARD -std=c++11)
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_FLAGS "-std=c++11 -Wall -Wno-deprecated-register")

add_subdirectory(deps)
add_subdirectory(opentime)
add_subdirectory(opentimelineio)
add_subdirectory(py-opentimelineio)






