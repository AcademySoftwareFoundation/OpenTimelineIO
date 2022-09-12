find_package(PythonLibs REQUIRED)

include_directories(${PROJECT_SOURCE_DIR}/src
    ${PROJECT_SOURCE_DIR}/src/deps
    ${PROJECT_SOURCE_DIR}/src/deps/optional-lite/include
    ${PYTHON_INCLUDE_DIRS})

list(APPEND examples conform)
list(APPEND examples flatten_video_tracks)
list(APPEND examples summarize_timing)
list(APPEND examples io_perf_test)
list(APPEND examples upgrade_downgrade_example)
if(OTIO_PYTHON_INSTALL)
    list(APPEND examples python_adapters_child_process)
    list(APPEND examples python_adapters_embed)
endif()
foreach(example ${examples})
    add_executable(${example} ${example}.cpp util.h util.cpp)
    target_link_libraries(${example} OTIO::opentimelineio ${PYTHON_LIBRARIES})
    set_target_properties(${example} PROPERTIES FOLDER examples)
endforeach()
