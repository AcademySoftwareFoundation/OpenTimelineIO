#pragma once
#include <pybind11/pybind11.h>
#include "opentimelineio/anyVector.h"
#include "opentimelineio/vectorIndexing.h"
#include "otio_bindings.h"
#include "otio_utils.h"

namespace py = pybind11;

struct AnyVectorProxy : public AnyVector::MutationStamp {
    using MutationStamp = AnyVector::MutationStamp;

    static void throw_array_was_deleted() {
        throw py::value_error("underlying C++ AnyVector object has been destroyed");
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
            throw py::index_error();
        }
        return any_to_py(v[index]);
    }

    void set_item(int index, PyAny* pyAny) {
        AnyVector& v = fetch_any_vector();
        index = adjusted_vector_index(index, v);
        if (index < 0 || index >= int(v.size())) {
            throw py::index_error();
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
            throw py::index_error();
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

