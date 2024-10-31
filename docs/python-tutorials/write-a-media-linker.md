# Writing an OTIO Media Linker

OpenTimelineIO Media Linkers are plugins that allow OTIO to replace MissingReferences with valid, site specific MediaReferences after an adapter reads a file.

The current MediaLinker can be specified as an argument to `otio.adapters.read_from_file` or via an environment variable.  If one is specified, then it will run after the adapter reads the contents of the file before it is returned back.

```python
    #/usr/bin/env python
    import opentimelineio as otio
    mytimeline = otio.adapters.read_from_file("something.edl", media_linker_name="awesome_studios_media_linker")
```

After the EDL adapter reads something.edl, the media linker "awesome_studios_media_linker" will run and link the media in the file (if it can).


## Registering Your Media Linker
 
To create a new OTIO Adapter, you need to create a file mymedialinker.py. Then add a manifest that points at that python file:


```json
        {
            "OTIO_SCHEMA" : "PluginManifest.1",
            "media_linkers" : [
                {
                    "OTIO_SCHEMA" : "MediaLinker.1",
                    "name" : "awesome_studios_media_linker",
                    "filepath" : "mymedialinker.py"
                 }
            ],
            "adapters" : [
            ]
        }
```
          
Then you need to add this manifest to your {term}`OTIO_PLUGIN_MANIFEST_PATH` environment variable.

Finally, to specify this linker as the default media linker, set {term}`OTIO_DEFAULT_MEDIA_LINKER` to the name of the media linker:

```bash
    export OTIO_DEFAULT_MEDIA_LINKER="awesome_studios_media_linker"
```

To package and share your media linker, follow [these instructions](write-an-adapter.md#packaging-and-sharing-custom-adapters).

## Writing a Media Linker
 
To write a media linker, write a python file with a "link_media_reference" function in it that takes two arguments: "in_clip" (the clip to try and add a media reference to) and "media_linker_argument_map" (arguments passed from the calling function to the media linker.

For example:

```python
    def link_media_reference(in_clip, media_linker_argument_map):
        d.update(media_linker_argument_map)
        # you'll probably want to set it to something other than a missing reference
        in_clip.media_reference = otio.schema.MissingReference(
            name=in_clip.name + "_tweaked",
            metadata=d
        )
```

## For Testing

The otioconvert.py script has a --media-linker argument you can use to test out your media linker (once its on the path).

```bash
    env OTIO_PLUGIN_MANIFEST_PATH=mymanifest.otio.json:$OTIO_PLUGIN_MANIFEST_PATH bin/otioconvert.py -i somefile.edl --media-linker="awesome_studios_media_linker" -o /var/tmp/test.otio
```
