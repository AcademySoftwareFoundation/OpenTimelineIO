// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include <pybind11/pybind11.h>
#include "otio_utils.h"

#include "opentimelineio/anyDictionary.h"

namespace py = pybind11;

struct AnyDictionaryProxy : public AnyDictionary::MutationStamp {
    using MutationStamp = AnyDictionary::MutationStamp;

    AnyDictionaryProxy() {}

    // TODO: Should we instead just pass an AnyDictionary?
    AnyDictionaryProxy(MutationStamp *d) {
        any_dictionary = d->any_dictionary;
    }

    AnyDictionaryProxy(const AnyDictionaryProxy& other) // Copy constructor. Required to convert a py::handle to an AnyDictionaryProxy.
    {
        AnyDictionary* d = new AnyDictionary;

        AnyDictionary::iterator ptr;
        for (ptr = other.any_dictionary->begin(); ptr != other.any_dictionary->end(); ptr++) {
            d->insert(*ptr);
        }

        any_dictionary = d;
    }

    ~AnyDictionaryProxy() {
    }

    static void throw_dictionary_was_deleted() {
        throw py::value_error("Underlying C++ AnyDictionary has been destroyed");
    }

    struct Iterator {
        Iterator(MutationStamp& s)
            : mutation_stamp(s),
              it(s.any_dictionary->begin()),
              starting_stamp { s.stamp } {
        }

        MutationStamp& mutation_stamp;
        AnyDictionary::iterator it;
        int64_t starting_stamp;
    
        Iterator* iter() {
            return this;
        }
        
        pybind11::object next() {
            if (!mutation_stamp.any_dictionary) {
                throw_dictionary_was_deleted();
            }
            else if (mutation_stamp.stamp != starting_stamp) {
                throw py::value_error("container mutated during iteration");
            }
            else if (it == mutation_stamp.any_dictionary->end()) {
                throw py::stop_iteration();
            }

            std::string const& key = it->first;
            ++it;
            return plain_string(key);
        }
    };

    py::object get_item(std::string const& key) {
        AnyDictionary& m = fetch_any_dictionary();

        auto e = m.find(key);
        if (e == m.end()) {
            throw py::key_error(key);
        }
        return any_to_py(e->second);
    }

    void set_item(std::string const& key, PyAny* pyAny) {
        AnyDictionary& m = fetch_any_dictionary();
        auto it = m.find(key);
        if (it != m.end()) {
            std::swap(it->second, pyAny->a);
        }
        else {
            m.emplace(key, std::move(pyAny->a));
        }
    }
    
    void del_item(std::string const& key) {
        AnyDictionary& m = fetch_any_dictionary();        
        auto e = m.find(key);
        if (e == m.end()) {
            throw py::key_error(key);
        }
        m.erase(e);
    }

    int len() {
        return int(fetch_any_dictionary().size());
    }
    
    Iterator* iter() {
        (void) fetch_any_dictionary();
        return new Iterator(*this);
    }

    AnyDictionary& fetch_any_dictionary() const {
        if (!any_dictionary) {
            throw_dictionary_was_deleted();
        }
        return *any_dictionary;
    }
};

// Taken from https://github.com/pybind/pybind11/issues/1176#issuecomment-343312352
// This is a custom type caster for the AnyDictionaryProxy class. This makes AnyDictionaryProxy
// accept both AnyDictionaryProxy and py::dict.
namespace pybind11 { namespace detail {
    template <> struct type_caster<AnyDictionaryProxy> : public type_caster_base<AnyDictionaryProxy> {
        using base = type_caster_base<AnyDictionaryProxy>;
    public:

        // Override the type reported in docstings. opentimelineio.core.Metadata is defined
        // in Python. It's defined as a union of a dict and AnyDictionary.
        // This will allow mypy to do its job.
        static constexpr auto name = const_name("opentimelineio.core.Metadata");

        /**
         * Conversion part 1 (Python->C++): convert a PyObject into an any
         * instance or return false upon failure. The second argument
         * indicates whether implicit conversions should be applied.
         */
        bool load(handle src, bool convert) {
            // First try to convert using the base (default) type caster for AnyDictionaryProxy.
            if (base::load(src, convert)) {
                return true;
            }

            // If we got a dict, then do our own thing to convert the dict into an AnyDictionaryProxy.
            else if (py::isinstance<py::dict>(src)) {
                auto proxy = new AnyDictionaryProxy();
                AnyDictionary&& d = py_to_cpp(py::cast<py::dict>(src));
                proxy->fetch_any_dictionary().swap(d);
                value = proxy;
                return true;
            }

            return false;
        }

        /**
         * Conversion part 2 (C++ -> Python): convert an any instance into
         * a Python object. The second and third arguments are used to
         * indicate the return value policy and parent object (for
         * ``return_value_policy::reference_internal``) and are generally
         * ignored by implicit casters.
         */
        // static handle cast(AnyDictionaryProxy *src, return_value_policy policy, handle parent) {
        //     /* Do any additional work here */
        //     return base::cast(src, policy, parent);
        // }
    };
}}
