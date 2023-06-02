// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <string>
#include "py-opentimelineio/bindings-common/casters.h"
#include "opentimelineio/any.h"
#include "opentimelineio/stringUtils.h"
#include "opentimelineio/serializableObject.h"
#include "opentimelineio/vectorIndexing.h"
#include "opentimelineio/safely_typed_any.h"

using namespace opentimelineio::OPENTIMELINEIO_VERSION;

void install_external_keepalive_monitor(SerializableObject* so, bool apply_now);

bool compare_typeids(std::type_info const& lhs, std::type_info const& rhs);

template <typename T>
struct managing_ptr {
    managing_ptr(T* ptr)
             : _retainer(ptr) {
        install_external_keepalive_monitor(ptr, false);
    }

    T* get() const {
        return _retainer.value;
    }
    
    SerializableObject::Retainer<> _retainer;
};
PYBIND11_DECLARE_HOLDER_TYPE(T, managing_ptr<T>);

template <typename V, typename VALUE_TYPE = typename V::value_type>
struct MutableSequencePyAPI : public V {
    class Iterator {
    public:
        Iterator(V& v)
            : _v(v),
              _it(0) {
        }
            
        Iterator* iter() {
            return this;
        }
        
        VALUE_TYPE next() {
            if (_it == _v.size()) {
                throw pybind11::stop_iteration();
            }

            return _v[_it++];
        }

    private:
        V& _v;
        size_t _it;
    };

    VALUE_TYPE get_item(int index) {
        V& v = static_cast<V&>(*this);
        index = adjusted_vector_index(index, v);
        if (index < 0 || index >= int(v.size())) {
            throw pybind11::index_error();
        }
        return v[index];
    }

    void set_item(int index, VALUE_TYPE value) {
        V& v = static_cast<V&>(*this);
        index = adjusted_vector_index(index, v);
        if (index < 0 || index >= int(v.size())) {
            throw pybind11::index_error();
        }
        v[index] = value;
    }
    
    void insert(int index, VALUE_TYPE value) {
        V& v = static_cast<V&>(*this);
        index = adjusted_vector_index(index, v);

        if (size_t(index) >= v.size()) {
            v.emplace_back(std::move(value));
        }
        else {
            v.insert(v.begin() + std::max(index, 0), std::move(value));
        }
    }

    void del_item(int index) {
        V& v = static_cast<V&>(*this);
        if (v.empty()) {
            throw pybind11::index_error();
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
        return static_cast<int>(this->size());
    }

    Iterator* iter() {
        return new Iterator(static_cast<V&>(*this));

    }

    static void define_py_class(pybind11::module m, std::string name) {
        typedef MutableSequencePyAPI This;
        using namespace pybind11::literals;

        pybind11::class_<This::Iterator>(m, (name + "Iterator").c_str())
            .def("__iter__", &This::Iterator::iter)
            .def("__next__", &This::Iterator::next);

        pybind11::class_<This>(m, name.c_str())
            .def(pybind11::init<>())
            .def("__internal_getitem__", &This::get_item, "index"_a)
            .def("__internal_setitem__", &This::set_item, "index"_a, "item"_a.none(false))
            .def("__internal_delitem__", &This::del_item, "index"_a)
            .def("__len__", &This::len)
            .def("__internal_insert", &This::insert, "index"_a, "item"_a.none(false))
            .def("__iter__", &This::iter, pybind11::return_value_policy::reference_internal);
    }
};

struct PyAny {
    PyAny() {
    }
    
    template <typename T>
    PyAny(T& value)
        : a(create_safely_typed_any(std::move(value))) {
    }

    PyAny(SerializableObject* value)
        : a(create_safely_typed_any(value)) {
    }

    any a;
};

pybind11::object any_to_py(any const& a, bool top_level = false);
pybind11::object plain_string(std::string const& s);
pybind11::object plain_int(int i);
any py_to_any(pybind11::handle const& o);

bool py_to_cpp(pybind11::bool_ const& o);
template<typename T>
T py_to_cpp(pybind11::int_ const& o);
double py_to_cpp(pybind11::float_ const& o);
std::string py_to_cpp(pybind11::str const& o);
AnyDictionary py_to_cpp(pybind11::dict const& o);
AnyVector py_to_cpp(pybind11::iterable const& o);
template<typename T>
T py_to_cpp(pybind11::handle const& o);
