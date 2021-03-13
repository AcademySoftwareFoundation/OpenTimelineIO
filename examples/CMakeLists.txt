find_package(PythonLibs REQUIRED)

include_directories(${PROJECT_SOURCE_DIR}/src
    ${PROJECT_SOURCE_DIR}/src/deps
    ${PROJECT_SOURCE_DIR}/src/deps/optional-lite/include
    ${PYTHON_INCLUDE_DIRS})

list(APPEND examples flatten_video_tracks)
list(APPEND examples summarize_timing)
foreach(example ${examples})
    add_executable(${example} ${example}.cpp util.cpp)
    target_link_libraries(${example} OTIO::opentimelineio ${PYTHON_LIBRARIES})
endforeach()

