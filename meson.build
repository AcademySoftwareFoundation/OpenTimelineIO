project('OpentimelineIO', 'cpp',
  version : '0.99',
  meson_version : '>= 0.50.0',
  subproject_dir: 'src/deps',
  default_options: ['cpp_std=c++11']
)

apiversion = '1.0'

cxx_no_install = get_option('OTIO_CXX_NOINSTALL')
python_version = get_option('python_version')
build_python = get_option('python')

python = import('python').find_installation(python_version, required: build_python)
if not python.found() and cxx_no_install
  error('Python is disabled and the CXX libraries won\'t be installed... nothing to do')
endif

pkgconfig = import('pkgconfig')

subdir('src')
if python.found()
  subdir('contrib')

  pathsep = host_machine.system() == 'windows' ? ';' : ':'
  PYTHONPATH = '@0@@1@@2@@1@@3@'.format(
    meson.current_build_dir() / 'src',
    pathsep,
    meson.current_source_dir() / 'contrib',
    meson.current_source_dir() / 'src',
  )
  PATH = '@0@@1@@2@'.format(
    meson.current_build_dir() / 'src',
    pathsep,
    meson.current_build_dir() / 'src' / 'opentimelineio'
  )

  env = environment()
  env.set('OTIO_DEFAULT_MEDIA_LINKER', '')
  env.set('PYTHONPATH', PYTHONPATH)
  env.append('PATH', PATH)
  env.set('OTIO_DISABLE_SHELLOUT_TESTS', '1')
  coverage = find_program(
    python.language_version().split('.')[0] == '3' ? 'coverage3' : 'coverage2',
    'coverage'
  )

  test(
    'Core OpenTimelineIO tests',
    coverage,
    args: ['run', '-a', '-m', 'unittest', 'discover', 'tests', '-vvv'],
    env: env,
    workdir: meson.current_source_dir()
  )

  test(
    'OpenTimelineIO contrib tests',
    coverage,
    args: ['run', '-a', '-m', 'unittest', 'discover', 'tests', '-vvv'],
    env: env,
    workdir: meson.current_source_dir() / 'contrib' / 'opentimelineio_contrib' / 'adapters',
    timeout: 120,
  )

  run_target('doc-model-update',
      command: [
        find_program('env'),
        'PYTHONPATH=@0@@1@$PYTHONPATH'.format(PYTHONPATH, pathsep),
        python.path(),
        meson.current_build_dir() / 'src' / 'opentimelineio' / 'console' / 'autogen_serialized_datamodel.py',
        '-o', meson.current_source_dir() /'docs/tutorials/otio-serialized-schema.md',
      ],
      depends: [pyopentimelineio],
  )

  pycodestyle = find_program('pycodestyle', required: false)
  pyflakes = find_program('pyflakes', required: false)
  flake8 = find_program('flake8', required: false)
  if flake8.found() and pyflakes.found() and pycodestyle.found()
    run_target('lint', command: [ flake8 ])
  else
    warning('Required linting tools were not found, not `lint` target created.')
  endif

  message('''To use opentimelineIO from the uninstalled environment set:

      export PYTHONPATH=@0@@1@$PYTHONPATH
      export PATH=@2@@1@$PATH

  '''.format(PYTHONPATH, pathsep, PATH))

else
  message('Python support was not built.')
endif