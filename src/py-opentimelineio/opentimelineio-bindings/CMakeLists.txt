pybind11_add_module(_otio
                    otio_errorStatusHandler.cpp
                    otio_anyDictionary.cpp
                    otio_anyVector.cpp
                    otio_bindings.cpp
                    otio_tests.cpp
                    otio_serializableObjects.cpp
                    otio_utils.cpp)

target_include_directories(_otio PUBLIC pybind11/include)
target_link_libraries(_otio PUBLIC opentimelineio opentime)
set_target_properties(_otio PROPERTIES INSTALL_RPATH "${CMAKE_INSTALL_PREFIX}/lib")
install(TARGETS _otio DESTINATION python/opentimelineio)


