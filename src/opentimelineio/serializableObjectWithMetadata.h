#pragma once

#include "opentimelineio/version.h"
#include "opentimelineio/serializableObject.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {
    
class SerializableObjectWithMetadata : public SerializableObject {
public:
    struct Schema {
        static auto constexpr name = "SerializableObjectWithMetadata";
        static int constexpr version = 1;
    };

    using Parent = SerializableObject;

    SerializableObjectWithMetadata(std::string const& name = std::string(),
                                   AnyDictionary const& metadata = AnyDictionary());

    std::string const& name() const {
        return _name;
    }

    void set_name(std::string const& name) {
        _name = name;
    }

    AnyDictionary& metadata() {
        return _metadata;
    }

    AnyDictionary const& metadata() const {
        return _metadata;
    }

protected:
    ~SerializableObjectWithMetadata();
    virtual bool read_from(Reader&);
    virtual void write_to(Writer&) const;

private:
    std::string _name;
    AnyDictionary _metadata;
};

} }
