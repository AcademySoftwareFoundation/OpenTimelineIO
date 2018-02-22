OpenTimelineIO
==============

Main web site: http://opentimeline.io/

GitHub: https://github.com/PixarAnimationStudios/OpenTimelineIO

Discussion Group: https://groups.google.com/forum/#!forum/open-timeline-io

![Supported Versions](https://img.shields.io/badge/python-2.7%2C%203.5-blue.svg)
[![Build Status](https://travis-ci.org/PixarAnimationStudios/OpenTimelineIO.svg?branch=master)](https://travis-ci.org/PixarAnimationStudios/OpenTimelineIO)

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

Use Cases
---------

- I have a timeline in Adobe Premiere, and I want to bring that cut into my
    in-house animation system.
- I have a timeline in Avid Media Composer, and my Producer wants to know a
     full list of the media I'm using.
- I am about to render a bunch of shots & I want to make sure my frame ranges
    match what Editorial is asking for (not too long or too short).
- The Editor just added some cross dissolves and I need to know how many more
     frames (at head or tail) of which shots need to be rendered.
- Legal needs a list of all the audio we're using (music, effects, dialogue) in
     the current cut.
- TDs/Animators want to get a cut from Editorial for reference, and then splice
     their updated renders/recordings into that cut.
- Editorial is working with proxy media (QuickTime, MXF, etc.) and I want to
    gather all the EXRs that correspond with that & bring those into Nuke.

For more use cases, see: https://github.com/PixarAnimationStudios/OpenTimelineIO/wiki/Use-Cases

Architecture
------------

See: https://github.com/PixarAnimationStudios/OpenTimelineIO/wiki/Architecture

Adapters
--------

OpenTimelineIO supports, or plans to support, conversion adapters for these
formats:

### Final Cut Pro XML ###

Final Cut 7 XML Format
- Status: Supported via the `fcp_xml` adapter
- https://developer.apple.com/library/content/documentation/AppleApplications/Reference/FinalCutPro_XML/AboutThisDoc/AboutThisDoc.html#//apple_ref/doc/uid/TP30001152-TPXREF101

Final Cut Pro X XML Format:
- Status: https://github.com/PixarAnimationStudios/OpenTimelineIO/issues/37
- https://developer.apple.com/library/mac/documentation/FinalCutProX/Reference/FinalCutProXXMLFormat/Introduction/Introduction.html

### Adobe Premiere Project ###

- Based on guidance from Adobe, we support interchange with Adobe Premiere via 
    the FCP 7 XML format (see above).

### CMX3600 EDL ###

- Status: Supported via the `cmx_3600` adapter
- Includes support for ASC_CDL color correction metadata
- Full specification: SMPTE 258M-2004 "For Television −− Transfer of Edit Decision Lists"
- http://xmil.biz/EDL-X/CMX3600.pdf
- https://documentation.apple.com/en/finalcutpro/usermanual/index.html#chapter=96%26section=1

### Avid AAF ###

- Status: Supports reading simple AAF compositions
  - Reading: https://github.com/PixarAnimationStudios/OpenTimelineIO/issues/1
  - Writing: https://github.com/PixarAnimationStudios/OpenTimelineIO/issues/236
- http://www.amwa.tv/downloads/specifications/aafobjectspec-v1.1.pdf
- http://www.amwa.tv/downloads/specifications/aafeditprotocol.pdf

- set ${OTIO_AAF_PYTHON_LIB} to point the location of the PyAAF module.

Contrib Adapters
----------------

The contrib area hosts adapters which come from the community (_not_ supported 
    by the core-otio team) and may require extra dependencies.

### RV Session File ###

- Status: write-only adapter supported via the `rv_session` adapter.
- need to set environment variables to locate `py-interp` and `rvSession.py` 
    from within the RV distribution
- set ${OTIO_RV_PYTHON_BIN} to point at `py-interp` from within rv, for 
    example:
    `setenv OTIO_RV_PYTHON_BIN /Applications/RV64.app/Contents/MacOS/py-interp`
- set ${OTIO_RV_PYTHON_LIB} to point at the parent directory of `rvSession.py`:
    `setenv OTIO_RV_PYTHON_LIB /Applications/RV64.app/Contents/src/python`
    
### Maya Sequencer ###

- Status: supported via the `maya_sequencer` adapter.
- set ${OTIO_MAYA_PYTHON_BIN} to point the location of `mayapy` within the maya 
    installation.

### HLS Playlist ###

- Status: supported via the `hls_playlist` adapter.

### Avid Log Exchange (ALE) ###

- Status: supported via the `ale` adapter.

### Text Burn-in Adapter ###

Uses FFmpeg to burn text overlays into video media.

- Status: supported via the `burnins` adapter.

Installing
----------

run:
```
python setup.py install
```

To build and install the project.

Makefile
--------

Even though the project is python, we provide a makefile with some utility 
targets.  These include targets for running unit tests and for running 
a linter to conform to style guide.  To run the target:

```bash
# run the unit tests
make test
# run the unit tests with verbose output
make test VERBOSE=1
# run the code through a linter
make lint
# generate a coverage report
make coverage
```

Developing
----------

Currently the code base is written against python2.7 and python3.5, in keeping 
with the pep8 style.  We ask that before you submit a pull request, you:

- run `make test` -- to ensure that none of the unit tests were broken
- run `make lint` -- to conform to pep8
- run `make coverage` -- to detect code which isn't covered

PEP8: https://www.python.org/dev/peps/pep-0008/

Contact
-------

For more information, please visit http://opentimeline.io/
or https://github.com/PixarAnimationStudios/OpenTimelineIO
or join our announcement mailing list: https://groups.google.com/forum/#!forum/open-timeline-io

