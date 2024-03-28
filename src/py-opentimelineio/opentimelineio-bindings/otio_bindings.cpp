// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
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

// temporarily disabling this feature while I chew on it
const static bool EXCEPTION_ON_DOUBLE_REGISTER = false;

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


    // @TODO: further discussion required about preventing double registering
#if 0
    if (
            !TypeRegistry::instance().register_type(
                schema_name,
                schema_version,
                nullptr,
                create,
                schema_name
            )
            && EXCEPTION_ON_DOUBLE_REGISTER
    ) {
        auto err = ErrorStatusHandler();
        err.error_status = ErrorStatus(
                ErrorStatus::INTERNAL_ERROR,
                "Schema: " + schema_name + " has already been registered."
        );
    }
#else
    TypeRegistry::instance().register_type(
            schema_name,
            schema_version,
            nullptr,
            create,
            schema_name
    );
#endif
}

static bool register_upgrade_function(std::string const& schema_name,
                                      int version_to_upgrade_to,
                                      std::function<void(AnyDictionaryProxy*)> const& upgrade_function_obj) {
    std::function<void (AnyDictionary* d)> upgrade_function =  [upgrade_function_obj](AnyDictionary* d) {
        py::gil_scoped_acquire acquire;
        
        auto ptr = d->get_or_create_mutation_stamp();
        upgrade_function_obj((AnyDictionaryProxy*)ptr);
    };
    
    // further discussion required about preventing double registering
#if 0
    if (
            !TypeRegistry::instance().register_upgrade_function(
                schema_name,
                version_to_upgrade_to,
                upgrade_function
            ) //&& EXCEPTION_ON_DOUBLE_REGISTER
    )
    {
        auto err = ErrorStatusHandler();
        err.error_status = ErrorStatus(
                ErrorStatus::INTERNAL_ERROR,
                "Upgrade function already exists for " + schema_name
        );
        return false;
    }

    return true;
#else
    return TypeRegistry::instance().register_upgrade_function(
            schema_name,
            version_to_upgrade_to,
            upgrade_function
    );
#endif
}

static bool 
register_downgrade_function(
        std::string const& schema_name,
        int version_to_downgrade_from,
        std::function<void(AnyDictionaryProxy*)> const& downgrade_function_obj)
{
    std::function<void (AnyDictionary* d)> downgrade_function = ( 
            [downgrade_function_obj](AnyDictionary* d) 
            {
                py::gil_scoped_acquire acquire;

                auto ptr = d->get_or_create_mutation_stamp();
                downgrade_function_obj((AnyDictionaryProxy*)ptr);
            }
    );

    // further discussion required about preventing double registering
#if 0
    if (
            !TypeRegistry::instance().register_downgrade_function(
                schema_name,
                version_to_downgrade_from,
                downgrade_function
            ) //&& EXCEPTION_ON_DOUBLE_REGISTER
    )
    {
        auto err = ErrorStatusHandler();
        err.error_status = ErrorStatus(
                ErrorStatus::INTERNAL_ERROR,
                "Downgrade function already exists for " + schema_name
        );
        return false;
    }
    return true;
#else
    return TypeRegistry::instance().register_downgrade_function(
            schema_name,
            version_to_downgrade_from,
            downgrade_function
    ) ;
#endif
    
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
    // Import _opentime before actually creating the bindings
    // for _otio. This allows the import of _otio without
    // manually importing _opentime before. For example: python -c 'import opentimelineio._otio'
    py::module_::import("opentimelineio._opentime");

    m.doc() = "Bindings to C++ OTIO implementation";

    otio_exception_bindings(m);
    otio_any_dictionary_bindings(m);
    otio_any_vector_bindings(m);
    otio_imath_bindings(m);
    otio_serializable_object_bindings(m);
    otio_tests_bindings(m);

    m.def(
            "_serialize_json_to_string",
            [](
                PyAny* pyAny,
                const schema_version_map& schema_version_targets,
                int indent
              ) 
            {
                auto result = serialize_json_to_string(
                        pyAny->a,
                        &schema_version_targets,
                        ErrorStatusHandler(),
                        indent
                );

                return result;
            },
            "value"_a,
            "schema_version_targets"_a,
            "indent"_a
    )
     .def("_serialize_json_to_file",
          [](
              PyAny* pyAny,
              std::string filename,
              const schema_version_map& schema_version_targets,
              int indent
          ) {
              return serialize_json_to_file(
                      pyAny->a,
                      filename,
                      &schema_version_targets,
                      ErrorStatusHandler(),
                      indent
              );
          },
          "value"_a,
          "filename"_a,
          "schema_version_targets"_a,
          "indent"_a)
     .def("deserialize_json_from_string",
          [](std::string input) {
              std::any result;
              deserialize_json_from_string(input, &result, ErrorStatusHandler());
              return any_to_py(result, true /*top_level*/);
          }, "input"_a,
          R"docstring(Deserialize json string to in-memory objects.

:param str input: json string to deserialize

:returns: root object in the string (usually a Timeline or SerializableCollection)
:rtype: SerializableObject

)docstring")
     .def("deserialize_json_from_file",
          [](std::string filename) {
              std::any result;
              deserialize_json_from_file(filename, &result, ErrorStatusHandler());
              return any_to_py(result, true /*top_level*/);
          }, 
          "filename"_a,
          R"docstring(Deserialize json file to in-memory objects.

:param str filename: path to json file to read

:returns: root object in the file (usually a Timeline or SerializableCollection)
:rtype: SerializableObject

)docstring");

    py::class_<PyAny>(m, "PyAny")
        // explicitly map python bool, int and double classes so that they
        // do NOT accidentally cast in valid values
        .def(py::init([](py::bool_ b) { 
                    bool result = b.cast<bool>();
                    return new PyAny(result); 
                    }))
        .def(py::init([](py::int_ i) { 
                    int64_t result = i.cast<int64_t>();
                    return new PyAny(result); 
                    }))
        .def(py::init([](py::float_ d) { 
                    double result = d.cast<double>();
                    return new PyAny(result); 
                    }))
        .def(py::init([](std::string s) { return new PyAny(s); }))
        .def(py::init([](py::none) { return new PyAny(); }))
        .def(py::init([](SerializableObject* s) { return new PyAny(s); }))
        .def(py::init([](RationalTime rt) { return new PyAny(rt); }))
        .def(py::init([](TimeRange tr) { return new PyAny(tr); }))
        .def(py::init([](TimeTransform tt) { return new PyAny(tt); }))
        .def(py::init([](AnyVectorProxy* p) { return new PyAny(p->fetch_any_vector()); }))
        .def(py::init([](AnyDictionaryProxy* p) { return new PyAny(p->fetch_any_dictionary()); }))
        ;

    m.def("register_serializable_object_type", &register_python_type,
          "class_object"_a, "schema_name"_a, "schema_version"_a);
    m.def("set_type_record", &set_type_record, "serializable_obejct"_a, "schema_name"_a);
    m.def("install_external_keepalive_monitor", &install_external_keepalive_monitor,
          "so"_a, "apply_now"_a);
    m.def("instance_from_schema", &instance_from_schema,
          "schema_name"_a, "schema_version"_a, "data"_a, R"docstring(
Return an instance of the schema from data in the data_dict.

:raises UnsupportedSchemaError: when the requested schema version is greater than the registered schema version.
)docstring");
    m.def("type_version_map",
             []() {
                schema_version_map tmp;
                TypeRegistry::instance().type_version_map(tmp);
                return tmp;
             },
             R"docstring(Fetch the currently registered schemas and their versions.

:returns: Map of all registered schema names to their current versions.
:rtype: dict[str, int])docstring"
    );
    m.def("register_upgrade_function", &register_upgrade_function,
          "schema_name"_a,
          "version_to_upgrade_to"_a,
          "upgrade_function"_a);
    m.def("register_downgrade_function", &register_downgrade_function,
          "schema_name"_a,
          "version_to_downgrade_from"_a,
          "downgrade_function"_a);
    m.def(
            "release_to_schema_version_map",
            [](){ return label_to_schema_version_map(CORE_VERSION_MAP);},
            R"docstring(Fetch the compiled in CORE_VERSION_MAP.  

The CORE_VERSION_MAP maps OTIO release versions to maps of schema name to schema version and is autogenerated by the OpenTimelineIO build and release system.  For example: `{"0.15.0": {"Clip": 2, ...}}`

:returns: dictionary mapping core version label to schema_version_map
:rtype: dict[str, dict[str, int]])docstring" 
    );
    m.def("flatten_stack", [](Stack* s) {
            return flatten_stack(s, ErrorStatusHandler());
        }, "in_stack"_a);
    m.def("flatten_stack", [](std::vector<Track*> tracks) {
            return flatten_stack(tracks, ErrorStatusHandler());
        }, "tracks"_a);        

    void _build_any_to_py_dispatch_table();
    _build_any_to_py_dispatch_table();
}
