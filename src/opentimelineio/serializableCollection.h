#pragma once

#include "opentimelineio/version.h"
#include "opentimelineio/serializableObjectWithMetadata.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {
    
class SerializableCollection : public SerializableObjectWithMetadata {
public:
    struct Schema {
        static auto constexpr name = "SerializableCollection";
        static int constexpr version = 1;
    };

    using Parent = SerializableObjectWithMetadata;

    SerializableCollection(std::string const& name = std::string(),
                           std::vector<SerializableObject*> children = std::vector<SerializableObject*>(),
                           AnyDictionary const& metadata = AnyDictionary());

    std::vector<Retainer<SerializableObject>> const& children() const {
        return _children;
    }

    std::vector<Retainer<SerializableObject>>& children() {
        return _children;
    }

    void set_children(std::vector<SerializableObject*> const& children);

    void clear_children();
    
    void insert_child(int index, SerializableObject* child);

    bool set_child(int index, SerializableObject* child, ErrorStatus* error_status);

    bool remove_child(int index, ErrorStatus* error_status);

protected:
    virtual ~SerializableCollection();

    virtual bool read_from(Reader&);
    virtual void write_to(Writer&) const;

private:
    std::vector<Retainer<SerializableObject>> _children;
};

} }
