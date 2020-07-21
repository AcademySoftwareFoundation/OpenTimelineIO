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
    INSTALL_RPATH "${OTIO_PYTHON_INSTALL_DIR}/lib/opentimelineio")

if(OTIO_PYTHON_INSTALL_DIR)
    install(TARGETS _otio DESTINATION "${OTIO_PYTHON_INSTALL_DIR}/lib/opentimelineio")
endif()

#------------------------------------------------------------------------------
# Install the Python scripts

add_custom_target(py-opentimelineio ALL
    COMMAND ${CMAKE_COMMAND} -E copy_directory
    ${PROJECT_SOURCE_DIR}/src/py-opentimelineio/opentimelineio
    ${OTIO_PYTHON_INSTALL_DIR}/lib/opentimelineio
)

add_dependencies(_otio py-opentimelineio)

install(DIRECTORY DESTINATION ${OTIO_PYTHON_INSTALL_DIR}/bin)

if(WIN32)
    set(OTIO_SCRIPT_SUFFIX ".bat")
else()
    set(OTIO_SCRIPT_SUFFIX "")
endif()

set(OTIO_SCRIPTS otioview otiocat otioconvert otiostat otiopluginfo)
foreach(OTIO_SCRIPT ${OTIO_SCRIPTS})
    set(fname ${CMAKE_CURRENT_BINARY_DIR}/${OTIO_SCRIPT}${OTIO_SCRIPT_SUFFIX})
    file(WRITE ${fname}
        "#!/bin/sh\npython -c \"exec(\\\"import opentimelineio.console\\nopentimelineio.console.${OTIO_SCRIPT}.main()\\\")\"\n")
    list(APPEND OTIO_SCRIPT_PATHS "${fname}")
endforeach()

install(
    FILES ${OTIO_SCRIPT_PATHS}
    PERMISSIONS OWNER_EXECUTE OWNER_WRITE OWNER_READ GROUP_EXECUTE GROUP_READ WORLD_EXECUTE WORLD_READ
    DESTINATION ${OTIO_PYTHON_INSTALL_DIR}/bin
)
