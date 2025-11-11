// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/serializableObject.h"
#include "opentimelineio/typeRegistry.h"
#include <stdint.h>

// demonstrates a minimal custom SerializableObject written in C++ with upgrade
// and downgrade functions

namespace otio = opentimelineio::OPENTIMELINEIO_VERSION_NS;

// define the custom class
class SimpleClass : public otio::SerializableObject
{
public:
    struct Schema
    {
        static auto constexpr name   = "SimpleClass";
        static int constexpr version = 2;
    };

    void set_new_field(int64_t val) { _new_field = val; }
    int64_t new_field() const { return _new_field; }

protected:
    using Parent = SerializableObject;

    virtual ~SimpleClass() = default;

    // methods for serialization
    virtual bool 
    read_from(Reader& reader) override
    {
        auto result = (
            reader.read("new_field", &_new_field) 
            && Parent::read_from(reader)
        );

        return result;
    }

    // ...and deserialization
    virtual void 
    write_to(Writer& writer) const override
    {
        Parent::write_to(writer);
        writer.write("new_field", _new_field);
    }

private:
    int64_t _new_field;
};

int
main(
        int argc,
        char *argv[]
)
{
    // register type and upgrade/downgrade functions
    otio::TypeRegistry::instance().register_type<SimpleClass>();

    // 1->2
    otio::TypeRegistry::instance().register_upgrade_function(
        SimpleClass::Schema::name,
        2,
        [](otio::AnyDictionary* d)
        {
            (*d)["new_field"] = (*d)["my_field"];
            d->erase("my_field");
        }
    );
    // 2->1
    otio::TypeRegistry::instance().register_downgrade_function(
        SimpleClass::Schema::name,
        2,
        [](otio::AnyDictionary* d)
        {
            (*d)["my_field"] = (*d)["new_field"];
            d->erase("new_field");
        }
    );

    otio::ErrorStatus err;

    auto sc = otio::SerializableObject::Retainer<SimpleClass>(new SimpleClass());
    sc->set_new_field(12);

    // write it out to disk, without changing it
    sc->to_json_file("/var/tmp/simpleclass.otio", &err);

    otio::schema_version_map downgrade_manifest = {
        {"SimpleClass", 1}
    };

    // write it out to disk, downgrading to version 1
    sc->to_json_file("/var/tmp/simpleclass.otio", &err, &downgrade_manifest);

    // read it back, upgrading automatically back up to version 2 of the schema
    otio::SerializableObject::Retainer<SimpleClass> sc2(
            dynamic_cast<SimpleClass*>(
                SimpleClass::from_json_file("/var/tmp/simpleclass.otio", &err)
            )
    );

    assert(sc2->new_field() == sc->new_field());

    std::cout << "Upgrade/Downgrade demo complete." << std::endl;

    return 0;
}
