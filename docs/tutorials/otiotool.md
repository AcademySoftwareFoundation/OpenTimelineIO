# otiotool Tutorial

`otiotool` is a command-line utility in OpenTimelineIO for inspecting, manipulating, and transforming OTIO timeline files. This tutorial covers its main features and usage patterns, with practical examples.

## Installation

`otiotool` is included with several other command line utilities as part of the
OpenTimelineIO Python module. You can install it via typical Python utilities
like `pip`, etc. See [Quickstart](./quickstart#install-otio]) for details.

[!NOTE] If you have
[uv installed](https://docs.astral.sh/uv/), then you can use `otiotool` with
this handy shortcut without having to deal with any installation:

```bash
uvx --from opentimelineio otiotool
```

## Basic Usage

`otiotool` reads one or more OTIO timeline files, optionally makes changes to the timelines, and outputs a text report and/or a new OTIO file with the result.

To run `otiotool` for reporting, use options like `--list-clips` or `--list-tracks`. The report output is
printed to the console:

```bash
otiotool --input <input_file.otio> [more inputs...] [options]
```

Report output can be redirected from standard output
to a file like any terminal program:

```bash
otiotool --input <input_file.otio> [more inputs...] [options] > report.txt
```

To run `otiotool` to create a new OTIO file, use:

```bash
otiotool --input <input_file.otio> [more inputs...] [options] --output <output_file.otio>
```

Many of `otiotool`'s command line options have a long and a short form. For example: `--input` is also `-i`, and `--output` is `-o`.

Multiple options of `otiotool` can be combined into
a single invocation. For example, you might read a file,
trim it, remove some tracks, verify missing media into
a report and output a new file all in one command like this:

```bash
otiotool -i multitrack.otio -trim 20 30 --video-only --verify-media -o output.otio > report.txt
```

For a complete listing of all options use `otiotool -h`.

## Phases

Unlike some other command line tools, the order in which options appear on
the command line does not matter. For example these two commands do the same thing:

```bash
otiotool -i input.otio --flatten -o output.otio
otiotool --flatten -o output.otio -i input.otio
```

Instead, the features of this tool work in phases, as follows:

1. Input

    Input files provided by the `--input <filename>` argument(s) are read into
    memory. Files may be OTIO format, or any format supported by adapter
    plugins.

2. Filtering

    Options such as `--video-only`, `--audio-only`, `--only-tracks-with-name`,
    `--only-tracks-with-index`, `--only-clips-with-name`,
    `--only-clips-with-name-regex`, `--remove-transitions`, and `--trim` will remove
    content. Only the tracks, clips, etc. that pass all of the filtering options
    provided are passed to the next phase.

3. Combine

    If specified, the `--stack` or `--concat` operations are
    performed (in that order) to combine all of the input timeline(s) into one.

4. Flatten

    If `--flatten` is specified, multiple tracks are flattened into one.

5. Relink

    The `--relink-by-name` option, will scan the specified folder(s) looking for
    files which match the name of each clip in the input timeline(s).
    If matching files are found, clips will be relinked to those files (using
    file:// URLs). Clip names are matched to filenames ignoring file extension.
    If specified, the `--copy-media-to-folder` option, will copy or download
    all linked media, and relink the OTIO to reference the local copies.

6. Remove/Redact

    The `--remove-metadata-key` option allows you to remove a specific piece of
    metadata from all objects.
    If specified, the `--redact` option, will remove ALL metadata and rename all
    objects in the OTIO with generic names (e.g. "Track 1", "Clip 17", etc.)

7. Inspect

    Options such as `--stats`, `--list-clips`, `--list-tracks`, `--list-media`,
    `--verify-media`, `--list-markers`, `--verify-ranges`, and `--inspect`
    will examine the OTIO and print information to standard output.

8. Output

    Finally, if the `--output <filename>` option is specified, the resulting
    OTIO will be written to the specified file. The extension of the output
    filename is used to determine the format of the output (e.g. OTIO or any
    format supported by the adapter plugins.) If you need to output an older
    schema version, see the `--downgrade` option.


## Listing Timeline Contents

### List Tracks
Prints all tracks in the timeline:
```bash
otiotool -i multitrack.otio --list-tracks
```
Output:
```
TIMELINE: OTIO TEST - multitrack.Exported.01
TRACK: Sequence (Video)
TRACK: Sequence 2 (Video)
TRACK: Sequence 3 (Video)
```

### List Clips, Markers, etc.
Prints all clips and markers in the timeline:
```bash
otiotool -i screening_example.otio --list-clips --list-markers
```
Output:
```
TIMELINE: Example_Screening.01
  CLIP: ZZ100_501 (LAY3)
  CLIP: ZZ100_502A (LAY3)
  CLIP: ZZ100_503A (LAY1)
  CLIP: ZZ100_504C (LAY1)
  MARKER: global: 00:59:49:13 local: 01:00:01:14 duration: 0.0 color: RED name: ANIM FIX NEEDED
  MARKER: global: 00:59:50:13 local: 01:00:02:14 duration: 0.0 color: PINK
  ...
```

## Filtering Tracks and Clips

### Video or Audio Only
List only video or audio clips:
```bash
otiotool -i premiere_example.otio --video-only --list-clips
otiotool -i premiere_example.otio --audio-only --list-clips
```

### Filter by Track Name or Index
```bash
otiotool -i multitrack.otio --only-tracks-with-name "Sequence 3" --list-clips
otiotool -i multitrack.otio --only-tracks-with-index 3 --list-clips
```

Indexes for `--only-tracks-with-index` begin at 1 for the first track, and that you often want to use it in combination with `--video-only` or `--audio-only`.

### Filter Clips by Name or Regex
```bash
otiotool -i premiere_example.otio --list-clips --only-clips-with-name "sc01_sh010_anim.mov"
otiotool -i premiere_example.otio --list-clips --only-clips-with-name-regex "sh\d+_anim"
```

The `--only-clips-with-name-regex` option uses the [Python Regular Expression syntax](https://docs.python.org/3/library/re.html).

## Media Information

### List Media References
```bash
otiotool -i multitrack.otio --list-tracks --list-clips --list-media
```

### Verify Media Existence
Checks if media files exist. Only local file paths are checked by `otiotool`, not URLs or other non-file path media references.
```bash
otiotool -i premiere_example.otio --verify-media
```

## Statistics and Inspection

### Print Timeline Stats
```bash
otiotool -i multitrack.otio --stats
```
Output:
```
Name: OTIO TEST - multitrack.Exported.01
Start:    00:00:00:00
End:      00:02:16:18
Duration: 00:02:16:18
```

### Inspect Items
Show details for a specific item:
```bash
otiotool -i multitrack.otio --inspect "KOLL"
```
Output:
```
TIMELINE: OTIO TEST - multitrack.Exported.01
  ITEM: KOLL-HD.mp4 (<class 'opentimelineio._otio.Clip'>)
    source_range: TimeRange(RationalTime(0, 24), RationalTime(640, 24))
    trimmed_range: TimeRange(RationalTime(0, 24), RationalTime(640, 24))
    visible_range: TimeRange(RationalTime(0, 24), RationalTime(640, 24))
    range_in_parent: TimeRange(RationalTime(1198, 24), RationalTime(640, 24))
    trimmed range in timeline: TimeRange(RationalTime(1198, 24), RationalTime(640, 24))
    visible range in timeline: TimeRange(RationalTime(1198, 24), RationalTime(640, 24))
    range in Sequence 3 (<class 'opentimelineio._otio.Track'>): TimeRange(RationalTime(1198, 24), RationalTime(640, 24))
    range in NestedScope (<class 'opentimelineio._otio.Stack'>): TimeRange(RationalTime(1198, 24), RationalTime(640, 24))
```

## Input/Output

### Input File(s)

Multiple input files can be specified via `--input` like this:

```bash
otiotool -i one.otio two.otio three.otio --concat -o result.otio
```

[!NOTE] When `otiotool` is given multiple inputs, the order of those inputs will affect the outcome of `--concat`, `--stack`, and any text reports printed to the console.

### Output File

Modifications to the timeline(s) can be written out to a new file with the
`--output <filename.otio>` option.

[!NOTE] The input files are never modified unless the
output path specifies the same file, in which case that file will be overwritten (not recommended).

### Multiple Timelines

If the result is a single timeline, then the output file will contain that timeline
as expected. However, if there were multiple input files and those timelines
were not combined with `--concat` or `--stack` then the output will be a single
file containing a SerializableCollection with multiple timelines. This is a
supported OTIO feature, but many tools and workflows expect only a single
timeline in an OTIO file.

### Standard In/Out

You can chain `otiotool` with other tools on the command
line.

If you specify the `--output` file as a single `-` then the resulting OTIO will
be printed as text to stdout instead of a file. 

```bash
otiotool -i multitrack.otio --video-only -o - | grep MissingReference
```

You can also use `-` as an
input from stdin.

```bash
curl https://example.com/some/path/premiere_example.otio | otiotool -i - --verify-media --stats
```

### Format Conversion

The format of the input and output file is inferred
from the filename extension. It can be `.otio` for an OTIO file, or any other
file format supported by an available [OTIO adapter plugin](./adapters).

Thus `otiotool`
can operate much like `otioconvert` however some more advanced conversion
options are only available in `otioconvert`. If you need both, you can write
to an intermediate OTIO file and convert to/from the other format in a separate
step.

```bash
otiotool -i multitrack.otio --flatten video --video-only -o single-track.otio
```

Combined with conversion to EDL (via [this adapter plugin](https://github.com/OpenTimelineIO/otio-cmx3600-adapter)):
```bash
uvx --from opentimelineio --with otio-cmx3600-adapter otiotool -i multitrack.otio --flatten video --video-only -o single-track.edl
```

## Timeline Manipulation

### Trim Timeline
Trim to a time range:
```bash
otiotool -i multitrack.otio --trim 20.5 40 -o output.otio
otiotool -i multitrack.otio --trim 00:01:00:00 00:02:00:00 -o output.otio
```

The start and end times for `--trim` can be either a floating point number of seconds
or timecode `HH:MM:SS:FF` in the frame rate inferred from the timeline itself.

### Flatten Tracks
Combine multiple tracks into one with `--flatten <TYPE>` where `TYPE` is either `video`, `audio`, or `all`:
```bash
otiotool -i multitrack.otio --flatten video -o output.otio --list-tracks
```

### Stack or Concatenate Timelines
Stack multiple timelines:
```bash
otiotool -i multitrack.otio premiere_example.otio --stack -o output.otio --list-tracks
```
Concatenate timelines end-to-end:
```bash
otiotool -i multitrack.otio premiere_example.otio --concat -o output.otio --stats
```

### Redact Timeline
Replace names of clips, tracks, etc. with generic labels:
```bash
otiotool -i multitrack.otio --redact -o output.otio --list-clips
```

### Remove Transitions
Remove all transitions:
```bash
otiotool -i transition.otio --remove-transitions -o output.otio
```

## OTIO Schema Versions

When `otiotool` reads an older OTIO format, it will automatically upgrade
the file to the newest schema supported by `otiotool`.

When working with an application or workflow that requires an older OTIO
file format, you can use `otiotool` to downgrade an OTIO to a specific schema
version which is compatible.

See [Versioning Schemas](./versioning-schemas) to understand this in detail.

```bash
otiotool --list-versions
```
Output:
```
Available versions for --downgrade FAMILY:VERSION
  OTIO_CORE:0.14.0
  OTIO_CORE:0.15.0
  OTIO_CORE:0.16.0
  OTIO_CORE:0.17.0
```

```bash
otiotool -i multitrack.otio --downgrade OTIO_CORE:0.14.0 -o old-format.otio
```
