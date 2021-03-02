#pragma once

#include "opentimelineio/serializableObjectWithMetadata.h"
#include <ImathBox.h>

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {

class Bounds : public SerializableObjectWithMetadata {
public:
    struct Schema {
       static auto constexpr name = "Bounds";
       static int constexpr version = 1;
    };

    using Parent = SerializableObjectWithMetadata;

    explicit Bounds(std::string const& name = std::string(),
                    optional<Imath::Box2d> const& box = nullopt,
                    AnyDictionary const& metadata = AnyDictionary());

    optional<Imath::Box2d> const& box() const {
        return _box;
    }

    void set_box(optional<Imath::Box2d> const & box) {
        _box = box;
    }

protected:
    virtual ~Bounds() = default;

    virtual bool read_from(Reader&);
    virtual void write_to(Writer&) const;

private:
    optional<Imath::Box2d> _box;
};

} }

