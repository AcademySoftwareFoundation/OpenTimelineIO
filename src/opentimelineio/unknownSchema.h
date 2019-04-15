#pragma once

#include "opentimelineio/version.h"
#include "opentimelineio/serializableObject.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {
    
class UnknownSchema : public SerializableObject {
public:
    struct Schema {
        static auto constexpr name = "UnknownSchema";
        static int constexpr version = 1;
    };

    UnknownSchema(std::string const& original_schema_name, int original_schema_version);

    std::string const& original_schema_name() const {
        return _original_schema_name;
    }
    
    int original_schema_version() const {
        return _original_schema_version;
    }

    virtual bool read_from(Reader&);
    virtual void write_to(Writer&) const;

    virtual bool is_unknown_schema() const;

private:
    virtual ~UnknownSchema();

    virtual std::string const& _schema_name_for_reference() const;

    std::string _original_schema_name;
    int _original_schema_version;

    AnyDictionary _data;
    
    friend class TypeRegistry;
    friend class SerializableObject::Writer;
};

} }
