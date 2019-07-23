otio_headers = [
    'errorStatus.h',
    'rationalTime.h',
    'stringPrintf.h',
    'timeRange.h',
    'timeTransform.h',
    'version.h',

]

libopentime = build_target('opentime',
    'errorStatus.cpp',
    'rationalTime.cpp',
    target_type: cxx_no_install ? 'static_library' : 'both_libraries',
    version : '1.0',
    include_directories : [configinc],
    install : not cxx_no_install)

if not cxx_no_install
    install_headers(otio_headers, subdir : 'opentime')
    pkgconfig.generate(
        libopentime,
        description: 'OpentimelineIO times handling library',
        name: 'opentime-' + apiversion,
        version: apiversion
    )

    libopentime_dep = declare_dependency(
        link_with : libopentime.get_shared_lib(),
        include_directories : [configinc],
    )
endif