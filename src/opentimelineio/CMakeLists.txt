#------------------------------------------------------------------------------
# opentimelineio/CMakeLists.txt

set(OPENTIMELINEIO_HEADER_FILES
    any.h
    anyDictionary.h
    anyVector.h
    clip.h
    composable.h
    composition.h
    deserialization.h
    effect.h
    errorStatus.h
    externalReference.h
    freezeFrame.h
    gap.h
    generatorReference.h
    imageSequenceReference.h
    item.h
    linearTimeWarp.h
    marker.h
    mediaReference.h
    missingReference.h
    optional.h
    safely_typed_any.h
    serializableCollection.h
    serializableObject.h
    serializableObjectWithMetadata.h
    serialization.h
    stack.h
    stackAlgorithm.h
    timeEffect.h
    timeline.h
    track.h
    trackAlgorithm.h
    transition.h
    typeRegistry.h
    unknownSchema.h
    vectorIndexing.h
    version.h)

add_library(opentimelineio ${OTIO_SHARED_OR_STATIC_LIB} 
    clip.cpp
    composable.cpp
    composition.cpp
    deserialization.cpp
    effect.cpp
    errorStatus.cpp
    externalReference.cpp
    freezeFrame.cpp
    gap.cpp
    generatorReference.cpp
    imageSequenceReference.cpp
    item.cpp
    linearTimeWarp.cpp
    marker.cpp
    mediaReference.cpp
    missingReference.cpp
    safely_typed_any.cpp
    serializableCollection.cpp
    serializableObject.cpp
    serializableObjectWithMetadata.cpp
    serialization.cpp
    stack.cpp
    stackAlgorithm.cpp
    stringUtils.cpp
    stringUtils.h # stringUtils.h is a private header
    timeEffect.cpp
    timeline.cpp
    track.cpp
    trackAlgorithm.cpp
    transition.cpp
    typeRegistry.cpp
    unknownSchema.cpp 
    CORE_VERSION_MAP.cpp
    ${OPENTIMELINEIO_HEADER_FILES})

add_library(OTIO::opentimelineio ALIAS opentimelineio)

target_include_directories(opentimelineio
    PRIVATE       "${IMATH_INCLUDES}"
                  "${PROJECT_SOURCE_DIR}/src"
                  "${PROJECT_SOURCE_DIR}/src/deps"
                  "${PROJECT_SOURCE_DIR}/src/deps/optional-lite/include"
                  "${PROJECT_SOURCE_DIR}/src/deps/rapidjson/include"
                  "${IMATH_INCLUDES}")

target_link_libraries(opentimelineio 
    PUBLIC opentime ${OTIO_IMATH_TARGETS})

set_target_properties(opentimelineio PROPERTIES
    DEBUG_POSTFIX "${OTIO_DEBUG_POSTFIX}"
    LIBRARY_OUTPUT_NAME "opentimelineio"
    POSITION_INDEPENDENT_CODE TRUE
    WINDOWS_EXPORT_ALL_SYMBOLS true)

if(APPLE)
    set_target_properties(opentimelineio PROPERTIES 
        INSTALL_NAME_DIR "@loader_path"
        MACOSX_RPATH ON)
endif()

# override any global CXX_FLAGS settings that came from dependencies
target_compile_options(opentimelineio PRIVATE
     $<$<OR:$<CXX_COMPILER_ID:Clang>,$<CXX_COMPILER_ID:AppleClang>,$<CXX_COMPILER_ID:GNU>>:
     -Wall>
     $<$<CXX_COMPILER_ID:MSVC>: /W4>
     $<$<CXX_COMPILER_ID:MSVC>: /EHsc>
)

if(OTIO_CXX_INSTALL)
    install(FILES ${OPENTIMELINEIO_HEADER_FILES} 
            DESTINATION "${OTIO_RESOLVED_CXX_INSTALL_DIR}/include/opentimelineio")

    set(OPENTIMELINEIO_INCLUDES ${OTIO_RESOLVED_CXX_INSTALL_DIR}/include)
    if(OTIO_DEPENDENCIES_INSTALL)
        list(APPEND OPENTIMELINEIO_INCLUDES ${OTIO_RESOLVED_CXX_INSTALL_DIR}/include/opentimelineio/deps)
    endif()

    install(TARGETS opentimelineio
           EXPORT OpenTimelineIOConfig
           INCLUDES DESTINATION "${OPENTIMELINEIO_INCLUDES}"
           ARCHIVE DESTINATION "${OTIO_RESOLVED_CXX_DYLIB_INSTALL_DIR}"
           LIBRARY DESTINATION "${OTIO_RESOLVED_CXX_DYLIB_INSTALL_DIR}"
           RUNTIME DESTINATION "${OTIO_RESOLVED_CXX_DYLIB_INSTALL_DIR}")

    install(EXPORT OpenTimelineIOConfig
           DESTINATION "${OTIO_RESOLVED_CXX_INSTALL_DIR}/share/opentimelineio"
           NAMESPACE OTIO:: )
endif()
