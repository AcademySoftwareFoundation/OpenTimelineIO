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

target_include_directories(_otio PUBLIC pybind11/include)
target_link_libraries(_otio PUBLIC opentimelineio opentime)
set_target_properties(_otio PROPERTIES
    LIBRARY_OUTPUT_NAME "${modname}"
    LIBRARY_OUTPUT_DIRECTORY "${OTIO_PYTHON_INSTALL_DIR}/python${PYTHON_VERSION_MAJOR}_${PYTHON_VERSION_MINOR}"
    DEBUG_POSTFIX "${OTIO_DEBUG_POSTFIX}"
    INSTALL_RPATH "${OTIO_PYTHON_INSTALL_DIR}/python${PYTHON_VERSION_MAJOR}_${PYTHON_VERSION_MINOR}/lib")
if(OTIO_PYTHON_INSTALL_DIR)
    install(TARGETS _otio DESTINATION "${OTIO_PYTHON_INSTALL_DIR}")
endif()

