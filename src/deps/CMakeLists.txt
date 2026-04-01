


#----- Other dependencies

# detect if the submodules haven't been updated
if(NOT OTIO_FIND_PYBIND11 AND OTIO_PYTHON_INSTALL)
    # pybind11 only needed when building Python bindings
    set(DEPS_SUBMODULES ${DEPS_SUBMODULES} pybind11)
endif()

if(NOT OTIO_FIND_IMATH)
    set(DEPS_SUBMODULES ${DEPS_SUBMODULES} Imath)
endif()

if(NOT OTIO_FIND_RAPIDJSON)
    set(DEPS_SUBMODULES ${DEPS_SUBMODULES} rapidjson)
endif()

foreach(submodule IN LISTS DEPS_SUBMODULES)
    file(GLOB SUBMOD_CONTENTS "${submodule}/*")
    list(LENGTH SUBMOD_CONTENTS SUBMOD_CONTENT_LEN)
    if(SUBMOD_CONTENT_LEN EQUAL 0)
        message(
            FATAL_ERROR "Error: the submodule ${submodule} is empty.  You may \
            need to install git and run: 'git submodule update' to remedy this."
        )
    endif()
endforeach()

if(NOT OTIO_FIND_PYBIND11 AND OTIO_PYTHON_INSTALL)
    # pybind11 only needed when building Python bindings
    add_subdirectory(pybind11)
endif()

# Calling add_subdirectory(rapidjson) will try to build
# such as example/CMakeLists.txt which has not been updated for CMake
# 4.0 compatibility and will break our builds. rapidjson is a header
# only library, code in src/opentimelineio/ only needs it to be present
# to pick up the headers.
# If building rapidjson ends up required, the CMake variables:
#
# RAPIDJSON_BUILD_DOC
# RAPIDJSON_BUILD_EXAMPLES
# RAPIDJSON_BUILD_TESTS
#
# coud be overriden from ON to OFF to avoid trying to build
# subcomponents we don't need.

if(NOT OTIO_FIND_IMATH)
    # preserve BUILD_SHARED_LIBS options for this project, but set it off for Imath
    option(BUILD_SHARED_LIBS "Build shared libraries" ON)
    set(BUILD_SHARED_LIBS OFF)

    # If we do not want Imath to install headers and CMake files use the EXCLUDE_FROM_ALL option
    if(OTIO_CXX_INSTALL AND OTIO_DEPENDENCIES_INSTALL)
        add_subdirectory(Imath)
    else()
        add_subdirectory(Imath EXCLUDE_FROM_ALL)
    endif()
endif()

