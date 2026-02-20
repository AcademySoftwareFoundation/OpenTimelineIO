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
