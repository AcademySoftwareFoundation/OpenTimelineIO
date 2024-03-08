# File Bundles

## Overview

This document describes OpenTimelineIO's file bundle formats, `otiod` and `otioz`, as well as how to use the internal adapters to generate file bundles.  The OTIOZ/D File Bundle format packages OpenTimelineIO data and associated media into a single file.  This can be useful for sending, archiving and interchange.

## OTIOZ/D File Bundle Format Details

File bundles have two separate encodings, OTIOZ and OTIOD.  OTIOD is an encoding that uses a directory hierarchy of files, and OTIOZ is the identical structure packed into a single zipfile, currently using the python `zipfile` library.  In either case they will contain a content.otio which is the cut information.

### Structure

File bundles have a consistent structure:

OTIOD:

```
something.otiod (directory)
├── content.otio (file)
└── media (directory)
    ├── media1 (file)
    ├── media2 (file)
    └── media3 (file)
```

OTIOZ (adds the version.txt file and is encoded in a zipfile):

```
something.otioz (zipfile)
├── content.otio (file)
├── version.txt (file)
└── media (directory)
    ├── media1 (file)
    ├── media2 (file)
    └── media3 (file)
```

### content.otio file

This is an OpenTimelineIO file whose media references are either `MissingReference`s, or `ExternalReference`s with target_urls that are relative paths pointing into the `media` directory.

### version.txt file

This file encodes the otioz version of the file, with no other text, in the form:

```
1.0.0
```

### "media" Directory

The `media` directory contains all the media files that the `ExternalReference`s `target_url`s in the `content.otio` point at, in a flat structure.  Each media file must have a unique basename, but can be encoded in whichever codec/container the user wishes (otio is unable to decode or encode the media files).

## Adapter Usage

## Read Adapter Behavior

When a bundle is read from disk using the OpenTimelineIO API (using `read_from_file`, for example), only the `content.otio` file is extracted from the bundle and returned.  

For example, to view the timeline (not the media) of an otioz file in `otioview`, you can run:

`otioview sommething.otioz`

This will _only_ read the `content.otio` from the bundle, so is usually a fast operation to run, and does not decode or unzip any of the media in the media directory.

### extract_to_directory Optional Argument:

extract_to_directory: if a value other than `None` is passed in, will extract the contents of the bundle into the directory at the path passed into the `extract_to_directory` argument.

### Read Adapter Example

Extract the contents of the bundle and convert to an rv playlist:

`otioconvert -i /var/tmp/somefile.otioz -a extract_to_directory=/var/tmp/somefile -o /var/tmp/somefile/somefile.rv`

## Write Adapter

### Source Timeline Constraints

For creating otio bundles using the provided python adapter, an OTIO file is used as input.  There are some constraints on the source timeline.

#### Unique Basenames

Because file bundles have a flat namespace for media, and media will be copied into the bundle, the `ExternalReference` media references in the source OTIO must have a target_url fields pointing at media files with unique basenames.  For example, if there are media references that point at:

`/project_a/academy_leader.mov`

and:

`/project_b/academy_leader.mov`

Because the basename of both files is `academy_leader.mov`, this will be an error.  The adapters have different policies for how to handle media references.  See below for more information.

#### Expected Source Timeline External Reference URL Format

The file bundle adapters expect the `target_url` field of any `media_reference`s in the source timeline to be in one of two forms (as produced by python's urlparse library):

- absolute path:  "file:///path/to/some/file" (encodes "/path/to/some/file")
- relative path: "path/to/some/file" (assumes the path is relative to the current working directory when invoking the adapter on the source timeline).

### MediaReferencePolicy Option

When building a file bundle using the OTIOZ/OTIOD adapters, you can set the 'media reference policy', which is described by an enum in the file_bundle_utils module.  The policies can be:

- (default) `ErrorIfNotFile`: will raise an exception if a media reference is found that is of type `ExternalReference` but that does not point at a `target_url`.
- `MissingIfNotFile`: will replace any media references that meet the above condition with a `MissingReference`, preserving the original media reference in the metadata of the new `MissingReference`.
- `AllMissing`: will replace all media references with `MissingReference`, preserving the original media reference in metadata on the new object.

When running in `AllMissing` mode, no media will be put into the bundle.

To use this argument with `otioconvert` from the commandline,  you can use the `-A` flag with the argument name `media_policy`:

```
otioconvert -i <somefile> -o path/to/outputfile.otioz -A media_policy="AllMissing"
```

### Write Adapter Example

Convert an otio into a zip bundle:

`otioconvert -i somefile.otio -o /var/tmp/somefile.otioz`
