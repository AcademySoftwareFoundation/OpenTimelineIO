#include "opentimelineio/serializableObjectWithMetadata.h"

SerializableObjectWithMetadata::SerializableObjectWithMetadata(std::string const& name,
                                                               AnyDictionary const& metadata)
    : _name(name),
      _metadata(metadata)
{
}

SerializableObjectWithMetadata::~SerializableObjectWithMetadata() {
}

bool SerializableObjectWithMetadata::read_from(Reader& reader) {
    return reader.read("metadata", &_metadata) &&
        reader.read("name", &_name) &&
        SerializableObject::read_from(reader);
}

void SerializableObjectWithMetadata::write_to(Writer& writer) const {
    SerializableObject::write_to(writer);
    writer.write("metadata", _metadata);
    writer.write("name", _name);
}
