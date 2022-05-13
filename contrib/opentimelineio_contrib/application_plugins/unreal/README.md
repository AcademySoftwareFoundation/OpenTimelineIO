# OpenTimelineIO Unreal Engine Plugin

This OpenTimelineIO application plugin provides a configurable framework for
mapping between an OTIO timeline and an Unreal Engine level sequence hierarchy.

In the context of this plugin, OTIO stacks and clips map to level sequences;
stacks being interpreted as sequences containing shot tracks, and clips as
individual shot sections and their referenced sub-sequences. This approach
supports arbitrarily nested (or flat) Sequencer pipelines in UE, and leans on
implementation-defined hooks as a translation layer.

When importing a timeline, if a referenced level sequence does not yet exist,
it will be created at the configured path prior to adding it as a sub-sequence.
This capability enables some very useful automation workflows, supporting
simultaneous timeline syncing and setup of shot scaffolding.

The plugin itself optionally registers a UE Factory (import mechanism) and
Exporter (export mechanism) to add native support for importing any
OTIO-supported file format into a level sequence hierarchy, and exporting a
level sequence hierarchy to one OTIO-supported file format (*.otio by default).
These interfaces make OTIO import and export available in Unreal Editor, but in
most cases implementors will want to use the `otio_unreal` Python package to
directly integrate these interfaces into pipeline-specific workflows.

**NOTE**

This plugin's import function wraps all Unreal Editor changes in a
`ScopedEditorTransaction`, making the operation revertable with a single
`undo` action.

## Feature Matrix

This table outlines OTIO features which are currently supported by this plugin.
For unsupported features, contributions are welcome.

| Feature                  | Supported |
|--------------------------| --------- |
| Single Track of Clips    |     ✔     |
| Multiple Video Tracks    |     ✔     |
| Audio Tracks & Clips     |     ✖     |
| Gap/Filler               |     ✔     |
| Markers                  |     ✔     |
| Nesting                  |     ✔     |
| Transitions              |     ✖     |
| Audio/Video Effects      |     ✖     |
| Linear Speed Effects     |     ✔     |
| Fancy Speed Effects      |     ✖     |
| Color Decision List      |     ✖     |
| Image Sequence Reference |     ✖     |

## Install

There are two options for installing this plugin:

### Unreal Engine Plugin

To add the OpenTimelineIO Unreal Engine plugin to a UE project, move the
`OpenTimelineIO` directory to one of the two UE plugin search paths:

- Engine: `/<UE Root>/Engine/Plugins`
- Game: `/<Project Root>/Plugins`

To make the plugin fully self-contained, install the OTIO Python packages to
one or more platform-specific `site-packages` directories within this plugin's
`Content/Python/Lib/` folder. See each platform's `site-packages/README.md`
file for more detailed installation instructions.

After an Unreal Editor restart the `OpenTimelineIO (OTIO)` plugin can be
enabled in UE's `Plugins` dialog. Following another restart, all plugin
functionality and Python packages will be available in Unreal Editor.

### Python Only

To make this plugin available in Unreal Editor without installing it as a UE
plugin, simply add the contained `otio_unreal` Python package location and the
OTIO Python package location(s) to the `UE_PYTHONPATH` environment variable. UE
will run `init_unreal.py` on startup to register the import and export
interfaces, and these packages will be available in Unreal's Python
environment. Alternatively these same paths can be added to the `Python` plugin
`Additional Paths` property in UE project settings.

## Hooks

This plugin supports several custom OTIO hooks for implementing
pipeline-specific mapping between timelines and level sequences. Unless the
required `unreal` metadata is written to a timeline prior to import, at least
one import hook is required to successfully import a timeline. No hooks are
required to export a timeline, but can be used to setup media references
for rendered outputs.

| Hook                     | Stage  | Description                                                                                                                                                                                                 |
|--------------------------| ------ |-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| otio_ue_pre_import       | Import | Called to modify or replace a timeline prior to creating or updating a level sequence hierarchy during an OTIO import: <br/>`hook_function :: otio.schema.Timeline, Optional[Dict] => otio.schema.Timeline` |
| otio_ue_pre_import_item  | Import | Called to modify a stack or clip in-place prior to using it to update a level sequence or shot section during an OTIO import: <br/>`hook_function :: otio.schema.Item, Optional[Dict] => None`              |
| otio_ue_post_export      | Export | Called to modify or replace a timeline following an OTIO export from a level sequence hierarchy: <br/>`hook_function :: otio.schema.Timeline, Optional[Dict] => otio.schema.Timeline`                       |
| otio_ue_post_export_clip | Export | Called to modify a clip in-place following it being created from a shot section during an OTIO export: <br/>`hook_function :: otio.schema.Clip, Optional[Dict] => None`                                     |

The primary goal of the import hooks are to add the following metadata to each
stack and clip in the timeline which should map to a level sequence asset path
in Unreal Engine:

`"metadata": {"unreal": {"sub_sequence": "/Game/Path/To/Sequence.Sequence"}}`

Conversely, the goal of the export hooks are to interpret and convert this
metadata into media references which point to rendered outputs from a movie
render queue. By default all media references are set to `MissingReference`
on export.

Each of these goals can be implemented at a global level (updating the timeline
once) or a granular level (updating each stack and clip in-place).

See the [OTIO documentation](https://opentimelineio.readthedocs.io/en/latest/tutorials/write-a-hookscript.html)
for instructions on adding hooks to the OTIO environment.

**Note**

The root level sequence should be referenced by the timeline's top-level
"tracks" stack. In practice though, implementors may find it is preferrable
to create a custom menu command which uses the current level sequence as
the root for a more adaptable user experience. A custom command could also
leverage a GUI with embedded `otioview` for previewing the effects of a
sequence update prior to committing to the change.

## Environment Variables

OTIO import/export behavior in Unreal Engine can also be configured with
a number of supported environment variables. None of these are required.

| Variable                  | Description                                                                                                                                               | Example        |
|---------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|----------------|
| OTIO_UE_REGISTER_UCLASSES | `1` (the default) enables OTIO uclass registration in UE, adding OTIO to native import and export interfaces. Set to `0` to disable all registration.     | `0`            |
| OTIO_UE_IMPORT_SUFFIXES   | Comma-separated list of OTIO adapter suffixes to register for import into UE. If undefined, all adapters are registered.                                  | `otio,edl,xml` |
| OTIO_UE_EXPORT_SUFFIX     | One OTIO adapter suffix to register for export from UE. Defaults to `otio`.                                                                               | `edl`          |

## Python API

The `otio_unreal` Python package provides an API to assist in implementing
this plugin into pipeline-specific tools and user interfaces. See the
`otio_unreal.adapter` module for the main interface documentation.

## Known Issues

- Registering an `unreal.Factory` via Python, as is done for the OTIO
  importer, doesn't pass the current Unreal Content Browser location to the
  created `unreal.AssetImportTask` `destination_path` attribute, preventing
  creation of the root level sequence in the expected directory when importing
  via a Content Browser context menu. If a hook defines `sub_sequence` in the
  imported timeline's root "tracks" stack `unreal` metadata, the level
  sequence will be created at that pipeline-defined location, otherwise it will
  be created in a default `/Game/Sequences` directory.
