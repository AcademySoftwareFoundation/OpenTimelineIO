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

