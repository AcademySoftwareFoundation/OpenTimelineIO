#------------------------------------------------------------------------------
# py-opentimelineio/CMakeLists.txt

add_subdirectory(opentime-bindings)
add_subdirectory(opentimelineio-bindings)

if(OTIO_INSTALL_PYTHON_MODULES)
    # Install pure-python OTIO packages to match PyPI wheel structure
    install(DIRECTORY "${PROJECT_SOURCE_DIR}/src/py-opentimelineio/opentimelineio/"
        DESTINATION "${OTIO_RESOLVED_PYTHON_INSTALL_DIR}/opentimelineio")

    if(OTIO_INSTALL_COMMANDLINE_TOOLS)
        install(DIRECTORY "${PROJECT_SOURCE_DIR}/src/opentimelineview"
            DESTINATION "${OTIO_RESOLVED_PYTHON_INSTALL_DIR}")
    endif()

endif()
