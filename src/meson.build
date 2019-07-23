configinc = include_directories('.')
subdir('opentime')
subdir('deps')
subdir('opentimelineio')
subdir('py-opentimelineio')

if python.found()
    install_subdir('opentimelineview',
            install_dir: python.get_install_dir(pure: false,
        )
    )
    configure_file(input: 'opentimelineview/console.py',
                   output: 'otioview',
                   copy: true,
                   install_dir: get_option('bindir'))
endif
