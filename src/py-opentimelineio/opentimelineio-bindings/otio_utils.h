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

namespace pybind11 { namespace detail {
    template<> struct type_caster<any> {
    public:
        /**
         * This macro establishes the name 'any' in
         * function signatures and declares a local variable
         * 'value' of type any
         */
        PYBIND11_TYPE_CASTER(AnyDictionary, const_name("Metadata[str, Union[bool, int, float, str, None, SerializableObject, RationalTime]]"));

        /**
         * Conversion part 1 (Python->C++): convert a PyObject into an any
         * instance or return false upon failure. The second argument
         * indicates whether implicit conversions should be applied.
         */
        bool load(handle src, bool) {
            // TODO: Use what's in SOWithMetadata and otio_utils::py_to_any2.
            // The idea is that we could simply use AnyDictionary as input parameters for
            // metadata and this load method here would take care of basically
            // taking the input and converting it to AnyDictionaryProxy? Or actually
            // here we wuld simply take a dict and return AnyDictionary.
            // Then in the cast method, it's where we would convert the AnyDictionary to
            // and AnyDictionaryProxy.

            // if (pybind11::isinstance<pybind11::bool_>(src)) {
            //     bool result = src.cast<bool>();
            //     value = create_safely_typed_any(std::move(result));
            //     return true;
            // }

            // if (pybind11::isinstance<pybind11::int_>(src)) {
            //     int64_t result = src.cast<int64_t>();
            //     value = create_safely_typed_any(std::move(result));
            //     return true;
            // }

            // if (pybind11::isinstance<pybind11::float_>(src)) {
            //     double result = src.cast<double>();
            //     value = create_safely_typed_any(std::move(result));
            //     return true;
            // }

            // if (pybind11::isinstance<std::string>(src)) {
            //     std::string result = src.cast<std::string>();
            //     value = create_safely_typed_any(std::move(result));
            //     return true;
            // }

            // if (src.is_none()) {
            //     value = any();
            //     return true;
            // }

            // if (pybind11::isinstance<SerializableObject*>(src)) {
            //     // ((SerializableObject*)src.ptr())
            //     // SerializableObject result = src.cast<SerializableObject>();
            //     value = create_safely_typed_any(((SerializableObject*)src.ptr()));
            //     return true;
            // }

            // if (pybind11::isinstance<RationalTime>(src)) {
            //     RationalTime result = src.cast<RationalTime>();
            //     value = create_safely_typed_any(std::move(result));
            //     return true;
            // }

            // if (pybind11::isinstance<TimeRange>(src)) {
            //     TimeRange result = src.cast<TimeRange>();
            //     value = create_safely_typed_any(std::move(result));
            //     return true;
            // }

            // if (pybind11::isinstance<TimeTransform>(src)) {
            //     TimeTransform result = src.cast<TimeTransform>();
            //     value = create_safely_typed_any(std::move(result));
            //     return true;
            // }

            // if (pybind11::isinstance<AnyVectorProxy*>(src)) {
            //     AnyVectorProxy* result = src.cast<AnyVectorProxy*>();
            //     value = create_safely_typed_any(std::move(result));
            //     return true;
            // }
            return false;
        }

        /**
         * Conversion part 2 (C++ -> Python): convert an any instance into
         * a Python object. The second and third arguments are used to
         * indicate the return value policy and parent object (for
         * ``return_value_policy::reference_internal``) and are generally
         * ignored by implicit casters.
         */
        static handle cast(any src, return_value_policy /* policy */, handle /* parent */) {
            if (compare_typeids(src.type(), typeid(bool))) {
                return pybind11::cast(safely_cast_bool_any(&src));
            }

            if (compare_typeids(src.type(), typeid(bool))) {
                return pybind11::cast(safely_cast_bool_any(&src));
            }
        }
    };
}}

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
any py_to_any2(pybind11::handle const& o);

bool py_to_any3(pybind11::bool_ const& o);
template<typename T>
T py_to_any3(pybind11::int_ const& o);
double py_to_any3(pybind11::float_ const& o);
std::string py_to_any3(pybind11::str const& o);
AnyDictionary py_to_any3(pybind11::dict const& o);
AnyVector py_to_any3(pybind11::iterable const& o);

AnyDictionary py_to_any_dictionary(pybind11::object const& o);
