#ifndef OTIO_SERIALIZABLE_COLLECTION_H
#define OTIO_SERIALIZABLE_COLLECTION_H

#include "serializableObjectWithMetadata.h"

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

    std::vector<Retainer<SerializableObject>> const& children() const;
    std::vector<Retainer<SerializableObject>>& children();

    // These exist to allow conformance to  Python/Swift collections/sequences
    // C++ APIs can directly mutate the non-const return value of children().

    void set_children(std::vector<SerializableObject*> const& children);
    void clear_children();
    void insert_child(int index, SerializableObject* child);
    bool set_child(int index, SerializableObject* child, std::string* err_msg = nullptr);
    bool remove_child(int index, std::string* err_msg = nullptr);

protected:
    virtual ~SerializableCollection();

    virtual bool read_from(Reader&);
    virtual void write_to(Writer&) const;

private:
    std::vector<Retainer<SerializableObject>> _children;
};

#endif
