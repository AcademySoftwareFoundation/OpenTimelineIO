


#----- Other dependencies

# detect if the submodules haven't been updated
set(DEPS_SUBMODULES pybind11)

if(NOT OTIO_FIND_RAPIDJSON)
    set(DEPS_SUBMODULES ${DEPS_SUBMODULES} rapidjson)
endif()
if(NOT OTIO_FIND_BUNDLE_LIBS)
    set(DEPS_SUBMODULES ${DEPS_SUBMODULES} zlib)
endif()

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

if(NOT OTIO_FIND_BUNDLE_LIBS)
    set(BUILD_SHARED_LIBS OFF)
    set(BUILD_TESTING OFF)
    set(CMAKE_POSITION_INDEPENDENT_CODE ON)
    set(ZLIB_BUILD_TESTING OFF)
    # \bug The zlib shared libraries are only enabled to workaround a bug in
    # the minizip CMake file. We still link to the static zlib.
    #set(ZLIB_BUILD_SHARED OFF)
    set(ZLIB_BUILD_MINIZIP ON)
    set(MINIZIP_BUILD_SHARED OFF)
    set(MINIZIP_BUILD_TESTING OFF)
    set(MINIZIP_ENABLE_BZIP2 OFF)
    add_subdirectory(zlib)
endif()
