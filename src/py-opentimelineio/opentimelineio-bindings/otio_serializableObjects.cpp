// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include <pybind11/pybind11.h>
#include <pybind11/operators.h>
#include <pybind11/stl.h>
#include "otio_errorStatusHandler.h"

#include "opentimelineio/clip.h"
#include "opentimelineio/composable.h"
#include "opentimelineio/composition.h"
#include "opentimelineio/effect.h"
#include "opentimelineio/externalReference.h"
#include "opentimelineio/freezeFrame.h"
#include "opentimelineio/gap.h"
#include "opentimelineio/generatorReference.h"
#include "opentimelineio/imageSequenceReference.h"
#include "opentimelineio/item.h"
#include "opentimelineio/linearTimeWarp.h"
#include "opentimelineio/marker.h"
#include "opentimelineio/mediaReference.h"
#include "opentimelineio/missingReference.h"
#include "opentimelineio/stack.h"
#include "opentimelineio/timeEffect.h"
#include "opentimelineio/timeline.h"
#include "opentimelineio/track.h"
#include "opentimelineio/transition.h"
#include "opentimelineio/serializableCollection.h"
#include "opentimelineio/stack.h"
#include "opentimelineio/unknownSchema.h"

#include "otio_utils.h"
#include "otio_anyDictionary.h"

#include "ImathBox.h"

namespace py = pybind11;
using namespace pybind11::literals;

using MarkerVectorProxy =
    MutableSequencePyAPI<std::vector<SerializableObject::Retainer<Marker>>, Marker*>;

using EffectVectorProxy =
    MutableSequencePyAPI<std::vector<SerializableObject::Retainer<Effect>>, Effect*>;

using TrackVectorProxy =
    MutableSequencePyAPI<std::vector<SerializableObject::Retainer<Track>>, Track*>;

using SOWithMetadata = SerializableObjectWithMetadata;

namespace {

    template<typename T>
    std::vector<T*> vector_or_default(optional<std::vector<T*>> item) {
        if (item.has_value()) {
            return item.value();
        }

        return std::vector<T*>();
    }

    template<typename T, typename U>
    bool find_children(T* t, py::object descended_from_type, optional<TimeRange> const& search_range, bool shallow_search, std::vector<SerializableObject*>& l) {
        if (descended_from_type.is(py::type::handle_of<U>()))
        {
            for (const auto& child : t->template find_children<U>(ErrorStatusHandler(), search_range, shallow_search)) {
                l.push_back(child.value);
            }
            return true;
        }
        return false;
    }

    template<typename T>
    std::vector<SerializableObject*> find_children(T* t, py::object descended_from_type, optional<TimeRange> const& search_range, bool shallow_search = false) {
        std::vector<SerializableObject*> l;
        if (find_children<T, Clip>(t, descended_from_type, search_range, shallow_search, l)) ;
        else if (find_children<T, Composition>(t, descended_from_type, search_range, shallow_search, l)) ;
        else if (find_children<T, Gap>(t, descended_from_type, search_range, shallow_search, l)) ;
        else if (find_children<T, Item>(t, descended_from_type, search_range, shallow_search, l)) ;
        else if (find_children<T, Stack>(t, descended_from_type, search_range, shallow_search, l)) ;
        else if (find_children<T, Timeline>(t, descended_from_type, search_range, shallow_search, l)) ;
        else if (find_children<T, Track>(t, descended_from_type, search_range, shallow_search, l)) ;
        else if (find_children<T, Transition>(t, descended_from_type, search_range, shallow_search, l)) ;
        else
        {
            for (const auto& child : t->template find_children<Composable>(ErrorStatusHandler(), search_range, shallow_search)) {
                l.push_back(child.value);
            }
        }
        return l;
    }

    template<typename T>
    std::vector<SerializableObject*> find_clips(T* t, optional<TimeRange> const& search_range, bool shallow_search = false) {
        std::vector<SerializableObject*> l;
        for (const auto& clip : t->find_clips(ErrorStatusHandler(), search_range, shallow_search)) {
            l.push_back(clip.value);
        }
        return l;
    }
}

/*
template <typename T> static std::string repr(T const& value) {
    return pybind11::cast<std::string>(pybind11::repr(pybind11::cast(value)));
}

template <typename T> static std::string repr(optional<T> const& value) {
    return value ? repr(*value) : "None";
}

static std::string repr(AnyDictionary& value) {
    auto proxy = (AnyDictionaryProxy*) value.get_or_create_mutation_stamp();
    return repr(proxy);
}

template <typename T> static std::string str(T const& value) {
    return pybind11::cast<std::string>(pybind11::str(pybind11::cast(value)));
}

template <typename T> static std::string str(optional<T> const& value) {
    return value ? str(*value) : "None";
}

static std::string str(AnyDictionary& value) {
    auto proxy = (AnyDictionaryProxy*) value.get_or_create_mutation_stamp();
    return str(proxy);
}
*/

template <typename CONTAINER, typename ITEM>
class ContainerIterator {
public:
    ContainerIterator(CONTAINER* container)
        : _container(container),
          _it(0) {
    }

    ContainerIterator* iter() {
        return this;
    }

    ITEM next() {
        if (_it == _container->children().size()) {
            throw pybind11::stop_iteration();
        }

        return _container->children()[_it++];
    }

private:
    CONTAINER* _container;
    size_t _it;
};

static void define_bases1(py::module m) {
    py::class_<SerializableObject, managing_ptr<SerializableObject>>(m, "SerializableObject", py::dynamic_attr(), "Superclass for all classes whose instances can be serialized.")
        .def(py::init<>())
        .def_property_readonly("_dynamic_fields", [](SerializableObject* s) {
                auto ptr = s->dynamic_fields().get_or_create_mutation_stamp();
                return (AnyDictionaryProxy*)(ptr); }, py::return_value_policy::take_ownership)
        .def("is_equivalent_to", &SerializableObject::is_equivalent_to, "other"_a.none(false))
        .def("clone", [](SerializableObject* so) {
                return so->clone(ErrorStatusHandler()); })
        .def("to_json_string", [](SerializableObject* so, int indent) {
                return so->to_json_string(ErrorStatusHandler(), {}, indent); },
            "indent"_a = 4)
        .def("to_json_file", [](SerializableObject* so, std::string file_name, int indent) {
                return so->to_json_file(file_name, ErrorStatusHandler(), {}, indent); },
            "file_name"_a,
            "indent"_a = 4)
        .def_static("from_json_file", [](std::string file_name) {
                return SerializableObject::from_json_file(file_name, ErrorStatusHandler()); },
            "file_name"_a)
        .def_static("from_json_string", [](std::string input) {
                return SerializableObject::from_json_string(input, ErrorStatusHandler());
            },
            "input"_a)
        .def("schema_name", &SerializableObject::schema_name)
        .def("schema_version", &SerializableObject::schema_version)
        .def_property_readonly("is_unknown_schema", &SerializableObject::is_unknown_schema);

    py::class_<UnknownSchema, SerializableObject, managing_ptr<UnknownSchema>>(m, "UnknownSchema")
        .def_property_readonly("original_schema_name", &UnknownSchema::original_schema_name)
        .def_property_readonly("original_schema_version", &UnknownSchema::original_schema_version);

    py::class_<SOWithMetadata, SerializableObject,
               managing_ptr<SOWithMetadata>>(m, "SerializableObjectWithMetadata", py::dynamic_attr())
        .def(py::init([](std::string name, AnyDictionaryProxy* metadata) {
                    AnyDictionary d = metadata->fetch_any_dictionary();
                    return new SOWithMetadata(name, d);
                }),
            py::arg_v("name"_a = std::string()),
            py::arg_v("metadata"_a = py::none()))
        .def(py::init([](std::string name, py::dict metadata) {
                    // AnyDictionary d = metadata.fetch_any_dictionary();

                    AnyDictionary* d = new AnyDictionary();
                    PyObject *source = metadata.ptr();

                    PyObject *key, *value;
                    Py_ssize_t pos = 0;

                    while (PyDict_Next(source, &pos, &key, &value)) {
                        if (!PyUnicode_Check(key)) {
                            throw py::key_error("Keys should be of type string");
                        }

                        const char* key_name = PyUnicode_AsUTF8(key);
                        (*d)[key_name] = value;
                    }

                    return new SOWithMetadata(name, (*d));
                }),
            py::arg_v("name"_a = std::string()),
            py::arg_v("metadata"_a = py::none()))
        .def_property_readonly("metadata", [](SOWithMetadata* s) {
                auto ptr = s->metadata().get_or_create_mutation_stamp();
            return (AnyDictionaryProxy*)(ptr); }, py::return_value_policy::take_ownership)
        .def_property("name", [](SOWithMetadata* so) {
                return plain_string(so->name());
            }, &SOWithMetadata::set_name);
}

static void define_bases2(py::module m) {
    MarkerVectorProxy::define_py_class(m, "MarkerVector");
    EffectVectorProxy::define_py_class(m, "EffectVector");

    auto marker_class =
        py::class_<Marker, SOWithMetadata, managing_ptr<Marker>>(m, "Marker", py::dynamic_attr(), R"docstring(
A marker indicates a marked range of time on an item in a timeline, usually with a name, color or other metadata.

The marked range may have a zero duration. The marked range is in the owning item's time coordinate system.
)docstring")
        .def(py::init([](
                        std::string name,
                        TimeRange marked_range,
                        std::string const& color,
                        py::object metadata) {
                          return new Marker(
                                  name,
                                  marked_range,
                                  color,
                                  py_to_any_dictionary(metadata));
                      }),
             py::arg_v("name"_a = std::string()),
             "marked_range"_a = TimeRange(),
             "color"_a = std::string(Marker::Color::red),
             py::arg_v("metadata"_a = py::none()))
        .def_property("color", &Marker::color, &Marker::set_color, "Color string for this marker (for example: 'RED'), based on the :class:`~Color` enum.")
        .def_property("marked_range", &Marker::marked_range, &Marker::set_marked_range, "Range this marker applies to, relative to the :class:`.Item` this marker is attached to (e.g. the :class:`.Clip` or :class:`.Track` that owns this marker).");

    py::class_<Marker::Color>(marker_class, "Color")
        .def_property_readonly_static("PINK", [](py::object /* self */) { return Marker::Color::pink; })
        .def_property_readonly_static("RED", [](py::object /* self */) { return Marker::Color::red; })
        .def_property_readonly_static("ORANGE", [](py::object /* self */) { return Marker::Color::orange; })
        .def_property_readonly_static("YELLOW", [](py::object /* self */) { return Marker::Color::yellow; })
        .def_property_readonly_static("GREEN", [](py::object /* self */) { return Marker::Color::green; })
        .def_property_readonly_static("CYAN", [](py::object /* self */) { return Marker::Color::cyan; })
        .def_property_readonly_static("BLUE", [](py::object /* self */) { return Marker::Color::blue; })
        .def_property_readonly_static("PURPLE", [](py::object /* self */) { return Marker::Color::purple; })
        .def_property_readonly_static("MAGENTA", [](py::object /* self */) { return Marker::Color::magenta; })
        .def_property_readonly_static("BLACK", [](py::object /* self */) { return Marker::Color::black; })
        .def_property_readonly_static("WHITE", [](py::object /* self */) { return Marker::Color::white; });


    using SerializableCollectionIterator = ContainerIterator<SerializableCollection, SerializableObject*>;
    py::class_<SerializableCollectionIterator>(m, "SerializableCollectionIterator", py::dynamic_attr())
        .def("__iter__", &SerializableCollectionIterator::iter)
        .def("__next__", &SerializableCollectionIterator::next);

    py::class_<SerializableCollection, SOWithMetadata,
               managing_ptr<SerializableCollection>>(m, "SerializableCollection", py::dynamic_attr(), R"docstring(
A container which can hold an ordered list of any serializable objects. Note that this is not a :class:`.Composition` nor is it :class:`.Composable`.

This container approximates the concept of a bin - a collection of :class:`.SerializableObject`\s that do
not have any compositional meaning, but can serialize to/from OTIO correctly, with metadata and
a named collection.

A :class:`~SerializableCollection` is useful for serializing multiple timelines, clips, or media references to a single file.
)docstring")
        .def(py::init([](std::string const& name, optional<std::vector<SerializableObject*>> children,
                         py::object metadata) {
                          return new SerializableCollection(name,
                                                vector_or_default<SerializableObject>(children),
                                                py_to_any_dictionary(metadata)); }),
             py::arg_v("name"_a = std::string()),
             "children"_a = py::none(),
             py::arg_v("metadata"_a = py::none()))
        .def("__internal_getitem__", [](SerializableCollection* c, int index) {
                index = adjusted_vector_index(index, c->children());
                if (index < 0 || index >= int(c->children().size())) {
                    throw py::index_error();
                }
                return c->children()[index].value;
            }, "index"_a)
        .def("__internal_setitem__", [](SerializableCollection* c, int index, SerializableObject* item) {
                index = adjusted_vector_index(index, c->children());
                c->set_child(index, item, ErrorStatusHandler());
            }, "index"_a, "item"_a)
        .def("__internal_delitem__", [](SerializableCollection* c, int index) {
                index = adjusted_vector_index(index, c->children());
                c->remove_child(index, ErrorStatusHandler());
            }, "index"_a)
        .def("__internal_insert", [](SerializableCollection* c, int index, SerializableObject* item) {
                index = adjusted_vector_index(index, c->children());
                c->insert_child(index, item);
            }, "index"_a, "item"_a)
        .def("__len__", [](SerializableCollection* c) {
                return c->children().size();
            })
        .def("__iter__", [](SerializableCollection* c) {
                return new SerializableCollectionIterator(c);
            })
        .def("find_clips", [](SerializableCollection* c, optional<TimeRange> const& search_range, bool shallow_search) {
                return find_clips(c, search_range, shallow_search);
            }, "search_range"_a = nullopt, "shallow_search"_a = false)
        .def("find_children", [](SerializableCollection* c, py::object descended_from_type, optional<TimeRange> const& search_range, bool shallow_search) {
                return find_children(c, descended_from_type, search_range, shallow_search);
            }, "descended_from_type"_a = py::none(), "search_range"_a = nullopt, "shallow_search"_a = false);

}

static void define_items_and_compositions(py::module m) {
    auto composable_class = py::class_<Composable, SOWithMetadata,
               managing_ptr<Composable>>(m, "Composable", py::dynamic_attr(), R"docstring(
An object that can be composed within a :class:`~Composition` (such as :class:`~Track` or :class:`.Stack`).
)docstring");

    py::class_<Item, Composable, managing_ptr<Item>>(m, "Item", py::dynamic_attr())
        .def(py::init([](std::string name, optional<TimeRange> source_range,
                         optional<std::vector<Effect*>> effects, optional<std::vector<Marker*>> markers, py::bool_ enabled, py::object metadata) {
                          return new Item(name, source_range,
                                          py_to_any_dictionary(metadata),
                                          vector_or_default<Effect>(effects),
                                          vector_or_default<Marker>(markers),
                                          enabled); }),
             py::arg_v("name"_a = std::string()),
             "source_range"_a = nullopt,
             "effects"_a = py::none(),
             "markers"_a = py::none(),
             "enabled"_a = true,
             py::arg_v("metadata"_a = py::none()))
        .def_property("enabled", &Item::enabled, &Item::set_enabled, "If true, an Item contributes to compositions. For example, when an audio/video clip is ``enabled=false`` the clip is muted/hidden.")
        .def_property("source_range", &Item::source_range, &Item::set_source_range)
        .def("available_range", [](Item* item) {
            return item->available_range(ErrorStatusHandler());
            })
        .def("trimmed_range", [](Item* item) {
            return item->trimmed_range(ErrorStatusHandler());
        })
        .def_property_readonly("markers", [](Item* item) {
            return ((MarkerVectorProxy*) &item->markers());
            })
        .def_property_readonly("effects", [](Item* item) {
            return ((EffectVectorProxy*) &item->effects());
            })
        .def("duration", [](Item* item) {
            return item->duration(ErrorStatusHandler());
            })
        .def("visible_range", [](Item* item) {
            return item->visible_range(ErrorStatusHandler());
            })
        .def("trimmed_range_in_parent", [](Item* item) {
            return item->trimmed_range_in_parent(ErrorStatusHandler());
            })
        .def("range_in_parent", [](Item* item) {
            return item->range_in_parent(ErrorStatusHandler());
            })
        .def("transformed_time", [](Item* item, RationalTime t, Item* to_item) {
            return item->transformed_time(t, to_item, ErrorStatusHandler());
            }, "time"_a, "to_item"_a)
        .def("transformed_time_range", [](Item* item, TimeRange time_range, Item* to_item) {
            return item->transformed_time_range(time_range, to_item, ErrorStatusHandler());
            }, "time_range"_a, "to_item"_a)
        .def_property_readonly("available_image_bounds", [](Item* item) {
            return item->available_image_bounds(ErrorStatusHandler());
            });

    auto transition_class =
        py::class_<Transition, Composable, managing_ptr<Transition>>(m, "Transition", py::dynamic_attr(), "Represents a transition between the two adjacent items in a :class:`.Track`. For example, a cross dissolve or wipe.")
        .def(py::init([](std::string const& name, std::string const& transition_type,
                         RationalTime in_offset, RationalTime out_offset,
                         py::object metadata) {
                          return new Transition(name, transition_type,
                                                in_offset, out_offset,
                                                py_to_any_dictionary(metadata)); }),
             py::arg_v("name"_a = std::string()),
             "transition_type"_a = std::string(),
             "in_offset"_a = RationalTime(),
             "out_offset"_a = RationalTime(),
             py::arg_v("metadata"_a = py::none()))
        .def_property("transition_type", &Transition::transition_type, &Transition::set_transition_type, "Kind of transition, as defined by the :class:`Type` enum.")
        .def_property("in_offset", &Transition::in_offset, &Transition::set_in_offset, "Amount of the previous clip this transition overlaps, exclusive.")
        .def_property("out_offset", &Transition::out_offset, &Transition::set_out_offset, "Amount of the next clip this transition overlaps, exclusive.")
        .def("duration", [](Transition* t) {
            return t->duration(ErrorStatusHandler());
            })
        .def("range_in_parent", [](Transition* t) {
            return t->range_in_parent(ErrorStatusHandler());
            }, "Find and return the range of this item in the parent.")
        .def("trimmed_range_in_parent", [](Transition* t) {
            return t->trimmed_range_in_parent(ErrorStatusHandler());
            }, "Find and return the timmed range of this item in the parent.");

    py::class_<Transition::Type>(transition_class, "Type", R"docstring(
Enum encoding types of transitions.

Other effects are handled by the :class:`Effect` class.
)docstring")
        .def_property_readonly_static("SMPTE_Dissolve", [](py::object /* self */) { return Transition::Type::SMPTE_Dissolve; })
        .def_property_readonly_static("Custom", [](py::object /* self */) { return Transition::Type::Custom; });


    py::class_<Gap, Item, managing_ptr<Gap>>(m, "Gap", py::dynamic_attr())
        .def(py::init([](std::string name, TimeRange source_range, optional<std::vector<Effect*>> effects,
                         optional<std::vector<Marker*>> markers, py::object metadata) {
                          return new Gap(source_range, name,
                                         vector_or_default<Effect>(effects),
                                         vector_or_default<Marker>(markers),
                                         py_to_any_dictionary(metadata)); }),
             py::arg_v("name"_a = std::string()),
             "source_range"_a = TimeRange(),
             "effects"_a = py::none(),
             "markers"_a = py::none(),
             py::arg_v("metadata"_a = py::none()))
       .def(py::init([](std::string name, RationalTime duration, optional<std::vector<Effect*>> effects,
                        optional<std::vector<Marker*>> markers, py::object metadata) {
                          return new Gap(duration, name,
                                         vector_or_default<Effect>(effects),
                                         vector_or_default<Marker>(markers),
                                         py_to_any_dictionary(metadata)); }),
             py::arg_v("name"_a = std::string()),
             "duration"_a = RationalTime(),
             "effects"_a = py::none(),
             "markers"_a = py::none(),
             py::arg_v("metadata"_a = py::none()));

    auto clip_class = py::class_<Clip, Item, managing_ptr<Clip>>(m, "Clip", py::dynamic_attr(), R"docstring(
A :class:`~Clip` is a segment of editable media (usually audio or video).

Contains a :class:`.MediaReference` and a trim on that media reference.
)docstring")
        .def(py::init([](std::string name, MediaReference* media_reference,
                         optional<TimeRange> source_range, py::object metadata,
                         const std::string&  active_media_reference) {
                          return new Clip(name, media_reference, source_range, py_to_any_dictionary(metadata), active_media_reference);
                      }),
             py::arg_v("name"_a = std::string()),
             "media_reference"_a = nullptr,
             "source_range"_a = nullopt,
             py::arg_v("metadata"_a = py::none()),
             "active_media_reference"_a = std::string(Clip::default_media_key))
        .def_property_readonly_static("DEFAULT_MEDIA_KEY",[](py::object /* self */) { 
            return Clip::default_media_key; 
           })
        .def_property("media_reference", &Clip::media_reference, &Clip::set_media_reference)
        .def_property("active_media_reference_key", &Clip::active_media_reference_key, [](Clip* clip, std::string const& new_active_key) { 
            clip->set_active_media_reference_key(new_active_key, ErrorStatusHandler()); 
            })
        .def("media_references", &Clip::media_references) 
        .def("set_media_references", [](Clip* clip, Clip::MediaReferences const& media_references, std::string const& new_active_key) {
            clip->set_media_references(media_references, new_active_key, ErrorStatusHandler());
            });

    using CompositionIterator = ContainerIterator<Composition, Composable*>;
    py::class_<CompositionIterator>(m, "CompositionIterator")
        .def("__iter__", &CompositionIterator::iter)
        .def("__next__", &CompositionIterator::next);

    py::class_<Composition, Item, managing_ptr<Composition>>(m, "Composition", py::dynamic_attr(), R"docstring(
Base class for an :class:`~Item` that contains :class:`~Composable`\s.

Should be subclassed (for example by :class:`.Track` and :class:`.Stack`), not used directly.
)docstring")
        .def(py::init([](std::string name,
                         optional<std::vector<Composable*>> children,
                         optional<TimeRange> source_range, py::object metadata) {
                          Composition* c = new Composition(name, source_range,
                                                           py_to_any_dictionary(metadata));
                          c->set_children(vector_or_default<Composable>(children), ErrorStatusHandler());
                          return c;
                      }),
             py::arg_v("name"_a = std::string()),
             "children"_a = py::none(),
             "source_range"_a = nullopt,
             py::arg_v("metadata"_a = py::none()))
        .def_property_readonly("composition_kind", &Composition::composition_kind)
        .def("is_parent_of", &Composition::is_parent_of, "other"_a)
        .def("range_of_child_at_index", [](Composition* c, int index) {
            return c->range_of_child_at_index(index, ErrorStatusHandler());
            }, "index"_a)
        .def("trimmed_range_of_child_at_index", [](Composition* c, int index) {
            return c->trimmed_range_of_child_at_index(index, ErrorStatusHandler());
            }, "index"_a)
        .def("range_of_child", [](Composition* c, Composable* child, Composable* /* ignored */) {
            return c->range_of_child(child, ErrorStatusHandler());
            }, "child"_a, "reference_space"_a = nullptr)
        .def("trimmed_range_of_child", [](Composition* c, Composable* child, Composable* /* ignored */) {
            return c->trimmed_range_of_child(child, ErrorStatusHandler());
            }, "child"_a, "reference_space"_a = nullptr)
        .def("trimmed_child_range", &Composition::trim_child_range,
             "child_range"_a)
        .def("trim_child_range", &Composition::trim_child_range,
             "child_range"_a)
        .def("range_of_all_children", [](Composition* t) {
                py::dict d;
                for (auto e: t->range_of_all_children(ErrorStatusHandler())) {
                    d[py::cast(e.first)] = py::cast(e.second);
                }
                return d;
            })
        .def("child_at_time", [](Composition* t, RationalTime const& search_time, bool shallow_search) {
                auto result = t->child_at_time(search_time, ErrorStatusHandler(), shallow_search);
                return result.value;
            }, "search_time"_a, "shallow_search"_a = false)
        .def("children_in_range", [](Composition* t, TimeRange const& search_range) {
                std::vector<SerializableObject*> l;
                for (const auto& child : t->children_in_range(search_range, ErrorStatusHandler())) {
                    l.push_back(child.value);
                }
                return l;
            }, "search_range"_a)
        .def("find_children", [](Composition* c, py::object descended_from_type, optional<TimeRange> const& search_range, bool shallow_search) {
                return find_children(c, descended_from_type, search_range, shallow_search);
            }, "descended_from_type"_a = py::none(), "search_range"_a = nullopt, "shallow_search"_a = false)
        .def("handles_of_child", [](Composition* c, Composable* child) {
                auto result = c->handles_of_child(child, ErrorStatusHandler());
                return py::make_tuple(py::cast(result.first), py::cast(result.second));
            }, "child"_a)
        .def("has_clips", &Composition::has_clips)
        .def("__internal_getitem__", [](Composition* c, int index) {
                index = adjusted_vector_index(index, c->children());
                if (index < 0 || index >= int(c->children().size())) {
                    throw py::index_error();
                }
                return c->children()[index].value;
            }, "index"_a)
        .def("__internal_setitem__", [](Composition* c, int index, Composable* composable) {
                index = adjusted_vector_index(index, c->children());
                c->set_child(index, composable, ErrorStatusHandler());
            }, "index"_a, "item"_a)
        .def("__internal_delitem__", [](Composition* c, int index) {
                index = adjusted_vector_index(index, c->children());
                c->remove_child(index, ErrorStatusHandler());
            }, "index"_a)
        .def("__internal_insert", [](Composition* c, int index, Composable* composable) {
                index = adjusted_vector_index(index, c->children());
                c->insert_child(index, composable, ErrorStatusHandler());
            }, "index"_a, "item"_a)
        .def("__contains__", &Composition::has_child, "composable"_a)
        .def("__len__", [](Composition* c) {
                return c->children().size();
            })
        .def("__iter__", [](Composition* c) {
                return new CompositionIterator(c);
            });

    composable_class
        .def(py::init([](std::string const& name,
                         py::object metadata) {
                          return new Composable(name, py_to_any_dictionary(metadata));
                      }),
             py::arg_v("name"_a = std::string()),
             py::arg_v("metadata"_a = py::none()))
        .def("parent", &Composable::parent)
        .def("visible", &Composable::visible)
        .def("overlapping", &Composable::overlapping);

    auto track_class = py::class_<Track, Composition, managing_ptr<Track>>(m, "Track", py::dynamic_attr());

    py::enum_<Track::NeighborGapPolicy>(track_class, "NeighborGapPolicy")
        .value("around_transitions", Track::NeighborGapPolicy::around_transitions)
        .value("never", Track::NeighborGapPolicy::never);

    track_class
        .def(py::init([](std::string name, optional<std::vector<Composable*>> children,
                         optional<TimeRange> const& source_range,
                         std::string const& kind, py::object metadata) {
                          auto composable_children = vector_or_default<Composable>(children);
                          Track* t = new Track(
                                  name,
                                  source_range,
                                  kind,
                                  py_to_any_dictionary(metadata)
                          );
                          if (!composable_children.empty())
                              t->set_children(composable_children, ErrorStatusHandler());
                          return t;
                      }),
             py::arg_v("name"_a = std::string()),
             "children"_a = py::none(),
             "source_range"_a = nullopt,
             "kind"_a = std::string(Track::Kind::video),
             py::arg_v("metadata"_a = py::none()))
        .def_property("kind", &Track::kind, &Track::set_kind)
        .def("neighbors_of", [](Track* t, Composable* item, Track::NeighborGapPolicy policy) {
                auto result =  t->neighbors_of(item, ErrorStatusHandler(), policy);
                return py::make_tuple(py::cast(result.first.take_value()), py::cast(result.second.take_value()));
            }, "item"_a, "policy"_a = Track::NeighborGapPolicy::never)
        .def("find_clips", [](Track* t, optional<TimeRange> const& search_range, bool shallow_search) {
                return find_clips(t, search_range, shallow_search);
            }, "search_range"_a = nullopt, "shallow_search"_a = false);

    py::class_<Track::Kind>(track_class, "Kind")
        .def_property_readonly_static("Audio", [](py::object /* self */) { return Track::Kind::audio; })
        .def_property_readonly_static("Video", [](py::object /* self */) { return Track::Kind::video; });


    py::class_<Stack, Composition, managing_ptr<Stack>>(m, "Stack", py::dynamic_attr())
        .def(py::init([](std::string name,
                         optional<std::vector<Composable*>> children,
                         optional<TimeRange> const& source_range,
                         optional<std::vector<Marker*>> markers,
                         optional<std::vector<Effect*>> effects,
                         py::object metadata) {
                          auto composable_children = vector_or_default<Composable>(children);
                          Stack* s = new Stack(
                                  name,
                                  source_range,
                                  py_to_any_dictionary(metadata),
                                  vector_or_default<Effect>(effects),
                                  vector_or_default<Marker>(markers)
                          );
                          if (!composable_children.empty()) {
                              s->set_children(composable_children, ErrorStatusHandler());
                          }
                          return s;
                      }),
             py::arg_v("name"_a = std::string()),
             "children"_a = py::none(),
             "source_range"_a = nullopt,
             "markers"_a = py::none(),
             "effects"_a = py::none(),
             py::arg_v("metadata"_a = py::none()))
        .def("find_clips", [](Stack* s, optional<TimeRange> const& search_range, bool shallow_search) {
                return find_clips(s, search_range, shallow_search);
            }, "search_range"_a = nullopt, "shallow_search"_a = false);

    py::class_<Timeline, SerializableObjectWithMetadata, managing_ptr<Timeline>>(m, "Timeline", py::dynamic_attr())
        .def(py::init([](std::string name,
                         optional<std::vector<Composable*>> children,
                         optional<RationalTime> global_start_time,
                         py::object metadata) {
                          auto composable_children = vector_or_default<Composable>(children);
                          Timeline* t = new Timeline(name, global_start_time,
                                                     py_to_any_dictionary(metadata));
                          if (!composable_children.empty())
                              t->tracks()->set_children(composable_children, ErrorStatusHandler());
                          return t;
                      }),
             py::arg_v("name"_a = std::string()),
             "tracks"_a = py::none(),
             "global_start_time"_a = nullopt,
             py::arg_v("metadata"_a = py::none()))
        .def_property("global_start_time", &Timeline::global_start_time, &Timeline::set_global_start_time)
        .def_property("tracks", &Timeline::tracks, &Timeline::set_tracks)
        .def("duration", [](Timeline* t) {
                return t->duration(ErrorStatusHandler());
            })
        .def("range_of_child", [](Timeline* t, Composable* child) {
                return t->range_of_child(child, ErrorStatusHandler());
            })
        .def("video_tracks", &Timeline::video_tracks)
        .def("audio_tracks", &Timeline::audio_tracks)
        .def("find_clips", [](Timeline* t, optional<TimeRange> const& search_range, bool shallow_search) {
                return find_clips(t, search_range, shallow_search);
            }, "search_range"_a = nullopt, "shallow_search"_a = false)
        .def("find_children", [](Timeline* t, py::object descended_from_type, optional<TimeRange> const& search_range, bool shallow_search) {
                return find_children(t, descended_from_type, search_range, shallow_search);
            }, "descended_from_type"_a = py::none(), "search_range"_a = nullopt, "shallow_search"_a = false);
}

static void define_effects(py::module m) {
    py::class_<Effect, SOWithMetadata, managing_ptr<Effect>>(m, "Effect", py::dynamic_attr())
        .def(py::init([](std::string name,
                         std::string effect_name,
                         py::object metadata) {
                          return new Effect(name, effect_name, py_to_any_dictionary(metadata)); }),
             py::arg_v("name"_a = std::string()),
             "effect_name"_a = std::string(),
             py::arg_v("metadata"_a = py::none()))
        .def_property("effect_name", &Effect::effect_name, &Effect::set_effect_name);

    py::class_<TimeEffect, Effect, managing_ptr<TimeEffect>>(m, "TimeEffect", py::dynamic_attr(), "Base class for all effects that alter the timing of an item.")
        .def(py::init([](std::string name,
                         std::string effect_name,
                         py::object metadata) {
                          return new TimeEffect(name, effect_name, py_to_any_dictionary(metadata)); }),
             py::arg_v("name"_a = std::string()),
             "effect_name"_a = std::string(),
             py::arg_v("metadata"_a = py::none()));

    py::class_<LinearTimeWarp, TimeEffect, managing_ptr<LinearTimeWarp>>(m, "LinearTimeWarp", py::dynamic_attr(), R"docstring(
A time warp that applies a linear speed up or slow down across the entire clip.
)docstring")
        .def(py::init([](std::string name,
                         double time_scalar,
                         py::object metadata) {
                          return new LinearTimeWarp(name, "LinearTimeWarp", time_scalar,
                                                    py_to_any_dictionary(metadata)); }),
             py::arg_v("name"_a = std::string()),
             "time_scalar"_a = 1.0,
             py::arg_v("metadata"_a = py::none()))
        .def_property("time_scalar", &LinearTimeWarp::time_scalar, &LinearTimeWarp::set_time_scalar, R"docstring(
Linear time scalar applied to clip. 2.0 means the clip occupies half the time in the parent item, i.e. plays at double speed,
0.5 means the clip occupies twice the time in the parent item, i.e. plays at half speed.

Note that adjusting the time_scalar of a :class:`~LinearTimeWarp` does not affect the duration of the item this effect is attached to.
Instead it affects the speed of the media displayed within that item.
)docstring");

    py::class_<FreezeFrame, LinearTimeWarp, managing_ptr<FreezeFrame>>(m, "FreezeFrame", py::dynamic_attr(), "Hold the first frame of the clip for the duration of the clip.")
        .def(py::init([](std::string name, py::object metadata) {
                    return new FreezeFrame(name, py_to_any_dictionary(metadata)); }),
            py::arg_v("name"_a = std::string()),
            py::arg_v("metadata"_a = py::none()));
}

static void define_media_references(py::module m) {
    py::class_<MediaReference, SOWithMetadata,
               managing_ptr<MediaReference>>(m, "MediaReference", py::dynamic_attr())
        .def(py::init([](std::string name,
                         optional<TimeRange> available_range,
                         py::object metadata,
                         optional<Imath::Box2d> const& available_image_bounds) {
                          return new MediaReference(name, available_range, py_to_any_dictionary(metadata), available_image_bounds); }),
             py::arg_v("name"_a = std::string()),
             "available_range"_a = nullopt,
             py::arg_v("metadata"_a = py::none()),
             "available_image_bounds"_a = nullopt)

        .def_property("available_range", &MediaReference::available_range, &MediaReference::set_available_range)
        .def_property("available_image_bounds", &MediaReference::available_image_bounds, &MediaReference::set_available_image_bounds) 
        .def_property_readonly("is_missing_reference", &MediaReference::is_missing_reference);

    py::class_<GeneratorReference, MediaReference,
               managing_ptr<GeneratorReference>>(m, "GeneratorReference", py::dynamic_attr())
        .def(py::init([](std::string name, std::string generator_kind,
                         optional<TimeRange> const& available_range,
                         py::object parameters, py::object metadata,
                         optional<Imath::Box2d> const& available_image_bounds) {
                          return new GeneratorReference(name, generator_kind,
                                                        available_range,
                                                        py_to_any_dictionary(parameters),
                                                        py_to_any_dictionary(metadata),
                                                        available_image_bounds); }),
             py::arg_v("name"_a = std::string()),
             "generator_kind"_a = std::string(),
             "available_range"_a = nullopt,
             "parameters"_a = py::none(),
             py::arg_v("metadata"_a = py::none()),
             "available_image_bounds"_a = nullopt)
        .def_property("generator_kind", &GeneratorReference::generator_kind, &GeneratorReference::set_generator_kind)
        .def_property_readonly("parameters", [](GeneratorReference* g) {
                auto ptr = g->parameters().get_or_create_mutation_stamp();
                return (AnyDictionaryProxy*)(ptr); }, py::return_value_policy::take_ownership);


    py::class_<MissingReference, MediaReference,
               managing_ptr<MissingReference>>(m, "MissingReference", py::dynamic_attr(), R"docstring(
Represents media for which a concrete reference is missing.

Note that a :class:`~MissingReference` may have useful metadata, even if the location of the media is not known.
)docstring")
        .def(py::init([](
                        std::string name,
                        optional<TimeRange> available_range,
                        py::object metadata,
                        optional<Imath::Box2d> const& available_image_bounds) {
                    return new MissingReference(
                                  name,
                                  available_range,
                                  py_to_any_dictionary(metadata),
                                  available_image_bounds); 
                    }),
             py::arg_v("name"_a = std::string()),
             "available_range"_a = nullopt,
             py::arg_v("metadata"_a = py::none()),
             "available_image_bounds"_a = nullopt);


    py::class_<ExternalReference, MediaReference,
               managing_ptr<ExternalReference>>(m, "ExternalReference", py::dynamic_attr())
        .def(py::init([](std::string target_url,
                         optional<TimeRange> const& available_range,
                         py::object metadata,
                         optional<Imath::Box2d> const& available_image_bounds) {
                          return new ExternalReference(target_url,
                                                        available_range,
                                                        py_to_any_dictionary(metadata),
                                                        available_image_bounds); }),
             "target_url"_a = std::string(),
             "available_range"_a = nullopt,
             py::arg_v("metadata"_a = py::none()),
             "available_image_bounds"_a = nullopt)
        .def_property("target_url", &ExternalReference::target_url, &ExternalReference::set_target_url);

    auto imagesequencereference_class = py:: class_<ImageSequenceReference, MediaReference,
            managing_ptr<ImageSequenceReference>>(m, "ImageSequenceReference", py::dynamic_attr(), R"docstring(
An ImageSequenceReference refers to a numbered series of single-frame image files. Each file can be referred to by a URL generated by the :class:`~ImageSequenceReference`.

Image sequences can have URLs with discontinuous frame numbers, for instance if you've only rendered every other frame in a sequence, your frame numbers may be 1, 3, 5, etc. This is configured using the ``frame_step`` attribute. In this case, the 0th image in the sequence is frame 1 and the 1st image in the sequence is frame 3. Because of this there are two numbering concepts in the image sequence, the image number and the frame number.

Frame numbers are the integer numbers used in the frame file name. Image numbers are the 0-index based numbers of the frames available in the reference. Frame numbers can be discontinuous, image numbers will always be zero to the total count of frames minus 1.

An example for 24fps media with a sample provided each frame numbered 1-1000 with a path ``/show/sequence/shot/sample_image_sequence.%04d.exr`` might be

.. code-block:: json

    {
      "available_range": {
        "start_time": {
          "value": 0,
          "rate": 24
        },
        "duration": {
          "value": 1000,
          "rate": 24
        }
      },
      "start_frame": 1,
      "frame_step": 1,
      "rate": 24,
      "target_url_base": "file:///show/sequence/shot/",
      "name_prefix": "sample_image_sequence.",
      "name_suffix": ".exr"
      "frame_zero_padding": 4,
    }

The same duration sequence but with only every 2nd frame available in the sequence would be

.. code-block:: json

    {
      "available_range": {
        "start_time": {
          "value": 0,
          "rate": 24
        },
        "duration": {
          "value": 1000,
          "rate": 24
        }
      },
      "start_frame": 1,
      "frame_step": 2,
      "rate": 24,
      "target_url_base": "file:///show/sequence/shot/",
      "name_prefix": "sample_image_sequence.",
      "name_suffix": ".exr"
      "frame_zero_padding": 4,
    }

A list of all the frame URLs in the sequence can be generated, regardless of frame step, with the following list comprehension

.. code-block:: python

    [ref.target_url_for_image_number(i) for i in range(ref.number_of_images_in_sequence())]

Negative ``start_frame`` is also handled. The above example with a ``start_frame`` of ``-1`` would yield the first three target urls as:

- ``file:///show/sequence/shot/sample_image_sequence.-0001.exr``
- ``file:///show/sequence/shot/sample_image_sequence.0000.exr``
- ``file:///show/sequence/shot/sample_image_sequence.0001.exr``
)docstring");

    py::enum_<ImageSequenceReference::MissingFramePolicy>(imagesequencereference_class, "MissingFramePolicy", "Behavior that should be used by applications when an image file in the sequence can't be found on disk.")
        .value("error", ImageSequenceReference::MissingFramePolicy::error, "Application should stop and raise an error.")
        .value("hold", ImageSequenceReference::MissingFramePolicy::hold, "Application should hold the last available frame before the missing frame.")
        .value("black", ImageSequenceReference::MissingFramePolicy::black, "Application should use a black frame in place of the missing frame");

    imagesequencereference_class
        .def(py::init([](std::string target_url_base,
                         std::string name_prefix,
                         std::string name_suffix,
                         int start_frame,
                         int frame_step,
                         double const rate,
                         int frame_zero_padding,
                         ImageSequenceReference::MissingFramePolicy const missing_frame_policy,
                         optional<TimeRange> const& available_range,
                         py::object metadata,
                         optional<Imath::Box2d> const& available_image_bounds) {
                          return new ImageSequenceReference(target_url_base,
                                                            name_prefix,
                                                            name_suffix,
                                                            start_frame,
                                                            frame_step,
                                                            rate,
                                                            frame_zero_padding,
                                                            missing_frame_policy,
                                                            available_range,
                                                            py_to_any_dictionary(metadata),
                                                            available_image_bounds); }),
                        "target_url_base"_a = std::string(),
                        "name_prefix"_a = std::string(),
                        "name_suffix"_a = std::string(),
                        "start_frame"_a = 1L,
                        "frame_step"_a = 1L,
                        "rate"_a = 1,
                        "frame_zero_padding"_a = 0,
                        "missing_frame_policy"_a = ImageSequenceReference::MissingFramePolicy::error,
                        "available_range"_a = nullopt,
                        py::arg_v("metadata"_a = py::none()),
                        "available_image_bounds"_a = nullopt)
        .def_property("target_url_base", &ImageSequenceReference::target_url_base, &ImageSequenceReference::set_target_url_base, "Everything leading up to the file name in the ``target_url``.")
        .def_property("name_prefix", &ImageSequenceReference::name_prefix, &ImageSequenceReference::set_name_prefix, "Everything in the file name leading up to the frame number.")
        .def_property("name_suffix", &ImageSequenceReference::name_suffix, &ImageSequenceReference::set_name_suffix, "Everything after the frame number in the file name.")
        .def_property("start_frame", &ImageSequenceReference::start_frame, &ImageSequenceReference::set_start_frame, "The first frame number used in file names.")
        .def_property("frame_step", &ImageSequenceReference::frame_step, &ImageSequenceReference::set_frame_step, "Step between frame numbers in file names.")
        .def_property("rate", &ImageSequenceReference::rate, &ImageSequenceReference::set_rate, "Frame rate if every frame in the sequence were played back.")
        .def_property("frame_zero_padding", &ImageSequenceReference::frame_zero_padding, &ImageSequenceReference::set_frame_zero_padding, "Number of digits to pad zeros out to in frame numbers.")
        .def_property("missing_frame_policy", &ImageSequenceReference::missing_frame_policy, &ImageSequenceReference::set_missing_frame_policy, "Directive for how frames in sequence not found during playback or rendering should be handled.")
        .def("end_frame", &ImageSequenceReference::end_frame, "Last frame number in the sequence based on the :attr:`rate` and :attr:`.available_range`.")
        .def("number_of_images_in_sequence", &ImageSequenceReference::number_of_images_in_sequence, "Returns the number of images based on the :attr:`rate` and :attr:`.available_range`.")
        .def("frame_for_time", [](ImageSequenceReference *seq_ref, RationalTime time) {
                return seq_ref->frame_for_time(time, ErrorStatusHandler());
        }, "time"_a, "Given a :class:`.RationalTime` within the available range, returns the frame number.")
        .def("target_url_for_image_number", [](ImageSequenceReference *seq_ref, int image_number) {
                return seq_ref->target_url_for_image_number(
                        image_number,
                        ErrorStatusHandler()
                );
        }, "image_number"_a, R"docstring(Given an image number, returns the ``target_url`` for that image.

This is roughly equivalent to:

.. code-block:: python

   f"{target_url_prefix}{(start_frame + (image_number * frame_step)):0{value_zero_padding}}{target_url_postfix}"

)docstring")
        .def("presentation_time_for_image_number", [](ImageSequenceReference *seq_ref, int image_number) {
                return seq_ref->presentation_time_for_image_number(
                        image_number,
                        ErrorStatusHandler()
                );
        }, "image_number"_a, "Given an image number, returns the :class:`.RationalTime` at which that image should be shown in the space of :attr:`.available_range`.");

}

void otio_serializable_object_bindings(py::module m) {
    define_bases1(m);
    define_bases2(m);
    define_effects(m);
    define_media_references(m);
    define_items_and_compositions(m);
}

