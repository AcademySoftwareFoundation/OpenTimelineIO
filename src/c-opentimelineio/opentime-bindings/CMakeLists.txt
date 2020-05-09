set(OPENTIME_HEADER_FILES
    include/copentime/timeRange.h
    include/copentime/rationalTime.h
    )

add_library(copentime SHARED
            src/timeRange.cpp
            src/rationalTime.cpp
            ${OPENTIME_HEADER_FILES})

target_include_directories(copentime PUBLIC
 "${PROJECT_SOURCE_DIR}/../"
 "${PROJECT_SOURCE_DIR}/opentime-bindings/include/")
target_link_libraries(copentime opentime)
set_target_properties(opentime PROPERTIES INSTALL_RPATH "${CMAKE_INSTALL_PREFIX}/lib"
			MACOSX_RPATH true WINDOWS_EXPORT_ALL_SYMBOLS true)
install(TARGETS copentime
        RUNTIME DESTINATION bin
        LIBRARY DESTINATION lib)

if (NOT OTIO_CXX_NOINSTALL)
    install(FILES ${OPENTIME_HEADER_FILES} DESTINATION include/copentime)
endif (NOT OTIO_CXX_NOINSTALL)
