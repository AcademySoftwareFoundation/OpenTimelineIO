
# Force rpath
set(CMAKE_SKIP_BUILD_RPATH FALSE)
set(CMAKE_BUILD_WITH_INSTALL_RPATH FALSE)
if(APPLE)
  set(CMAKE_MACOSX_RPATH ON)
endif()

# Use the link path as the rpath
set(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)

# if not set, use a default path
# ref: Imath's cmake scripts.
# https://github.com/AcademySoftwareFoundation/Imath/blob/master/config/ImathSetup.cmake
#
if(NOT CMAKE_INSTALL_RPATH)
  list(FIND CMAKE_PLATFORM_IMPLICIT_LINK_DIRECTORIES "${CMAKE_INSTALL_PREFIX}/lib" isSystemDir)
  if("${isSystemDir}" STREQUAL "-1")
    if("${CMAKE_SYSTEM}" MATCHES "Linux")
      get_filename_component(tmpSysPath "${CMAKE_INSTALL_FULL_LIBDIR}" NAME)
      if(NOT tmpSysPath)
        set(tmpSysPath "lib")
      endif()
      set(CMAKE_INSTALL_RPATH "\\\$ORIGIN/../${tmpSysPath};${CMAKE_INSTALL_FULL_LIBDIR}")
      set(tmpSysPath)
    elseif(APPLE)
      set(CMAKE_INSTALL_RPATH "@loader_path/../lib;@executable_path/../lib;${CMAKE_INSTALL_FULL_LIBDIR}")
    else()
      set(CMAKE_INSTALL_RPATH "${CMAKE_INSTALL_FULL_LIBDIR}")
    endif()
  endif()
  set(isSystemDir)
endif()

add_subdirectory(opentime-bindings)
add_subdirectory(opentimelineio-bindings)
