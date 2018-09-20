#
# Copyright 2018 Pixar Animation Studios
#
# Licensed under the Apache License, Version 2.0 (the "Apache License")
# with the following modification; you may not use this file except in
# compliance with the Apache License and the following modification to it:
# Section 6. Trademarks. is deleted and replaced with:
#
# 6. Trademarks. This License does not grant permission to use the trade
#    names, trademarks, service marks, or product names of the Licensor
#    and its affiliates, except as required to comply with Section 4(c) of
#    the License and to reproduce the content of the NOTICE file.
#
# You may obtain a copy of the Apache License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the Apache License with the above modification is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the Apache License for the specific
# language governing permissions and limitations under the Apache License.
#

from . import (
    # exceptions,
    plugins,
    core,
)

__doc__ = """HookScripts are plugins that run at defined points ('Hooks').

They expose a hook_function with signature:
    hook_function :: otio.schema.Timeline, Dict -> otio.schema.Timeline

Both hook scripts and the hooks they attach to are defined in the plugin
manifest.

You can attach multiple hook scripts to a hook.  They will be executed in list
order, first to last.

They are defined by the manifests HookScripts and hooks areas.  For example:

{
    "OTIO_SCHEMA" : "PluginManifest.1",
    "hook_scripts" : [
        {
            "OTIO_SCHEMA" : "HookScript.1",
            "name" : "example hook",
            "execution_scope" : "in process",
            "filepath" : "example.py"
        }
    ],
    "hooks" : {
        "pre_adapter_write" : ["example hook"],
        "post_adapter_read" : []
    }
}

# the 'hook_scripts' area loads the python modules with the 'hook_function's to
# call in them.  The 'hooks' area defines the hooks (and any associated 
# scripts).  You can further query and modify these from python.

In other words:

import opentimelineio as otio
hook_list = otio.hooks.scripts_attached_to("some_hook") # -> ['a','b','c']

# to run the hook scripts:
otio.hooks.run("some_hook", some_timeline, optional_argument_dict)

# this will pass (some_timeline, optional_argument_dict) to 'a', which will
# a new timeline that will get passed into 'b' with optional_argument_dict,
# etc.

# To Edit the order, change the order in the list:
hook_list[0], hook_list[2] = hook_list[2], hook_list[0]
print hook_list # ['c','b','a']

# Now c will run, then b, then a.

# To delete a function the list:
del hook_list[1]
"""

@core.register_type
class HookScript(plugins.PythonPlugin):
    _serializable_label = "HookScript.1"

    def __init__(
        self,
        name=None,
        execution_scope=None,
        filepath=None,
    ):
        plugins.PythonPlugin.__init__(self, name, execution_scope, filepath)

    def run(self, in_timeline, argument_map={}):
        return self._execute_function(
            "hook_function",
            in_timeline=in_timeline,
            argument_map=argument_map
        )

    def __str__(self):
        return "HookScript({}, {}, {})".format(
            repr(self.name),
            repr(self.execution_scope),
            repr(self.filepath)
        )

    def __repr__(self):
        return (
            # @TODO: check this path to make sure it holds up as things settle
            "otio.hooks.HookScript("
            "name={}, "
            "execution_scope={}, "
            "filepath={}"
            ")".format(
                repr(self.name),
                repr(self.execution_scope),
                repr(self.filepath)
            )
        )


def names():
    """Return a list of all the registered hooks."""

    return plugins.ActiveManifest().hooks.keys()

def available_hookscript_names():
    return [hs.name for hs in plugins.ActiveManifest().hook_scripts]

def available_hookscripts():
    return plugins.ActiveManifest().hook_scripts

def list_attached_scripts_to(hook):
    return plugins.ActiveManifest().hooks[hook]


