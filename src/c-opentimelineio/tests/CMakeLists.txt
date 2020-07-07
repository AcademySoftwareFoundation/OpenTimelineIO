# Download and unpack googletest at configure time
configure_file(CMakeLists.txt.in googletest-download/CMakeLists.txt)
execute_process(COMMAND ${CMAKE_COMMAND} -G "${CMAKE_GENERATOR}" .
        RESULT_VARIABLE result
        WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/googletest-download)
if (result)
    message(FATAL_ERROR "CMake step for googletest failed: ${result}")
endif ()
execute_process(COMMAND ${CMAKE_COMMAND} --build .
        RESULT_VARIABLE result
        WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/googletest-download)
if (result)
    message(FATAL_ERROR "Build step for googletest failed: ${result}")
endif ()

# Prevent overriding the parent project's compiler/linker
# settings on Windows
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)

# Add googletest directly to our build. This defines
# the gtest and gtest_main targets.
add_subdirectory(${CMAKE_CURRENT_BINARY_DIR}/googletest-src
        ${CMAKE_CURRENT_BINARY_DIR}/googletest-build
        EXCLUDE_FROM_ALL)

# Define test executable and link against gtest_main
add_definitions(-DSAMPLE_DATA_DIR=${CMAKE_CURRENT_SOURCE_DIR}/sample_data/)
link_libraries(
        gtest_main
        copentime
        copentimelineio
)
add_executable(COpenTimeTests openTimeTests.cpp)
add_executable(COTIOComposableTests OTIOComposableTests.cpp)
add_executable(COTIOClipTests OTIOClipTests.cpp)
add_executable(COTIOCompositionTests OTIOCompositionTests.cpp)
add_executable(COTIOEffectTests OTIOEffectTests.cpp)
add_executable(COTIOGeneratorReferenceTests OTIOGeneratorReferenceTests.cpp)
add_executable(COTIOMarkerTests OTIOMarkerTests.cpp)
add_executable(COTIOMediaReferenceTests OTIOMediaReferenceTests.cpp)
add_executable(COTIOTransitionTests OTIOTransitionTests.cpp)
add_executable(COTIOUnknownSchemaTests OTIOUnknownSchemaTests.cpp)
add_executable(COTIOSerializableCollectionTests OTIOSerializableCollectionTests.cpp)
add_executable(COTIOItemTests OTIOItemTests.cpp)
add_executable(COTIOSerializableObjectTests OTIOSerializableObjectTests.cpp)
add_executable(COTIOTimelineTests OTIOTimelineTests.cpp)
add_executable(COTIOStackAlgoTests OTIOStackAlgoTests.cpp)
add_executable(COTIOTrackAlgoTests OTIOTrackAlgoTests.cpp)

include_directories(
        "${PROJECT_SOURCE_DIR}/opentime-bindings/include/"
        "${PROJECT_SOURCE_DIR}/opentimelineio-bindings/include/")

add_test(NAME COpenTimeTests COMMAND COpenTimeTests)
add_test(NAME COTIOComposableTests COMMAND COTIOComposableTests)
add_test(NAME COTIOClipTests COMMAND COTIOClipTests)
add_test(NAME COTIOCompositionTests COMMAND COTIOCompositionTests)
add_test(NAME COTIOEffectTests COMMAND COTIOEffectTests)
add_test(NAME COTIOGeneratorReferenceTests COMMAND COTIOGeneratorReferenceTests)
add_test(NAME COTIOMarkerTests COMMAND COTIOMarkerTests)
add_test(NAME COTIOMediaReferenceTests COMMAND COTIOMediaReferenceTests)
add_test(NAME COTIOTransitionTests COMMAND COTIOTransitionTests)
add_test(NAME COTIOUnknownSchemaTests COMMAND COTIOUnknownSchemaTests)
add_test(NAME COTIOSerializableCollectionTests COMMAND COTIOSerializableCollectionTests)
add_test(NAME COTIOItemTests COMMAND COTIOItemTests)
add_test(NAME COTIOSerializableObjectTests COMMAND COTIOSerializableObjectTests)
add_test(NAME COTIOTimelineTests COMMAND COTIOTimelineTests)
add_test(NAME COTIOStackAlgoTests COMMAND COTIOStackAlgoTests)
add_test(NAME COTIOTrackAlgoTests COMMAND COTIOTrackAlgoTests)