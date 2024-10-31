Welcome to OpenTimelineIO's documentation!
==================================================

Overview
--------

The OpenTimelineIO (OTIO) project aims to solve modern VFX and Post Production workflow challenges like conform, project migration, and interchange across software and platforms in a reliable, open source and reproducible manner. 

OpenTimelineIO is:

* :doc:`an ecosystem of video tools and integrations. <intros/integrations>`
* :doc:`an interchange file format for editorial cut information. <schema/otio-file-format-specification>`
* :doc:`an cross platform API for timeline data. <cxx/bridges>`

You can think of OTIO as a modern Edit Decision List (EDL) that also includes an API for reading, writing, and
manipulating editorial data. 

OpenTimelineIO’s API's and language bindings allows application developers to integrate OpenTimelineIO support into their products, 
and allows studios and developers to build an ecosystem of compatible pipeline tools. 

See our OTIO fundamentals guide, and intros for [Creatives](intros/creatives.md), Pipeline Architects, Integrators and Developers, and our FAQs. 

OpenimelineIO is a [Academy Software Foundation](https://www.aswf.io) incubation project.


Links
---------
`OpenTimelineIO Home Page <http://opentimeline.io/>`_

`OpenTimelineIO Discussion Group <https://lists.aswf.io/g/otio-discussion>`_


Getting Started
---------------
.. toctree::
   :maxdepth: 1
   :caption: Getting Started

   intros/installation.md
   intros/creatives.md
   intros/pipeline.md
   intros/integrators.md
   intros/integrations.md
   intros/roadmap.md
   intros/contributing.md

User Tutorials
--------------
.. toctree::
   :maxdepth: 1
   :caption: User Tutorials

   user_tutorials/sample_media.md
   user_tutorials/roundtripping.md
   user_tutorials/animation-shot-frame-ranges
   user_tutorials/conform-new-renders-into-cut
   user_tutorials/shots-added-removed-from-cut


API Fundamentals
----------------
.. toctree::
   :maxdepth: 1
   :caption: API Fundamentals
   
   fundamentals/introduction
   fundamentals/otio-timeline-structure
   fundamentals/time-ranges
   fundamentals/spatial-coordinates


Python Fundamentals
-------------------
.. toctree::
   :maxdepth: 1
   :caption: Python Fundamentals

   python/architecture
   python/feature-matrix
   python/adapters.md
   python/otio-plugins.md 
   python/otio-env-variables.md 


Python Tutorials
-------------------
.. toctree::
   :maxdepth: 1
   :caption: Python Tutorials

   python-tutorials/write-an-adapter
   python-tutorials/write-a-media-linker
   python-tutorials/write-a-hookscript
   python-tutorials/write-a-schemadef
   python-tutorials/developing-a-new-schema
   python-tutorials/versioning-schemas

API References
--------------

.. toctree::
   :maxdepth: 3
   :caption: API References

   python_reference

   cxx/bridges.md
   cxx/cxx.md
   cxx/older.md

Schema References
-----------------

.. toctree::
   :maxdepth: 2
   :caption: Schema References

   schema/otio-filebundles
   schema/otio-file-format-specification
   schema/otio-serialized-schema
   schema/otio-serialized-schema-only-fields


Utilities
---------

.. toctree::
   :maxdepth: 1
   :caption: Utilities

   utilities/otio_convert_quickstart.md
   utilities/otio_viewer_quickstart.md
   utilities/raven.md


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
