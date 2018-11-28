#ifndef OTIO_SERIALIZABLEOBJECTWITHMETADATA_H
#define OTIO_SERIALIZABLEOBJECTWITHMETADATA_H

#include "serializableObject.h"
    
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

    virtual std::string debug_description() { return string_printf("SerializableObjectWM named %s at %p (schema %s)",
                                                                   _name.c_str(), this,
                                                                   schema_name().c_str()); }

protected:
    ~SerializableObjectWithMetadata();

    virtual bool read_from(Reader&);
    virtual void write_to(Writer&) const;

private:
    std::string _name;
    AnyDictionary _metadata;
};

#endif
