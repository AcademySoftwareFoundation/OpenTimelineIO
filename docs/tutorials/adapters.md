# Adapters

OpenTimelineIO supports, or plans to support, conversion adapters for many
existing file formats.

## Final Cut Pro XML

Final Cut 7 XML Format
- Status: Supported via the `fcp_xml` adapter
- [Reference](https://developer.apple.com/library/archive/documentation/AppleApplications/Reference/FinalCutPro_XML/AboutThisDoc/AboutThisDoc.html#//apple_ref/doc/uid/TP30001152-TPXREF101)

Final Cut Pro X XML Format:
- Status: Supported via the `fcpx_xml` adapter
- [Intro to FCP X XML](https://developer.apple.com/library/mac/documentation/FinalCutProX/Reference/FinalCutProXXMLFormat/Introduction/Introduction.html)

## Adobe Premiere Project

- Based on guidance from Adobe, we support interchange with Adobe Premiere via
    the FCP 7 XML format (see above).

## CMX3600 EDL

- Status: Supported via the `cmx_3600` adapter
- Includes support for ASC_CDL color correction metadata
- Full specification: SMPTE 258M-2004 "For Television −− Transfer of Edit Decision Lists"
- http://xmil.biz/EDL-X/CMX3600.pdf
- [Reference](https://prohelp.apple.com/finalcutpro_help-r01/English/en/finalcutpro/usermanual/chapter_96_section_0.html)

## Avid AAF

- Status: Reads and writes AAF compositions
  - includes clip, gaps, transitions but not markers or effects
  - This adapter is still in progress, see the ongoing work here: [AAF Project](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/projects/1)
- [Spec](https://static.amwa.tv/ms-01-aaf-object-spec.pdf)
- [Protocol](https://static.amwa.tv/as-01-aaf-edit-protocol-spec.pdf)

- Depends on the [PyAAF2](https://github.com/markreidvfx/pyaaf2) module, so either:
    - `pip install pyaaf2`
    - ...or set `${OTIO_AAF_PYTHON_LIB}` to point the location of the PyAAF2 module

# Contrib Adapters

The contrib area hosts adapters which come from the community (_not_ supported
    by the core-otio team) and may require extra dependencies.

## RV Session File

- Status: write-only adapter supported via the `rv_session` adapter.
- need to set environment variables to locate `py-interp` and `rvSession.py`
    from within the RV distribution
- set `${OTIO_RV_PYTHON_BIN}` to point at `py-interp` from within rv, for
    example:
    `setenv OTIO_RV_PYTHON_BIN /Applications/RV64.app/Contents/MacOS/py-interp`
- set `${OTIO_RV_PYTHON_LIB}` to point at the parent directory of `rvSession.py`:
    `setenv OTIO_RV_PYTHON_LIB /Applications/RV64.app/Contents/src/python`

## HLS Playlist

- Status: supported via the `hls_playlist` adapter.

## Avid Log Exchange (ALE)

- Status: supported via the `ale` adapter.

## Text Burn-in Adapter

Uses FFmpeg to burn text overlays into video media.

- Status: supported via the `burnins` adapter.

## GStreamer Editing Services Adapter

- Status: supported via the `xges` adapter.

## Kdenlive Adapter

- Status: supported via the kdenlive adapter
