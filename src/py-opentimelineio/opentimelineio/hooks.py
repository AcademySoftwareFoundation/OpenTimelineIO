# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

from . import (
    plugins,
    core,
)

__doc__ = """
HookScripts are plugins that run at defined points ("Hooks").

They expose a ``hook_function`` with signature:

.. py:function:: hook_function(timeline: opentimelineio.schema.Timeline, optional_argument_dict: dict[str, Any]) -> opentimelineio.schema.Timeline  # noqa
   :noindex:

   Hook function signature

Both hook scripts and the hooks they attach to are defined in the plugin
manifest.

Multiple scripts can be attached to a hook. They will be executed in list
order, first to last.

They are defined by the manifests :class:`HookScript`\\s and hooks areas.

.. code-block:: json

   {
       "OTIO_SCHEMA" : "PluginManifest.1",
       "hook_scripts" : [
           {
               "OTIO_SCHEMA" : "HookScript.1",
               "name" : "example hook",
               "filepath" : "example.py"
           }
       ],
       "hooks" : {
           "pre_adapter_write" : ["example hook"],
           "post_adapter_read" : []
       }
   }

The ``hook_scripts`` area loads the python modules with the ``hook_function``\\s to
call in them.  The ``hooks`` area defines the hooks (and any associated
scripts). You can further query and modify these from python.

.. code-block:: python

   import opentimelineio as otio
   hook_list = otio.hooks.scripts_attached_to("some_hook") # -> ['a','b','c']

   # to run the hook scripts:
   otio.hooks.run("some_hook", some_timeline, optional_argument_dict)

This will pass (some_timeline, optional_argument_dict) to ``a``, which will
a new timeline that will get passed into ``b`` with ``optional_argument_dict``,
etc.

To edit the order, change the order in the list:

.. code-block:: python

   hook_list[0], hook_list[2] = hook_list[2], hook_list[0]
   print hook_list # ['c','b','a']

Now ``c`` will run, then ``b``, then ``a``.

To delete a function the list:

.. code-block:: python

   del hook_list[1]

----
"""


@core.register_type
class HookScript(plugins.PythonPlugin):
    _serializable_label = "HookScript.1"

    def __init__(
        self,
        name=None,
        filepath=None,
    ):
        """HookScript plugin constructor."""

        super().__init__(name, filepath)

    def run(self, in_timeline, argument_map={}):
        """Run the hook_function associated with this plugin."""

        # @TODO: should in_timeline be passed in place?  or should a copy be
        #        made?
        return self._execute_function(
            "hook_function",
            in_timeline=in_timeline,
            argument_map=argument_map
        )

    def __str__(self):
        return "HookScript({}, {})".format(
            repr(self.name),
            repr(self.filepath)
        )

    def __repr__(self):
        return (
            "otio.hooks.HookScript("
            "name={}, "
            "filepath={}"
            ")".format(
                repr(self.name),
                repr(self.filepath)
            )
        )


def names():
    """Return a list of all the registered hooks."""

    return plugins.ActiveManifest().hooks.keys()


def available_hookscript_names():
    """Return the names of HookScripts that have been registered."""

    return [hs.name for hs in plugins.ActiveManifest().hook_scripts]


def available_hookscripts():
    """Return the HookScripts objects that have been registered."""
    return plugins.ActiveManifest().hook_scripts


def scripts_attached_to(hook):
    """Return an editable list of all the hook scripts that are attached to
    the specified hook, in execution order.  Changing this list will change the
    order that scripts run in, and deleting a script will remove it from
    executing
    """

    # @TODO: Should this return a copy?
    return plugins.ActiveManifest().hooks[hook]


def run(hook, tl, extra_args=None):
    """Run all the scripts associated with hook, passing in tl and extra_args.

    Will return the return value of the last hook script.

    If no hookscripts are defined, returns tl.
    """

    hook_scripts = plugins.ActiveManifest().hooks[hook]
    for name in hook_scripts:
        hs = plugins.ActiveManifest().from_name(name, "hook_scripts")
        tl = hs.run(tl, extra_args)
    return tl
