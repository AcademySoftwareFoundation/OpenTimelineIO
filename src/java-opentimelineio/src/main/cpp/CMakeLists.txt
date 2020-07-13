add_library(jotio SHARED
        io_opentimeline_opentime_ErrorStatus.cpp
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
        io_opentimeline_opentimelineio_SerializableObject_Retainer.cpp)

target_include_directories(jotio PUBLIC
        "${PROJECT_SOURCE_DIR}/../")

target_link_libraries(jotio opentime)
target_link_libraries(jotio opentimelineio)