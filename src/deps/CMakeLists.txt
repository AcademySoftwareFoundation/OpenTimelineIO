add_subdirectory(pybind11)
install(FILES any/any.hpp DESTINATION include/opentimelineio/deps/any)
install(FILES optional-lite/include/nonstd/optional.hpp
	DESTINATION include/opentimelineio/deps/nonstd)
	
