OpenTimelineIO
=======
[![OpenTimelineIO](docs/_static/OpenTimelineIO@3xDark.png)](http://opentimeline.io)
==============

[![Supported VFX Platform Versions](https://img.shields.io/badge/vfx%20platform-2023--2027-lightgrey.svg)](http://www.vfxplatform.com/)
![Supported Versions](https://img.shields.io/badge/python-3.9%2C%203.10%2C%203.11%2C%203.12%2C%203.13%2C%203.14%2C%203.15-blue)
[![Build Status](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/actions/workflows/python-package.yml/badge.svg)](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/actions/workflows/python-package.yml)
[![codecov](https://codecov.io/gh/AcademySoftwareFoundation/OpenTimelineIO/branch/main/graph/badge.svg)](https://codecov.io/gh/AcademySoftwareFoundation/OpenTimelineIO)
[![docs](https://readthedocs.org/projects/opentimelineio/badge/?version=latest)](https://opentimelineio.readthedocs.io/en/latest/index.html)
[![CII Best Practices](https://bestpractices.coreinfrastructure.org/projects/2288/badge)](https://bestpractices.coreinfrastructure.org/projects/2288)

Links
-----

* Main web site: http://opentimeline.io/
* Documentation: https://opentimelineio.readthedocs.io/
* Wiki (more documentation): https://github.com/AcademySoftwareFoundation/OpenTimelineIO/wiki
* GitHub: https://github.com/AcademySoftwareFoundation/OpenTimelineIO
* [Discussion group](https://lists.aswf.io/g/otio-discussion)
* [Slack channel](https://academysoftwarefdn.slack.com/messages/CMQ9J4BQC)
  * To join, create an account here first: https://slack.aswf.io/
* [Presentations](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/wiki/Presentations)

DEVELOPMENT STATUS
------------------

OpenTimelineIO is a mature framework widely deployed across the film and
television industries. It is natively supported in most non-linear editing
applications, and has deep integration in game engines, digital content creation
tools and adjacent industries as well.

The API for OpenTimelineIO is considered stable, but is still undergoing
active development, refinement and bug fixes. Work is underway to strengthen
the mathematical and theoretical underpinnings of OpenTimelineIO. The current
version of OpenTimelineIO may be confidently deployed in your domain.

We encourage all developers and end users to provide feedback, requests, 
comments, and/or code contributions.

Overview
--------

OpenTimelineIO is an interchange format and API for editorial cut information.
OTIO contains information about the order and length of cuts and
 references to external media. It is not however, a container format for media.

For integration with applications, the core OTIO library is implemented in C++
and provides an in-memory data model, as well as library functions for
interpreting, manipulating, and serializing that data model. Within the core is
a dependency-less library for dealing strictly with time, `opentime`.

The project also supports an official python binding, which is intended to be
an idiomatic and ergonomic binding for python developers.  The python binding
includes a plugin system which supports a number of different types of plugins,
most notably adapters, which can be used to read and write legacy formats into
the OTIO data model.

Documentation
--------------
Documentation, including quick start, architecture, use cases, API docs, and much more, is available on [ReadTheDocs](https://opentimelineio.readthedocs.io/)

Supported VFX Platforms
-----------------
The current release supports:
- VFX platform 2023 - 2027
- Python 3.9 - 3.15

See also [OpenTimelineIO VFX Reference Platform Support Matrix](VERSIONS.md) for details of which versions of OTIO support which VFX Reference Platform years.

For more information on our vfxplatform support policy: [Contribution Guidelines Documentation Page](https://opentimelineio.readthedocs.io/en/latest/tutorials/contributing.html)
For more information on the vfxplatform: [VFX Platform Homepage](https://vfxplatform.com)

Adapter Plugins
---------------

To provide interoperability with other file formats or applications lacking a
native integration, the opentimelineio community has built a number of python
adapter plugins. This includes Final Cut Pro XML, AAF, CMX 3600 EDL, and more.

**Note: for releases after v0.16, the [OpenTimelineIO PyPI package](https://pypi.org/project/OpenTimelineIO/) will only include the core libraries and file formats. Users that need the full set of adapter plugins should use the [OpenTimelineIO-Plugins PyPI Package](https://pypi.org/project/OpenTimelineIO-Plugins/). Each OpenTimelineIO release will have a matching OpenTimelineIO-Plugins release.**

For more information: https://github.com/AcademySoftwareFoundation/OpenTimelineIO/issues/1386

For more information about this, including supported formats, see: https://opentimelineio.readthedocs.io/en/latest/tutorials/adapters.html

All adapters except the native `.otio`, `.otioz` and `.otiod` have been relocated to separate repositories under the OpenTimelineIO organization located here: https://github.com/OpenTimelineIO
The OTIO python bindings also support several other kinds of plugins, for more information see:

* [Media Linkers](https://opentimelineio.readthedocs.io/en/latest/tutorials/write-a-media-linker.html) - Generate media references to local media according to your local conventions.
* [HookScripts](https://opentimelineio.readthedocs.io/en/latest/tutorials/write-a-hookscript.html) - Scripts that can run at various points during OTIO execution (_ie_ before the media linker)
* [SchemaDefs](https://opentimelineio.readthedocs.io/en/latest/tutorials/write-a-schemadef.html) - Define OTIO schemas.

Installing / Quick-Start
------------------------

The Python-wrapped version of OpenTimelineIO is publicly available [via PyPI](https://pypi.org/project/OpenTimelineIO/).  You can install OpenTimelineIO via:

`python -m pip install opentimelineio`

For detailed installation instructions and notes on how to run the included viewer program, see: https://opentimelineio.readthedocs.io/en/latest/tutorials/quickstart.html


Example Usage
-------------

C++:

```c++
#include <iostream>

#include "opentimelineio/timeline.h"

void
main()
{
    OTIO_NS::SerializableObject::Retainer<OTIO_NS::Timeline> tl(
            dynamic_cast<OTIO_NS::Timeline*>(
                OTIO_NS::Timeline::from_json_file("taco.otio")
        )
    );
    for (const auto& cl : tl->find_clips())
    {
        OTIO_NS::RationalTime dur = cl->duration();
        std::cout << "Name: " << cl->name() << " [";
        std::cout << dur.value() << "/" << dur.rate() << "]" << std::endl;
    }
}
```

Python:

```python
import opentimelineio as otio

timeline = otio.adapters.read_from_file("foo.aaf")
for clip in timeline.find_clips():
  print(clip.name, clip.duration())
```

There are more code examples here: https://github.com/AcademySoftwareFoundation/OpenTimelineIO/tree/main/examples

Also, looking through the unit tests is a great way to see what OTIO can do:
https://github.com/AcademySoftwareFoundation/OpenTimelineIO/tree/main/tests

Developing
----------

If you want to contribute to the project, please see: https://opentimelineio.readthedocs.io/en/latest/tutorials/contributing.html

Also please review our [AI Policy](https://opentimelineio.readthedocs.io/en/latest/tutorials/contributing.html#ai-coding-tools) if using AI coding assistance tools.

You can get the latest development version via:

`git clone git@github.com:AcademySoftwareFoundation/OpenTimelineIO.git --recursive `

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then create
the development environment and compile the native extensions:

```sh
uv sync --locked
uv run python -m unittest discover -s tests
uv run ruff check .
```

The package supports Python 3.9–3.15. `uv.lock` pins development dependencies
across supported Python versions; it does not add runtime dependencies to OTIO.
Use `uv sync --locked --group docs` to install documentation tools (Python 3.11+).
No environment activation is needed with `uv run`.

The Makefile provides the same commands as `make sync`, `make test`, `make lint`,
`make format-check`, and `make coverage`. Run `make format-python` to apply Ruff's
formatting pipeline: `ruff format` followed by lint autofixes for double quotes,
import sorting, and removal of trailing commas from list literals. `make format-check`
checks that combined result without editing files. The existing `make format`
target formats C++.

VS Code recommends the Python, Pylance, and Ruff extensions and uses `.venv`.
Saving applies Ruff's lint fixes. Run the **Format Python** task for the full
pipeline. Format-on-save is disabled because VS Code runs formatting after save
code actions, which would reintroduce list trailing commas after cleanup.

### Development container

With Docker and the recommended Dev Containers extension installed, run
**Dev Containers: Reopen in Container** in VS Code. The container is based on
`aswf/ci-otio:2026`, matching the CY2026 CI toolchain. First-time setup installs
the locked development and documentation dependencies using the image's Python.
It runs as a non-root user and keeps its Python environment and native Python
build cache under `/home/vscode`, separate from your host environment.

The VS Code task picker includes Python environment setup, extension rebuilds,
tests, coverage, linting, distribution builds, and documentation checks. Use
**Docs: Build HTML**, then **Docs: Serve HTML** to preview the docs on port 8000.
The default build task rebuilds the Python extensions; the default test task
runs the Python suite.

C++ tasks prompt for a CMake preset: choose `dev` for the host toolchain or
`vfx2026` inside the container. Run **C++: Configure** before **C++: Build** and
**C++: Run tests**. **C++: Install SDK** installs into the preset's build directory,
without requiring administrator access. Build directories are separated by
preset and operating system. Host C++ tasks require CMake 3.21+ and a compiler;
initialize submodules before using the host preset.

The ASWF image targets Linux x86-64. Use a native x86-64 Docker host or a remote
development host for this container; emulation on ARM hosts can fail in uv.
The development container is built and tested on a native CI runner.

`uv build` creates a source distribution and builds a wheel from that archive.
The build backend is scikit-build-core, which invokes the existing CMake build.
A C++ compiler and zlib development files are still required. Standard PEP 517
frontends, including `python -m pip install .`, remain supported.

CMake options can be passed with build configuration settings, for example:

```sh
uv sync --locked --reinstall-package opentimelineio -Ccmake.define.CMAKE_CXX_STANDARD=17
```

The `CMAKE_ARGS` environment variable is also supported. After editing C++ code,
run `uv sync --locked --reinstall-package opentimelineio` to rebuild the extensions;
pure Python edits are available immediately in the editable installation.

### VFX Reference Platform builds

Modern Python tooling does not change the required VFX Reference Platform
runtime, compiler, or dependency versions. The CY2023–CY2027 CI jobs use the
[ASWF build containers](https://github.com/AcademySoftwareFoundation/aswf-docker),
their Python interpreter and compiler, and their preinstalled dependencies.
They disable uv-managed Python and automatic Python downloads.

In a studio or Reference Platform environment, select that environment's Python
explicitly rather than downloading a replacement:

```sh
UV_NO_MANAGED_PYTHON=1 UV_PYTHON_DOWNLOADS=never uv sync --locked --python /path/to/platform/python
```

See [the support matrix](VERSIONS.md) and the
[developer quickstart](docs/tutorials/quickstart.md) for CMake build instructions.

## C++ Coverage Builds

Enable coverage and select a persistent build directory when installing:

```sh
uv sync --locked --reinstall-package opentimelineio \
  -Ccmake.define.OTIO_CXX_COVERAGE=ON \
  -Ccmake.build-type=Debug -Cbuild-dir=build/coverage
make coverage
make lcov OTIO_CXX_BUILD_TMP_DIR=build/coverage
```

The old `OTIO_CXX_DEBUG_BUILD`, `OTIO_CXX_BUILD_TMP_DIR`, and
`OTIO_CXX_COVERAGE_BUILD` packaging variables are replaced by scikit-build-core's
`cmake.build-type`, `build-dir`, and `cmake.define.OTIO_CXX_COVERAGE` settings.

License
-------
OpenTimelineIO is open source software. Please see the [LICENSE.txt](LICENSE.txt) for details.

Nothing in the license file or this project grants any right to use Pixar or any other contributor’s trade names, trademarks, service marks, or product names.

Contact
-------

For more information, please visit http://opentimeline.io/
or https://github.com/AcademySoftwareFoundation/OpenTimelineIO
or join our discussion forum: https://lists.aswf.io/g/otio-discussion
