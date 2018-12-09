#include "opentimelineio/stack.h"

Stack::Stack(std::string const& name,
             optional<TimeRange> const& source_range,
             AnyDictionary const& metadata)
    : Parent( name, source_range, metadata) {
}

Stack::~Stack() {
}

std::string const& Stack::composition_kind() const {
    static std::string kind = "Stack";
    return kind;
}

bool Stack::read_from(Reader& reader) {
    return Parent::read_from(reader);
}

void Stack::write_to(Writer& writer) const {
    Parent::write_to(writer);
}
