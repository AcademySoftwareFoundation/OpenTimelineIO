// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/composition.h"
#include "opentimelineio/serializableObjectWithMetadata.h"
#include "opentimelineio/timeline.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

class Clip;

/// @brief A container which can hold an ordered list of any serializable objects.
///
/// Note that this is not a Composition nor is it Composable.
///
/// This container approximates the concept of a bin - a collection of
/// SerializableObjects that do not have any compositional meaning, but can
/// serialize to/from OTIO correctly, with metadata and a named collection.
///
/// A SerializableCollection is useful for serializing multiple timelines,
/// clips, or media references to a single file.
class OTIO_API_TYPE SerializableCollection
    : public SerializableObjectWithMetadata
{
public:
    /// @brief This struct provides the SerializableCollection schema.
    struct Schema
    {
        static auto constexpr name   = "SerializableCollection";
        static int constexpr version = 1;
    };

    using Parent = SerializableObjectWithMetadata;

    /// @brief Create a new serializable collection.
    ///
    /// @param name The name of the collection.
    /// @param child The list of children in the collection. Note that the
    /// collection keeps a retainer to each child.
    /// @param metadata The metadata for the collection.
    OTIO_API SerializableCollection(
        std::string const&               name = std::string(),
        std::vector<SerializableObject*> children =
            std::vector<SerializableObject*>(),
        AnyDictionary const& metadata = AnyDictionary());

    /// @brief Return the list of children.
    std::vector<Retainer<SerializableObject>> const& children() const noexcept
    {
        return _children;
    }

    /// @brief Modify the list of children.
    std::vector<Retainer<SerializableObject>>& children() noexcept
    {
        return _children;
    }

    /// @brief Set the list of children.
    OTIO_API void
    set_children(std::vector<SerializableObject*> const& children);

    /// @brief Clear the children.
    OTIO_API void clear_children();

    /// @brief Insert a child at the given index. Note that the collection
    /// keeps a retainer to the child.
    OTIO_API void insert_child(int index, SerializableObject* child);

    /// @brief Set the child at the given index. Note that the collection
    /// keeps a retainer to the child.
    OTIO_API bool set_child(
        int                 index,
        SerializableObject* child,
        ErrorStatus*        error_status = nullptr);

    /// @brief Remove the child at the given index.
    OTIO_API bool remove_child(int index, ErrorStatus* error_status = nullptr);

    /// @brief Find child clips.
    ///
    /// @param error_status The return status.
    /// @param search_range An optional range to limit the search.
    /// @param shallow_search The search is recursive unless shallow_search is
    /// set to true.
    OTIO_API std::vector<Retainer<Clip>> find_clips(
        ErrorStatus*                    error_status   = nullptr,
        std::optional<TimeRange> const& search_range   = std::nullopt,
        bool                            shallow_search = false) const;

    /// @brief Find child objects that match the given template type.
    ///
    /// @param error_status The return status.
    /// @param search_range An optional range to limit the search.
    /// @param shallow_search The search is recursive unless shallow_search is
    /// set to true.
    template <typename T = Composable>
    OTIO_API std::vector<Retainer<T>> find_children(
        ErrorStatus*             error_status   = nullptr,
        std::optional<TimeRange> search_range   = std::nullopt,
        bool                     shallow_search = false) const;

protected:
    virtual ~SerializableCollection();

    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

private:
    std::vector<Retainer<SerializableObject>> _children;
};

template <typename T>
inline std::vector<SerializableObject::Retainer<T>>
SerializableCollection::find_children(
    ErrorStatus*             error_status,
    std::optional<TimeRange> search_range,
    bool                     shallow_search) const
{
    std::vector<Retainer<T>> out;
    for (const auto& child: _children)
    {
        // filter out children who are not descended from the specified type
        if (auto valid_child = dynamic_cast<T*>(child.value))
        {
            out.push_back(valid_child);
        }

        // if not a shallow_search, for children that are serializable collections,
        // compositions, or timelines, recurse into their children
        if (!shallow_search)
        {
            if (auto collection =
                    dynamic_cast<SerializableCollection*>(child.value))
            {
                const auto valid_children =
                    collection->find_children<T>(error_status, search_range);
                if (is_error(error_status))
                {
                    return out;
                }
                for (const auto& valid_child: valid_children)
                {
                    out.push_back(valid_child);
                }
            }
            else if (auto composition = dynamic_cast<Composition*>(child.value))
            {
                const auto valid_children =
                    composition->find_children<T>(error_status, search_range);
                if (is_error(error_status))
                {
                    return out;
                }
                for (const auto& valid_child: valid_children)
                {
                    out.push_back(valid_child);
                }
            }
            else if (auto timeline = dynamic_cast<Timeline*>(child.value))
            {
                const auto valid_children =
                    timeline->find_children<T>(error_status, search_range);
                if (is_error(error_status))
                {
                    return out;
                }
                for (const auto& valid_child: valid_children)
                {
                    out.push_back(valid_child);
                }
            }
        }
    }
    return out;
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
