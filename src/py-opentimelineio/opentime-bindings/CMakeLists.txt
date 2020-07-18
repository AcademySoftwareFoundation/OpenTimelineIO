pybind11_add_module(_opentime
                    opentime_bindings.cpp
                    opentime_rationalTime.cpp
                    opentime_timeRange.cpp
                    opentime_timeTransform.cpp
                    opentime_bindings.h)

target_include_directories(_opentime PUBLIC pybind11/include)
target_link_libraries(_opentime PUBLIC opentimelineio opentime)

set_target_properties(_opentime PROPERTIES
    LIBRARY_OUTPUT_NAME "${MODNAME}"
    DEBUG_POSTFIX "${OTIO_DEBUG_POSTFIX}"
    INSTALL_RPATH "${OTIO_PYTHON_INSTALL_DIR}/python/lib")

if (OTIO_PYTHON_INSTALL_DIR)
    install(TARGETS _opentime DESTINATION "${OTIO_PYTHON_INSTALL_DIR}")
endif()

