C++ Implementation Details
==========================

Dependencies
++++++++++++

The  C++ OpentimelineIO (OTIO) library implementation will have the following
dependencies:

    * `rapidjson <https://github.com/Tencent/rapidjson>`_
    * any (C++ class)
    * optional (C++ class)
    * The C++ Opentime library (see below)

The need for an "optional" (i.e. a container class that holds either no value
or some specific value, for a given type T) is currently small, but does occur
in one key place (schemas which need to hold either a ``TimeRange`` or indicate
their time range is undefined).

In contrast, the need for an "any" (a C++ type-erased container) is pervasive,
as it is the primary mechanism that serialization and deserialization rest
upon.  It is also the bridge to scripting systems like Python that are not
strongly typed. The C++17 standard defines the types ``std::optional`` and
``std::any`` and these types are available in ``std::experimental`` in some
other cases, and our implementation targets those.  However, since many
(probably most) sites are not yet compiling with C++17, our implementation
makes available public domain C++11 compliant versions of these types:

    - `any (C++11 compliant) <https://github.com/thelink2012/any/blob/master/any.hpp>`_
    - `optional (C++11 compliant) <https://github.com/martinmoene/optional-lite>`_

Support for Python will require `pybind11 <https://github.com/pybind/pybind11>`_.

The C++ Opentime library (i.e. ``RationalTime``, ``TimeRange`` and
``TimeTransform``) will have no outside dependencies.  In fact, given the
current Python specification, a C++ Opentime API (should) be fairly
straightforward and uncontroversial.

Reminder: these
`sample header files <https://github.com/davidbaraff/OpenTimelineIO/tree/master/proposed-c%2B%2B-api/opentime>`_
exist only to show the API; namespacing and other niceties are omitted.

Starting Examples
+++++++++++++++++

Defining a Schema
-----------------

Before jumping into specifics, let's provide some simple examples of what we
anticipate code for defining and using schemas will look like.  Consider the
``Marker`` schema, which adds a ``TimeRange`` and a color to a schema which
already defines properties ``name`` and ``metadata``: ::

    class Marker : public SerializableObjectWithMetadata {
    public:
        struct Schema {
            static std::string constexpr name = "Marker";
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
	void set_color(std::string const& color);

    protected:
        virtual ~Marker();

        virtual bool read_from(Reader&);
        virtual void write_to(Writer&) const;

    private:
        TimeRange _marked_range;
	std::color _color;
    };

The constructor takes four properties, two of which (``marked_range`` and
``color``) are stored directly in ``Marker``, with the remaining two (``name``
and ``metadata``) handled by the base class ``SerializableObjectWithMetadata``.

For the OTIO API, we will write standard getters/setters to access properties;
outside of OTIO, users could adopt this technique or provide other mechanisms
(e.g. public access to member variables, if they like).  The supplied Python
binding code will allow users to define their own schemas in Python exactly as
they do today, with no changes required.

The ``Schema`` structure exists so that this type can be added to the OTIO type
registry with a simple call: ::
  
    TypeRegistry::instance()::register_type<Marker>();

The call to add a schema to the type registry would be done within the OTIO
library itself for schemas known to OTIO; for schemas defined outside OTIO, the
author of the schema would need to make the above call for their class early in
a program's execution.

Reading/Writing Properties
--------------------------

Code must also be written to read/write the new properties.  This is simple as
well: ::

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

Even when we define more complex properties, the reading/writing code is as
simple as shown above, in almost all cases.

When an error is encountered in reading, ``read_from`` should set the error
on the ``Reader`` instance and return ``false``: ::

    bool Marker::read_from(Reader& reader) {
        if (!reader.read(“color”, &_color)) {
            return false;
        }
        if (_color == “invalid_value”) {
            reader.error( ErrorStatus(ErrorStatus::JSON_PARSE_ERROR,
                                                      “invalid_value not allowed for color”));
            return false;
    }
        return reader.read(“marked_range”, &_marked_range) &&
            Parent::read_from(reader);
    }

This is a contrived example but it describes the basic mechanics. Adjust the
details above as appropriate for your case.

.. Note::
   Properties are written to the JSON file in the order they are written
   to from within ``write_to()``.  But the reading code need not be in the same order,
   and changes in the ordering of either the reading or writing code will not
   break compatibility with previously written JSON files.

   However, it is vital to invoke ``Parent::read_from()`` *after* reading all
   of the derived class properties, while for writing ``Parent::write_to()``
   must be invoked *before* writing the derived class properties.

.. Note::
   Also note that the order of properties within a JSON file for data
   that is essentially a ``std::map<>`` (see ``AnyDictionary`` below)
   is always alphabetical by key.  This ensures deterministic JSON file
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
available to C++, in some cases as strongly typed data, while in other cases as
untyped data (i.e. presented as an ``any``).

For discussion purposes, let us consider that all data that is read and written
to JSON is transported as a C++ ``any``.  What can that ``any`` hold?

First, the ``any`` can be empty, which corresponds with a ``null`` JSON value.
The ``any`` could also hold any of the following "atomic" types: ``bool``,
``int``, ``double``, ``std::string``, ``RationalTime``, ``TimeRange`` and
``TimeTransform``.  All but the last three are immediately expressible in JSON,
while the three Opentime types are read/written as compound structures with the
same format that the current Python implementation delivers.  The final
"atomic" type that an ``any`` can hold is a ``SerializableObject*``, which
represents the C++ base class for all schemas.  (Note: it will not be valid for
an ``any`` to hold a pointer to a derived class, for example, a ``Clip*``
value.  The actual C++ static type in the ``any`` will always be a pointer to
the base class ``SerializableObject``.)

Next, for any of the above atomic types ``T``, excepting for
``SerializableObject*``, an ``any`` can store a type of ``optional<T>``.
(Supporting serialization of an ``optional<SerializableObject*>`` would be
ambiguous and unneeded; putting a null pointer of type ``SerializableObject*``
in an ``any``, is written as a ``null`` to the JSON file.)

Finally, the ``any`` can hold two more types: an ``AnyDictionary`` and an
``AnyVector``.  For this discussion, consider an ``AnyDictionary`` to be the
type ``std::map<std::string, any>`` and the type ``AnyVector`` to be the type
``std::vector<any>``.  The actual implementation is subtly different, but not
to end-users: the API for both these types exactly mirrors the APIs of
``std::vector<any>`` and ``std::map<std::string, any>`` respectively.  The
``AnyVector`` and ``AnyDictionary`` types are of course the JSON array and
object types.

C++ Properties
++++++++++++++

In most cases, we expect C++ schemas to hold data as strongly-typed properties.
The notable exception is that low in the inheritance hierarchy, a C++ property
named ``metadata`` which is of type ``AnyDictionary`` is made available, which
allows clients to story data of any type they want.  Manipulating such data
will be as simple as always, from an untyped language like Python, while in
C++/Swift, the typical and necessary querying and casting would need to be
written.

As we saw above, declaring and handling reading/writing for "atomic" property
types (e.g. ``std::string``, ``TimeRange``) is straightforward and requires
little effort.  Additionally, reading/writing support is automatically provided
for the (recursively defined) types ``std::vector<P>``, ``std::list<P>`` and
``std::map<std::string, P>`` where ``P`` is itself a serializable property
type.  Accordingly, one is free to declare a property of type
``std::vector<std::map<std::string, std::list<TimeRange>>>`` and it will
serialize and deserialize properly.  However, such a type might be hard to
reflect/bind in a Python or Swift bridge.  Our current implementation however
bridges one-level deep types such as ``std::vector<RationalTime>`` or
``std::map<std::string, double>`` to Python (and later Swift) quite easily and
idiomatically.

Finally, one can declare lists and dictionaries for schema objects, in as
strongly typed fashion as required.  That is, a property might be a list of
schema objects of any type, or the property might specify a particular derived
class the schema object must satisfy.  Again, this is taken care of
automatically: ::

  class DerivedSchema : public SerializableObject {
     ...
  private:
     std::vector<MediaReference*> _extra_references;   // (don't actually do this)
  };

In this case, the derived schema could choose to store extra media references.
The reading/writing code would simply call: ::

   reader.read("extra_references", &_extra_references)

To read the property, and: ::

    writer.write("extra_references", _extra_references)

To write the property.

.. Note::
   The comment "don't actually do this" will be explained in the next section;
   the actual type of this property needs to be slightly different.  The code
   for reading/writing the property however is correct.
   
Object Graphs and Serialization
+++++++++++++++++++++++++++++++

The current Python implementation assumes that no schema object is referenced
more than once, when it comes to serialization and deserialization.
Specifically, the object "graph" is assumed to implicitly be a tree, although
this is not always enforced.  For example, the current Python implementation
has this bug: ::

  clip1 = otio.schema.Clip("clip1")
  clip2 = otio.schema.Clip("clip2")
  ext_ref = otio.schema.ExternalReference("/path/someFile.mov")
  clip1.media_reference = ext_ref
  clip2.media_reference = ext_ref

As written, modifying ``ext_ref`` modifies the external media reference data
for both ``clip1`` and ``clip2``.  However, if one serializes and then
deserializes this data, the serialized data replicates the external references.
Thus, upon reading back this object graph, the new clips no longer share the
same media reference.

The C++ implementation for serialization will not have this limitation.  That
means that the object structure need no longer be a tree; it doesn't, strictly
speaking, even need to be a DAG: ::

   Clip* clip1 = new Clip();
   Clip* clip2 = new Clip();

   clip1->metadata()["other_clip"] = clip2;
   clip2->metadata()["other_clip"] = clip1;

This will work just fine: writing/reading or simply cloning ``clip1`` would yield a
new ``clip1`` that pointed to a new ``clip2`` and vice versa.

.. Note::
   This really does work, except that it forms an unbreakable retain cycle
   in memory that is only broken by manually severing one of the links by removing,
   for example, the value under "other_clip" in one of the metadata dictionaries.

The above example shows what one could (but shouldn't do).  More practical
examples are that clips could now share media references, or that metadata
could contain references to arbitrary schemas for convenience.

Most importantly, arbitrary serialization lets us separate the concepts of "I
am responsible for reading/writing you" from the "I am your (one and only)
parent" from "I am responsible to deleting you when no longer needed." In the
current Python implementation, these concepts are not explicitly defined,
mostly because of the automatic nature of memory management in Python.  In C++,
we must be far more explicit though.

Memory Management
+++++++++++++++++

The final topic we must deal with is memory management. Languages like Python
and Swift naturally make use of reference counted class instances. We considered
such a route in C++, by requiring that manipulations be done not in terms of
``SerializableObject*`` pointers, but rather using
``std::shared_ptr<SerializableObject>`` (and the corresponding
``std::weak_ptr``).  While some end users would find this a comfortable route,
there are others who would not.  Additionally (and this is a topic that is very
deep, but that we are happy to discuss further) the ``std::shared_ptr<>``
route, coupled with the ``pybind`` binding system (or even with the older
``boost`` Python binding system) wouldn't provide an adequate end-user
experience in Python.  (And we would expect similar difficulties in Swift.)

Consider the following requirements from the perspective of an OTIO user in a
Python framework.  In Python, a user types: ::

  clip = otio.schema.Clip()

Behind the scenes, in C++, an actual ``Clip`` instance has been created.  From
the user's perspective, they "own" this clip, and if they immediately type: ::

  del clip

Then they would expect the Python clip object to be destroyed (and the actual
C++ ``Clip`` instance to be deleted).  Anything less than this is a memory
leak.

But what if before typing ``del clip`` the Python user puts that clip into a
composition?  Now neither the Python object corresponding to the clip *nor* the
actual C++ ``Clip`` instance can be destroyed while the composition has that
clip as a child.

The same situation applies if the end user does not create the objects directly
from Python.  Reading back a JSON file from Python creates all objects in C++
and hands back only the top-most object to Python.  Yet that object (and any
other objects subsequently exposed and held by Python) must remain undeletable
from C++ while the Python interpreter has a reference to those objects.

It might seem like shared pointers would fix all this but in fact, they do not.
The reason is that there are in reality two objects: the C++ instance, and the
reflected object in Python.  (While it might be feasible to "auto-create" the
reflected Python object whenever it was needed, and really think of having one
object, this choice makes it impossible to allow defining new schemas in
Python.  The same consequence applies to allowing for new schemas to be defined
in Swift.) Ensuring a system that does not leak memory, and that also keeps
both objects alive as long as either side (C++ or the bridged language) is,
simply put, challenging.

With all that as a preamble, here is our proposed solution for C++:

- A new instance of a schema object is created by a call to ``new``.  - All
  schema objects have protected destructors.  Given a raw pointer to a schema
  object, client code may not directly invoke the ``delete`` operator, but may
  write: ::

    Clip* c = new Clip();
    ...
    c->possibly_delete();    // returns true if c was deleted

- The OTIO C++ API uses raw pointers exclusively in all its function signatures
  (e.g. property access functions, property modifier functions, constructors,
  etc.).
- Schema objects prevent premature destruction of schema instances they are
  interested in by storing them in variables of type
  ``SerializableObject::Retainer<T>`` where ``T`` is of type
  ``SerializableObject`` (or derived from it).

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

In this example, the ``ExtendedEffect`` schema has a property named ``best``
that must be a ``MediaReference``.  To indicate that it needs to retain its
instance, the schema stores the property not as a raw pointer, but using the
``Retainer`` structure.

Nothing special needs to be done for the reading/writing code, and there is
automatic two-way conversion between ``Retainer<MediaReference>`` and
``MediaReference*`` which keeps the code simple.  Even testing if the property
is set (as ``best_or_other()`` does) is done as if we were using raw pointers.

The implementation of all this works as follow:

- Creating a new schema instance starts the instance with an internal count of 0.
- Putting a schema instance into a ``Retainer`` object increases the count by 1.
- Destroying the retainer object or reassigning a new instance to it decreases the
  count by 1 of the object if any in the retainer object.  If this causes the count
  to reach zero, the schema instance is destroyed.
- The ``possibly_delete()`` member function of ``SerializableObject*`` checks that
  the count of the instance is zero, and if so deletes the object in question.
- An ``any`` instance holding a ``SerializableObject*`` actually holds a
  ``Retainer<SerializableObject>``.  That is, blind data safely retains schema instances.

The only rules that a developer needs to know is:

- A new instance of a schema object is created by a call to ``new``.
- If your class wants to hold onto something, it needs to store it
  using a ``Retainer<T>`` type.
- If the caller created a schema object (by calling ``new``, or equivalently, by obtaining
  the instance via a ``deserialize`` call) they are responsible for calling
  ``possibly_delete()`` when they are done with the instance, or by giving the
  pointer to someone else to hold.

In practice, these rules mean that only the "root" of the object graph needs to
be held by a user in C++ to prevent destruction of the entire graph, and that
calling ``possibly_delete()`` on the root of the graph will cause deletion of
the entire structure (assuming no cyclic references) and/or assuming the root
isn't currently sitting in the Python interpreter.

We have extensively tested this scheme with Python and written code for all the
defined schema instances that exist so far.  The code has proven to be
lightweight and simple to read and write, with few surprises encountered.  The
Python experience has been unchanged from the original implementation.

Examples
--------

Here are some examples that illustrate these rules: ::

   Track* t = new Track;

   Clip* c1 = new Clip;
   c1->possibly_delete();    // c1 is deleted

   Clip* c2 = new Clip;
   t->add_child(c2);
   c2->possibly_delete();   // no effect
   t->possibly_delete();   // deletes t and c2

Here is an example that would lead to a crash: ::

    Track* t = new Track;
    Clip* c1 = new Clip;
    t->add_child(c1);           // t is now responsible for c1
    t->remove_child(0);         // t destroyed c1 when it was removed

    std::cout << c1->name();    // <crash>

To illustrate the above point in a less contrived fashion, consider this incorrect code: ::

    void remove_at_index(Composition* c, int index) {
    #if DEBUG
        Item* item = c->children()[index];
    #endif
        c->remove_child(index);

    #if DEBUG
        std::cout << "Debug: removed item named " << item->name();
    #endif
   }

This could crash, because the call to ``remove_child()`` might have destroyed ``item``.
A correct version of this code would be: ::

    void remove_at_index(Composition* c, int index) {
    #if DEBUG
        SerializableObject::Retainer<Item> item = c->children()[index];
    #endif
        c->remove_child(index);

    #if DEBUG
        std::cout << "Debug: removed item named " << item.value->name();
    #endif
   }

.. Note::
    We do not expect the following scenario to arise, but it
    is certainly possible to write a function which returns a raw pointer
    back to the user *and* also gives them the responsibility for possibly
    deleting it: ::

        Item* remove_and_return_named_item(Composition* c, std::string const& name) {
            auto& children = c->children();
            for (size_t i = 0; i < children.size(); ++i) {
                if (children[i].value->name() == name) {
                    SerializableObject::Retainer<Item> r_item(children[i]);
                    c->remove_child(i);
                    return r_item.take_value();
                }
            }
            return nullptr;
        }

    The raw pointer in a ``Retainer`` object is accessed via the ``value`` member.
    The call to ``take_value()`` decrements 
    the reference count of the pointed to object but does not delete the instance
    if the count drops to zero.  The pointer is returned to the caller, and
    the ``Retainer`` instance sets its internal pointer to null.
    Effectively, this delivers a raw
    pointer back to the caller, while also giving them the responsibility to try to delete
    the object if they were the only remaining owner of the object.


Error Handling
++++++++++++++

The C++ implementation will not make use of C++ exceptions.  A function which
can "fail" will indicate this by taking an argument ``ErrorStatus*
error_status``.  The ``ErrorStatus`` structure has two members: an enum code
and a "details" string.  In some cases, the details string may give more
information than the enum code (e.g. for a missing key the details string would
be the missing string) while for other cases, the details string might simply
be a translation of the error code string (e.g. "method not implemented").

Here are examples in the proposed API of some "failable" functions: ::

  class SerializableObject {
    ...
    static SerializableObject* from_json_string(std::string const& input, ErrorStatus* error_status);
    ...
    SerializableObject* clone(std::string* err_msg = nullptr) const;
  };

  class Composition {
    ...
    bool set_children(std::vector<Composable*> const& children, ErrorStatus* error_status);
    
    bool insert_child(int index, Composable* child, ErrorStatus* error_status);

    bool set_child(int index, Composable* child, ErrorStatus* error_status);
    ...
 };

The ``Composition`` schema in particular offers multiple failure paths, ranging
from invalid indices, to trying to add children which are already parented in
another composition.  Note that the proposed failure mechanism makes it awkward
to allow constructors to "fail" gracefully.  Accordingly, a class like
``Composition`` doesn't allow ``children`` to be passed into its constructor,
but requires a call to ``set_children()`` after construction.  Neither the
Python API (nor the Swift API) would be subject to this limitation.

The OpenTime and OpenTimelineIO libraries both have their own error
definitions. The tables below outline the errors, which python exceptions they
raise, and what their semantic meaning is.

.. csv-table:: OpenTime Errors
    :header: "Value", "Python Exception Type", "Meaning"
    
    OK, n/a, No Error
    INVALID_TIMECODE_RATE, ``ValueError``, "Timecode rate isn't a valid SMPTE rate"
    INVALID_TIMECODE_STRING,  ``ValueError``, "String is not properly formatted SMPTE timecode string"
    TIMECODE_RATE_MISMATCH,  ``ValueError``, " Timecode string has a frame number higher than the frame rate"
    INVALID_TIME_STRING,  ``ValueError``,
    NEGATIVE_VALUE,  ``ValueError``,
    INVALID_RATE_FOR_DROP_FRAME_TIMECODE,  ``ValueError``, "Timecode rate isn't valid for SMPTE Drop-Frame Timecode"

.. csv-table:: OpenTimelineIO error codes
   :header: "Value", "Python Exception Type", "Meaning"
   
    OK, n/a, No Error
    NOT_IMPLEMENTED, ``NotImplementedError``, "A feature is known but deliberately unimplemented"
    UNRESOLVED_OBJECT_REFERENCE, ``ValueError``, "An object reference is unresolved while reading"
    DUPLICATE_OBJECT_REFERENCE, ``ValueError``, "An object reference is duplicated while reading"
    MALFORMED_SCHEMA, ``ValueError``, "The Schema string was invalid"
    JSON_PARSE_ERROR, ``ValueError``, "Malformed JSON encountered when parsing"
    CHILD_ALREADY_PARENTED, ``ValueError``, "Attempted to add a child to a collection when it's already a member of another collection instance"
    
    FILE_OPEN_FAILED, ``ValueError``, "failed to open file for reading"
    FILE_WRITE_FAILED, ``ValueError``, "failed to open file for writing"
    SCHEMA_ALREADY_REGISTERED, ``ValueError``,
    SCHEMA_NOT_REGISTERED, ``ValueError``,
    SCHEMA_VERSION_UNSUPPORTED, ``UnsupportedSchemaError``,
    KEY_NOT_FOUND, ``KeyError``, "The key used for a mapping doesn't exist in the collection"
    ILLEGAL_INDEX, ``IndexError``, "The collection index is out of bounds"
    TYPE_MISMATCH, ``ValueError``,
    INTERNAL_ERROR, ``ValueError``, "Internal error (aka this is a bug)"
    NOT_AN_ITEM, ``ValueError``,
    NOT_A_CHILD_OF, ``NotAChildError``,
    NOT_A_CHILD, ``NotAChildError``,
    NOT_DESCENDED_FROM, ``NotAChildError``,
    CANNOT_COMPUTE_AVAILABLE_RANGE, ``CannotComputeAvailableRangeError``,
    INVALID_TIME_RANGE, ``ValueError``,
    OBJECT_WITHOUT_DURATION, ``ValueError``,
    CANNOT_TRIM_TRANSITION, ``ValueError``,

.. todo: Add a section discussing how to add additional error types.

Thread Safety
++++++++++++++

Multiple threads should be able to examine or traverse the same graph of
constructed objects safely.  If a thread mutates or makes any modifications to
objects, then only that single thread may do so safely.  Moreover, additional
threads could not safely read the objects while the mutation was underway.  It
is the responsibility of client code to ensure this however.


Proposed OTIO C++ Header Files
++++++++++++++++++++++++++++++

`Proposed stripped down OTIO C++ header files <https://github.com/davidbaraff/OpenTimelineIO/tree/sample-c%2B%2B-headers/proposed-c%2B%2B-api/otio>`_.


Extended Memory Management Discussion
++++++++++++++++++++++++++++++++++++++

There have been a number of questions about the proposed approach which embeds
a reference count in ``SerializableObject`` and uses a templated wrapper,
``Retainer<>`` to manipulate the reference count.  This raises the obvious
question, why not simply used ``std::shared_ptr<>``?  If we only had C++ to
deal with, that would be an obvious choice; however, wrapping to other
languages complicates things.

Here is a deeper discussion of the issues involved.

What makes this complicated is the following set of rules/constraints:

#.  If you access a given C++ object X in Python, this creates a Python wrapper
    object instance P which corresponds to X.  As long as the C++ object X
    remains alive, P must persist.  This is true even if it appears that
    the Python interpreter holds no references to P, because as long as X
    exists, it could always be given back to Python for manipulation.

    In particular, it is not acceptable to destroy P, and then regenerate
    a new instance P2, as if this was the first time X had been exposed to Python.
    This rule is imperative in a world where we can extend the schema hierarchy
    by deriving in Python.  (It is also useful to allow Python code to add arbitrary
    dynamic data onto P, in a persistent fashion.)

    Note that using pybind11 with shared pointers in the
    standard way does *not* satisfy this rule: the pybind11/shared
    pointer approach will happily regenerate a new instance P2
    for X if Python loses all references to the original P.

#.  As long as Python holds a reference to P, corresponding to some C++ object X,
    the C++ object X cannot be deleted, for obvious reasons.

#.  Say that C++ ``SerializableObject`` B is made a child of A.  As long as A retains B, then B
    cannot be destroyed.  The same holds if C++ code outside OTIO chooses to retain
    particular C++ objects.

#.  If a C++ object X exists, and (3) does not hold, then if X is deleted, and a Python wrapper
    instance P corresponding to X exists, then P must be destroyed when X is destroyed.

    Consider the implications of this rule in conjunction with rule (2).

#.  If a C++ object X wasn’t ever given out to Python, there will be no corresponding wrapper instance P
    for that C++ object.  Note however that it may be that the C++ object X was created by
    virtue of a Python wrapper instance P being constructed from Python.  Until that C++ object X
    is passed to C++ in some way, then X will exist only as long as P does.

How can we satisfy all these constraints, while ensuring we don't create retain
cycles (which might be fixable with Python garbage collection, but also
might not)?  Here is the solution we came up with; if you have an alternate
suggestion, we would be happy to hear it.

Our scheme works as follows:

  - When you create a Python wrapper instance P for a C++ object X, the
    Python instance P holds within itself a ``Retainer<>`` which holds X.  The
    existence of that retainer bumps the reference count of the C++
    object up by 1.

  - Whenever X's C++ reference count increases past 1, which means there is at least one C++
    ``Retainer<>`` object in addition to the one in P, a "keep-alive" reference to P is created
    and held by X.  This ensures that P won’t be destroyed even if the Python interpreter appears
    to lose all references to P, because we've hidden one away. (Remember, the C++ object X could
    always be passed back to Python, and we can’t/don’t want to regenerate a new P corresponding to X.)

  -  However, when X's C++ count reference count drops back to one, then we know that P is now
     the only reason we are keeping X alive.  At this point, the keep-alive reference to P is destroyed.
     That means that if/when Python loses the last reference to P, we can (and should) allow
     both P and X to be destroyed. Of course, if X's reference
     count bumps up above 1 before that happens, a new keep-alive reference to P would be created.

The tricky part here is the interaction of watching the reference count of C++
objects oscillate from 1 to greater than one, and vice versa.  (There is no way
of watching the Python reference count change, and even if we could, the
performance constraints this would be entail would be likely untenable.)

Essentially, we are monitoring changes in whether or not there is a single
unique ``Retainer<>`` instance pointing to a given C++ object, or multiple
such retainers.  We’ve verified with some extremely processor intensive
multi-threading/multi-core tests that our coding of the mutation of the C++
reference count, coupled with creating/destroying the Python keep-alive
references (when necessary) is: leak free, thread-safe, and deadlock free (the
last being tricky, since there is both a mutex in the C++ object X protecting
the reference count and Python keep-alive callback mechanism, as well as a GIL
lock to contend with whenever we actually manipulate Python references).

Our reasons for not considering ``std::shared_ptr`` as an implementation
mechanism are two-fold.  First, we wanted to keep the C++ API simple, and we
have opted for raw C++ pointers in most API functions, with ``Retainer<>``
objects only as members of structures/classes where we need to indicate
ownership of an object.  However, even if the community opted to use a
smart-pointer approach for the OTIO API, ``std::shared_ptr`` wouldn't work (as
far as we know), because there is no facility in it that would let us
catch/monitor transitions between reference count values of one, and greater
than one.

We hope this answers questions about why we have chosen our particular
implementation.  This is the only solution we have found that satisfies all the
constraints we listed above, and should work with Swift as well.  We are very
happy though to hear ideas for different ways to do all of this.
