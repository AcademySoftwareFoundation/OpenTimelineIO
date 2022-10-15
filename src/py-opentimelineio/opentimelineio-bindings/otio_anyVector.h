// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once
#include <pybind11/pybind11.h>
#include "opentimelineio/anyVector.h"
#include "opentimelineio/vectorIndexing.h"
#include "otio_bindings.h"
#include "otio_utils.h"

namespace py = pybind11;

struct AnyVectorProxy : public AnyVector::MutationStamp {
    using MutationStamp = AnyVector::MutationStamp;

    AnyVectorProxy() {}
    AnyVectorProxy(const AnyVectorProxy& other) // Copy constructor. Required to convert a py::handle to an AnyVectorProxy.
    {
        AnyVector* v = new AnyVector;

        AnyVector::iterator ptr;
        for (ptr = other.any_vector->begin(); ptr < other.any_vector->end(); ptr++) {
            v->push_back(*ptr);
        }
        any_vector = v;
    }

    static void throw_array_was_deleted() {
        throw py::value_error("Underlying C++ AnyVector object has been destroyed");
    }

    struct Iterator {
        Iterator(MutationStamp& s)
            : mutation_stamp(s),
              it(0) {
        }

        MutationStamp& mutation_stamp;
        size_t it;
    
        Iterator* iter() {
            return this;
        }
        
        py::object next() {
            if (!mutation_stamp.any_vector) {
                throw_array_was_deleted();
            }
            else if (it == mutation_stamp.any_vector->size()) {
                throw py::stop_iteration();
            }

            return any_to_py((*mutation_stamp.any_vector)[it++]);
        }
    };

    py::object get_item(int index) {
        AnyVector& v = fetch_any_vector();
        index = adjusted_vector_index(index, v);
        if (index < 0 || index >= int(v.size())) {
            throw py::index_error("list index out of range");
        }
        return any_to_py(v[index]);
    }

    void set_item(int index, PyAny* pyAny) {
        AnyVector& v = fetch_any_vector();
        index = adjusted_vector_index(index, v);
        if (index < 0 || index >= int(v.size())) {
            throw py::index_error("list assignment index out of range");
        }
        std::swap(v[index], pyAny->a);
    }
    
    void insert(int index, PyAny* pyAny) {
        AnyVector& v = fetch_any_vector();
        index = adjusted_vector_index(index, v);

        if (size_t(index) >= v.size()) {
            v.emplace_back(std::move(pyAny->a));
        }
        else {
            v.insert(v.begin() + std::max(index, 0), std::move(pyAny->a));
        }
    }

    void del_item(int index) {
        AnyVector& v = fetch_any_vector();
        if (v.empty()) {
            throw py::index_error("list index out of range");
        }

        index = adjusted_vector_index(index, v);

        if (size_t(index) >= v.size()) {
            v.pop_back();
        }
        else {
            v.erase(v.begin() + std::max(index, 0));
        }
    }

    int len() {
        return int(fetch_any_vector().size());
    }

    Iterator* iter() {
        (void) fetch_any_vector();
        return new Iterator(*this);
    }

    AnyVector& fetch_any_vector() {
        if (!any_vector) {
            throw_array_was_deleted();
        }
        return *any_vector;
    }
};

