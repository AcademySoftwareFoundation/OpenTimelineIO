
add_executable(otiodiff otiodiff.cpp trackDiff.cpp trackDiff.h)
target_link_libraries(otiodiff OTIO::opentimelineio)
target_include_directories(otiodiff PRIVATE 
    ../
    ../deps
    ../deps/optional-lite/include
    ./dtl)
install(TARGETS otiodiff
        RUNTIME DESTINATION "${CMAKE_INSTALL_PREFIX}/bin")

