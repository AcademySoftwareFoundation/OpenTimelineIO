OTIO Import and Export plugins
===============================
These plugins will let you import and export sequences in Hiero directly to/from OTIO files without 
having to go via an XML or EDL.


Features:
---------
* Multiple tracks
* Tags
* Markers
* Simple re-time (reverese, constant slowdown, constant speedup)
* Fade in/out and cross dissolves
* Nested sequences are created separately and replaced with gaps in the main sequence.
* Linked audio/video when clip shares same media source
   

Install:
--------
Make sure the plugins are available to Hiero on startup. One way to do this is by updating/setting 
Hiero's plugin environment variable.<br>
Add `<OTIO_INSTALL_PATH>/opentimelineio_contrib/application_plugins/hiero` to the `HIERO_PLUGIN_PATH` 
environment variable.<br>

Alernatively you can copy the exporter files to `"~/.nuke/Python/Startup/otioexporter"` or 
`"~/.nuke/Python/Startup/otioimporter"` (for Hiero12+) or `"~/.hiero/...` (for earlier releases) 
and they should appear in Hiero.

Make sure you have OTIO available in `PYTHONPATH` before you launch.


Usage OTIO Import:
------------------
Right click in a project bin and select `"Import->Import OTIO"`. 
Select an `".otio"` file and it should create a sequence with associated clips.


Usage OTIOExportTask:
---------------------
In Hiero's export dialog choose `"Process as Sequence"` and create a new preset called `"OTIO Export"`.<br>
Add a new **PATH** and choose `"OTIO Exporter"` from the list of available exporters in the **CONTENT** column.<br> 
Make sure to either use the `"{ext}"` token or end your filename with a `".otio"` extension.<br>
The `"include tags"` checkbox toggles inclusion of tags assigned to clips in the OTIO metadata.<br>
Tags get stored as markers.


Some Use Cases:
---------------
* Exchange edit with other OTIO compatible applications or tools
* Combined with other scripts and tools, transcode sequence/shots to formats not supported by Hiero
* Preview edit in an other application or toolset


Limitations:
----
* Tags/markers are applied to both clips and track items on import if no metadata indicates source type. 
