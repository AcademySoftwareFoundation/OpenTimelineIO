# Writing a Hook Script

OpenTimelineIO Hook Scripts are plugins that run at predefined points during the execution of various OTIO functions, for example after an adapter has read a file into memory but before the media linker has run.

To write a new hook script, you create a python source file that defines a 
function named ``hook_function`` with signature:
``hook_function :: otio.schema.Timeline, Dict => otio.schema.Timeline``

The first argument is the timeline to process, and the second one is a dictionary of arguments that can be passed to it by the adapter or media linker.  Only one hook function can be defined per python file.

For example:
```python
def hook_function(tl, argument_map=None):
    for cl in tl.each_clip():
        cl.metadata['example_hook_function_was_here'] = True
    return tl
```

This will insert some extra metadata into each clip.

This plugin can then be registered with the system by configuring a plugin manifest.

## Registering Your Hook Script
 
To create a new OTIO hook script, you need to create a file myhooks.py. Then add a manifest that points at that python file:

```json
{
    "OTIO_SCHEMA" : "PluginManifest.1",
    "hook_scripts" : [
        {
            "OTIO_SCHEMA" : "HookScript.1",
            "name" : "example hook",
            "filepath" : "myhooks.py"
        }
    ],
    "hooks" : {
        "pre_adapter_write" : ["example hook"],
        "post_adapter_read" : [],
        "post_adapter_write" : [],
        "post_media_linker" : []
    }
}
```

The ``hook_scripts`` section will register the plugin with the system, and the ``hooks`` section will attach the scripts to hooks.

Then you need to add this manifest to your {term}`OTIO_PLUGIN_MANIFEST_PATH` environment variable.
You may also define media linkers and adapters via the same manifest.

## Running a Hook Script

If you would like to call a hook script from a plugin, the hooks need not be one of the ones that OTIO pre-defines.  You can have a plugin adapter or media linker, for example, that defines its own hooks and calls your own custom studio specific hook scripts.  To run a hook script from your custom code, you can call:

```python
otio.hooks.run("some_hook", some_timeline, optional_argument_dict)
```

This will call the ``some_hook`` hook script and pass in ``some_timeline`` and ``optional_argument_dict``.

## Order of Hook Scripts

To query which hook scripts are attached to a given hook, you can call:

```python
import opentimelineio as otio
hook_list = otio.hooks.scripts_attached_to("some_hook") 
```

Note that ``hook_list`` will be in order of execution.  You can rearrange this list, or edit it to change which scripts will run (or not run) and in which order.

To Edit the order, change the order in the list:
```python
hook_list[0], hook_list[2] = hook_list[2], hook_list[0]
print hook_list # ['c','b','a']
```

Now c will run, then b, then a.

To delete a function in the list:
```python
del hook_list[1]
```

## Example Hooks

### Replacing part of a path for drive mapping

An example use-case would be to create a pre-write adapter hook that checks the argument map for a style being identified as nucoda and then performs a path replacement on the reference url:

```python
def hook_function(in_timeline,argument_map=None):
    adapter_args = argument_map.get('adapter_arguments')
    if adapter_args and adapter_args.get('style') == 'nucoda':
        for in_clip in in_timeline.each_clip():
            ''' Change the Path to use windows drive letters ( Nucoda is not otherwise forward slash sensitive ) '''
            if in_clip.media_reference:
                in_clip.media_reference.target_url = in_clip.media_reference.target_url.replace(r'/linux/media/path','S:')
```

### Add an incremental copy of otio file to backup folder

Example of a post adapter write hook that creates a timestamped copy of newly written file in a hidden "incremental" folder:

```python
import os
import time
import shutil

def hook_function(in_timeline, argument_map=None):
    # Adapter will add "_filepath" to argument_map
    filepath = argument_map.get('_filepath')

    backup_name = "{filename}.{time}".format(
        filename=os.path.basename(filepath),
        time=time.time()
    )
    incrpath = os.path.join(
        os.path.dirname(filepath),
        '.incremental',
        backup_name
    )   
    shutil.copyfile(filepath, incrpath)

    return in_timeline    
```

Please note that if a "post adapter write hook" changes `in_timeline` in any way, the api will not automatically update the already serialized file.  The changes will only exist in the in-memory object, because the hook runs _after_ the file is serialized to disk.

## Implementing Adapter-specific hooks

While OTIO ships with a set of pre-defined hooks (e.g. `pre_adapter_write`), you can also define your own hooks in your adapter.
These can be useful to give the user more fine-grained control over the execution of your adapter and make it work for their specific workflow.
A good example is media embedding within Avids AAF files: Depending on the workflow, media references might have to be transcoded to be compatible with the AAF format.
To achieve this, the AAF adapter could define a hook which users can leverage to transcode the files before embedding is attempted.

To define a custom hook in your adapter, you need to implement the `adapter_hook_names` function in your adapter module.
You can define as many hooks as you like, but try to use the native hooks where possible to keep the API consistent. 

```python
# my_aaf_adapter.py

def read_from_file(self, filepath, **kwargs):
    ...

def write_to_file(self, timeline, filepath, **kwargs):
    ...

def adapter_hook_names() -> List[str]:
    """Returns names of custom hooks implemented by this adapter."""
    return [
        "my_custom_adapter_hook"
    ]
```

The new hooks also need to be added to the adapter plugin manifest.

```json
{
    "OTIO_SCHEMA" : "PluginManifest.1",
    "adapters" : [
        {
            "OTIO_SCHEMA" : "Adapter.1",
            "name" : "My AAF Adapter",
            "execution_scope" : "in process",
            "filepath" : "adapters/my_aaf_adapter.py",
            "suffixes" : ["aaf"]
        }
    ],
    "hook_scripts" : [
        {
            "OTIO_SCHEMA" : "HookScript.1",
            "name" : "script_attached_to_custom_adapter_hook",
            "filepath" : "my_custom_adapter_hook_script.py"
        }
    ],
    "hooks" : {
        "pre_adapter_write" : [],
        "post_adapter_read" : [],
        "post_adapter_write" : [],
        "post_media_linker" : [],
        "my_custom_adapter_hook" : ["script_attached_to_custom_adapter_hook"]
    }
}
```

A custom hook script might look like this:

```python
# my_custom_adapter_hook_script.py

def hook_function(timeline, custom_argument, argument_map=None):
    # Do something with the timeline
    print(
        f"Running custom adapter hook with custom argument value '{custom_argument}'"
        f"and argument map: {argument_map}"
    )
    return timeline
```

Attached hook scripts can then be run anywhere using the `otio.hooks.run` function:

```python
# my_aaf_adapter.py

def write_to_file(self, timeline, filepath, **kwargs):
    # Do something
    ...
    # Run custom hook script with it's custom arguments and pass hook_argument_map along
    otio.hooks.run(
        "my_custom_adapter_hook", timeline, 
        custom_argument="some_value", 
        argument_map=kwargs.get("hook_argument_map", {})
    )
    ...
    # Do something more
```