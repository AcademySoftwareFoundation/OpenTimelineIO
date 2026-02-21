include_directories(
    ${PROJECT_SOURCE_DIR}/src
    ${PROJECT_SOURCE_DIR}/src/deps
    ${PROJECT_SOURCE_DIR}/src/deps/optional-lite/include
    ${PROJECT_SOURCE_DIR}/src/tests
    ${CMAKE_BINARY_DIR}/src
)

list(APPEND tests_opentime test_opentime)
foreach(test ${tests_opentime})
	add_executable(${test} utils.h utils.cpp ${test}.cpp)
	target_link_libraries(${test} opentime)
    target_compile_definitions(${test} PUBLIC OTIO_TESTS_DIR="${CMAKE_CURRENT_SOURCE_DIR}")
	set_target_properties(${test} PROPERTIES FOLDER tests)
	add_test(NAME ${test} COMMAND ${test})
endforeach()

list(APPEND tests_opentimelineio
    test_clip
    test_serialization
    test_serializableCollection
    test_stack_algo
    test_timeline
    test_track
    test_editAlgorithm
    test_composition
    test_url_conversions
    test_otiod
    test_otioz)
foreach(test ${tests_opentimelineio})
    add_executable(${test} utils.h utils.cpp ${test}.cpp)
    target_link_libraries(${test} opentimelineio)
    target_compile_definitions(${test} PUBLIC OTIO_TESTS_DIR="${CMAKE_CURRENT_SOURCE_DIR}")
    set_target_properties(${test} PROPERTIES FOLDER tests)
    add_test(NAME ${test} COMMAND ${test})
endforeach()
