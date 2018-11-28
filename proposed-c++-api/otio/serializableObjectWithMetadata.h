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

    std::string const& name() const;
    void set_name(std::string const& name);

    AnyDictionary& metadata();
    AnyDictionary const& metadata() const;

protected:
    ~SerializableObjectWithMetadata();

    virtual bool read_from(Reader&);
    virtual void write_to(Writer&) const;

private:
    std::string _name;
    AnyDictionary _metadata;
};

#endif
