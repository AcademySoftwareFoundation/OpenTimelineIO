OTIOExportTask
==============
This plugin will let you export a sequence in Hiero directly to an OTIO file without having to go via an XML or EDL.


Features:
---------
* Multiple tracks
* Tags in metadata
* Simple retimes
* Basic transitions
   

Install:
--------
Make sure the exporter is available to Hiero on startup. One way to do this is by updating/setting Hiero's plugin 
environment variable.<br>
Add `<OTIO_INSTALL_PATH>/opentimelineio_contrib/application_plugins/hiero` to the `HIERO_PLUGIN_PATH` environment variable.<br>
Because Hiero is a bit strange you have to point the environment variable to the `"hiero"` folder where Hiero can find 
`"Python"`and do it's import magic. Not all the way in to the `"otioexporter"` folder as one might think.

Alernatively you can copy the exporter files to `"~/.hiero/Python/Startup/otioexporter"` and they should appear in Hiero.

It goes without saying, but make sure you also have OTIO available in `PYTHONPATH` before you launch.

Usage:
------
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
