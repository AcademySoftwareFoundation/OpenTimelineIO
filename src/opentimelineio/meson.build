otio_headers = [
    'any.h', 'anyDictionary.h', 'anyVector.h', 'clip.h', 'composable.h', 'composition.h',
    'deserialization.h', 'effect.h', 'errorStatus.h', 'externalReference.h', 'freezeFrame.h',
    'gap.h', 'generatorReference.h', 'item.h', 'linearTimeWarp.h', 'marker.h', 'mediaReference.h',
    'missingReference.h', 'optional.h', 'safely_typed_any.h', 'serializableCollection.h', 'serializableObject.h',
    'serializableObjectWithMetadata.h', 'serialization.h', 'stack.h', 'stackAlgorithm.h', 'stringUtils.h',
    'timeEffect.h', 'timeline.h', 'track.h', 'trackAlgorithm.h', 'transition.h', 'typeRegistry.h',
    'unknownSchema.h', 'vectorIndexing.h', 'version.h',
]

incdirs = [configinc, anydir, optional_lite_dir, rapidjson_dir]
libopentimelineio = build_target('opentimelineio',
    'clip.cpp', 'composable.cpp', 'composition.cpp', 'deserialization.cpp', 'effect.cpp',
    'errorStatus.cpp', 'externalReference.cpp', 'freezeFrame.cpp', 'gap.cpp', 'generatorReference.cpp',
    'item.cpp', 'linearTimeWarp.cpp', 'marker.cpp', 'mediaReference.cpp', 'missingReference.cpp',
    'safely_typed_any.cpp', 'serializableObject.cpp', 'serializableObjectWithMetadata.cpp', 'serializableCollection.cpp',
    'serialization.cpp', 'stack.cpp', 'stackAlgorithm.cpp', 'stringUtils.cpp', 'timeEffect.cpp',
    'timeline.cpp', 'track.cpp', 'trackAlgorithm.cpp', 'transition.cpp', 'typeRegistry.cpp',
    'unknownSchema.cpp',
    target_type: cxx_no_install ? 'static_library' : 'both_libraries',
    version : '1.0',
    link_with: libopentime,
    include_directories : incdirs,
    install : not cxx_no_install)

if not cxx_no_install
    install_headers(otio_headers, subdir : 'opentimelineio')
    pkgconfig.generate(
        libopentimelineio,
        description: 'OpentimelineIO core library',
        name: 'opentimelineio-' + apiversion,
        version: apiversion
    )
endif

libopentimelineio_dep = declare_dependency(
    link_with : libopentimelineio,
    include_directories : incdirs,
)

if not python.found()
    subdir_done()
endif

# Building python bindings directly from here so we can use opentimeline IO uninstalled
pyotio_dir = '..' / 'py-opentimelineio' / 'opentimelineio-bindings'
pyotio_headers = [
    pyotio_dir / 'otio_errorStatusHandler.h',
    pyotio_dir / 'otio_anyDictionary.h',
    pyotio_dir / 'otio_bindings.h',
    pyotio_dir / 'otio_utils.h'
]

pyopentimelineio = python.extension_module('_otio',
    sources : [
        pyotio_dir / 'otio_errorStatusHandler.cpp',
        pyotio_dir / 'otio_anyDictionary.cpp',
        pyotio_dir / 'otio_anyVector.cpp',
        pyotio_dir / 'otio_bindings.cpp',
        pyotio_dir / 'otio_tests.cpp',
        pyotio_dir / 'otio_serializableObjects.cpp',
        pyotio_dir / 'otio_utils.cpp',
    ] + pyotio_headers,
    link_with: cxx_no_install ? libopentimelineio : libopentimelineio.get_static_lib(),
    include_directories : [configinc, anydir, optional_lite_dir, rapidjson_dir, pybind11_dir],
    dependencies : [python.dependency()],
    install: true,
    subdir: 'opentimelineio',
)

pyopentime_dir = '..' / 'py-opentimelineio' / 'opentime-bindings'
python.extension_module('_opentime',
    sources : [
        pyopentime_dir / 'opentime_bindings.cpp',
        pyopentime_dir / 'opentime_rationalTime.cpp',
        pyopentime_dir / 'opentime_timeRange.cpp',
        pyopentime_dir / 'opentime_timeTransform.cpp',
        pyopentime_dir / 'opentime_bindings.h',
    ],
    link_with: cxx_no_install ? libopentime : libopentime.get_static_lib(),
    include_directories : [configinc, anydir, optional_lite_dir, rapidjson_dir, pybind11_dir],
    dependencies : [python.dependency()],
    install: true,
    subdir: 'opentimelineio',
)

# Copy all python files to the right directory so we can use OpentimelineIO uninstalled by simply setting
# PYTHONPATH
res = run_command(python, '-c', '''
import os
import sys
for f in os.listdir(sys.argv[1]):
    try:
        os.symlink(os.path.join(sys.argv[1], f), os.path.join(sys.argv[2], f))
    except OSError as e:
        pass
''', meson.current_source_dir() / '..'/ 'py-opentimelineio' / 'opentimelineio/', meson.current_build_dir())

if res.returncode() != 0
    error('Could not create symlinks:\n @0@'.format(res.stderr()))
endif

foreach cmd: ['otiocat', 'otioconvert', 'otiostat']
    configure_file(input: '..'/ 'py-opentimelineio' / 'opentimelineio' / 'console' / cmd + '.py',
                   output: cmd, copy: true, install_dir: get_option('bindir'))
endforeach