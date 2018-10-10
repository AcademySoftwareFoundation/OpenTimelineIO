# Quickstart

This is for users who wish to get started using the "OTIOView" application to inspect the contents of editorial timelines.

## Install Prerequisites

OTIOView has an additional prerequisite to OTIO:

- Try `pip install PySide2`
- If that doesn't work, try downloading PySide2 here: <a href="https://wiki.qt.io/Qt_for_Python" target="_blank">https://wiki.qt.io/Qt_for_Python</a>

You probably want the prebuilt binary for your platform.  PySide2 generally includes a link to the appropriate version of Qt as well.

## Install OTIO

- `pip install opentimelineio`

## Configure Environment Variables for extra adapters

By default, when you install OTIO you will only get the "Core" adapters, which include CMX EDL, Final Cut Pro 7 XML, and the built in JSON format.  In order to get access to the "contrib" adapters (which includes the maya sequencer, rv and others) you'll need to set some environment variables.  If you need support for these formats, please consult the 
<a href="https://opentimelineio.readthedocs.io/en/latest/tutorials/adapters.html" target="_blank"> Adapters documentation page for details</a>

## Run OTIOView

Once you have pip installed OpenTimelineIO, you should be able to run:

    otioview path/to/your/file.edl