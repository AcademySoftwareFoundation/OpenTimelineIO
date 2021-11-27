include_directories(${PROJECT_SOURCE_DIR}/src
    ${PROJECT_SOURCE_DIR}/src/deps
    ${PROJECT_SOURCE_DIR}/src/deps/optional-lite/include
	${PROJECT_SOURCE_DIR}/src/tests)

list(APPEND tests_opentime test_opentime)
foreach(test ${tests_opentime})
	add_executable(${test} tests.h ${test}.cpp)
	target_link_libraries(${test} opentime)
	set_target_properties(${test} PROPERTIES FOLDER tests)
	add_test(${test} ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/${test}${CMAKE_EXECUTABLE_SUFFIX})
endforeach()

list(APPEND tests_opentimelineio test_clip)
foreach(test ${tests_opentimelineio})
	add_executable(${test} tests.h ${test}.cpp)
	target_link_libraries(${test} opentimelineio)
	set_target_properties(${test} PROPERTIES FOLDER tests)
	add_test(${test} ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/${test}${CMAKE_EXECUTABLE_SUFFIX})
endforeach()
