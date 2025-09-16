#------------------------------------------------------------------------------
# opentimelineio/CMakeLists.txt

set(OPENTIMELINEIO_HEADER_FILES
    anyDictionary.h
    anyVector.h
    clip.h
    colorManagementEffects.h
    composable.h
    composition.h
    deserialization.h
    algo/editAlgorithm.h
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
    transformEffects.h
    transition.h
    typeRegistry.h
    unknownSchema.h
    vectorIndexing.h
    version.h
    volumeEffects.h)

add_library(opentimelineio ${OTIO_SHARED_OR_STATIC_LIB} 
    clip.cpp
    colorManagementEffects.cpp
    composable.cpp
    composition.cpp
    deserialization.cpp
    algo/editAlgorithm.cpp
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
    transformEffects.cpp
    transition.cpp
    typeRegistry.cpp
    unknownSchema.cpp
    volumeEffects.cpp
    CORE_VERSION_MAP.cpp
    ${OPENTIMELINEIO_HEADER_FILES})

add_library(OTIO::opentimelineio ALIAS opentimelineio)

target_include_directories(opentimelineio
    PRIVATE "${PROJECT_SOURCE_DIR}/src")

if(OTIO_FIND_RAPIDJSON)
    target_include_directories(opentimelineio
        PRIVATE "${RapidJSON_INCLUDE_DIRS}")
else()
    target_include_directories(opentimelineio
        PRIVATE "${PROJECT_SOURCE_DIR}/src/deps/rapidjson/include")
endif()


target_link_libraries(opentimelineio 
    PUBLIC opentime Imath::Imath)

set_target_properties(opentimelineio PROPERTIES
    DEBUG_POSTFIX "${OTIO_DEBUG_POSTFIX}"
    LIBRARY_OUTPUT_NAME "opentimelineio"
    POSITION_INDEPENDENT_CODE TRUE
    WINDOWS_EXPORT_ALL_SYMBOLS true)

if(BUILD_SHARED_LIBS)
    set_target_properties(opentimelineio PROPERTIES
        SOVERSION ${OTIO_SOVERSION}
        VERSION ${OTIO_VERSION})
endif()

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

    install(TARGETS opentimelineio
           EXPORT OpenTimelineIOTargets
           INCLUDES DESTINATION "${OPENTIMELINEIO_INCLUDES}"
           ARCHIVE DESTINATION "${OTIO_RESOLVED_CXX_DYLIB_INSTALL_DIR}"
           LIBRARY DESTINATION "${OTIO_RESOLVED_CXX_DYLIB_INSTALL_DIR}"
           RUNTIME DESTINATION "${OTIO_RESOLVED_CXX_DYLIB_INSTALL_DIR}")

    install(EXPORT OpenTimelineIOTargets
           DESTINATION "${OTIO_RESOLVED_CXX_INSTALL_DIR}/share/opentimelineio"
           NAMESPACE OTIO:: )

    include(CMakePackageConfigHelpers)
    configure_package_config_file(
        ${CMAKE_CURRENT_SOURCE_DIR}/OpenTimelineIOConfig.cmake.in
        ${CMAKE_CURRENT_BINARY_DIR}/OpenTimelineIOConfig.cmake
        INSTALL_DESTINATION
            ${OTIO_RESOLVED_CXX_INSTALL_DIR}/share/opentimelineio
        NO_SET_AND_CHECK_MACRO
        NO_CHECK_REQUIRED_COMPONENTS_MACRO
    )

    install(
        FILES
            ${CMAKE_CURRENT_BINARY_DIR}/OpenTimelineIOConfig.cmake
        DESTINATION
            ${OTIO_RESOLVED_CXX_INSTALL_DIR}/share/opentimelineio
    )
endif()
