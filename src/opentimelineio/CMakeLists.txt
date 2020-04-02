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
    stringUtils.h
    timeEffect.h
    timeline.h
    track.h
    trackAlgorithm.h
    transition.h
    typeRegistry.h
    unknownSchema.h
    vectorIndexing.h
    version.h)

add_library(opentimelineio SHARED
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
            item.cpp
            linearTimeWarp.cpp
            marker.cpp
            mediaReference.cpp
            missingReference.cpp
            safely_typed_any.cpp
            serializableObject.cpp
            serializableObjectWithMetadata.cpp
            serializableCollection.cpp
            serialization.cpp
            stack.cpp
            stackAlgorithm.cpp
            stringUtils.cpp
            timeEffect.cpp
            timeline.cpp
            track.cpp
            trackAlgorithm.cpp
            transition.cpp
            typeRegistry.cpp
            unknownSchema.cpp ${OPENTIMELINEIO_HEADER_FILES})

target_include_directories(opentimelineio PUBLIC
                           "${PROJECT_SOURCE_DIR}/src"
                           "${PROJECT_SOURCE_DIR}/src/deps"
                           "${PROJECT_SOURCE_DIR}/src/deps/optional-lite/include"
                           "${PROJECT_SOURCE_DIR}/src/deps/rapidjson/include")

target_link_libraries(opentimelineio PUBLIC opentime)
set_target_properties(opentimelineio PROPERTIES INSTALL_RPATH "${CMAKE_INSTALL_PREFIX}/lib"
			MACOSX_RPATH true WINDOWS_EXPORT_ALL_SYMBOLS true)
install(TARGETS opentimelineio 
        RUNTIME DESTINATION bin
        LIBRARY DESTINATION lib)

if (NOT OTIO_CXX_NOINSTALL)
    install(FILES ${OPENTIMELINEIO_HEADER_FILES} DESTINATION include/opentimelineio)
endif (NOT OTIO_CXX_NOINSTALL)


