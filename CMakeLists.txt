if (WINDOWS)
cmake_minimum_required(VERSION 3.17.0)
else()
cmake_minimum_required(VERSION 3.9.4)
endif()

project(OPENTIMELINEIO_ROOT)

add_subdirectory(src)

