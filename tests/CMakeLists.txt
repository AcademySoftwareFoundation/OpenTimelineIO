include_directories(${PROJECT_SOURCE_DIR}/src
    ${PROJECT_SOURCE_DIR}/src/deps
    ${PROJECT_SOURCE_DIR}/src/deps/optional-lite/include
	${PROJECT_SOURCE_DIR}/src/tests)

add_executable(test_opentimelineio
	main.cpp
	test_clip.cpp
	test_opentime.cpp
	utils.h
	utils.cpp)
target_link_libraries(test_opentimelineio opentimelineio)
set_target_properties(test_opentimelineio PROPERTIES FOLDER tests)
add_test(test_opentimelineio ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/test_opentimelineio${CMAKE_EXECUTABLE_SUFFIX})
