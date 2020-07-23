pybind11_add_module(_opentime
                    opentime_bindings.cpp
                    opentime_rationalTime.cpp
                    opentime_timeRange.cpp
                    opentime_timeTransform.cpp
                    opentime_bindings.h)

target_include_directories(_opentime 
    PRIVATE pybind11/include
    PRIVATE "${PROJECT_SOURCE_DIR}/src"
    PRIVATE "${PROJECT_SOURCE_DIR}/src/deps"
    PRIVATE "${PROJECT_SOURCE_DIR}/src/deps/optional-lite/include")

target_link_libraries(_opentime PUBLIC opentimelineio opentime)

set_target_properties(_opentime PROPERTIES
    LIBRARY_OUTPUT_NAME "${MODNAME}"
    DEBUG_POSTFIX "${OTIO_DEBUG_POSTFIX}")

if(APPLE)
    set_target_properties(_opentime PROPERTIES 
        INSTALL_NAME_DIR "@loader_path"
        MACOSX_RPATH true)
endif()

if (OTIO_PYTHON_INSTALL_DIR)
    install(TARGETS _opentime DESTINATION "${OTIO_PYTHON_INSTALL_DIR}")
endif()

