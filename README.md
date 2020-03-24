OpenTimelineIO
=======
[![OpenTimelineIO](docs/_static/OpenTimelineIO@3xDark.png)](http://opentimeline.io)
==============

[![Supported VFX Platform Versions](https://img.shields.io/badge/vfx%20platform-2016--2020-lightgrey.svg)](http://www.vfxplatform.com/)
![Supported Versions](https://img.shields.io/badge/python-2.7%2C%203.6%2C%203.7-blue.svg)
[![Build Status](https://travis-ci.com/PixarAnimationStudios/OpenTimelineIO.svg?branch=master)](https://travis-ci.com/PixarAnimationStudios/OpenTimelineIO)
[![codecov](https://codecov.io/gh/PixarAnimationStudios/OpenTimelineIO/branch/master/graph/badge.svg)](https://codecov.io/gh/PixarAnimationStudios/OpenTimelineIO)
[![docs](https://readthedocs.org/projects/opentimelineio/badge/?version=latest)](https://opentimelineio.readthedocs.io/en/latest/index.html)

Main web site: http://opentimeline.io/

Documentation: https://opentimelineio.readthedocs.io/

GitHub: https://github.com/PixarAnimationStudios/OpenTimelineIO

Discussion group: https://lists.aswf.io/g/otio-discussion

Slack channel: https://academysoftwarefdn.slack.com/messages/CMQ9J4BQC
To join, create an account here first: https://slack.aswf.io/

PUBLIC BETA NOTICE
------------------

OpenTimelineIO is currently in Public Beta. That means that it may be missing
some essential features and there are large changes planned. During this phase
we actively encourage you to provide feedback, requests, comments, and/or
contributions.

Overview
--------

OpenTimelineIO is an interchange format and API for editorial cut information.
OTIO is not a container format for media, rather it contains information about
the order and length of cuts and references to external media.

OTIO includes both a file format and an API for manipulating that format. It
also includes a plugin architecture for writing adapters to convert
from/to existing editorial timeline formats. It also implements a dependency-
less library for dealing strictly with time, `opentime`.

You can provide adapters for your video editing tool or pipeline as needed.
Each adapter allows for import/export between that proprietary tool and the
OpenTimelineIO format.

Documentation
--------------
Documentation, including quick start, architecture, use cases, API docs, and much more, is available on [ReadTheDocs](https://opentimelineio.readthedocs.io/)

Adapters
--------

OpenTimelineIO supports, or plans to support, conversion adapters for many
existing file formats, such as Final Cut Pro XML, AAF, CMX 3600 EDL, etc.

See: https://opentimelineio.readthedocs.io/en/latest/tutorials/adapters.html

Other Plugins
-------------

OTIO also supports several other kinds of plugins, for more information see:

* [Media Linkers](https://opentimelineio.readthedocs.io/en/latest/tutorials/write-a-media-linker.html) - Generate media references to local media according to your local conventions.
* [HookScripts](https://opentimelineio.readthedocs.io/en/latest/tutorials/write-a-hookscript.html) - Scripts that can run at various points during OTIO execution (_ie_ before the media linker)
* [SchemaDefs](https://opentimelineio.readthedocs.io/en/latest/tutorials/write-a-schemadef.html) - Define OTIO schemas.

Installing / Quick-Start
------------------------

The python-wrapped version of OpenTimelineIO is publicly available via pypy.  You can install OpenTimelineIO via:

`pip install opentimelineio`

For detailed installation instructions and notes on how to run the included viewer program, see: https://opentimelineio.readthedocs.io/en/latest/tutorials/quickstart.html


Example Usage
-------------

```
import opentimelineio as otio

timeline = otio.adapters.read_from_file("foo.aaf")
for clip in timeline.each_clip():
  print clip.name, clip.duration()
```

There are more code examples here: https://github.com/PixarAnimationStudios/OpenTimelineIO/tree/master/examples

Also, looking through the unit tests is a great way to see what OTIO can do:
https://github.com/PixarAnimationStudios/OpenTimelineIO/tree/master/tests

OTIO includes a viewer program as well (see the quickstart section for instructions on installing it):

![OTIO View Screenshot](docs/_static/otioview.png)

Developing
----------

If you want to contribute to the project, please see: https://opentimelineio.readthedocs.io/en/latest/tutorials/contributing.html

You can get the latest development version via:

`git clone git@github.com:PixarAnimationStudios/OpenTimelineIO.git OpenTimelineIO`

You can install development dependencies with `pip install .[dev]`

You can also install the PySide2 dependency with `pip install .[view]`

Currently the code base is written against python 2.7, python 3.6 and 3.7, in keeping 
with the pep8 style.  We ask that before you submit a pull request, you:

- run `make test` -- to ensure that none of the unit tests were broken
- run `make lint` -- to conform to pep8
- run `make coverage` -- to detect code which isn't covered

PEP8: https://www.python.org/dev/peps/pep-0008/

License
-------
OpenTimelineIO is open source software. Please see ![LICENSE.txt](LICENSE.txt) for details.

Nothing in the license file or this project grants any right to use Pixar or any other contributor’s trade names, trademarks, service marks, or product names.

Contact
-------

For more information, please visit http://opentimeline.io/
or https://github.com/PixarAnimationStudios/OpenTimelineIO
or join our discussion forum: https://lists.aswf.io/g/otio-discussion

