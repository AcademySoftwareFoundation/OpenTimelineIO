set(OPENTIMELINEIO_HEADER_FILES
        include/copentimelineio/any.h
        include/copentimelineio/anyDictionary.h
        include/copentimelineio/anyVector.h
        include/copentimelineio/serializableObject.h
        include/copentimelineio/serializableObjectWithMetadata.h
        include/copentimelineio/serialization.h
        include/copentimelineio/deserialization.h
        include/copentimelineio/unknownSchema.h
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
        ${OPENTIMELINEIO_HEADER_FILES})

target_include_directories(copentimelineio PUBLIC
        "${PROJECT_SOURCE_DIR}/../"
        "${PROJECT_SOURCE_DIR}/../deps/"
        "${PROJECT_SOURCE_DIR}/opentimelineio-bindings/include/")

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
