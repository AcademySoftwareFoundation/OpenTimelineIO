cmake_minimum_required(VERSION 2.8.12)
project(opentime)

add_subdirectory(pybind11)
pybind11_add_module(opentime opentime.cpp py_opentime.cpp)
