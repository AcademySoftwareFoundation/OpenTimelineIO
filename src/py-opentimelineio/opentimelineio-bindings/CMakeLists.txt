set(_OTIO_HEADER_FILES
    otio_errorStatusHandler.h
    otio_anyDictionary.h
    otio_bindings.h
    otio_utils.h)

pybind11_add_module(_otio
                    otio_errorStatusHandler.cpp
                    otio_anyDictionary.cpp
                    otio_anyVector.cpp
                    otio_bindings.cpp
                    otio_tests.cpp
                    otio_serializableObjects.cpp
                    otio_utils.cpp ${_OTIO_HEADER_FILES})

target_include_directories(_otio 
    PRIVATE pybind11/include
    PRIVATE "${PROJECT_SOURCE_DIR}/src"
    PRIVATE "${PROJECT_SOURCE_DIR}/src/deps"
    PRIVATE "${PROJECT_SOURCE_DIR}/src/deps/optional-lite/include")

target_link_libraries(_otio PUBLIC opentimelineio opentime)

set_target_properties(_otio PROPERTIES
    LIBRARY_OUTPUT_NAME "${modname}"
    DEBUG_POSTFIX "${OTIO_DEBUG_POSTFIX}"
    INSTALL_RPATH "${OTIO_PYTHON_INSTALL_DIR}/opentimelineio")

if(OTIO_PYTHON_INSTALL_DIR)
    install(TARGETS _otio DESTINATION "${OTIO_PYTHON_INSTALL_DIR}/opentimelineio")
endif()

#------------------------------------------------------------------------------
# Install the Python scripts

add_custom_target(py-opentimelineio ALL
    COMMAND ${CMAKE_COMMAND} -E copy_directory
    ${PROJECT_SOURCE_DIR}/src/py-opentimelineio/opentimelineio
    ${OTIO_PYTHON_INSTALL_DIR}/opentimelineio
)

add_dependencies(_otio py-opentimelineio)
