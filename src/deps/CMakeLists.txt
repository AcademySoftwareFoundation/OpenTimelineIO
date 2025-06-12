


#----- Other dependencies

# detect if the submodules haven't been updated
set(DEPS_SUBMODULES pybind11)

if(NOT OTIO_FIND_RAPIDJSON)
    set(DEPS_SUBMODULES ${DEPS_SUBMODULES} rapidjson)
endif()
if(NOT OTIO_FIND_MINIZIP_NG)
    set(DEPS_SUBMODULES ${DEPS_SUBMODULES} minizip-ng)
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

if(NOT OTIO_FIND_MINIZIP_NG)
    set(BUILD_SHARED_LIBS OFF)
    set(CMAKE_POSITION_INDEPENDENT_CODE ON)
    set(MZ_COMPAT OFF)
    set(MZ_ZLIB ON)
    set(MZ_BZIP2 OFF)
    set(MZ_LZMA OFF)
    set(MZ_ZSTD OFF)
    set(MZ_LIBCOMP OFF)
    set(MZ_PKCRYPT OFF)
    set(MZ_WZAES OFF)
    set(MZ_OPENSSL OFF)
    set(MZ_LIBBSD OFF)
    set(MZ_ICONV OFF)
    add_subdirectory(minizip-ng)
endif()
