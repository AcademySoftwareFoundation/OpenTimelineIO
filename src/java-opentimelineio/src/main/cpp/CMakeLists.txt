add_library(jotio SHARED
        io_opentimeline_opentime_RationalTime.cpp
        io_opentimeline_opentime_ErrorStatus.cpp)

target_include_directories(jotio PUBLIC
        "${PROJECT_SOURCE_DIR}/../")

target_link_libraries(jotio opentime)
target_link_libraries(jotio opentimelineio)