OpenTimelineIO
==============

PRE-RELEASE NOTICE
-----------------

We intend to release OpenTimelineIO as an open source project. Prior to
release, a few people (like you) have early access to the project. Please see
the contact section at the bottom if you have questions about this.

Overview
--------

OpenTimelineIO is an interchange format and API for editorial cut information.
OTIO is not a container format for media, rather it contains information about
the order and length of cuts and references to external media.

OTIO includes both a file format and an API for manipulating that format.  It
also includes a plugin architecture for writing adapters to convert
from/to existing editorial timeline formats.  It also implements a dependency-
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

Architecture
------------

TODO: INSERT POINTER TO CONCEPTUAL ARCHITECTURE DOCUMENT

Adapters
--------

OpenTimelineIO supports, or plans to support, conversion adapters for these
formats:

### Final Cut Pro FCPXML Document ###

- TODO: Not yet implemented
- https://developer.apple.com/library/mac/documentation/FinalCutProX/Reference/FinalCutProXXMLFormat/Introduction/Introduction.html

### Adobe Premiere Project ###

- TODO: Not yet implemented
- TODO: Documentation?

### CMX3600 EDL ###

- Limited support
- http://xmil.biz/EDL-X/CMX3600.pdf

### Avid AAF ###

- TODO: Not yet implemented
- http://www.amwa.tv/downloads/specifications/aafobjectspec-v1.1.pdf
- http://www.amwa.tv/downloads/specifications/aafeditprotocol.pdf

Installing
----------

run:
```
python setup.py install
```

To build and install the project.

Makefile
--------

Even though the project is python, we provide a makefile with some utility targets.  These include targets for running unit tests and for running pep8/autopep8 to conform to style guide.

Developing
----------

Currently the code base is written against python2.7 and python3.5.  Before committing please run your changes through pep8/autopep8.

Contact
-------

For more information, please visit http://opentimeline.io/
or https://github.com/PixarAnimationStudios/OpenTimelineIO

