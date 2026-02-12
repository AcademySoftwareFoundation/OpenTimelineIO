// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/serializableCollection.h"
#include "opentimelineio/clip.h"
#include "opentimelineio/vectorIndexing.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

SerializableCollection::SerializableCollection(
    std::string const&               name,
    std::vector<SerializableObject*> children,
    AnyDictionary const&             metadata)
    : Parent(name, metadata)
    , _children(children.begin(), children.end())
{}

SerializableCollection::~SerializableCollection()
{}

void
SerializableCollection::clear_children()
{
    _children.clear();
}

void
SerializableCollection::set_children(
    std::vector<SerializableObject*> const& children)
{
    _children = decltype(_children)(children.begin(), children.end());
}

void
SerializableCollection::insert_child(int index, SerializableObject* child)
{
    index = adjusted_vector_index(index, _children);
    if (index >= int(_children.size()))
    {
        _children.emplace_back(child);
    }
    else
    {
        _children.insert(_children.begin() + std::max(index, 0), child);
    }
}

bool
SerializableCollection::set_child(
    int                 index,
    SerializableObject* child,
    ErrorStatus*        error_status)
{
    index = adjusted_vector_index(index, _children);
    if (index < 0 || index >= int(_children.size()))
    {
        if (error_status)
        {
            *error_status = ErrorStatus::ILLEGAL_INDEX;
        }
        return false;
    }

    _children[index] = child;
    return true;
}

bool
SerializableCollection::remove_child(int index, ErrorStatus* error_status)
{
    if (_children.empty())
    {
        if (error_status)
        {
            *error_status = ErrorStatus::ILLEGAL_INDEX;
        }
        return false;
    }

    index = adjusted_vector_index(index, _children);

    if (size_t(index) >= _children.size())
    {
        _children.pop_back();
    }
    else
    {
        _children.erase(_children.begin() + std::max(index, 0));
    }

    return true;
}

bool
SerializableCollection::read_from(Reader& reader)
{
    return reader.read("children", &_children) && Parent::read_from(reader);
}

void
SerializableCollection::write_to(Writer& writer) const
{
    Parent::write_to(writer);
    writer.write("children", _children);
}

std::vector<SerializableObject::Retainer<Clip>>
SerializableCollection::find_clips(
    ErrorStatus*                    error_status,
    std::optional<TimeRange> const& search_range,
    bool                            shallow_search) const
{
    return find_children<Clip>(error_status, search_range, shallow_search);
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
