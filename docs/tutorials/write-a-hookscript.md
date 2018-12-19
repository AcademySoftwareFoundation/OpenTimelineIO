# Writing a Hook Script

OpenTimelineIO Hook Scripts are plugins that run at predefined points during the execution of various OTIO functions, for example after an adapter has read a file into memory but before the media linker has run.

To write a new hook script, you create a python source file that defines a 
a function named ``hook_function`` with signature:
``hook_function :: otio.schema.Timeline, Dict => otio.schema.Timeline``

The first argument is the timeline to process, and the second one is a dictionary of arguments that can be passed to it.  Only one hook function can be defined per python file.

For example:
```python

def hook_function(tl, arg_dict):
    for cl in tl.each_clip():
        cl.metadata['example_hook_function_was_here'] = True
    return tl
```

This will insert some extra metadata into each clip.

This plugin can then be registered with the system by configuring a plugin manifest.

## Registering Your Hook Script
 
To create a new OTIO hook script, you need to create a file myhooks.py. Then add a manifest that points at that python file:

```
{
    "OTIO_SCHEMA" : "PluginManifest.1",
    "hook_scripts" : [
        {
            "OTIO_SCHEMA" : "HookScript.1",
            "name" : "example hook",
            "execution_scope" : "in process",
            "filepath" : "myhooks.py"
        }
    ],
    "hooks" : {
        "pre_adapter_write" : ["example hook"],
        "post_adapter_read" : [],
        "post_media_linker" : []
    }
}
```

The ``hook_scripts`` section will register the plugin with the system, and the ``hooks`` section will attach the scripts to hooks.

Then you need to add this manifest to your `$OTIO_PLUGIN_MANIFEST_PATH` environment variable (which is "`:`" separated).  You may also define media linkers and adapters via the same manifest.

## Running a Hook Script

If you would like to call a hook script from a plugin, the hooks need not be one of the ones that otio pre-defines.  You can have a plugin adapter or media linker, for example, that defines its own hooks and calls your own custom studio specific hook scripts.  To run a hook script from your custom code, you can call:

``otio.hooks.run("some_hook", some_timeline, optional_argument_dict)``

This will call the ``some_hook`` hook script and pass in ``some_timeline`` and ``optional_argument_dict``.

## Order of Hook Scripts

To query which hook scripts are attached to a given hook, you can call:

```
import opentimelineio as otio
hook_list = otio.hooks.scripts_attached_to("some_hook") 
```

Note that ``hook_list`` will be in order of execution.  You can rearrange this list, or edit it to change which scripts will run (or not run) and in which order.

To Edit the order, change the order in the list:
```
hook_list[0], hook_list[2] = hook_list[2], hook_list[0]
print hook_list # ['c','b','a']
```

Now c will run, then b, then a.

To delete a function the list:
```
del hook_list[1]
```
