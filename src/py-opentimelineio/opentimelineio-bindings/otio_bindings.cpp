#include <pybind11/pybind11.h>
#include "otio_anyDictionary.h"
#include "otio_anyVector.h"
#include "otio_bindings.h"
#include "otio_utils.h"
#include "otio_errorStatusHandler.h"
#include "opentimelineio/serialization.h"
#include "opentimelineio/deserialization.h"
#include "opentimelineio/serializableObject.h"
#include "opentimelineio/typeRegistry.h"
#include "opentimelineio/stackAlgorithm.h"

namespace py = pybind11;
using namespace pybind11::literals;

static void register_python_type(py::object class_object,
                                 std::string schema_name,
                                 int schema_version) {
    std::function<SerializableObject* ()> create =
        [class_object]() {
            py::gil_scoped_acquire acquire;

            py::object python_so = class_object();
            SerializableObject::Retainer<> r(py::cast<SerializableObject*>(python_so));

            // we need to dispose of the reference to python_so now,
            // while r exists to keep the object we just created alive.
            // (If we let python_so be destroyed when we leave the function,
            // then the C++ object we just created would be immediately
            // destroyed then.)

            python_so = py::object();
            return r.take_value();
    };

    TypeRegistry::instance().register_type(schema_name, schema_version,
                                           nullptr, create, schema_name);
}

static bool register_upgrade_function(std::string const& schema_name,
                                      int version_to_upgrade_to,
                                      py::object const& upgrade_function_obj) {
    std::function<void (AnyDictionary* d)> upgrade_function =  [upgrade_function_obj](AnyDictionary* d) {
        py::gil_scoped_acquire acquire;
        
        auto ptr = d->get_or_create_mutation_stamp();
        py::object dobj = py::cast((AnyDictionaryProxy*)ptr);
        upgrade_function_obj(dobj);
    };
    
    return TypeRegistry::instance().register_upgrade_function(schema_name, version_to_upgrade_to,
                                                             upgrade_function);
}

static void set_type_record(SerializableObject* so, std::string schema_name) {
    TypeRegistry::instance().set_type_record(so, schema_name, ErrorStatusHandler());
}

static SerializableObject* instance_from_schema(std::string schema_name,
                                                int schema_version, py::object data) {
    AnyDictionary object_data = py_to_any_dictionary(data);
    auto result = TypeRegistry::instance().instance_from_schema(schema_name, schema_version,
                                                         object_data, ErrorStatusHandler());
    return result;
}

PYBIND11_MODULE(_otio, m) {
    m.doc() = "Bindings to C++ OTIO implementation";
    otio_exception_bindings(m);
    otio_any_dictionary_bindings(m);
    otio_any_vector_bindings(m);
    otio_serializable_object_bindings(m);
    otio_tests_bindings(m);

    m.def("_serialize_json_to_string",
          [](PyAny* pyAny, int indent) {
              return serialize_json_to_string(pyAny->a, ErrorStatusHandler(), indent);
          }, "value"_a, "indent"_a)
     .def("_serialize_json_to_file",
          [](PyAny* pyAny, std::string filename, int indent) {
              return serialize_json_to_file(pyAny->a, filename, ErrorStatusHandler(), indent);
          }, "value"_a, "filename"_a, "indent"_a)
     .def("deserialize_json_from_string",
          [](std::string input) {
              any result;
              deserialize_json_from_string(input, &result, ErrorStatusHandler());
              return any_to_py(result, true /*top_level*/);
          }, "input"_a)
     .def("deserialize_json_from_file",
          [](std::string filename) {
              any result;
              deserialize_json_from_file(filename, &result, ErrorStatusHandler());
              return any_to_py(result, true /*top_level*/);
          }, "filename"_a);

    py::class_<PyAny>(m, "PyAny")
        .def(py::init([](bool b) { return new PyAny(b); }))
        .def(py::init([](int i) { return new PyAny(i); }))
        .def(py::init([](int64_t i) { return new PyAny(i); }))
        .def(py::init([](double d) { return new PyAny(d); }))
        .def(py::init([](std::string s) { return new PyAny(s); }))
        .def(py::init([](py::none) { return new PyAny(); }))
        .def(py::init([](SerializableObject* s) { return new PyAny(s); }))
        .def(py::init([](RationalTime rt) { return new PyAny(rt); }))
        .def(py::init([](TimeRange tr) { return new PyAny(tr); }))
        .def(py::init([](TimeTransform tt) { return new PyAny(tt); }))
        .def(py::init([](AnyVectorProxy* p) { return new PyAny(p->fetch_any_vector()); }))
        .def(py::init([](AnyDictionaryProxy* p) { return new PyAny(p->fetch_any_dictionary()); }));

    m.def("register_serializable_object_type", &register_python_type,
          "class_object"_a, "schema_name"_a, "schema_version"_a);
    m.def("set_type_record", &set_type_record, "serializable_obejct"_a, "schema_name"_a);
    m.def("install_external_keepalive_monitor", &install_external_keepalive_monitor,
          "so"_a, "apply_now"_a);
    m.def("instance_from_schema", &instance_from_schema,
          "schema_name"_a, "schema_version"_a, "data"_a);
    m.def("register_upgrade_function", &register_upgrade_function,
          "schema_name"_a,
          "version_to_upgrade_to"_a,
          "upgrade_function"_a);
    m.def("flatten_stack", [](Stack* s) {
            return flatten_stack(s, ErrorStatusHandler());
        }, "in_stack"_a);
    m.def("flatten_stack", [](py::object tracks) {
            return flatten_stack(py_to_vector<Track*>(tracks), ErrorStatusHandler());
        }, "tracks"_a);        

    void _build_any_to_py_dispatch_table();
    _build_any_to_py_dispatch_table();
}
