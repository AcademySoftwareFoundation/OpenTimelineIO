if (OTIO_PYTHON_INSTALL)
	add_subdirectory(pybind11)
endif()
if (NOT OTIO_CXX_NOINSTALL)
    install(FILES any/any.hpp DESTINATION include/opentimelineio/deps/any)
    install(FILES optional-lite/include/nonstd/optional.hpp
    	DESTINATION include/opentimelineio/deps/nonstd)
endif (NOT OTIO_CXX_NOINSTALL)

# detect if the submodules haven't been updated
set(DEPS_SUBMODULES any optional-lite rapidjson)
if (OTIO_PYTHON_INSTALL)
	set(DEPS_SUBMODULES ${DEPS_SUBMODULES} pybind11)
endif()
foreach (submodule IN LISTS DEPS_SUBMODULES)
    file(GLOB SUBMOD_CONTENTS ${submodule})
    list(LENGTH SUBMOD_CONTENTS SUBMOD_CONTENT_LEN)
    if (SUBMOD_CONTENT_LEN EQUAL 0)
        message(
            FATAL_ERROR "Error: the submodule ${submodule} is empty.  You may \
            need to install git and run: 'git submodule update' to remedy this."
        )
    endif()
endforeach()
