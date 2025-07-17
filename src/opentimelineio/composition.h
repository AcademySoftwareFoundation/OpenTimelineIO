// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/item.h"
#include "opentimelineio/version.h"
#include <set>

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

class Clip;

/// @brief Base class for an Item that contains Composables.
///
/// Should be subclassed (for example by Track Stack), not used directly.
class Composition : public Item
{
public:
    /// @brief This struct provides the Composition schema.
    struct Schema
    {
        static auto constexpr name   = "Composition";
        static int constexpr version = 1;
    };

    using Parent = Item;

    /// @brief Create a new composition.
    ///
    /// @param name The name of the composition.
    /// @param source_range The source range of the composition.
    /// @param metadata The metadata for the composition.
    /// @param effects The list of effects for the composition. Note that the
    /// the composition keeps a retainer to each effect.
    /// @param markers The list of markers for the composition. Note that the
    /// the composition keeps a retainer to each marker.
    Composition(
        std::string const&              name         = std::string(),
        std::optional<TimeRange> const& source_range = std::nullopt,
        AnyDictionary const&            metadata     = AnyDictionary(),
        std::vector<Effect*> const&     effects      = std::vector<Effect*>(),
        std::vector<Marker*> const&     markers      = std::vector<Marker*>(),
        std::optional<Color> const&     color        = std::nullopt);

    /// @brief Return the kind of composition.
    virtual std::string composition_kind() const;

    /// @brief Return the list of children.
    std::vector<Retainer<Composable>> const& children() const noexcept
    {
        return _children;
    }

    /// @brief Clear the children.
    void clear_children();

    /// @brief Set the list of children. Note that the composition keeps a
    /// retainer to each child.
    bool set_children(
        std::vector<Composable*> const& children,
        ErrorStatus*                    error_status = nullptr);

    /// @brief Insert a child. Note that the composition keeps a retainer to the child.
    bool insert_child(
        int          index,
        Composable*  child,
        ErrorStatus* error_status = nullptr);

    /// @brief Set the child at the given index. Note that the composition keeps a
    /// retainer to the child.
    bool set_child(
        int          index,
        Composable*  child,
        ErrorStatus* error_status = nullptr);

    /// @brief Remove the child at the given index.
    bool remove_child(int index, ErrorStatus* error_status = nullptr);

    /// @brief Append the child. Note that the composition keeps a retainer to
    /// the child.
    bool append_child(Composable* child, ErrorStatus* error_status = nullptr)
    {
        return insert_child(int(_children.size()), child, error_status);
    }

    /// @brief Return the index of the given child.
    int index_of_child(
        Composable const* child,
        ErrorStatus*      error_status = nullptr) const;

    /// @brief Return whether this is the parent of the given child.
    bool is_parent_of(Composable const* other) const;

    /// @brief Return the in and out handles of the given child.
    virtual std::pair<std::optional<RationalTime>, std::optional<RationalTime>>
    handles_of_child(
        Composable const* child,
        ErrorStatus*      error_status = nullptr) const;

    /// @brief Return the range of the given child.
    virtual TimeRange range_of_child_at_index(
        int          index,
        ErrorStatus* error_status = nullptr) const;

    /// @brief Return the trimmed range of the given child.
    virtual TimeRange trimmed_range_of_child_at_index(
        int          index,
        ErrorStatus* error_status = nullptr) const;

    /// @brief Return the range of the given child.
    ///
    /// @todo Leaving out reference_space argument for now.
    TimeRange range_of_child(
        Composable const* child,
        ErrorStatus*      error_status = nullptr) const;

    /// @brief Return the trimmed range of the given child.
    std::optional<TimeRange> trimmed_range_of_child(
        Composable const* child,
        ErrorStatus*      error_status = nullptr) const;

    /// @brief Return the given range trimmed to this source range.
    std::optional<TimeRange> trim_child_range(TimeRange child_range) const;

    /// @brief Return whether this contains the given child.
    bool has_child(Composable* child) const;

    /// @brief Return whether this contains any child clips.
    bool has_clips() const;

    /// @brief Return the range of all children.
    virtual std::map<Composable*, TimeRange>
    range_of_all_children(ErrorStatus* error_status = nullptr) const;

    /// @brief Return the child that overlaps with the given time.
    ///
    /// @param search_time The search time.
    /// @param error_status The return status.
    /// @param shallow_search The search is recursive unless shallow_search is
    /// set to true.
    Retainer<Composable> child_at_time(
        RationalTime const& search_time,
        ErrorStatus*        error_status   = nullptr,
        bool                shallow_search = false) const;

    /// @brief Return all objects within the given search_range.
    virtual std::vector<Retainer<Composable>> children_in_range(
        TimeRange const& search_range,
        ErrorStatus*     error_status = nullptr) const;

    /// @brief Find child objects that match the given template type.
    ///
    /// @param error_status The return status.
    /// @param search_range An optional range to limit the search.
    /// @param shallow_search The search is recursive unless shallow_search is
    /// set to true.
    template <typename T = Composable>
    std::vector<Retainer<T>> find_children(
        ErrorStatus*             error_status   = nullptr,
        std::optional<TimeRange> search_range   = std::nullopt,
        bool                     shallow_search = false) const;
   
    /// @brief Find child clips.
    ///
    /// @param error_status The return status.
    /// @param search_range An optional range to limit the search.
    /// @param shallow_search The search is recursive unless shallow_search is
    /// set to true.
    std::vector<Retainer<Clip>> find_clips(
        ErrorStatus*                    error_status   = nullptr,
        std::optional<TimeRange> const& search_range   = std::nullopt,
        bool                            shallow_search = false) const;

protected:
    virtual ~Composition();

    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

    std::vector<Composition*> _path_from_child(
        Composable const* child,
        ErrorStatus*      error_status = nullptr) const;

private:
    // XXX: python implementation is O(n^2) in number of children
    std::vector<Composable*>
    _children_at_time(RationalTime, ErrorStatus* error_status = nullptr) const;

    // Return the index of the last item in seq such that all e in seq[:index]
    // have key_func(e) <= tgt, and all e in seq[index:] have key_func(e) > tgt.
    //
    // Thus, seq.insert(index, value) will insert value after the rightmost item
    // such that meets the above condition.
    //
    // lower_search_bound and upper_search_bound bound the slice to be searched.
    //
    // Assumes that seq is already sorted.
    int64_t _bisect_right(
        RationalTime const&                             tgt,
        std::function<RationalTime(Composable*)> const& key_func,
        ErrorStatus*                                    error_status = nullptr,
        std::optional<int64_t> lower_search_bound = std::optional<int64_t>(0),
        std::optional<int64_t> upper_search_bound = std::nullopt) const;

    // Return the index of the last item in seq such that all e in seq[:index]
    // have key_func(e) < tgt, and all e in seq[index:] have key_func(e) >= tgt.
    //
    // Thus, seq.insert(index, value) will insert value before the leftmost item
    // such that meets the above condition.
    //
    // lower_search_bound and upper_search_bound bound the slice to be searched.
    //
    // Assumes that seq is already sorted.
    int64_t _bisect_left(
        RationalTime const&                             tgt,
        std::function<RationalTime(Composable*)> const& key_func,
        ErrorStatus*                                    error_status = nullptr,
        std::optional<int64_t> lower_search_bound = std::optional<int64_t>(0),
        std::optional<int64_t> upper_search_bound = std::nullopt) const;

    std::vector<Retainer<Composable>> _children;

    // This is for fast lookup only, and varies automatically
    // as _children is mutated.
    std::set<Composable*> _child_set;
};

template <typename T>
inline std::vector<SerializableObject::Retainer<T>>
Composition::find_children(
    ErrorStatus*             error_status,
    std::optional<TimeRange> search_range,
    bool                     shallow_search) const
{
    std::vector<Retainer<T>>          out;
    std::vector<Retainer<Composable>> children;
    if (search_range)
    {
        // limit the search to children who are in the search_range
        children = children_in_range(*search_range, error_status);
        if (is_error(error_status))
        {
            return out;
        }
    }
    else
    {
        // otherwise search all the children
        children = _children;
    }
    for (const auto& child: children)
    {
        if (auto valid_child = dynamic_cast<T*>(child.value))
        {
            out.push_back(valid_child);
        }

        // if not a shallow_search, for children that are compositions,
        // recurse into their children
        if (!shallow_search)
        {
            if (auto composition = dynamic_cast<Composition*>(child.value))
            {
                if (search_range)
                {
                    search_range = transformed_time_range(
                        *search_range,
                        composition,
                        error_status);
                    if (is_error(error_status))
                    {
                        return out;
                    }
                }

                const auto valid_children = composition->find_children<T>(
                    error_status,
                    search_range,
                    shallow_search);
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

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
