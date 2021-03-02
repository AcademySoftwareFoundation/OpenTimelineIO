#include "opentimelineio/bounds.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {

Bounds::Bounds(std::string const& name,
               optional<Imath::Box2d> const& box,
               AnyDictionary const& metadata)
    : Parent(name, metadata),
      _box( box ) {
}

bool Bounds::read_from(Reader& reader) {
    return reader.read("box", &_box) &&
           Parent::read_from(reader);
}

void Bounds::write_to(Writer& writer) const {
    Parent::write_to(writer);
    writer.write("box", _box);
}

} }
