# File Bundles

## Overview

This document describes OpenTimelineIO's file bundle formats, otiod and otioz.  The intent is that they make it easier to package and send or archive OpenTimelineIO data and associated media.

## Structure

File bundles, regardless of how they're encoded, have a consistent structure:

- something.otioz (or .otiod)
    - content.otio
    - media
        - media1
        - media2
        - media3

### content.otio file

This is a normal OpenTimelineIO file.  The only caveat is that all of its media references are either ExternalReferences with relative target_urls pointing into the `media` directory or `MissingReference`.

### Media Directory

The media directory contains all the media files in a flat structure.  They must have unique basenames.  The format of the media isn't restricted.

## Read Behavior

When a bundle is read from disk, the `content.otio` file is extracted from the bundle and returned.  For example, to view the timeline (not the media) of an otioz file in `otioview`, you can run:

`otioview sommething.otioz`

This will _only_ read the `content.otio` from the bundle, so is usually a fast operation to run.

## MediaReferencePolicy

When building a file bundle using the OTIOZ/OTIOD adapters, you can set the 'media reference policy', which is described by an enum in the file_bundle_utils module.  The policies can be:

- ErrorIfNotFile: will raise an exception if a media reference is found that is of type `ExternalReference` but that does not point at a `target_url`.
- MissingIfNotFile: will replace any media references that meet the above condition with a `MissingReference`, preserving the original media reference in the metadata of the new `MissingReference`.
- AllMissing: will replace all media references with `MissingReference`, preserving the original media reference in metadata on the new object.

## OTIOD

The OTIOD adapter will build a bundle in a directory stucture on disk.  The adapter will gather up all the files it can and copy them to the destination directory, and then build the `.otio` file with local relative path references into that directory.

## OTIOZ

The OTIOD adapter will build a bundle into a zipfile (using the zipfile library).

### Optional Arguments:

- Read:
    - extract_to_directory: if a value other than `None` is passed in, will extract the contents of the bundle into the directory at the path passed into the `extract_to_directory` argument.

## Example usage in otioconvert

### Convert an otio into a zip bundle

`otioconvert -i somefile.otio -o /var/tmp/somefile.otioz` 

### Extract the contents of the bundle and convert to an rv playlist

`otioconvert -i /var/tmp/somefile.otioz -a extract_to_directory=/var/tmp/somefile -o /var/tmp/somefile/somefile.rv`
