# install(FILES
#          __init__.py
#         exceptions.py
#         hooks.py
#         media_linker.py 
#         opentime.py
#         test_utils.py
#         DESTINATION python/opentimelineio)
# 
# install(DIRECTORY
#         adapters
#         algorithms
#         console
#         core
#         plugins
#         schema
#         schemadef
#         DESTINATION python/opentimelineio
#         FILES_MATCHING PATTERN "*.py"
#                        PATTERN "*.json")

add_subdirectory(opentime-bindings)
add_subdirectory(opentimelineio-bindings)
