// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "otio_utils.h"
#include "otio_anyDictionary.h"
#include "otio_anyVector.h"
#include "opentime/rationalTime.h"
#include "opentime/timeRange.h"
#include "opentime/timeTransform.h"
#include "opentimelineio/serializableObject.h"
#include "opentimelineio/safely_typed_any.h"
#include "opentimelineio/stringUtils.h"

#include <Imath/ImathBox.h>

#include <map>
#include <cstring>

namespace py = pybind11;

bool compare_typeids(std::type_info const& lhs, std::type_info const& rhs) {
    return lhs.name() == rhs.name() || !strcmp(lhs.name(), rhs.name());
}

static std::map<std::type_info const*, std::function<py::object (std::any const&, bool)>> _py_cast_dispatch_table;
static std::map<std::string, std::function<py::object (std::any const&, bool)>> _py_cast_dispatch_table_by_name;

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

    t[&typeid(void)] = [](std::any const& /* a */, bool) { return py::none(); };
    t[&typeid(bool)] = [](std::any const& a, bool) { return py::cast(safely_cast_bool_any(a)); };
    t[&typeid(int)] = [](std::any const& a, bool) {  return plain_int(safely_cast_int_any(a)); };
    t[&typeid(int64_t)] = [](std::any const& a, bool) {  return plain_int(safely_cast_int64_any(a)); };
    t[&typeid(uint64_t)] = [](std::any const& a, bool) {  return plain_uint(safely_cast_uint64_any(a)); };
    t[&typeid(double)] = [](std::any const& a, bool) { return py::cast(safely_cast_double_any(a)); };
    t[&typeid(std::string)] = [](std::any const& a, bool) { return py::cast(safely_cast_string_any(a)); };
    t[&typeid(RationalTime)] = [](std::any const& a, bool) { return py::cast(safely_cast_rational_time_any(a)); };
    t[&typeid(TimeRange)] = [](std::any const& a, bool) { return py::cast(safely_cast_time_range_any(a)); };
    t[&typeid(TimeTransform)] = [](std::any const& a, bool) { return py::cast(safely_cast_time_transform_any(a)); };
    t[&typeid(IMATH_NAMESPACE::V2d)] = [](std::any const& a, bool) { return py::cast(safely_cast_point_any(a)); };
    t[&typeid(IMATH_NAMESPACE::Box2d)] = [](std::any const& a, bool) { return py::cast(safely_cast_box_any(a)); };
    t[&typeid(SerializableObject::Retainer<>)] = [](std::any const& a, bool) {
        SerializableObject* so = safely_cast_retainer_any(a);
        return py::cast(managing_ptr<SerializableObject>(so)); };
    t[&typeid(AnyDictionaryProxy*)] = [](std::any const& a, bool) { return py::cast(std::any_cast<AnyDictionaryProxy*>(a)); };
    t[&typeid(AnyVectorProxy*)] = [](std::any const& a, bool) { return py::cast(std::any_cast<AnyVectorProxy*>(a)); };

    t[&typeid(AnyDictionary)] = [](std::any const& a, bool top_level) {
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
    
    t[&typeid(AnyVector)] = [](std::any const& a, bool top_level) {
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

static void py_to_any(py::object const& o, std::any* result) {
    if (_value_to_any.is_none()) {
        py::object core = py::module::import("opentimelineio.core");
        _value_to_any = core.attr("_value_to_any");
    }

    result->swap(_value_to_any(o).cast<PyAny*>()->a);
}

AnyDictionary py_to_any_dictionary(py::object const& o) {
    if (o.is_none()) {
        return AnyDictionary();
    }

    std::any a;
    py_to_any(o, &a);
    if (!compare_typeids(a.type(), typeid(AnyDictionary))) {
        throw py::type_error(string_printf("Expected an AnyDictionary (i.e. metadata); got %s instead",
                                           type_name_for_error_message(a).c_str()));
    }

    return safely_cast_any_dictionary_any(a);
}

py::object any_to_py(std::any const& a, bool top_level) {
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
