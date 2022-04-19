#include "opentimelineio/multiMediaReference.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

MultiMediaReference::MultiMediaReference(
    std::string const& name, AnyDictionary const& metadata)
    : Parent(name, metadata)
{}

bool
MultiMediaReference::read_from(Reader& reader)
{
    return reader.read_if_present("available_range", &_available_range) &&
           Parent::read_from(reader);
}

void
MultiMediaReference::write_to(Writer& writer) const
{
    Parent::write_to(writer);
    writer.write("available_range", _available_range);
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
