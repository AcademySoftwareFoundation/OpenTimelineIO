#include "opentimelineio/transition.h"

Transition::Transition(std::string const& name,
                       std::string const& transition_type,
                       RationalTime in_offset,
                       RationalTime out_offset,
                       AnyDictionary const& metadata)
    : Parent(name, metadata),
      _transition_type(transition_type),
      _in_offset(in_offset),
      _out_offset(out_offset) {
}

Transition::~Transition() {
}

bool Transition::overlapping() const {
    return true;
}

bool Transition::read_from(Reader& reader) {
    return reader.read("in_offset", &_in_offset) &&
        reader.read("out_offset", &_out_offset) &&
        reader.read("transition_type", &_transition_type) &&
        Parent::read_from(reader);
}

void Transition::write_to(Writer& writer) const {
    Parent::write_to(writer);
    writer.write("in_offset", _in_offset);
    writer.write("out_offset", _out_offset);
    writer.write("transition_type", _transition_type);
}


RationalTime Transition::duration(ErrorStatus* error_status) const {
    return _in_offset + _out_offset;
}
