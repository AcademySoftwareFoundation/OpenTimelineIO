#------------------------------------------------------------------------------
# py-opentimelineio/opentime-bindings/CMakeLists.txt

pybind11_add_module(_opentime
                    opentime_bindings.cpp
                    opentime_rationalTime.cpp
                    opentime_timeRange.cpp
                    opentime_timeTransform.cpp
                    opentime_bindings.h)

target_include_directories(_opentime 
    PRIVATE pybind11/include
    PRIVATE "${PROJECT_SOURCE_DIR}/src"
    PRIVATE "${PROJECT_SOURCE_DIR}/src/deps"
    PRIVATE "${PROJECT_SOURCE_DIR}/src/deps/optional-lite/include"
    PRIVATE "${CMAKE_BINARY_DIR}/src"
)

target_link_libraries(_opentime PUBLIC opentimelineio opentime)

set_target_properties(_opentime PROPERTIES
    LIBRARY_OUTPUT_NAME "_opentime"
    DEBUG_POSTFIX "${OTIO_DEBUG_POSTFIX}")

# The version of pybind11 we are currently using generates an overwhelming number of
# compiler warnings; until we update pybind11, suprress the warnings:
target_compile_options(_opentime PRIVATE
    $<$<OR:$<CXX_COMPILER_ID:Clang>,$<CXX_COMPILER_ID:AppleClang>,$<CXX_COMPILER_ID:GNU>>:
        -Wno-range-loop-analysis>
    $<$<OR:$<CXX_COMPILER_ID:Clang>,$<CXX_COMPILER_ID:AppleClang>,$<CXX_COMPILER_ID:GNU>>:
        -Wno-unused-value>
    $<$<CXX_COMPILER_ID:MSVC>: /EHsc>
)

if(APPLE)
    set_target_properties(_opentime PROPERTIES 
        INSTALL_NAME_DIR "@loader_path"
        MACOSX_RPATH ON)
elseif(UNIX)
    set_target_properties(_opentime PROPERTIES 
        INSTALL_RPATH "$ORIGIN"
        INSTALL_RPATH_USE_LINK_PATH OFF)
endif()

install(TARGETS _opentime
        ARCHIVE DESTINATION "${OTIO_RESOLVED_CXX_DYLIB_INSTALL_DIR}"
        LIBRARY DESTINATION "${OTIO_RESOLVED_CXX_DYLIB_INSTALL_DIR}"
        RUNTIME DESTINATION "${OTIO_RESOLVED_CXX_DYLIB_INSTALL_DIR}")
