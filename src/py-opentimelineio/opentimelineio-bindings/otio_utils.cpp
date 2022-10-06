// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "otio_utils.h"
#include "otio_anyDictionary.h"
#include "otio_anyVector.h"
#include "opentimelineio/any.h"
#include "opentime/rationalTime.h"
#include "opentime/timeRange.h"
#include "opentime/timeTransform.h"
#include "opentimelineio/serializableObject.h"
#include "opentimelineio/safely_typed_any.h"
#include "opentimelineio/stringUtils.h"

#include <map>
#include <cstring>

namespace py = pybind11;

bool compare_typeids(std::type_info const& lhs, std::type_info const& rhs) {
    return lhs.name() == rhs.name() || !strcmp(lhs.name(), rhs.name());
}

static std::map<std::type_info const*, std::function<py::object (any const&, bool)>> _py_cast_dispatch_table;
static std::map<std::string, std::function<py::object (any const&, bool)>> _py_cast_dispatch_table_by_name;

py::object plain_string(std::string const& s) {
    #if PY_MAJOR_VERSION >= 3
        PyObject *p = PyUnicode_FromString(s.c_str());
    #else
        PyObject *p = PyString_FromString(s.c_str());
    #endif
    return py::reinterpret_steal<py::object>(p);
}

py::object plain_int(int i) {
    PyObject *p = PyLong_FromLong(i);
    return py::reinterpret_steal<py::object>(p);
}

py::object plain_int(int64_t i) {
    PyObject *p = PyLong_FromLongLong(i);
    return py::reinterpret_steal<py::object>(p);
}

py::object plain_uint(uint64_t i) {
    PyObject *p = PyLong_FromUnsignedLongLong(i);
    return py::reinterpret_steal<py::object>(p);
}

void _build_any_to_py_dispatch_table() {
    auto& t = _py_cast_dispatch_table;

    t[&typeid(void)] = [](any const& /* a */, bool) { return py::none(); };
    t[&typeid(bool)] = [](any const& a, bool) { return py::cast(safely_cast_bool_any(a)); };
    t[&typeid(int)] = [](any const& a, bool) {  return plain_int(safely_cast_int_any(a)); };
    t[&typeid(int64_t)] = [](any const& a, bool) {  return plain_int(safely_cast_int64_any(a)); };
    t[&typeid(uint64_t)] = [](any const& a, bool) {  return plain_uint(safely_cast_uint64_any(a)); };
    t[&typeid(double)] = [](any const& a, bool) { return py::cast(safely_cast_double_any(a)); };
    t[&typeid(std::string)] = [](any const& a, bool) { return py::cast(safely_cast_string_any(a)); };
    t[&typeid(RationalTime)] = [](any const& a, bool) { return py::cast(safely_cast_rational_time_any(a)); };
    t[&typeid(TimeRange)] = [](any const& a, bool) { return py::cast(safely_cast_time_range_any(a)); };
    t[&typeid(TimeTransform)] = [](any const& a, bool) { return py::cast(safely_cast_time_transform_any(a)); };
    t[&typeid(SerializableObject::Retainer<>)] = [](any const& a, bool) {
        SerializableObject* so = safely_cast_retainer_any(a);
        return py::cast(managing_ptr<SerializableObject>(so)); };
    t[&typeid(AnyDictionaryProxy*)] = [](any const& a, bool) { return py::cast(any_cast<AnyDictionaryProxy*>(a)); };
    t[&typeid(AnyVectorProxy*)] = [](any const& a, bool) { return py::cast(any_cast<AnyVectorProxy*>(a)); };

    t[&typeid(AnyDictionary)] = [](any const& a, bool top_level) {
        AnyDictionary& d = temp_safely_cast_any_dictionary_any(a);
        if (top_level) {
            auto proxy = new AnyDictionaryProxy;
            proxy->fetch_any_dictionary().swap(d);
            return py::cast(proxy);
        }
        else {
            return py::cast((AnyDictionaryProxy*)d.get_or_create_mutation_stamp());
        }
    };
    
    t[&typeid(AnyVector)] = [](any const& a, bool top_level) {
        AnyVector& v = temp_safely_cast_any_vector_any(a);
        if (top_level) {
            auto proxy = new AnyVectorProxy;
            proxy->fetch_any_vector().swap(v);
            return py::cast(proxy);
        }
        return py::cast((AnyVectorProxy*)v.get_or_create_mutation_stamp());
    };

    for (auto e: t) {
        _py_cast_dispatch_table_by_name[e.first->name()] = e.second;
    }
}

static py::object _value_to_any = py::none();

static void py_to_any(py::object const& o, any* result) {
    if (_value_to_any.is_none()) {
        py::object core = py::module::import("opentimelineio.core");
        _value_to_any = core.attr("_value_to_any");
    }

    result->swap(_value_to_any(o).cast<PyAny*>()->a);
}

any py_to_any2(py::handle const& o) {
    py::type pytype = py::type::of(o);
    if (o.ptr() == nullptr || o.is_none()) {
        return any(nullptr);
    }

    if (py::isinstance<py::bool_>(o)) {
        return any(o.cast<bool>());
    }

    if (py::isinstance<py::int_>(o)) {
        try {
            return any(o.cast<std::int32_t>());
        } catch (...) {}

        try {
            return any(o.cast<std::int64_t>());
        } catch (...) {}

        try {
            return any(o.cast<std::uint32_t>());
        } catch (...) {}

        try {
            return any(o.cast<std::uint64_t>());
        } catch (...) {}

        throw std::runtime_error("Failed to convert Python int to C++ int");
    }

    if (py::isinstance<py::float_>(o)) {
        return any(o.cast<double>());
    }

    if (py::isinstance<py::str>(o)) {
        return any(o.cast<std::string>());
    }

    // Convert AnyDictionaryProxy and dict before vector and sequence because
    // a dict is a sequence.
    if (py::isinstance<AnyDictionaryProxy>(o)) {
        py::print("Converting AnyDictionaryProxy");
        return any(o.cast<AnyDictionaryProxy>().fetch_any_dictionary());
    }

    if (py::isinstance<py::dict>(o)) {
        py::print("Converting py::dict");
        AnyDictionary d;

        py::dict pyd = o.cast<py::dict>();
        for (auto &it : pyd) {
            if (!py::isinstance<py::str>(it.first)) {
                throw py::value_error("Keys must be of type string, not " + py::cast<std::string>(py::type::of(it.first).attr("__name__")));
            }

            d[it.first.cast<std::string>()] = any(py_to_any2(it.second));
        }

        return any(d);
    }

    if (py::isinstance<AnyVectorProxy>(o)) {
        py::print("Converting AnyVectorProxy");
        return any(o.cast<AnyVectorProxy>().fetch_any_vector());
    }

    if (py::isinstance<py::sequence>(o)) {
        py::print("Converting py::sequence");
        AnyVector av;
        for (auto &it : o) {
            av.push_back(py_to_any2(it));
        }
        return any(av);
    }

    throw py::value_error("Unsupported value type: " + py::cast<std::string>(pytype.attr("__name__")));
}

AnyDictionary py_to_any_dictionary(py::object const& o) {
    if (o.is_none()) {
        return AnyDictionary();
    }

    any a;
    py_to_any(o, &a);
    if (!compare_typeids(a.type(), typeid(AnyDictionary))) {
        throw py::type_error(string_printf("Expected an AnyDictionary (i.e. metadata); got %s instead",
                                           type_name_for_error_message(a).c_str()));
    }

    return safely_cast_any_dictionary_any(a);
}

AnyDictionary pydict_to_any_dictionary(py::dict const& o) {
    if (o.is_none()) {
        return AnyDictionary();
    }

    any a;
    py_to_any(o, &a);
    if (!compare_typeids(a.type(), typeid(AnyDictionary))) {
        throw py::type_error(string_printf("Expected an AnyDictionary (i.e. metadata); got %s instead",
                                           type_name_for_error_message(a).c_str()));
    }

    return safely_cast_any_dictionary_any(a);
}

std::vector<SerializableObject*> py_to_so_vector(pybind11::object const& o) {
    if (_value_to_so_vector.is_none()) {
        py::object core = py::module::import("opentimelineio.core");
        _value_to_so_vector = core.attr("_value_to_so_vector");
    }

    std::vector<SerializableObject*> result;
    if (o.is_none()) {
        return result;
    }

    /*
     * We're depending on _value_to_so_vector(), written in Python, to
     * not screw up, or we're going to crash.  (1) It has to give us
     * back an AnyVector.  (2) Every element has to be a
     * SerializableObject::Retainer<>.
     */

    py::object obj_vector = _value_to_so_vector(o);     // need to retain this here or we'll lose the any...
    AnyVector const& v = temp_safely_cast_any_vector_any(obj_vector.cast<PyAny*>()->a);

    result.reserve(v.size());
    for (auto e: v) {
        result.push_back(safely_cast_retainer_any(e));
    }
    return result;
}

py::object any_to_py(any const& a, bool top_level) {
    std::type_info const& tInfo = a.type();
    auto e = _py_cast_dispatch_table.find(&tInfo);

    if (e == _py_cast_dispatch_table.end()) {
        auto backup_e = _py_cast_dispatch_table_by_name.find(tInfo.name());
        if (backup_e != _py_cast_dispatch_table_by_name.end()) {
            _py_cast_dispatch_table[&tInfo] = backup_e->second;
            e = _py_cast_dispatch_table.find(&tInfo);
        }
    }

    if (e == _py_cast_dispatch_table.end()) {
        throw py::value_error(string_printf("Unable to cast any of type %s to python object",
                                            type_name_for_error_message(tInfo).c_str()));
    }

    return e->second(a, top_level);
}

struct KeepaliveMonitor {
    SerializableObject* _so;
    pybind11::object _keep_alive;
    
    KeepaliveMonitor(SerializableObject* so)
        : _so(so) {
    }
    
    void monitor() {
        pybind11::gil_scoped_acquire acquire;
        if (_so->current_ref_count() > 1) {
            if (!_keep_alive) {
                _keep_alive = pybind11::cast(_so);
            }
        }
        else {
            if (_keep_alive) {
                _keep_alive = pybind11::object();      // this could cause destruction
            }
        }
    }
};

void install_external_keepalive_monitor(SerializableObject* so, bool apply_now) {
    KeepaliveMonitor m { so };
    using namespace std::placeholders;
    // printf("Install external keep alive for %p: apply now is %d\n", so, apply_now);
    so->install_external_keepalive_monitor(std::bind(&KeepaliveMonitor::monitor, m),
                                           apply_now);
}
