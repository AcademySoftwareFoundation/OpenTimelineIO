C++ Proposal Details
====================

Caveats
+++++++

Both the code examples and the sample header files are written without regard
to either namespacing or how the `#include` structure will be implemented.  For
clarity, inline code definitions are omitted from header files though in many cases
they will be present in the final product.

TL;DR
+++++
* `Opentime C++ simplified header files <https://github.com/davidbaraff/OpenTimelineIO/tree/master/proposed-c%2B%2B-api/opentime>`_
* `OTIO C++ simplified header files <https://github.com/davidbaraff/OpenTimelineIO/tree/master/proposed-c%2B%2B-api/otio>`_.

Dependencies
++++++++++++

The  C++ OpentimelineIO (OTIO) library implementation will have the following dependencies:

    * `rapidjson <https://github.com/Tencent/rapidjson>`_
    * any (C++ class)
    * optional (C++ class)
    * The C++ Opentime library (see below)

The need for an "optional" (i.e. a container class that holds either no value
or some specific value, for a given type T) is currently small, but does occur
in one key place (schemas which need to hold either a ``TimeRange`` or
indicate their time range is undefined).

In contrast, the need for an "any" (a C++ type-erased container) is
pervasive, as it is the primary mechanism that serialization and deserialization
rest upon.  It is also the bridge to scripting systems like Python that are not strongly
typed. The C++17 standard defines the types ``std::optional`` and ``std::any`` and these
types are available in ``std::experimental`` in some other cases, and our implementation
targets those.  However, since many (probably most) sites are not yet compiling with
C++17, our implementation makes available public domain C++11 compliant versions
of these types:

    - `any (C++11 compliant) <https://github.com/thelink2012/any/blob/master/any.hpp>`_
    - `optional (C++11 compliant) <https://github.com/martinmoene/optional-lite>`_

Support for Python will require `pybind11 <https://github.com/pybind/pybind11>`_.

The C++ Opentime library (i.e. ``RationalTime``, ``TimeRange`` and ``TimeTransform``)
will have no outside dependencies.  In fact, given the current Python specification,
a C++ Opentime API 
(should) be fairly straightforward and uncontroversial.
Reminder: these
`sample header files <https://github.com/davidbaraff/OpenTimelineIO/tree/master/proposed-c%2B%2B-api/opentime>`_
exist only to show the API; namespacing and other niceties are ommitted.

Starting Examples
+++++++++++++++++

Defining a Schema
-----------------

Before jumping into specifics, let's provide some simple examples
of what we anticipate code for defining and using schemas will look like.
Consider the ``Marker`` schema, which adds a ``TimeRange`` and a color
to a schema which already defines properties ``name`` and ``metadata``: ::

    class Marker : public SerializableObjectWithMetadata {
    public:
        struct Schema {
            static auto constexpr name = "Marker";
            static int constexpr version = 1;
        };

	using Parent = SerializableObjectWithMetadata;

        Marker(std::string const& name = std::string(),
	       TimeRange const& marked_range = TimeRange(),
	       std::string const& color = std::string("red"),
               AnyDictionary const& metadata = AnyDictionary());

	TimeRange marked_range() const;
	void set_marked_range(TimeRange marked_range);

	std::string const& color() const;
	void set_color(std::string const& colir);

    protected:
        virtual ~Marker;

        virtual bool read_from(Reader&);
        virtual void write_to(Writer&) const;

    private:
        TimeRange _marked_range;
	std::color _color;
    };

The contructor takes four properties, two of which (``marked_range`` and ``color``) are stored
directly in ``Marker``, with the remaining two (``name`` and ``metadata``) handled by the
base class ``SerializableObjectWithMetadata``.

For the OTIO API, we will write standard getters/setters to access properties; outside of
OTIO, users could adopt this technique or provide other mechanisms (e.g. public access
to member variables, if they like).  The supplied Python binding code will allow
users to define their own schemas in Python exactly as they do today, with no changes required.

The ``Schema`` structure exists so that this type can be added to the OTIO type registry
with a simple call ::
  
    TypeRegistry::instance()::register_type<Marker>();

The call to add a schema to the type registry would be done within the OTIO
library itself for schemas known to OTIO; for schemas defined outside OTIO,
the author of the schema would need to make the above call for their class
early in a program's execution.

Reading/Writing Propeties
-------------------------

Code must also be written to read/write the new properties.  This is simple as well: ::

    bool Marker::read_from(Reader& reader) {
        return reader.read("color", &_color) &&
            reader.read("marked_range", &_marked_range) &&
	    Parent::read_from(reader);
     }

    void Marker::write_to(Writer& writer) const {
        Parent::write_to(writer);
        writer.write("color", _color);
        writer.write("marked_range", _marked_range);
    }

Even when we define more complex properties, the reading/writing code is as simple
as shown above, in almost all cases.

.. Note::
   Properties are written to the JSON file in the order they are written
   to from within ``write_to()``.  But the reading code need not be in the same order,
   and changes in the ordering of either the reading or writing code will not
   break compatability with previously written JSON files.

   However, it is vital to invoke ``Parent::read_from()`` *after* reading all
   of the derived class properties, while for writing ``Parent::write_to()``
   must be invoked *before* writing the derived class properties.

.. Note::
   Also note that the order of properties within a JSON file for data
   that is essentially an ``std::map<>`` (see ``AnyDictionary`` below)
   is always alphebetical by key.  This ensures deterministic JSON file
   writing which is important for comparison and testing.

Using Schemas
+++++++++++++

Creating and manipulating schema objects is also simple: ::

    Track* track = new Track();
    Clip* clip1 = new Clip("clip1", new ExternalReference("/path/someFile.mov"));
    Clip* clip2 = new Clip("clip2");

    track->append_child(clip1);
    track->append_child(clip2);

    ...

    for (Item* item: track->children()) {
        for (Effect* effect: item->effects()) {
             std::cout << effect->effect_name();
             ...
        }
    }
    

Serializable Data
+++++++++++++++++

Data in OTIO schemas must be read and written as JSON.  Data must also be
available to C++, in some cases as strongly typed data, while in
other cases as untyped data (i.e. presented as an ``any``).

For discussion purposes, let us consider that all data that is read and
written to JSON is transported as a C++ ``any``.  What can that ``any`` hold?

First, the ``any`` can be empty, which corresponds with a ``null`` JSON value.
The ``any`` could also hold any of the following "atomic" types:
``bool``, ``int``, ``double``, ``std::string``, ``RationalTime``, ``TimeRange``
and ``TimeTransform``.  All but the last three are immediately expressable
in JSON, while the three Opentime types are read/written as compound structures
with the same format that the current Python implementation delivers.
The final "atomic" type that an ``any`` can hold is a ``SerializableObject*``,
which represents the C++ base class for all schemas.  (Note: it will not be
valid for an ``any`` to hold a pointer to a derived class, for example, a ``Clip*`` value.
The actual C++ static type in the ``any`` will always be a pointer to the base class ``SerializableObject``.)

Next, for any of the above atomic types ``T``, excepting
for ``SerializableObject*``, an ``any`` can store a type of ``optional<T>``.

Finally, the ``any`` can hold two more types: an ``AnyDictionary`` and an
``AnyVector``.  For this discussion, consider an ``AnyDictionary`` to
be the type ``std::map<std::string, any>`` and the type ``AnyVector`` to be
the type ``std::vector<any>``.  The actual implementation is subtly different,
but not to end-users: the API for both these types exactly mirrors the
APIs of ``std::vector<any>``
and ``std::map<std::string, any>`` respectively.  The ``AnyVector`` and ``AnyDictionary`` types
are of course the JSON array and object types.

C++ Properties
++++++++++++++

In most cases, we expect C++ schemas to hold data as strongly-typed properties.  The notable
exception is that low in the inheritance hierarchy, a C++ property named ``metadata``
which is of type ``AnyDictionary`` is made available, which allows clients
to story data of any type they want.  Manipulating such data will be as simple
as always, from an untyped language like Python, while in C++/Swift, the
typical and necessary querying and casting would need to be written.

As we saw above, declaring and and handling read/writing for "atomic" property types
e.g. ``std::string``, ``TimeRange``) is straightforward and requires little effort.
Additionally, reading/writing support is automatically
provided for the (recursively defined) types ``std::vector<P>``, ``std::list<P>`` and ``std::map<std::string, P>``
where ``P`` is itself a serializable property type.  Accordingly, one is free
to declare a property of type ``std::vector<std::map<std::string, std::list<TimeRange>>>`` and it will
serialize and deserialize properly.  However, such a type might be hard to reflect/bind in
a Python or Swift bridge.  Our current implementation however bridges one-level deep types
such as ``std::vector<RationalTime>`` or ``std::map<std::string, double>`` to Python (and later Swift)
quite easily and idiomatically.

Finally, one can declare lists and dictionaries for schema objects, in as strongly typed
fashion as required.  That is, a property might be a list of schema objects of any type,
or the property might specify a particular derived class the schema object must satisfy.
Again, this is taken care of automatically: ::

  class DerivedSchema : public SerializableObject {
     ...
  private:
     std::vector<MediaReference*> _extra_references;   // (don't actually do this)
  };

In this case, the derived schema could choose to store extra media references.  The reading/writing
code would simply call ::

   reader.read("extra_references", &_extra_references)

and ::

    writer.write("extra_references", _extra_references)

to read/write the property.

.. Note::
   The comment "don't actually do this" will be explained in the next section; the
   actual type of this property needs to be slightly different.
   The code for reading/writing the property however is correct.
   
Object Graphs and Serialization
+++++++++++++++++++++++++++++++

The current Python implementation assumes that no schema object is referenced
more than once, when it comes to serialization and deserialization.  Specifically, the
object "graph" is assumed to implicitly be a tree, although this is not always enforced.
For example, the current Python implementation has this bug: ::

  clip1 = otio.schema.Clip("clip1")
  clip2 = otio.schema.Clip("clip2")
  ext_ref = otio.schema.ExternalReference("/path/someFile.mov")
  clip1.media_reference = ext_ref
  clip2.media_reference = ext_ref

As written, modifying ``ext_ref`` modifies the external media reference data for
both ``clip1`` and ``clip2``.  However, if one serializes and then deserializes this
data, the serialized data replicates the external references.  Thus, upon reading
back this object graph, the new clips no longer share the same media reference.

The C++ implementation for serialization will not have this limitation.
That means that the object structure need no longer be a tree; it doesn't, strictly speaking, even need
to be a DAG: ::

   Clip* clip1 = new Clip();
   Clip* clip2 = new Clip();

   clip1->metadata()["other_clip"] = clip2;
   clip2->metadata()["other_clip"] = clip1;

will work just fine: writing/reading or simply cloning ``clip1`` would yield
a new ``clip1`` that pointed to a new ``clip2`` and vice versa.

.. Note::
   This really does work, except that it forms an unbreakable retain cycle
   in memory that is only broken by manually severing one of the links by removing,
   for example, the value under "other_clip" in one of the metadata dictionaries.

The above example shows what one could (but shouldn't do).  More practical examples
are that clips could now share media references, or that metadata could contain
references to arbitrary schemas for convenience.

Most importantly, arbitrary serialization seperates lets us separate
the concepts of "I am responsible for reading/writing you" from the
"I am your (one and only) parent" from "I am responsible to deleting you when no longer needed."
In the current Python implementation, these concepts are not explicitly defined, mostly
because of the automatic nature of memory management in Python.  In C++,
we must be far more explicit though.

Memory Management
+++++++++++++++++

The final topic we must deal with is memory management. Languages like Python and Swift
natually make use of reference counted class instances. We considered such a route in C++,
by requiring that manipulations be done not in terms of ``SerializableObject*`` pointers,
but rather using ``std::shared_ptr<SerializableObject>`` (and the corresponding ``std::weak_ptr``).
While some end users would find this a comfortable route, there are others who would not.
Additionally (and this is a topic that is very deep, but that we are happy to discuss further)
the ``std::shared_ptr<>`` route, coupled with the ``pybind`` binding
system (or even with the older ``boost`` Python binding system) wouldn't provide an adequate
end-user experience in Python.  (And we would expect similar difficulties in Swift.)

Consider the following requirements from the perspective of an OTIO user in a Python framework.
In Python, a user types ::

  clip = otio.schema.Clip()

Behind the scenes, in C++, an actual ``Clip`` instance has been created.  From the
user's perspective, they "own" this clip, and if they immediate type ::

  del clip

then they would expect the Python clip object to be destroyed (and the actual C++ ``Clip`` instance
to be deleted).  Anything less than this is a memory leak.

But what if before typing ``del clip`` the Python user puts that clip into a composition?
Now neither the Python object corresponding to the clip *nor* the actual C++ ``Clip`` instance
can be destroyed while the composition has that clip as a child.

The same situation applies if the end user does not create the objects directly from Python.
Reading back a JSON file from Python creates all objects in C++ and hands back only the top-most
object to Python.  Yet that object (and any other objects subsequently exposed and held by Python)
must remain undeletable from C++ while the Python interpreter has a reference to those objects.

It might seem like shared pointers would fix all this but in fact, they do not.
The reason is that there are in reality two objects: the C++ instance, and the reflected object in Python.
(While it might be feasible to "auto-create" the reflected Python object whenever it was needed, and
really think of having one object, this choice makes it impossible to allow defining new schemas in Python.
The same consequence applies to allowing for new schemas to be defined in Swift.)
Ensuring a system that does not leak memory, and that also keeps both objects alive
as long as either side (C++ or the bridged language) is, simply put, challenging.

With all that as a preamble, here is our proposed solution for C++.

- A new instance of a schema object is created by a call to ``new``.
- All schema objects have protected destructors.  Give a raw pointer to
  a schema object, client code may not directly invoke the ``delete`` operator,
  but may write ::

    Clip* c = new Clip();
    ...
    c->possibly_delete();    // returns true if c was deleted

- The OTIO C++ API uses raw pointers exclusively in all its
  function signatures (e.g. property access functions, property modifier functions, constructors, etc.).
- Schema objects prevent premature destruction of schema instances they are interested
  in by storing them in variables of type ``SerializableObject::Retainer<T>`` where ``T``
  is of type ``SerializableObject`` (or derived from it).

For example: ::

  class ExtendedEffect : public Effect {
  public:
     ...
     MediaReference* best() const {
         return _best;
     }

     void set_best(MediaReference* best) {
         _best = best;
     }

     MediaReference* best_or_other() {
         return _best ? _best : some_other_reference();
     }

 private:
   Retainer<MediaReference> _best;
 };

In this example, the ``ExtendedEffect`` schema has a property named ``best`` that must be
a ``MediaReference``.  To indicate that it needs to retain its instance, the schema stores
the property not as a raw pointer, but using the ``Retainer`` structure.

Nothing special needs to be done for the reading/writing code, and there is automatic two-way
conversion between ``Retainer<MediaReference>`` and ``MediaReference*`` which keeps the code
simple.  Even testing if the property is set (as ``best_or_other()`` does) is done as
if we were using raw pointers.

The only rules that a developer needs to know is:

- Creating a new schema instance starts the instance with an internal count of 0.
- Putting a schema instance into a ``Retainer`` object increases the count by 1.
- Destroying the retainer object or reassigning a new instance to it decreases the
  count by 1 of the object if any in the retainer object.  If this causes the count
  to reach zero, the schema instance is destroyed.
- The possibly_delete() member function of ``SerializableObject*`` checks that
  the count of the instance is zero, and if so deletes the object in question.
- An ``any`` instance holding a ``SerializableObject*`` actually holds a
  ``Retainer<SerializableObject>``.  That is, blind data safely retains schema instances.

In practice, these rules mean that only the "root" of the object graph needs to be
held by a user in C++ to prevent destruction of the entire graph, and that calling
``possibly_delete()`` on the root of the graph will cause deletion of the entire
structure (assuming no cyclic references) and/or assuming the root isn't currently
sitting in the Python interpreter.

We have extensively tested this scheme with Python and written code for all the defined
schema instances that exist so far.  The code has proven to be lightweight and simple
to read and write, with few surprises encountered.  The Python experience has been
unchanged from the original implementation.

Examples
--------

This code shows when instances are actually deleted: ::

   Track* t = new Track;

   Clip* c1 = new Clip;
   c1->possibly_delete();    // c1 is deleted

   Clip* c2 = new Clip;
   t->add_child(c2);
   c2->possibly_delete();   // no effect
   t->possibly_delete();   // deletes t and c2

The only time that using a ``Retainer`` object might be necessary in client
code is as follows:  ::

  Track* t = get_some_track();
  int index = find_child_named(t, "clip1");  // assume this returned a valid index

  Clip* c = t->children()[index];
  t->remove_child(index);   // deletes c if t holds the last reference to c
  std::cout << c->name();   // <possible crash>

In this example, if the user tries to use ``c`` after the call
to ``remove_child()``, they will crash if the track held
the last reference to ``cc``.  The last three lines should instead
be written as: ::

  SerializableObject::Retainer<Clip> rc = t->children()[index];
  t->remove_child(index);   // child is NOT deleted because of the retainer

  Clip* c = rc.value;
  std::cout << c->name();

In actual practice, we believe that the need to write code of the above form
should occur extremely rarely.

Proposed OTIO C++ Header Files
++++++++++++++++++++++++++++++

`Proposed stripped down OTIO C++ header files <https://github.com/davidbaraff/OpenTimelineIO/tree/master/proposed-c%2B%2B-api/otio>`_.



  

   
   




    
