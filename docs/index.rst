Welcome to OpenTimelineIO's documentation!
==================================================

Overview
--------

OpenTimelineIO (OTIO) is an API and interchange format for editorial cut information. You can think
of it as a modern Edit Decision List (EDL) that also includes an API for reading, writing, and
manipulating editorial data. It also includes a plugin system for translating to/from existing
editorial formats as well as a plugin system for linking to proprietary media storage schemas.

OTIO supports clips, timing, tracks, transitions, markers, metadata, etc. but not embedded video or
audio. Video and audio media are referenced externally. We encourage 3rd party vendors, animation
studios and visual effects studios to work together as a community to provide adaptors for each
video editing tool and pipeline.

Links
---------
`OpenTimelineIO Home Page <http://opentimeline.io/>`_

`OpenTimelineIO Discussion Group <https://groups.google.com/forum/#!forum/open-timeline-io>`_

Latest Presentation
--------------------
`OpenTimelineIO FMX April 2018 Presentation Slides <_static/OpenTimelineIO_2018_04_26_FMX_Published.key.pdf>`_

Quick Start
------------
.. toctree::
   :maxdepth: 2

   tutorials/quickstart

Tutorials
------------
.. toctree::
   :maxdepth: 2

   tutorials/adapters
   tutorials/architecture
   tutorials/contributing
   tutorials/feature-matrix
   tutorials/otio-timeline-structure
   tutorials/time-ranges
   tutorials/write-an-adapter
   tutorials/write-a-media-linker
   tutorials/write-a-hookscript
   tutorials/write-a-schemadef
   tutorials/versioning-schemas
   tutorials/wrapping-otio

Use Cases
------------
.. toctree::
   :maxdepth: 2

   use-cases/animation-shot-frame-ranges
   use-cases/conform-new-renders-into-cut
   use-cases/shots-added-removed-from-cut

API Reference
-------------

.. toctree::
   :maxdepth: 2

   api/modules/opentimelineio

Schema Reference
----------------

.. toctree::
   :maxdepth: 2

   tutorials/otio-file-format-specification
   tutorials/otio-serialized-schema
   tutorials/otio-serialized-schema-only-fields

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
