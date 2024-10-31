# Writing an OTIO SchemaDef Plugin

OpenTimelineIO SchemaDef plugins are plugins that define new schemas within the
otio type registry system.
You might want to do this to add new schemas that are specific to your own
internal studio workflow and shouldn't be part of the generic OpenTimelineIO
package.

To write a new SchemaDef plugin, you create a Python source file that
defines and registers one or more new classes subclassed from
``otio.core.SerializeableObject``.  Multiple schema classes can be defined
and registered in one plugin, or you can use a separate plugin for each of them.

Here's an example of defining a very simple class called ``MyThing``:

```python
import opentimelineio as otio

@otio.core.register_type
class MyThing(otio.core.SerializableObject):
    """A schema for my thing."""

    _serializable_label = "MyThing.1"
    _name = "MyThing"

    def __init__(
        self,
        arg1=None,
        argN=None
    ):
        otio.core.SerializableObject.__init__(self)
        self.arg1 = arg1
        self.argN = argN

    arg1 = otio.core.serializable_field(
        "arg1",
        doc = ( "arg1's doc string")
    )

    argN = otio.core.serializable_field(
        "argN",
        doc = ( "argN's doc string")
    )

    def __str__(self):
        return "MyThing({}, {})".format(
            repr(self.arg1),
            repr(self.argN)
        )

    def __repr__(self):
        return "otio.schema.MyThing(arg1={}, argN={})".format(
            repr(self.arg1),
            repr(self.argN)
        )
```

In the example, the ``MyThing`` class has two parameters ``arg1`` and ``argN``,
but your schema class could have any number of parameters as needed to
contain the data fields you want to have in your class.

One or more class definitions like this one can be included in a plugin
source file, which must then be added to the plugin manifest as shown below.


## Registering Your SchemaDef Plugin

To create a new SchemaDef plugin, you need to create a Python source file
as shown in the example above.  Let's call it ``mything.py``.
Then you must add it to a plugin manifest:

```json
{
    "OTIO_SCHEMA" : "PluginManifest.1",
    "schemadefs" : [
        {
            "OTIO_SCHEMA" : "SchemaDef.1",
            "name" : "mything",
            "filepath" : "mything.py"
         }
    ]
}
```

The same plugin manifest may also include adapters and media linkers, if desired.

Then you need to add this manifest to your {term}`OTIO_PLUGIN_MANIFEST_PATH` environment
variable.

## Using the New Schema in Your Code

Now that we've defined a new otio schema, how can we create an instance of the
schema class in our code (for instance, in an adapter or media linker)?

SchemaDef plugins are loaded in a deferred way.  The load is triggered either
by reading a file that contains the schema or by manually asking the plugin for
its module object.  For example, if you have a `my_thing` schemadef module:

```python
import opentimelineio as otio

my_thing = otio.schema.schemadef.module_from_name('my_thing')
```

Once the plugin has been loaded, SchemaDef plugin modules are magically inserted 
into a namespace called ``otio.schemadef``, so you can create a class instance 
just like this:

```python
import opentimelineio as otio

mine = otio.schemadef.my_thing.MyThing(arg1, argN)
```

An alternative approach is to use the ``instance_from_schema``
mechanism, which requires that you create and provide a dict of the parameters:

```python
    mything = otio.core.instance_from_schema("MyThing", 1, {
        "arg1": arg1,
        "argN": argN
    })
```

This ``instance_from_schema`` approach has the added benefit of calling the
schema upgrade function to upgrade the parameters in the case where the requested
schema version is earlier than the current version defined by the schemadef plugin.
This seems rather unlikely to occur in practice if you keep your code up-to-date,
so the first technique of creating the class instance directly from
``otio.schemadef`` is usually preferred.
