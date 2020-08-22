# Adapters

OpenTimelineIO supports, or plans to support, conversion adapters for many
existing file formats.

### Final Cut Pro XML ###

Final Cut 7 XML Format
- Status: Supported via the `fcp_xml` adapter
- <a href="https://developer.apple.com/library/content/documentation/AppleApplications/Reference/FinalCutPro_XML/AboutThisDoc/AboutThisDoc.html#//apple_ref/doc/uid/TP30001152-TPXREF101" target="_blank">Reference</a>

Final Cut Pro X XML Format:
- Status: Supported via the `fcpx_xml` adapter
- <a href="https://developer.apple.com/library/mac/documentation/FinalCutProX/Reference/FinalCutProXXMLFormat/Introduction/Introduction.html" target="_blank">Intro to FCP X XML</a>

### Adobe Premiere Project ###

- Based on guidance from Adobe, we support interchange with Adobe Premiere via 
    the FCP 7 XML format (see above).

### CMX3600 EDL ###

- Status: Supported via the `cmx_3600` adapter
- Includes support for ASC_CDL color correction metadata
- Full specification: SMPTE 258M-2004 "For Television −− Transfer of Edit Decision Lists"
- http://xmil.biz/EDL-X/CMX3600.pdf
- <a href="https://documentation.apple.com/en/finalcutpro/usermanual/index.html#chapter=96%26section=1" target="_blank">Reference</a>

### Avid AAF ###

- Status: Reads and writes AAF compositions
  - includes clip, gaps, transitions but not markers or effects
  - This adapter is still in progress, see the ongoing work here: <a href="https://github.com/PixarAnimationStudios/OpenTimelineIO/projects/1" target="_blank">AAF Project</a>
- <a href="http://www.amwa.tv/downloads/specifications/aafobjectspec-v1.1.pdf" target="_blank">Spec</a>
- <a href="http://www.amwa.tv/downloads/specifications/aafeditprotocol.pdf" target="_blank">Protocol</a>

- Depends on the <a href="https://github.com/markreidvfx/pyaaf2" target="_blank">`PyAAF2`</a> module, so either:
    - `pip install pyaaf2`
    - ...or set `${OTIO_AAF_PYTHON_LIB}` to point the location of the PyAAF2 module

Contrib Adapters
----------------

The contrib area hosts adapters which come from the community (_not_ supported 
    by the core-otio team) and may require extra dependencies.

### RV Session File ###

- Status: write-only adapter supported via the `rv_session` adapter.
- need to set environment variables to locate `py-interp` and `rvSession.py` 
    from within the RV distribution
- set `${OTIO_RV_PYTHON_BIN}` to point at `py-interp` from within rv, for 
    example:
    `setenv OTIO_RV_PYTHON_BIN /Applications/RV64.app/Contents/MacOS/py-interp`
- set `${OTIO_RV_PYTHON_LIB}` to point at the parent directory of `rvSession.py`:
    `setenv OTIO_RV_PYTHON_LIB /Applications/RV64.app/Contents/src/python`
    
### Maya Sequencer ###

- Status: supported via the `maya_sequencer` adapter.
- set `${OTIO_MAYA_PYTHON_BIN}` to point the location of `mayapy` within the maya 
    installation.

### HLS Playlist ###

- Status: supported via the `hls_playlist` adapter.

### Avid Log Exchange (ALE) ###

- Status: supported via the `ale` adapter.

### Text Burn-in Adapter ###

Uses FFmpeg to burn text overlays into video media.

- Status: supported via the `burnins` adapter.

### GStreamer Editing Services Adapter ###

- Status: supported via the `xges` adapter.

### Kdenlive Adapter ###

- Status: supported via the kdenlive adapter

