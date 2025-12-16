


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
    set(BUILD_SHARED_LIBS OFF)
    add_subdirectory(Imath)
endif()

if(NOT OTIO_FIND_MINIZIP_NG)
    set(BUILD_SHARED_LIBS OFF)
    set(BUILD_TESTING OFF)
    set(CMAKE_POSITION_INDEPENDENT_CODE ON)
    set(MZ_COMPAT ON)
    set(MZ_ZLIB ON)
    set(MZ_ZLIB_FLAVOR zlib-ng)
    set(MZ_BZIP2 OFF)
    set(MZ_LZMA OFF)
    set(MZ_ZSTD OFF)
    set(MZ_LIBCOMP OFF)
    set(MZ_PKCRYPT OFF)
    set(MZ_WZAES OFF)
    set(MZ_OPENSSL OFF)
    set(MZ_LIBBSD OFF)
    set(MZ_ICONV OFF)
    set(MZ_FETCH_LIBS OFF)
    add_subdirectory(zlib-ng)
    add_subdirectory(minizip-ng)
endif()
