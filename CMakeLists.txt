cmake_minimum_required(VERSION 2.8.12)

install(DIRECTORY contrib/py-opentimelineio_contrib/
        DESTINATION python/opentimelineio_contrib)

add_subdirectory(src)
