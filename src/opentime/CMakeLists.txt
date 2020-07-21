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

set_target_properties(opentime PROPERTIES POSITION_INDEPENDENT_CODE TRUE)

target_include_directories(opentime PRIVATE "${PROJECT_SOURCE_DIR}/src")

set_target_properties(opentime PROPERTIES 
    DEBUG_POSTFIX "${OTIO_DEBUG_POSTFIX}"
    LIBRARY_OUTPUT_NAME "${MODNAME}"
    INSTALL_RPATH "${CMAKE_INSTALL_PREFIX}/lib"
    MACOSX_RPATH true WINDOWS_EXPORT_ALL_SYMBOLS true)
    
if (OTIO_CXX_INSTALL)
    install(FILES ${OPENTIME_HEADER_FILES} DESTINATION include/opentime)

    install(TARGETS opentime
        EXPORT OpenTimeConfig
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})

    export(TARGETS opentime
        NAMESPACE OTIO::
        FILE "${CMAKE_CURRENT_BINARY_DIR}/OpenTimeConfig.cmake")

    install(EXPORT OpenTimeConfig
        DESTINATION "${CMAKE_INSTALL_PREFIX}"
        NAMESPACE OTIO:: )
endif()

