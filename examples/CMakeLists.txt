find_package(PythonLibs REQUIRED)

include_directories(${PROJECT_SOURCE_DIR}/src
    ${CMAKE_CURRENT_BINARY_DIR}/../src
    ${PYTHON_INCLUDE_DIRS})

set(examples
    bundle
    conform
    flatten_video_tracks
    summarize_timing
    io_perf_test
    upgrade_downgrade_example)
if(OTIO_PYTHON_INSTALL)
    list(APPEND examples
        python_adapters_child_process
        python_adapters_embed)
endif()
foreach(example ${examples})
    add_executable(${example} ${example}.cpp util.h util.cpp)
    target_link_libraries(${example} OTIO::opentimelineio ${PYTHON_LIBRARIES})
    set_target_properties(${example} PROPERTIES FOLDER examples)
endforeach()
