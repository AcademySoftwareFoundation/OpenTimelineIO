pybind11_add_module(_opentime
                    opentime_bindings.cpp
                    opentime_rationalTime.cpp
                    opentime_timeRange.cpp
                    opentime_timeTransform.cpp
                    opentime_bindings.h)

target_include_directories(_opentime PUBLIC pybind11/include)
target_link_libraries(_opentime PUBLIC opentimelineio opentime)
set_target_properties(_opentime PROPERTIES INSTALL_RPATH "${CMAKE_INSTALL_PREFIX}/lib")

if (OTIO_PYTHON_OTIO_DIR)
    install(TARGETS _opentime DESTINATION "${OTIO_PYTHON_OTIO_DIR}")
endif (OTIO_PYTHON_OTIO_DIR)




