set(OPENTIMELINEIO_HEADER_FILES
        include/copentimelineio/any.h
        include/copentimelineio/anyDictionary.h
        include/copentimelineio/anyVector.h
        include/copentimelineio/serializableObject.h
        include/copentimelineio/serializableObjectWithMetadata.h
        include/copentimelineio/serialization.h
        include/copentimelineio/deserialization.h
        include/copentimelineio/unknownSchema.h
        include/copentimelineio/serializableObjectVector.h
        include/copentimelineio/serializableObjectRetainerVector.h
        include/copentimelineio/serializableCollection.h
        include/copentimelineio/typeRegistry.h
        include/copentimelineio/composable.h
        include/copentimelineio/item.h
        include/copentimelineio/effect.h
        include/copentimelineio/effectVector.h
        include/copentimelineio/effectRetainerVector.h
        include/copentimelineio/marker.h
        include/copentimelineio/markerVector.h
        include/copentimelineio/markerRetainerVector.h
        include/copentimelineio/mediaReference.h
        include/copentimelineio/missingReference.h
        include/copentimelineio/externalReference.h
        include/copentimelineio/timeEffect.h
        include/copentimelineio/linearTimeWarp.h
        include/copentimelineio/generatorReference.h
        include/copentimelineio/freezeFrame.h
        include/copentimelineio/transition.h
        include/copentimelineio/clip.h
        include/copentimelineio/gap.h
        include/copentimelineio/stack.h
        include/copentimelineio/mapComposableTimeRange.h
        include/copentimelineio/composition.h
        include/copentimelineio/composableRetainerVector.h
        include/copentimelineio/composableVector.h
        include/copentimelineio/optionalPairRationalTime.h
        include/copentimelineio/retainerPairComposable.h
        include/copentimelineio/track.h
        include/copentimelineio/trackVector.h
        include/copentimelineio/timeline.h
        include/copentimelineio/stackAlgorithm.h
        include/copentimelineio/trackAlgorithm.h
        include/copentimelineio/safely_typed_any.h
        )

add_library(copentimelineio SHARED
        src/any.cpp
        src/anyDictionary.cpp
        src/anyVector.cpp
        src/serializableObject.cpp
        src/serializableObjectWithMetadata.cpp
        src/serialization.cpp
        src/deserialization.cpp
        src/unknownSchema.cpp
        src/serializableObjectVector.cpp
        src/serializableObjectRetainerVector.cpp
        src/serializableCollection.cpp
        src/typeRegistry.cpp
        src/composable.cpp
        src/item.cpp
        src/effect.cpp
        src/effectVector.cpp
        src/effectRetainerVector.cpp
        src/marker.cpp
        src/markerVector.cpp
        src/markerRetainerVector.cpp
        src/mediaReference.cpp
        src/missingReference.cpp
        src/externalReference.cpp
        src/timeEffect.cpp
        src/linearTimeWarp.cpp
        src/generatorReference.cpp
        src/freezeFrame.cpp
        src/transition.cpp
        src/clip.cpp
        src/gap.cpp
        src/stack.cpp
        src/mapComposableTimeRange.cpp
        src/composition.cpp
        src/composableRetainerVector.cpp
        src/composableVector.cpp
        src/optionalPairRationalTime.cpp
        src/retainerPairComposable.cpp
        src/track.cpp
        src/trackVector.cpp
        src/timeline.cpp
        src/stackAlgorithm.cpp
        src/trackAlgorithm.cpp
        src/safely_typed_any.cpp
        ${OPENTIMELINEIO_HEADER_FILES})

target_include_directories(copentimelineio PUBLIC
        "${PROJECT_SOURCE_DIR}/../"
        "${PROJECT_SOURCE_DIR}/../deps/"
        "${PROJECT_SOURCE_DIR}/opentimelineio-bindings/include/"
        "${PROJECT_SOURCE_DIR}/opentime-bindings/include/")

target_link_libraries(copentimelineio opentime)
target_link_libraries(copentimelineio opentimelineio)
set_target_properties(copentimelineio PROPERTIES INSTALL_RPATH "${CMAKE_INSTALL_PREFIX}/lib"
        MACOSX_RPATH true WINDOWS_EXPORT_ALL_SYMBOLS true)
install(TARGETS copentimelineio
        RUNTIME DESTINATION bin
        LIBRARY DESTINATION lib)

if (NOT OTIO_CXX_NOINSTALL)
    install(FILES ${OPENTIMELINEIO_HEADER_FILES} DESTINATION include/copentimelineio)
endif (NOT OTIO_CXX_NOINSTALL)
