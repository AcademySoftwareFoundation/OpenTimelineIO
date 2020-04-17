OTIO Import and Export plugins
===============================
These plugins will let you import and export a sequence in Hiero directly to/from OTIO files without having to go via an XML or EDL.


Features:
---------
* Multiple tracks
* Tags in metadata (export)
* Markers (import for now, export soon)
* Simple retimes
* Fade in/out and cross dissolves
   

Install:
--------
Make sure the plugins are available to Hiero on startup. One way to do this is by updating/setting Hiero's plugin 
environment variable.<br>
Add `<OTIO_INSTALL_PATH>/opentimelineio_contrib/application_plugins/hiero` to the `HIERO_PLUGIN_PATH` environment variable.<br>

Alernatively you can copy the exporter files to `"~/.hiero/Python/Startup/otioexporter"` or `"~/.hiero/Python/Startup/otioimporter"` and they should appear in Hiero.

Make sure you have OTIO available in `PYTHONPATH` before you launch.

Usage OTIO Import:
------------------
Right click in a project bin and select `"Import->Import OTIO"`. Select an `".otio"` file and it should create a sequence with associated clips.

Usage OTIOExportTask:
---------------------
In Hiero's export dialog choose `"Process as Sequence"` and create a new preset called `"OTIO Export"`.<br>
Add a new **PATH** and choose `"OTIO Exporter"` from the list of available exporters in the **CONTENT** column.<br> 
Make sure to either use the `"{ext}"` token or end your filename with a `".otio"` extension.<br>
The `"include tags"` checkbox toggles inclusion of tags assigned to clips in the OTIO metadata.<br>
Tags get stored in `<OTIO_Clip>.metadata['Hiero']['tags']`.

Some Use Cases:
---------------
* Exchange edit with other OTIO compatible applications or tools
* Combined with other scripts and tools, transcode sequence/shots to formats not supported by Hiero
* Preview edit in an other application or toolset
