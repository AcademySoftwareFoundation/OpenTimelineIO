add_subdirectory(pybind11)
if (NOT OTIO_CXX_NOINSTALL)
    install(FILES any/any.hpp DESTINATION include/opentimelineio/deps/any)
    install(FILES optional-lite/include/nonstd/optional.hpp
    	DESTINATION include/opentimelineio/deps/nonstd)
endif (NOT OTIO_CXX_NOINSTALL)

	
