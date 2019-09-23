#include <pybind11/pybind11.h>
#include <pybind11/operators.h>
#include "otio_errorStatusHandler.h"

#include "opentimelineio/clip.h"
#include "opentimelineio/composable.h"
#include "opentimelineio/composition.h"
#include "opentimelineio/effect.h"
#include "opentimelineio/externalReference.h"
#include "opentimelineio/freezeFrame.h"
#include "opentimelineio/gap.h"
#include "opentimelineio/generatorReference.h"
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
    const std::string string_or_none_converter(py::object& thing) {
        if (thing.is(py::none())) {
            return std::string();
        }
        else {
            return py::str(thing);
        }
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

static py::arg_v name_arg = ("name"_a = std::string());
static py::arg_v metadata_arg = ("metadata"_a = py::none());

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
    py::class_<SerializableObject, managing_ptr<SerializableObject>>(m, "SerializableObject", py::dynamic_attr())
        .def(py::init<>())
        .def_property_readonly("_dynamic_fields", [](SerializableObject* s) {
                auto ptr = s->dynamic_fields().get_or_create_mutation_stamp();
                return (AnyDictionaryProxy*)(ptr); }, py::return_value_policy::take_ownership)
        .def("is_equivalent_to", &SerializableObject::is_equivalent_to, "other"_a.none(false))
        .def("clone", [](SerializableObject* so) {
                return so->clone(ErrorStatusHandler()); })
        .def("to_json_string", [](SerializableObject* so, int indent) {
                return so->to_json_string(ErrorStatusHandler(), indent); },
            "indent"_a = 4)
        .def("to_json_file", [](SerializableObject* so, std::string file_name, int indent) {
                return so->to_json_file(file_name, ErrorStatusHandler(), indent); },
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
        .def(py::init([](std::string name, py::object metadata) {
                    return new SOWithMetadata(name, py_to_any_dictionary(metadata));
                }),
            name_arg,
            metadata_arg)
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

    py::class_<Composable, SOWithMetadata,
               managing_ptr<Composable>>(m, "Composable", py::dynamic_attr())
        .def(py::init([](std::string const& name,
                         py::object metadata) {
                          return new Composable(name, py_to_any_dictionary(metadata));
                      }),
             name_arg,
             metadata_arg)
        .def("parent", &Composable::parent)
        .def("visible", &Composable::visible)
        .def("overlapping", &Composable::overlapping);

    auto marker_class =
        py::class_<Marker, SOWithMetadata, managing_ptr<Marker>>(m, "Marker", py::dynamic_attr())
        .def(py::init([](
                        py::object name,
                        TimeRange marked_range,
                        std::string const& color,
                        py::object metadata) {
                          return new Marker(
                                  string_or_none_converter(name),
                                  marked_range,
                                  color,
                                  py_to_any_dictionary(metadata));
                      }),
             name_arg,
             "marked_range"_a = TimeRange(),
             "color"_a = std::string(Marker::Color::red),
             metadata_arg)
        .def_property("color", &Marker::color, &Marker::set_color)
        .def_property("marked_range", &Marker::marked_range, &Marker::set_marked_range);

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
        .def("next", &SerializableCollectionIterator::next);

    py::class_<SerializableCollection, SOWithMetadata,
               managing_ptr<SerializableCollection>>(m, "SerializableCollection", py::dynamic_attr())
        .def(py::init([](std::string const& name, py::object children,
                         py::object metadata) {
                          return new SerializableCollection(name,
                                                py_to_vector<SerializableObject*>(children),
                                                py_to_any_dictionary(metadata)); }),
             name_arg,
             "children"_a = py::none(),
             metadata_arg)
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
            });
}

static void define_items_and_compositions(py::module m) {
    py::class_<Item, Composable, managing_ptr<Item>>(m, "Item", py::dynamic_attr())
        .def(py::init([](std::string name, optional<TimeRange> source_range,
                         py::object effects, py::object markers, py::object metadata) {
                          return new Item(name, source_range,
                                          py_to_any_dictionary(metadata),                                      
                                          py_to_vector<Effect*>(effects),
                                          py_to_vector<Marker*>(markers)); }),
             name_arg,
             "source_range"_a = nullopt,
             "effects"_a = py::none(),
             "markers"_a = py::none(),
             metadata_arg)
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
            }, "time_range"_a, "to_item"_a);

    auto transition_class =
        py::class_<Transition, Composable, managing_ptr<Transition>>(m, "Transition", py::dynamic_attr())
        .def(py::init([](std::string const& name, std::string const& transition_type,
                         RationalTime in_offset, RationalTime out_offset,
                         py::object metadata) {
                          return new Transition(name, transition_type,
                                                in_offset, out_offset,
                                                py_to_any_dictionary(metadata)); }),
             name_arg,
             "transition_type"_a = std::string(),
             "in_offset"_a = RationalTime(),
             "out_offset"_a = RationalTime(),
             metadata_arg)
        .def_property("transition_type", &Transition::transition_type, &Transition::set_transition_type)
        .def_property("in_offset", &Transition::in_offset, &Transition::set_in_offset)
        .def_property("out_offset", &Transition::out_offset, &Transition::set_out_offset)
        .def("duration", [](Transition* t) {
            return t->duration(ErrorStatusHandler());
            })
        .def("range_in_parent", [](Transition* t) {
            return t->range_in_parent(ErrorStatusHandler());
            })
        .def("trimmed_range_in_parent", [](Transition* t) {
            return t->trimmed_range_in_parent(ErrorStatusHandler());
            });


    py::class_<Transition::Type>(transition_class, "Type")
        .def_property_readonly_static("SMPTE_Dissolve", [](py::object /* self */) { return Transition::Type::SMPTE_Dissolve; })
        .def_property_readonly_static("Custom", [](py::object /* self */) { return Transition::Type::Custom; });
    

    py::class_<Gap, Item, managing_ptr<Gap>>(m, "Gap", py::dynamic_attr())
        .def(py::init([](std::string name, TimeRange source_range, py::object effects,
                         py::object markers, py::object metadata) {
                          return new Gap(source_range, name,
                                         py_to_vector<Effect*>(effects),
                                         py_to_vector<Marker*>(markers),
                                         py_to_any_dictionary(metadata)); }),
             name_arg,
             "source_range"_a = TimeRange(),
             "effect"_a = py::none(),
             "markers"_a = py::none(),
             metadata_arg)
       .def(py::init([](std::string name, RationalTime duration, py::object effects,
                        py::object markers, py::object metadata) {
                          return new Gap(duration, name,
                                         py_to_vector<Effect*>(effects),
                                         py_to_vector<Marker*>(markers),
                                         py_to_any_dictionary(metadata)); }),
             name_arg,
             "duration"_a = RationalTime(),
             "effect"_a = py::none(),
             "markers"_a = py::none(),
             metadata_arg);

    py::class_<Clip, Item, managing_ptr<Clip>>(m, "Clip", py::dynamic_attr())
        .def(py::init([](std::string name, MediaReference* media_reference,
                         optional<TimeRange> source_range, py::object metadata) {
                          return new Clip(name, media_reference, source_range, py_to_any_dictionary(metadata));
                      }),
             name_arg,
             "media_reference"_a = nullptr,
             "source_range"_a = nullopt,
             metadata_arg)
        .def_property("media_reference", &Clip::media_reference, &Clip::set_media_reference);

    using CompositionIterator = ContainerIterator<Composition, Composable*>;
    py::class_<CompositionIterator>(m, "CompositionIterator")
        .def("__iter__", &CompositionIterator::iter)
        .def("next", &CompositionIterator::next);

    py::class_<Composition, Item, managing_ptr<Composition>>(m, "Composition", py::dynamic_attr())
        .def(py::init([](std::string name,
                         py::object children,                         
                         optional<TimeRange> source_range, py::object metadata) {
                          Composition* c = new Composition(name, source_range,
                                                           py_to_any_dictionary(metadata));
                          c->set_children(py_to_vector<Composable*>(children), ErrorStatusHandler());
                          return c;
                      }),
             name_arg,
             "children"_a = py::none(),
             "source_range"_a = nullopt,
             metadata_arg)
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
        .def("handles_of_child", [](Composition* c, Composable* child) {
                auto result = c->handles_of_child(child, ErrorStatusHandler());
                return py::make_tuple(py::cast(result.first), py::cast(result.second));
            }, "child_a")
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
    
    auto track_class = py::class_<Track, Composition, managing_ptr<Track>>(m, "Track", py::dynamic_attr());

    py::enum_<Track::NeighborGapPolicy>(track_class, "NeighborGapPolicy")
        .value("around_transitions", Track::NeighborGapPolicy::around_transitions)
        .value("never", Track::NeighborGapPolicy::never);

    track_class
        .def(py::init([](py::object name, py::object children,
                         optional<TimeRange> const& source_range,
                         std::string const& kind, py::object metadata) {
                          auto composable_children = py_to_vector<Composable*>(children);
                          Track* t = new Track(
                                  string_or_none_converter(name),
                                  source_range,
                                  kind,
                                  py_to_any_dictionary(metadata)
                          );
                          if (!composable_children.empty())
                              t->set_children(composable_children, ErrorStatusHandler());
                          return t;
                      }),
             name_arg,
             "children"_a = py::none(),
             "source_range"_a = nullopt,
             "kind"_a = std::string(Track::Kind::video),
             metadata_arg)
        .def_property("kind", &Track::kind, &Track::set_kind)
        .def("neighbors_of", [](Track* t, Composable* item, Track::NeighborGapPolicy policy) {
                auto result =  t->neighbors_of(item, ErrorStatusHandler(), policy);
                return py::make_tuple(py::cast(result.first.take_value()), py::cast(result.second.take_value()));
            }, "item"_a, "policy"_a = Track::NeighborGapPolicy::never);

    py::class_<Track::Kind>(track_class, "Kind")
        .def_property_readonly_static("Audio", [](py::object /* self */) { return Track::Kind::audio; })
        .def_property_readonly_static("Video", [](py::object /* self */) { return Track::Kind::video; });

    
    py::class_<Stack, Composition, managing_ptr<Stack>>(m, "Stack", py::dynamic_attr())
        .def(py::init([](py::object name,
                         py::object children,
                         optional<TimeRange> const& source_range,
                         py::object markers,
                         py::object effects,
                         py::object metadata) {
                          auto composable_children = py_to_vector<Composable*>(children);
                          Stack* s = new Stack(
                                  string_or_none_converter(name),
                                  source_range,
                                  py_to_any_dictionary(metadata),
                                  py_to_vector<Effect*>(effects),
                                  py_to_vector<Marker*>(markers)
                          );
                          if (!composable_children.empty()) {
                              s->set_children(composable_children, ErrorStatusHandler());
                          }
                          auto composable_markers = py_to_vector<Marker*>(markers);
                          return s;
                      }),
             name_arg,
             "children"_a = py::none(),
             "source_range"_a = nullopt,
             "markers"_a = py::none(),
             "effects"_a = py::none(),
             metadata_arg
        );

    py::class_<Timeline, SerializableObjectWithMetadata, managing_ptr<Timeline>>(m, "Timeline", py::dynamic_attr())
        .def(py::init([](std::string name,
                         py::object children,
                         optional<RationalTime> global_start_time,
                         py::object metadata) {
                          auto composable_children = py_to_vector<Composable*>(children);
                          Timeline* t = new Timeline(name, global_start_time,
                                                     py_to_any_dictionary(metadata));
                          if (!composable_children.empty())
                              t->tracks()->set_children(composable_children, ErrorStatusHandler());
                          return t;
                      }),
             name_arg,
             "tracks"_a = py::none(),
             "global_start_time"_a = nullopt,
             metadata_arg)
        .def_property("global_start_time", &Timeline::global_start_time, &Timeline::set_global_start_time)
        .def_property("tracks", &Timeline::tracks, &Timeline::set_tracks)
        .def("duration", [](Timeline* t) {
                return t->duration(ErrorStatusHandler());
            })
        .def("range_of_child", [](Timeline* t, Composable* child) {
                return t->range_of_child(child, ErrorStatusHandler());
            })
        .def("video_tracks", &Timeline::video_tracks)
        .def("audio_tracks", &Timeline::audio_tracks);
}

static void define_effects(py::module m) {
    py::class_<Effect, SOWithMetadata, managing_ptr<Effect>>(m, "Effect", py::dynamic_attr())
        .def(py::init([](std::string name,
                         std::string effect_name,
                         py::object metadata) {
                          return new Effect(name, effect_name, py_to_any_dictionary(metadata)); }),
             name_arg,
             "effect_name"_a = std::string(),
             metadata_arg)
        .def_property("effect_name", &Effect::effect_name, &Effect::set_effect_name);

    py::class_<TimeEffect, Effect, managing_ptr<TimeEffect>>(m, "TimeEffect", py::dynamic_attr())
        .def(py::init([](std::string name,
                         std::string effect_name,
                         py::object metadata) {
                          return new TimeEffect(name, effect_name, py_to_any_dictionary(metadata)); }),
             name_arg,
             "effect_name"_a = std::string(),             
             metadata_arg);

    py::class_<LinearTimeWarp, TimeEffect, managing_ptr<LinearTimeWarp>>(m, "LinearTimeWarp", py::dynamic_attr())
        .def(py::init([](std::string name,
                         double time_scalar,
                         py::object metadata) {
                          return new LinearTimeWarp(name, "LinearTimeWarp", time_scalar,
                                                    py_to_any_dictionary(metadata)); }),
             name_arg,
             "time_scalar"_a = 1.0,
             metadata_arg)
        .def_property("time_scalar", &LinearTimeWarp::time_scalar, &LinearTimeWarp::set_time_scalar);

    py::class_<FreezeFrame, LinearTimeWarp, managing_ptr<FreezeFrame>>(m, "FreezeFrame", py::dynamic_attr())
        .def(py::init([](std::string name, py::object metadata) {
                    return new FreezeFrame(name, py_to_any_dictionary(metadata)); }),
            name_arg,
            metadata_arg);
}

static void define_media_references(py::module m) {
    py::class_<MediaReference, SOWithMetadata,
               managing_ptr<MediaReference>>(m, "MediaReference", py::dynamic_attr())
        .def(py::init([](std::string name,
                         optional<TimeRange> available_range,
                         py::object metadata) {
                          return new MediaReference(name, available_range, py_to_any_dictionary(metadata)); }),
             name_arg,
             "available_range"_a = nullopt,
             metadata_arg)
        .def_property("available_range", &MediaReference::available_range, &MediaReference::set_available_range)
        .def_property_readonly("is_missing_reference", &MediaReference::is_missing_reference);

    py::class_<GeneratorReference, MediaReference,
               managing_ptr<GeneratorReference>>(m, "GeneratorReference", py::dynamic_attr())
        .def(py::init([](std::string name, std::string generator_kind,
                         optional<TimeRange> const& available_range,
                         py::object parameters, py::object metadata) {
                          return new GeneratorReference(name, generator_kind,
                                                        available_range,
                                                        py_to_any_dictionary(parameters),
                                                        py_to_any_dictionary(metadata)); }),
             name_arg,
             "generator_kind"_a = std::string(),
             "available_range"_a = nullopt,
             "parameters"_a = py::none(),
             metadata_arg)
        .def_property("generator_kind", &GeneratorReference::generator_kind, &GeneratorReference::set_generator_kind)
        .def_property_readonly("parameters", [](GeneratorReference* g) {
                auto ptr = g->parameters().get_or_create_mutation_stamp();
                return (AnyDictionaryProxy*)(ptr); }, py::return_value_policy::take_ownership);


    py::class_<MissingReference, MediaReference,
               managing_ptr<MissingReference>>(m, "MissingReference", py::dynamic_attr())
        .def(py::init([](
                        py::object name,
                        optional<TimeRange> available_range,
                        py::object metadata) {
                    return new MissingReference(
                                  string_or_none_converter(name),
                                  available_range,
                                  py_to_any_dictionary(metadata)); 
                    }),
             name_arg,
             "available_range"_a = nullopt,
             metadata_arg);


    py::class_<ExternalReference, MediaReference,
               managing_ptr<ExternalReference>>(m, "ExternalReference", py::dynamic_attr())
        .def(py::init([](std::string target_url,
                         optional<TimeRange> const& available_range,
                         py::object metadata) {
                          return new ExternalReference(target_url,
                                                        available_range,
                                                        py_to_any_dictionary(metadata)); }),
             "target_url"_a = std::string(),
             "available_range"_a = nullopt,
             metadata_arg)
        .def_property("target_url", &ExternalReference::target_url, &ExternalReference::set_target_url);
}

void otio_serializable_object_bindings(py::module m) {
    define_bases1(m);
    define_bases2(m);
    define_effects(m);
    define_media_references(m);
    define_items_and_compositions(m);
}
    
