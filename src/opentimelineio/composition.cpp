#include "opentimelineio/composition.h"
#include "opentimelineio/vectorIndexing.h"
#include <set>

Composition::Composition(std::string const& name,
                         optional<TimeRange> const& source_range,
                         AnyDictionary const& metadata)
    : Parent(name, source_range, metadata)
{
}

Composition::~Composition() {
    clear_children();
}

std::string const& Composition::composition_kind() const {
    static std::string kind = "Composition";
    return kind;
}

void 
Composition::clear_children() {
    for (Composable* child: _children) {
        child->_set_parent(nullptr);
    }

    _children.clear();
}

bool 
Composition::set_children(std::vector<Composable*> const& children, ErrorStatus* error_status) {
    for (auto child : children) {
        if (child->parent()) {
            *error_status = ErrorStatus::CHILD_ALREADY_PARENTED;
            return false;
        }
    }

    for (auto child : children) {
        child->_set_parent(this);
    }

    _children = decltype(_children)(children.begin(), children.end());
    return true;
    
}

bool 
Composition::insert_child(int index, Composable* child, ErrorStatus* error_status) {
    if (child->parent()) {
        *error_status = ErrorStatus::CHILD_ALREADY_PARENTED;
        return false;
    }

    child->_set_parent(this);
        
    index = adjusted_vector_index(index, _children);
    if (index >= int(_children.size())) {
        _children.emplace_back(child);
    }
    else {
        _children.insert(_children.begin() + std::max(index, 0), child);
    }

    return true;
}

bool 
Composition::set_child(int index, Composable* child, ErrorStatus* error_status)
{
    if (child->parent()) {
        *error_status = ErrorStatus::CHILD_ALREADY_PARENTED;
        return false;
    }

    index = adjusted_vector_index(index, _children);
    if (index < 0 || index >= int(_children.size())) {
        *error_status = ErrorStatus::ILLEGAL_INDEX;
        return false;
    }

    child->_set_parent(this);
    _children[index] = child;
    return true;
}

bool 
Composition::remove_child(int index, ErrorStatus* error_status) {
    if (_children.empty()) {
        *error_status = ErrorStatus::ILLEGAL_INDEX;
        return false;
    }

    index = adjusted_vector_index(index, _children);

    if (size_t(index) >= _children.size()) {
        _children.back().value->_set_parent(nullptr);
        _children.pop_back();
    }
    else {
        index = std::max(index, 0);
        _children[index].value->_set_parent(nullptr);
        _children.erase(_children.begin() + index);
    }

    return true;
}

bool Composition::read_from(Reader& reader) {
    if (reader.read("children", &_children) &&
        Parent::read_from(reader)) {
        for (Composable* child : _children) {
            if (!child->_set_parent(this)) {
                reader.error(ErrorStatus::CHILD_ALREADY_PARENTED);
                return false;
            }
        }
    }
    return true;
}

void Composition::write_to(Writer& writer) const {
    Parent::write_to(writer);
    writer.write("children", _children);
}

bool Composition::is_parent_of(Composable const* other) const {
    Composition const* cur_parent = other->_parent;
    if (cur_parent == this)
        return true;
    
    std::set<Composition const*> visited;
    while (cur_parent && visited.count(cur_parent) == 0) {
        if (cur_parent == this)
            return true;

        visited.insert(cur_parent);
        cur_parent = cur_parent->_parent;
    }
    return false;
}

std::pair<optional<RationalTime>, optional<RationalTime>>
Composition::handles_of_child(Composable const* child) const {
    return std::make_pair(optional<RationalTime>(), optional<RationalTime>());
}

    
