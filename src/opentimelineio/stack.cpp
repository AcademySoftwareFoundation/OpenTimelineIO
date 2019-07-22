#include "opentimelineio/stack.h"
#include "opentimelineio/vectorIndexing.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {

Stack::Stack(
        std::string const& name,
        optional<TimeRange> const& source_range,
        AnyDictionary const& metadata, 
        std::vector<Effect*> const& effects,
        std::vector<Marker*> const& markers)
    : Parent( name, source_range, metadata, effects, markers) {
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


TimeRange Stack::range_of_child_at_index(int index, ErrorStatus* error_status) const {
    index = adjusted_vector_index(index, children());
    if (index < 0 || index >= int(children().size())) {
        *error_status = ErrorStatus::ILLEGAL_INDEX;
        return TimeRange();
    }
    
    Composable* child = children()[index];
    auto duration = child->duration(error_status);
    if (*error_status) {
        return TimeRange();
    }
    
    return TimeRange(RationalTime(0, duration.rate()), duration);
}

std::map<Composable*, TimeRange>
Stack::range_of_all_children(ErrorStatus* error_status) const {
    std::map<Composable*, TimeRange> result;
    auto kids = children();

    for (size_t i = 0; i < kids.size(); i++) {
        result[kids[i]] = range_of_child_at_index(int(i), error_status);
        if (*error_status) {
            break;
        }
    }

    return result;
}

TimeRange Stack::trimmed_range_of_child_at_index(int index, ErrorStatus* error_status) const {
    auto range = range_of_child_at_index(index, error_status);
    if (*error_status || !source_range()) {
        return range;
    }
    
    TimeRange const& sr = *source_range();
    return TimeRange(sr.start_time(),
                     std::min(range.duration(), sr.duration()));
}

TimeRange Stack::available_range(ErrorStatus* error_status) const {
    if (children().empty()) {
        return TimeRange();
    }
    
    auto duration = children()[0].value->duration(error_status);
    for (size_t i = 1; i < children().size() && !(*error_status); i++) {
        duration = std::max(duration, children()[i].value->duration(error_status));
    }
    
    return TimeRange(RationalTime(0, duration.rate()), duration);
}

} }
