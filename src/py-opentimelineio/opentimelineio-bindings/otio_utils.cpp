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
    t[&typeid(nullptr)] = [](any const& /* a */, bool) { return py::none(); };
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

any py_to_any(py::handle const& o) {
    if (o.ptr() == nullptr || o.is_none()) {
        return any(nullptr);
    }

    if (py::isinstance<py::bool_>(o)) {
        return any(py_to_cpp(py::cast<py::bool_>(o)));
    }

    if (py::isinstance<py::int_>(o)) {
        try {
            return any(py_to_cpp<std::int32_t>(py::cast<py::int_>(o)));
        } catch (...) {}

        try {
            return any(py_to_cpp<std::int64_t>(py::cast<py::int_>(o)));
        } catch (...) {}

        try {
            return any(py_to_cpp<std::uint32_t>(py::cast<py::int_>(o)));
        } catch (...) {}

        try {
            return any(py_to_cpp<std::uint64_t>(py::cast<py::int_>(o)));
        } catch (...) {}

        throw py::type_error("Failed to convert Python int to C++ int");
    }

    if (py::isinstance<py::float_>(o)) {
        return any(py_to_cpp(py::cast<py::float_>(o)));
    }

    if (py::isinstance<py::str>(o)) {
        return any(py_to_cpp(py::cast<py::str>(o)));
    }

    // Convert AnyDictionaryProxy and dict before vector and sequence because
    // a dict is a sequence.
    if (py::isinstance<AnyDictionaryProxy>(o)) {
        return any(o.cast<AnyDictionaryProxy>().fetch_any_dictionary());
    }

    if (py::isinstance<py::dict>(o)) {
        return any(py_to_cpp(py::cast<py::dict>(o)));
    }

    if (py::isinstance<AnyVectorProxy>(o)) {
        return any(o.cast<AnyVectorProxy>().fetch_any_vector());
    }

    if (py::isinstance<py::sequence>(o)) {
        return any(py_to_cpp(py::cast<py::iterable>(o)));
    }

    if (py::isinstance<RationalTime>(o)) {
        return any(py_to_cpp<RationalTime>(o));
    }

    if (py::isinstance<TimeRange>(o)) {
        return any(py_to_cpp<TimeRange>(o));
    }

    if (py::isinstance<TimeTransform>(o)) {
        return any(py_to_cpp<TimeTransform>(o));
    }

    py::type pytype = py::type::of(o);
    throw py::type_error("Unsupported value type: " + py::cast<std::string>(pytype.attr("__name__")));
}

bool py_to_cpp(py::bool_ const& o) {
    return o.cast<bool>();
}

template<typename T>
T py_to_cpp(py::int_ const& o) {
    return o.cast<T>();
}

double py_to_cpp(py::float_ const& o) {
    return o.cast<double>();
}

std::string py_to_cpp(py::str const& o) {
    return o.cast<std::string>();
}

AnyDictionary py_to_cpp(py::dict const& o) {
    AnyDictionary d = AnyDictionary();

    for (auto &it : o) {
        if (!py::isinstance<py::str>(it.first)) {
            throw py::value_error("Keys must be of type string, not " + py::cast<std::string>(py::type::of(it.first).attr("__name__")));
        }

        // Note that storing an any is expected, since AnyDictionary values
        // can only be of type any.
        d[it.first.cast<std::string>()] = py_to_any(it.second);
    }

    return d;
}

AnyVector py_to_cpp(py::iterable const& o) {
    AnyVector av = AnyVector();
    for (auto &it : o) {
        av.push_back(py_to_any(it));
    }
    return av;
}

template<typename T>
T py_to_cpp(py::handle const& o) {
    return o.cast<T>();
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
