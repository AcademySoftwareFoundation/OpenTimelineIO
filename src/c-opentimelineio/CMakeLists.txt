if (WINDOWS)
    cmake_minimum_required(VERSION 3.17.0)
else ()
    cmake_minimum_required(VERSION 3.9.4)
endif ()

project(COPENTIMELINEIO_ROOT)

enable_testing()

add_subdirectory(../../ build)
add_subdirectory(opentime-bindings)
add_subdirectory(opentimelineio-bindings)
add_subdirectory(tests)
