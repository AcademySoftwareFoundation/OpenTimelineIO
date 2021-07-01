
# detect if the submodules haven't been updated
set(DEPS_SUBMODULES any optional-lite pybind11 rapidjson)
foreach(submodule IN LISTS DEPS_SUBMODULES)
    file(GLOB SUBMOD_CONTENTS ${submodule})
    list(LENGTH SUBMOD_CONTENTS SUBMOD_CONTENT_LEN)
    if(SUBMOD_CONTENT_LEN EQUAL 0)
        message(
            FATAL_ERROR "Error: the submodule ${submodule} is empty.  You may \
            need to install git and run: 'git submodule update' to remedy this."
        )
    endif()
endforeach()

if(OTIO_PYTHON_INSTALL)
    add_subdirectory(pybind11)
endif()

if(OTIO_CXX_INSTALL AND OTIO_DEPENDENCIES_INSTALL)
    install(FILES any/any.hpp 
            DESTINATION "${OTIO_RESOLVED_CXX_INSTALL_DIR}/include/opentimelineio/deps/any")
    install(FILES optional-lite/include/nonstd/optional.hpp
    	    DESTINATION "${OTIO_RESOLVED_CXX_INSTALL_DIR}/include/opentimelineio/deps/nonstd")
endif()
