# Versioning Schemas


During development, it is natural that the fields on objects in OTIO change.  To accommodate this, OTIO has a system for handling version differences and upgrading older schemas to new ones.  There are two components:

1. `serializeable_label` on the class has a name and version field: `Foo.5` -- `Foo` is the schema name and `5` is the version.
2. `upgrade_function_for` decorator


Changing a Field
---------------------

For example, lets say you have class:

```python
import opentimelineio as otio

@otio.core.register_type
class SimpleClass(otio.core.SerializeableObject):
  serializeable_label = "SimpleClass.1"
  my_field = otio.core.serializeable_field("my_field", int)
```


And you want to change `my_field` to `new_field`.  To do this:

- Make the change in the class
- Bump the version number in the label
- add an upgrade function

So after the changes, you'll have:

```python
@otio.core.register_type
class SimpleClass(otio.core.SerializeableObject):
  serializeable_label = "SimpleClass.2"
  my_field = otio.core.serializeable_field("new_field", int)

@otio.core.upgrade_function_for(SimpleClass, 2)
def upgrade_one_to_two(data):
  return {"new_field" : data["my_field"] }
```

Lets change it again, so that `new_field` becomes `even_newer_field`.

```python
@otio.core.register_type
class SimpleClass(otio.core.SerializeableObject):
  serializeable_label = "SimpleClass.2"
  my_field = otio.core.serializeable_field("even_newer_field", int)

@otio.core.upgrade_function_for(SimpleClass, 2)
def upgrade_one_to_two(data):
  return {"new_field" : data["my_field"] }

# NOTE we now have a second upgrade function
@otio.core.upgrade_function_for(SimpleClass, 3)
def upgrade_two_to_three(data):
  return {"even_newer_field" : data["new_field"] }
```

Upgrade functions can be sparse - if version `3` to `4` doesn't require a function, for example, you don't need to write one.

Adding or Removing a Field
--------------------------------

Starting from the same class:

```python
@otio.core.register_type
class SimpleClass(otio.core.SerializeableObject):
  serializeable_label = "SimpleClass.1"
  my_field = otio.core.serializeable_field("my_field", int)
```

Adding or Removing a field is simpler.  In these cases, you don't need to write an upgrade function, since any new classes will be initialized through the constructor, and any removed fields will be ignored when reading from an older schema version.

So lets add a new field:

```python
@otio.core.register_type
class SimpleClass(otio.core.SerializeableObject):
  serializeable_label = "SimpleClass.2"
  my_field = otio.core.serializeable_field("my_field", int)
  other_field = otio.core.serializeable_field("other_field", int)
```

And then delete the original field:

```python
@otio.core.register_type
class SimpleClass(otio.core.SerializeableObject):
  serializeable_label = "SimpleClass.3"
  other_field = otio.core.serializeable_field("other_field", int)
```