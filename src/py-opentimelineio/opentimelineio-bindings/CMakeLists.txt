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
set_target_properties(_otio PROPERTIES INSTALL_RPATH "${CMAKE_INSTALL_PREFIX}/lib")
if (OTIO_PYTHON_OTIO_DIR)
    install(TARGETS _otio DESTINATION "${OTIO_PYTHON_OTIO_DIR}")
endif (OTIO_PYTHON_OTIO_DIR)

