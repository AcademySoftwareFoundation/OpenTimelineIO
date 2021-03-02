#------------------------------------------------------------------------------
# py-opentimelineio/opentimelineio-bindings/CMakeLists.txt

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
                    otio_imath.cpp
                    otio_tests.cpp
                    otio_serializableObjects.cpp
                    otio_utils.cpp 
                    ${_OTIO_HEADER_FILES})

target_include_directories(_otio 
    PRIVATE pybind11/include
    PRIVATE "${PROJECT_SOURCE_DIR}/src"
    PRIVATE "${PROJECT_SOURCE_DIR}/src/deps"
    PRIVATE "${PROJECT_SOURCE_DIR}/src/deps/optional-lite/include"
)

target_link_libraries(_otio PUBLIC opentimelineio opentime)

# The version of pybind11 we are currently using generates an overwhelming number of
# compiler warnings; until we update pybind11, suprress the warnings:
target_compile_options(_otio PRIVATE
     $<$<OR:$<CXX_COMPILER_ID:Clang>,$<CXX_COMPILER_ID:AppleClang>,$<CXX_COMPILER_ID:GNU>>:
     -Wno-range-loop-analysis>
     $<$<OR:$<CXX_COMPILER_ID:Clang>,$<CXX_COMPILER_ID:AppleClang>,$<CXX_COMPILER_ID:GNU>>:
     -Wno-unused-value>
     $<$<CXX_COMPILER_ID:MSVC>: /EHsc>
)

set_target_properties(_otio PROPERTIES
    LIBRARY_OUTPUT_NAME "_otio"
    DEBUG_POSTFIX "${OTIO_DEBUG_POSTFIX}")

if(APPLE)
    set_target_properties(_otio PROPERTIES 
        INSTALL_NAME_DIR "@loader_path"
        MACOSX_RPATH ON)
elseif(UNIX)
    set_target_properties(_otio PROPERTIES 
        INSTALL_RPATH "$ORIGIN"
        INSTALL_RPATH_USE_LINK_PATH OFF)
endif()

install(TARGETS _otio 
        ARCHIVE DESTINATION "${OTIO_RESOLVED_CXX_DYLIB_INSTALL_DIR}"
        LIBRARY DESTINATION "${OTIO_RESOLVED_CXX_DYLIB_INSTALL_DIR}"
        RUNTIME DESTINATION "${OTIO_RESOLVED_CXX_DYLIB_INSTALL_DIR}")


#------------------------------------------------------------------------------
# Install the Python scripts
# TODO as part of the installation step, the python files can be precompiled
# by executing
#        python -m compileall <file_1>.py <file_n>.py

# TODO install the plugins and adapters

add_custom_target(py-opentimelineio ALL
    COMMAND ${CMAKE_COMMAND} -E copy_directory
    ${PROJECT_SOURCE_DIR}/src/py-opentimelineio/opentimelineio
    ${OTIO_RESOLVED_PYTHON_INSTALL_DIR}/opentimelineio
)

add_dependencies(_otio py-opentimelineio)

if(OTIO_INSTALL_COMMANDLINE_TOOLS)
    install(DIRECTORY DESTINATION ${OTIO_RESOLVED_PYTHON_INSTALL_DIR}/bin)

    set(OTIO_COMMANDLINE_TOOLS otiocat otioconvert otiostat otiopluginfo)
    foreach(OTIO_TOOL ${OTIO_COMMANDLINE_TOOLS})
        set(fname ${CMAKE_CURRENT_BINARY_DIR}/${OTIO_TOOL})
        if (WIN32)
            set(fname "${fname}.bat")
            file(WRITE ${fname}
                "@python -c \"exec(\\\"import opentimelineio.console\\nopentimelineio.console.${OTIO_TOOL}.main()\\\")\" %*\n")
        else()
            file(WRITE ${fname}
                "#!/bin/sh\npython -c \"exec(\\\"import opentimelineio.console\\nopentimelineio.console.${OTIO_TOOL}.main()\\\")\" $*\n")
        endif()
        list(APPEND OTIO_SCRIPT_PATHS "${fname}")
    endforeach()

    # TODO install otioview
    # TODO run autogen_serialized_datamodel
    # TODO run autogen_plugin_documentation
    # TODO generate a setup.py automatically

    install(
        FILES ${OTIO_SCRIPT_PATHS}
        PERMISSIONS OWNER_EXECUTE OWNER_WRITE OWNER_READ GROUP_EXECUTE GROUP_READ WORLD_EXECUTE WORLD_READ
        DESTINATION ${OTIO_RESOLVED_PYTHON_INSTALL_DIR}/bin
    )
endif()
