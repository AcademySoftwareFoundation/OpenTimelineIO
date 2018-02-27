from setuptools import setup

setup(
    name='otio_counter',
    entry_points={
        'opentimelineio.plugins': 'otio_counter = otio_counter'
    },
    package_data={
        'otio_counter': [
            'plugin_manifest.json',
        ],
    },
    version='1.0.0',
    description='Adapter writes number of tracks to file.',
    packages=['otio_counter'],
    author='PIX System, LLC',
    author_email='ereinecke@pixsystem.com',
    keywords=['library', 'opentimelineio plugin'],
)
