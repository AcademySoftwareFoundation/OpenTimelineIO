#pragma once

#include "opentime/timeRange.h"
#include "opentimelineio/composable.h"
#include "opentimelineio/errorStatus.h"
#include "opentimelineio/optional.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

class Effect;
class Marker;

class Item : public Composable
{
public:
    struct Schema
    {
        static auto constexpr name   = "Item";
        static int constexpr version = 1;
    };

    using Parent = Composable;

    Item(
        std::string const&          name         = std::string(),
        optional<TimeRange> const&  source_range = nullopt,
        AnyDictionary const&        metadata     = AnyDictionary(),
        std::vector<Effect*> const& effects      = std::vector<Effect*>(),
        std::vector<Marker*> const& markers      = std::vector<Marker*>());

    virtual bool visible() const;
    virtual bool overlapping() const;

    optional<TimeRange> source_range() const noexcept { return _source_range; }

    void set_source_range(optional<TimeRange> const& source_range)
    {
        _source_range = source_range;
    }

    std::vector<Retainer<Effect>>& effects() noexcept { return _effects; }

    std::vector<Retainer<Effect>> const& effects() const noexcept
    {
        return _effects;
    }

    std::vector<Retainer<Marker>>& markers() noexcept { return _markers; }

    std::vector<Retainer<Marker>> const& markers() const noexcept
    {
        return _markers;
    }

    virtual RationalTime duration(ErrorStatus* error_status = nullptr) const;

    virtual TimeRange
    available_range(ErrorStatus* error_status = nullptr) const;

    TimeRange trimmed_range(ErrorStatus* error_status = nullptr) const
    {
        return _source_range ? *_source_range : available_range(error_status);
    }

    TimeRange visible_range(ErrorStatus* error_status = nullptr) const;

    optional<TimeRange>
    trimmed_range_in_parent(ErrorStatus* error_status = nullptr) const;

    TimeRange range_in_parent(ErrorStatus* error_status = nullptr) const;

    RationalTime transformed_time(
        RationalTime time,
        Item const*  to_item,
        ErrorStatus* error_status = nullptr) const;

    TimeRange transformed_time_range(
        TimeRange    time_range,
        Item const*  to_item,
        ErrorStatus* error_status = nullptr) const;

protected:
    virtual ~Item();

    virtual bool read_from(Reader&);
    virtual void write_to(Writer&) const;

private:
    optional<TimeRange>           _source_range;
    std::vector<Retainer<Effect>> _effects;
    std::vector<Retainer<Marker>> _markers;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
