set(OPENTIME_HEADER_FILES
    errorStatus.h
    rationalTime.h
    stringPrintf.h
    timeRange.h
    timeTransform.h)

add_library(opentime SHARED
            errorStatus.cpp
            rationalTime.cpp
            ${OPENTIME_HEADER_FILES})

target_include_directories(opentime PUBLIC "${PROJECT_SOURCE_DIR}/src")
set_target_properties(opentime PROPERTIES INSTALL_RPATH "${CMAKE_INSTALL_PREFIX}/lib"
			MACOSX_RPATH true)
install(TARGETS opentime LIBRARY DESTINATION lib)
install(FILES ${OPENTIME_HEADER_FILES} DESTINATION include/opentime)




