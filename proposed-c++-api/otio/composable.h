#ifndef OTIO_COMPOSABLE_H
#define OTIO_COMPOSABLE_H

#include "serializableObjectWithMetadata.h"

class Composition;

class Composable : public SerializableObjectWithMetadata {
public:
    struct Schema {
        static auto constexpr name = "Composable";
        static int constexpr version = 1;
    };

    using Parent = SerializableObjectWithMetadata;

    Composable(std::string const& name = std::string(),
               AnyDictionary const& metadata = AnyDictionary());

    virtual bool visible() const;
    virtual bool overlapping() const;

    Composition* parent() const;
    bool set_parent(Composition* parent);       // can fail

protected:
    virtual ~Composable();

    virtual bool read_from(Reader&);
    virtual void write_to(Writer&) const;

private:
    Composition* _parent;       // not serialized
};

#endif
