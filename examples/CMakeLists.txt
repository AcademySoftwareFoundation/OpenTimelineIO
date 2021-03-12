find_package(PythonLibs REQUIRED)
include_directories(${PROJECT_SOURCE_DIR}/src
    ${PROJECT_SOURCE_DIR}/src/deps
    ${PROJECT_SOURCE_DIR}/src/deps/optional-lite/include
    ${PYTHON_INCLUDE_DIRS})
foreach(example "summarize_timing")
    add_executable(${example} ${example}.cpp util.cpp)
    target_link_libraries(${example} OTIO::opentimelineio ${PYTHON_LIBRARIES})
endforeach()

