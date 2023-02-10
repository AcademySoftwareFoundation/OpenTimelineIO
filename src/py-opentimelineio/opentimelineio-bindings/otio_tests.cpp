// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include <pybind11/pybind11.h>
#include <pybind11/operators.h>

#include "opentimelineio/serializableObject.h"
#include "opentimelineio/serializableObjectWithMetadata.h"
#include "opentimelineio/serializableCollection.h"
#include "opentimelineio/timeline.h"
#include "otio_utils.h"
#include "otio_anyDictionary.h"
#include "otio_anyVector.h"

namespace py = pybind11;
using namespace pybind11::literals;

class TestObject : public SerializableObjectWithMetadata {
public:
    struct Schema {
        static auto constexpr name = "Test";
        static int constexpr version = 1;
    };

    using Parent = SerializableObjectWithMetadata;
    
    TestObject(std::string const& name = "")
        : SerializableObjectWithMetadata(name)
    {
        printf("Created test object named '%s' at %p\n", name.c_str(), this);
    }

    SerializableObject* lookup(std::string key) {
        std::any a = metadata()[key];
        if (a.type() == typeid(Retainer<>)) {
            return std::any_cast<Retainer<>>(a).value;
        }
        return nullptr;
    }

    bool read_from(Reader& reader) {
        return Parent::read_from(reader);
    }
    
    void write_to(Writer& writer) const {
        Parent::write_to(writer);
    }

    void add_key(std::string key, int value) {
        metadata()[key] = value;
    }
    
    std::string repr() const {
        return string_printf("<TestObject named '%s' at id %p>", name().c_str(), this);
    }
    
private:
    ~TestObject() {
        printf("Test object '%s' at %p being destroyed\n", name().c_str(), this);
    }
};

static void test_takeme(SerializableObject* so) {
    SerializableObject::Retainer<> r(so);
}

static int test_bash_retainers1(SerializableCollection* sc) {
    py::gil_scoped_release release;
    SerializableObject* so = sc->children()[0];

    int total = 0;
    for (size_t i = 0; i < 1024 * 10; i++) {
        SerializableObject::Retainer<> r(so);
        if (r.value) {
            total++;
        }
    }
    
    return total;
}

py::object test_bash_retainers2(SerializableCollection* sc, py::object materialize_obj) {
    SerializableObject* so = sc->children()[0];
    int total = 0;

    {
        py::gil_scoped_release release;

        for (size_t i = 0; i < 1024 * 10; i++) {
            SerializableObject::Retainer<> r(so);
            if (r.value) {
                total++;
            }
        }
    }

    materialize_obj();

    {
        py::gil_scoped_release release;
        for (size_t i = 0; i < 1024 * 10; i++) {
            SerializableObject::Retainer<> r(so);
            if (r.value) {
                total++;
            }
        }
    }

    return total > 0 ? py::cast(so) : py::none();
}

void test_gil_scoping() {
    {
        { py::gil_scoped_release release; }
        { py::gil_scoped_acquire acquire; }
    }

    {
        { py::gil_scoped_acquire acquire; }
        { py::gil_scoped_release release; }
    }

    {
        py::gil_scoped_acquire acquire;
        py::gil_scoped_release release;
    }

    {
        py::gil_scoped_release release;
        py::gil_scoped_acquire acquire;
    }
}

void otio_xyzzy(std::string msg) {
    printf("XYZZY: %s\n", msg.c_str());
    /* used as a debugger breakpoint */
}

/// test the behavior of big integers in OTIO
bool test_big_uint() {
    int64_t some_int = 4;
    uint64_t number_base = INT64_MAX;
    uint64_t giant_number = number_base + some_int;

    SerializableObjectWithMetadata* so = new SerializableObjectWithMetadata();

    so->metadata()["giant_number"] = giant_number;

    bool result = true;

    if (std::any_cast<uint64_t>(so->metadata()["giant_number"]) != giant_number) {
        return false;
    }

    so->possibly_delete();
    return true;
}


void test_AnyDictionary_destroy(AnyDictionaryProxy* d) {
    delete d->any_dictionary;
}

void test_AnyVector_destroy(AnyVectorProxy* v) {
    delete v->any_vector;
}

void otio_tests_bindings(py::module m) {
    TypeRegistry& r = TypeRegistry::instance();
    r.register_type<TestObject>();
    
    py::class_<TestObject, SerializableObjectWithMetadata,
               managing_ptr<TestObject>>(m, "TestObject", py::dynamic_attr())
        .def(py::init<std::string>(), "name"_a)
        .def("lookup", &TestObject::lookup, "key"_a)
        .def("__repr__", &TestObject::repr);

    py::module test = m.def_submodule("_testing", "Module for OTIO regression testing");
    test.def("takeme", &test_takeme);
    test.def("bash_retainers1", &test_bash_retainers1);
    test.def("bash_retainers2", &test_bash_retainers2);
    test.def("gil_scoping", &test_gil_scoping);
    test.def("xyzzy", &otio_xyzzy);
    test.def("test_big_uint", &test_big_uint);
    test.def("test_AnyDictionary_destroy", &test_AnyDictionary_destroy);
    test.def("test_AnyVector_destroy", &test_AnyVector_destroy);
}
