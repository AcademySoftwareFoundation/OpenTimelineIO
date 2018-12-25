#include "opentimelineio/generatorReference.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {
    
GeneratorReference::GeneratorReference(std::string const& name,
                                       std::string const& generator_kind,
                                       optional<TimeRange> const& available_range,
                                       AnyDictionary const& parameters,
                                       AnyDictionary const& metadata)
    : Parent(name, available_range, metadata),
      _generator_kind(generator_kind),
      _parameters(parameters) {
}

GeneratorReference::~GeneratorReference() {
}

bool GeneratorReference::read_from(Reader& reader) {
    return reader.read("generator_kind", &_generator_kind) &&
        reader.read("parameters", &_parameters) &&
        Parent::read_from(reader);
}

void GeneratorReference::write_to(Writer& writer) const {
    Parent::write_to(writer);
    writer.write("generator_kind", _generator_kind);
    writer.write("parameters", _parameters);
}

} }
