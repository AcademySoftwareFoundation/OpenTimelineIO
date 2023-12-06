# Versioning Schemas

## Overview

This document describes OpenTimelineIO's systems for dealing with different schema versions when reading files, writing files, or during development of the library itself.  It is intended for developers who are integrating OpenTimelineIO into their pipelines or applications, or working directly on OpenTimelineIO.

TL;DR for users: OpenTimelineIO should be able to read files produced by older versions of the library and be able to write files that are compatible with older versions of the library from newer versions.

## Schema/Version Introduction

Each SerializableObject (the base class of OpenTimelineIO) has `schema_name` and `schema_version` fields.  The `schema_name` is a string naming the schema, for example, `Clip`, and the `schema_version` is an integer of the current version number, for example, `3`.

SerializableObjects can be queried for these using the `.schema_name()` and `.schema_version()` methods.  For a given release of the OpenTimelineIO library, in-memory objects the library creates will always be the same schema version.  In other words, if `otio.schema.Clip()` instantiates an object with `schema_version` 2, there is no way to get an in-memory `Clip` object with version 1.

OpenTimelineIO can still interoperate with older and newer versions of the library by way of the schema upgrading/downgrading system.  As OpenTimelineIO deserializes json from a string or disk, it will upgrade the schemas to the version supported by the library before instantiating the concrete in-memory object.  Similarly, when serializing OpenTimelineIO back to disk, the user can instruct OpenTimelineIO to downgrade the JSON to older versions of the schemas.  In this way, a newer version of OpenTimelineIO can read files with older schemas, and a newer version of OpenTimelineIO can generate JSON with older schemas in it.

## Schema Upgrading

Once a type is registered to OpenTimelineIO, developers may also register upgrade functions.  In python, each upgrade function takes a dictionary and returns a dictionary.  In C++, the AnyDictionary is manipulated in place.  Each upgrade function is associated with a version number - this is the version number that it upgrades to.

C++ Example (can be viewed/run in `examples/upgrade_downgrade_example.cpp`):
<!-- C++ Example (can be viewed/run in [examples/upgrade_downgrade_example.cpp](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/blob/main/examples/upgrade_downgrade_example.cpp)): -->

```cpp
class SimpleClass : public otio::SerializableObject
{
public:
    struct Schema
    {
        static auto constexpr name   = "SimpleClass";
        static int constexpr version = 2;
    };

    void set_new_field(int64_t val) { _new_field = val; }
    int64_t new_field() const { return _new_field; }

protected:
    using Parent = SerializableObject;

    virtual ~SimpleClass() = default;

    virtual bool 
    read_from(Reader& reader) 
    {
        auto result = (
            reader.read("new_field", &_new_field) 
            && Parent::read_from(reader)
        );

        return result;
    }

    virtual void 
    write_to(Writer& writer) const 
    {
        Parent::write_to(writer);
        writer.write("new_field", _new_field);
    }

private:
    int64_t _new_field;
};

    // later, during execution:

    // register type and upgrade/downgrade functions
    otio::TypeRegistry::instance().register_type<SimpleClass>();

    // 1->2
    otio::TypeRegistry::instance().register_upgrade_function(
        SimpleClass::Schema::name,
        2,
        [](otio::AnyDictionary* d)
        {
            (*d)["new_field"] = (*d)["my_field"];
            d->erase("my_field");
        }
    );
```

Python Example:

```python
@otio.core.register_type
class SimpleClass(otio.core.SerializableObject):
  serializable_label = "SimpleClass.2"
  my_field = otio.core.serializable_field("new_field", int)

@otio.core.upgrade_function_for(SimpleClass, 2)
def upgrade_one_to_two(data):
  return {"new_field" : data["my_field"] }
```

When upgrading schemas, OpenTimelineIO will call each upgrade function in order in an attempt to get to the current version.  For example, if a schema is registered to have version 3, and a file with version 1 is read, OpenTimelineIO will attempt to call the 1->2 function, then the 2->3 function before instantiating the concrete class.

## Schema Downgrading

Similarly, once a type is registered, downgrade functions may be registered.  Downgrade functions take a dictionary of the version specified and return a dictionary of the schema version one lower.  For example, if a downgrade function is registered for version 5, that will downgrade from 5 to 4.

C++ Example, building off the prior section SimpleClass example (can be viewed/run in `examples/upgrade_downgrade_example.cpp`):
<!-- C++ Example, building off the prior section SimpleClass example (can be viewed/run in [examples/upgrade_downgrade_example.cpp](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/blob/main/examples/upgrade_downgrade_example.cpp)): -->

```cpp
// 2->1
otio::TypeRegistry::instance().register_downgrade_function(
    SimpleClass::Schema::name,
    2,
    [](otio::AnyDictionary* d)
    {
        (*d)["my_field"] = (*d)["new_field"];
        d->erase("new_field");
    }
);
```

Python Example:

```python
@otio.core.upgrade_function_for(SimpleClass, 2)
def downgrade_two_to_one(data):
  return {"my_field" : data["new_field"] }
```

To specify what version of a schema to downgrade to, the serialization functions include an optional `schema_version_targets` argument which is a map of schema name to target schema version.  During serialization, any schemas who are listed in the map and are of greater version than specified in the map will be converted to AnyDictionary and run through the necessary downgrade functions before being serialized.

Example C++:

```cpp
auto sc = otio::SerializableObject::Retainer<SimpleClass>(new SimpleClass());
sc->set_new_field(12);

// this will only downgrade the SimpleClass, to version 1
otio::schema_version_map downgrade_manifest = {
    {"SimpleClass", 1}
};

// write it out to disk, downgrading to version 1
sc->to_json_file("/var/tmp/simpleclass.otio", &err, &downgrade_manifest);
```

Example python:

```python
sc = SimpleClass()
otio.adapters.write_to_file(
    sc,
    "/path/to/output.otio",
    target_schema_versions={"SimpleClass":1}
)
```

### Schema-Version Sets

In addition to passing in dictionaries of desired target schema versions, OpenTimelineIO also provides some tools for having sets of schemas with an associated label.  The core C++ library contains a compiled-in map of them, the `CORE_VERSION_MAP`.   This is organized (as of v0.15.0) by library release versions label, ie "0.15.0", "0.14.0" and so on.  

In order to downgrade to version 0.15.0 for example:

```cpp
auto downgrade_manifest = otio::CORE_VERSION_MAP["0.15.0"];

// write it out to disk, downgrading to version 1
sc->to_json_file("/var/tmp/simpleclass.otio", &err, &downgrade_manifest);
```

In python, an additional level of indirection is provided, "FAMILY", which is intended to allow developers to define their own sets of target versions for their plugin schemas.  For example, a studio might have a family named "MYFAMILY" under which they organize labels for their internal releases of their own plugins.

These can be defined in a plugin manifest, which is a `.plugin_manifest.json` file found on the environment variable {term}`OTIO_PLUGIN_MANIFEST_PATH`.

For example:

```python
{
    "OTIO_SCHEMA" : "PluginManifest.1",
    "version_manifests": {
        "MYFAMILY": {
            "June2022": {
                "SimpleClass": 2,
                ...
            },
            "May2022": {
                "SimpleClass": 1,
                ...
            }
        }
    }
}
```

To fetch the version maps and work with this, the python API provides some additional functions:

```python
# example using a built in family
downgrade_manifest = otio.versioning.fetch_map("OTIO_CORE", "0.15.0")
otio.adapters.write_to_file(
    sc,
    "/path/to/file.otio", 
    target_schema_versions=downgrade_manifest
)

# using a custom family defined in a plugin manifest json file
downgrade_manifest = otio.versioning.fetch_map("MYFAMILY", "June2022")
otio.adapters.write_to_file(
    sc,
    "/path/to/file.otio", 
    target_schema_versions=downgrade_manifest
)

```

To fetch the version sets defined by the core from python, use the `OTIO_CORE` family of version sets.

See the [versioning module](../api/python/opentimelineio.versioning.rst) for more information on accessing these.

## Downgrading at Runtime

If you are using multiple pieces of software built with mismatched versions of OTIO, you may need to configure the newer one(s) to write out OTIO in an older format without recompiling or modifying the software.

You can accomplish this in two ways:
- The {term}`OTIO_DEFAULT_TARGET_VERSION_FAMILY_LABEL` environment variable can specify a family and version.
- The `otioconvert` utility program can downgrade an OTIO file to an older version.

### OTIO_DEFAULT_TARGET_VERSION_FAMILY_LABEL Environment Variable

If your software uses OTIO's Python adapter system, then you can set the {term}`OTIO_DEFAULT_TARGET_VERSION_FAMILY_LABEL` environment variable with a `FAMILY:VERSION` value.
For example, in a *nix shell: `env OTIO_DEFAULT_TARGET_VERSION_FAMILY_LABEL=OTIO_CORE:0.14.0 my_program`

The `OTIO_CORE` family is pre-populated with the core OTIO schema versions for previous OTIO releases, for example `0.14.0`. If you have custom schema that needs to be downgraded as well, you will need to specify your own family and version mapping, as described above.

### Downgrading with otioconvert

If your software uses OTIO's C++ API, then it does not look for the {term}`OTIO_DEFAULT_TARGET_VERSION_FAMILY_LABEL` environment variable, but you can convert an OTIO file after it has been created with the `otioconvert` utility.

You can either use a family like this:
```
env OTIO_DEFAULT_TARGET_VERSION_FAMILY_LABEL=OTIO_CORE:0.14.0 otioconvert -i input.otio -o output.otio
```

or you can specify the version mapping for each schema you care about like this:
```
otioconvert -i input.otio -o output.otio -A target_schema_versions="{'Clip':1, 'Timeline':1, 'Marker':2}"
```

## For Developers

During the development of OpenTimelineIO schemas, whether they are in the core or in plugins, it is expected that schemas will change and evolve over time.  Here are some processes for doing that.

### Changing a Field

Given `SimpleClass`:

```python
import opentimelineio as otio

@otio.core.register_type
class SimpleClass(otio.core.SerializableObject):
  serializable_label = "SimpleClass.1"
  my_field = otio.core.serializable_field("my_field", int)
```

And `my_field` needs to be renamed to `new_field`.  To do this:

- Make the change in the class
- Bump the version number in the label
- add upgrade and downgrade functions

```python
@otio.core.register_type
class SimpleClass(otio.core.SerializableObject):
  serializable_label = "SimpleClass.2"
  new_field = otio.core.serializable_field("new_field", int)

@otio.core.upgrade_function_for(SimpleClass, 2)
def upgrade_one_to_two(data):
  return {"new_field" : data["my_field"] }

@otio.core.downgrade_function_from(SimpleClass, 2)
def downgrade_two_to_one(data):
    return {"my_field": data["new_field"]}
```

Changing it again, now `new_field` becomes `even_newer_field`.

```python
@otio.core.register_type
class SimpleClass(otio.core.SerializableObject):
  serializable_label = "SimpleClass.2"
  even_newer_field = otio.core.serializable_field("even_newer_field", int)

@otio.core.upgrade_function_for(SimpleClass, 2)
def upgrade_one_to_two(data):
  return {"new_field" : data["my_field"] }

# NOTE we now have a second upgrade function
@otio.core.upgrade_function_for(SimpleClass, 3)
def upgrade_two_to_three(data):
  return {"even_newer_field" : data["new_field"] }

@otio.core.downgrade_function_from(SimpleClass, 2)
def downgrade_two_to_one(data):
    return {"my_field": data["new_field"]}

# ...and corresponding second downgrade function
@otio.core.downgrade_function_from(SimpleClass, 3)
def downgrade_two_to_one(data):
    return {"new_field": data["even_newer_field"]}
```

### Adding or Removing a Field

Starting from the same class:

```python
@otio.core.register_type
class SimpleClass(otio.core.SerializableObject):
  serializable_label = "SimpleClass.1"
  my_field = otio.core.serializable_field("my_field", int)
```

If a change to a schema is to add a field, for which the default value is the correct value for an old schema, then no upgrade or downgrade function is needed.  The parser ignores values that aren't in the schema.

Additionally, upgrade functions will be called in order, but they need not cover every version number.  So if there is an upgrade function for version 2 and 4, to get to version 4, OTIO will automatically apply function 2 and then function 4 in order, skipping the missing 3.

Downgrade functions must be called in order with no gaps.

Example of adding a field (`other_field`):

```python
@otio.core.register_type
class SimpleClass(otio.core.SerializableObject):
  serializable_label = "SimpleClass.2"
  my_field = otio.core.serializable_field("my_field", int)
  other_field = otio.core.serializable_field("other_field", int)
```

Removing a field (`my_field`):

```python
@otio.core.register_type
class SimpleClass(otio.core.SerializableObject):
  serializable_label = "SimpleClass.3"
  other_field = otio.core.serializable_field("other_field", int)
```

Similarly, when deleting a field, if the field is now ignored and does not contribute to computation, no upgrade or downgrade function is needed.
