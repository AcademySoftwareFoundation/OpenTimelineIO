add_library(jotio SHARED
        io_opentimeline_OTIOFinalizer.cpp
        otio_manager.cpp
        class_codes.cpp
        io_opentimeline_opentime_ErrorStatus.cpp
        io_opentimeline_OTIONative.cpp
        io_opentimeline_opentime_RationalTime.cpp
        io_opentimeline_opentime_TimeRange.cpp
        io_opentimeline_opentime_TimeTransform.cpp
        io_opentimeline_opentimelineio_Any.cpp
        io_opentimeline_opentimelineio_AnyDictionary.cpp
        io_opentimeline_opentimelineio_AnyDictionary_Iterator.cpp
        io_opentimeline_opentimelineio_AnyVector.cpp
        io_opentimeline_opentimelineio_AnyVector_Iterator.cpp
        io_opentimeline_opentimelineio_ErrorStatus.cpp
        io_opentimeline_opentimelineio_SerializableObject.cpp
        io_opentimeline_opentimelineio_SerializableObjectWithMetadata.cpp
#        io_opentimeline_opentimelineio_SerializableCollection.cpp
#        io_opentimeline_opentimelineio_Marker.cpp
#        io_opentimeline_opentimelineio_MediaReference.cpp
#        io_opentimeline_opentimelineio_MissingReference.cpp
#        io_opentimeline_opentimelineio_ExternalReference.cpp
#        io_opentimeline_opentimelineio_GeneratorReference.cpp
#        io_opentimeline_opentimelineio_Effect.cpp
#        io_opentimeline_opentimelineio_TimeEffect.cpp
#        io_opentimeline_opentimelineio_LinearTimeWarp.cpp
#        io_opentimeline_opentimelineio_FreezeFrame.cpp
#        io_opentimeline_opentimelineio_ImageSequenceReference.cpp
#        io_opentimeline_opentimelineio_Composable.cpp
#        io_opentimeline_opentimelineio_Item.cpp
#        io_opentimeline_opentimelineio_Composition.cpp
#        io_opentimeline_opentimelineio_Gap.cpp
#        io_opentimeline_opentimelineio_UnknownSchema.cpp
#        io_opentimeline_opentimelineio_Transition.cpp
#        io_opentimeline_opentimelineio_Clip.cpp
#        io_opentimeline_opentimelineio_Stack.cpp
#        io_opentimeline_opentimelineio_Track.cpp
#        io_opentimeline_opentimelineio_Timeline.cpp
#        io_opentimeline_opentimelineio_Algorithms.cpp
#        io_opentimeline_opentimelineio_Serialization.cpp
#        io_opentimeline_opentimelineio_Deserialization.cpp)
        )

target_include_directories(jotio PUBLIC
        "${PROJECT_SOURCE_DIR}/../")

target_link_libraries(jotio opentime)
target_link_libraries(jotio opentimelineio)