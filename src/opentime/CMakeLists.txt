#------------------------------------------------------------------------------
# opentime/CMakeLists.txt

set(OPENTIME_HEADER_FILES
    errorStatus.h
    rationalTime.h
    stringPrintf.h
    timeRange.h
    timeTransform.h
    version.h)

add_library(opentime ${OTIO_SHARED_OR_STATIC_LIB} 
            errorStatus.cpp
            rationalTime.cpp
            ${OPENTIME_HEADER_FILES})

add_library(OTIO::opentime ALIAS opentime)

target_include_directories(opentime PRIVATE "${PROJECT_SOURCE_DIR}/src")

set_target_properties(opentime PROPERTIES 
    DEBUG_POSTFIX "${OTIO_DEBUG_POSTFIX}"
    LIBRARY_OUTPUT_NAME "opentime"
    POSITION_INDEPENDENT_CODE TRUE
    WINDOWS_EXPORT_ALL_SYMBOLS true)

if(BUILD_SHARED_LIBS)
    set_target_properties(opentime PROPERTIES
        SOVERSION ${OTIO_SOVERSION}
        VERSION ${OTIO_VERSION})
endif()

if(APPLE)
    set_target_properties(opentime PROPERTIES 
        INSTALL_NAME_DIR "@loader_path"
        MACOSX_RPATH ON)
endif()

target_compile_options(opentime PRIVATE
     $<$<OR:$<CXX_COMPILER_ID:Clang>,$<CXX_COMPILER_ID:AppleClang>,$<CXX_COMPILER_ID:GNU>>:
     -Wall>
     $<$<CXX_COMPILER_ID:MSVC>: /W4>
     $<$<CXX_COMPILER_ID:MSVC>: /EHsc>
)

if(OTIO_CXX_INSTALL)
    install(FILES ${OPENTIME_HEADER_FILES} 
            DESTINATION "${OTIO_RESOLVED_CXX_INSTALL_DIR}/include/opentime")

    install(TARGETS opentime
            EXPORT OpenTimeTargets
            INCLUDES DESTINATION "${OTIO_RESOLVED_CXX_INSTALL_DIR}/include"
            ARCHIVE DESTINATION "${OTIO_RESOLVED_CXX_DYLIB_INSTALL_DIR}"
            LIBRARY DESTINATION "${OTIO_RESOLVED_CXX_DYLIB_INSTALL_DIR}"
            RUNTIME DESTINATION "${OTIO_RESOLVED_CXX_DYLIB_INSTALL_DIR}")

    install(EXPORT OpenTimeTargets
            DESTINATION "${OTIO_RESOLVED_CXX_INSTALL_DIR}/share/opentime"
            NAMESPACE OTIO:: )

    include(CMakePackageConfigHelpers)
    configure_package_config_file(
        ${CMAKE_CURRENT_SOURCE_DIR}/OpenTimeConfig.cmake.in
        ${CMAKE_CURRENT_BINARY_DIR}/OpenTimeConfig.cmake
        INSTALL_DESTINATION
            ${OTIO_RESOLVED_CXX_INSTALL_DIR}/share/opentime
        NO_SET_AND_CHECK_MACRO
        NO_CHECK_REQUIRED_COMPONENTS_MACRO
    )

    install(
        FILES
            ${CMAKE_CURRENT_BINARY_DIR}/OpenTimeConfig.cmake
        DESTINATION
            ${OTIO_RESOLVED_CXX_INSTALL_DIR}/share/opentime
    )
endif()

