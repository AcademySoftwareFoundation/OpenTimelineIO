#ifndef OTIO_ITEM_H
#define OTIO_ITEM_H

#include "composable.h"
#include "timeRange.h"
#include "optional.hpp"
    
class Effect;
class Marker;

class Item : public Composable {
public:
    struct Schema {
        static auto constexpr name = "Composable";
        static int constexpr version = 1;
    };

    using Parent = Composable;

    Item(std::string const& name = std::string(),
         optional<TimeRange> const& source_range = nullopt,
         AnyDictionary const& metadata = AnyDictionary(),
         std::vector<Effect*> const& effects = std::vector<Effect*>(),
         std::vector<Marker*> const& markers = std::vector<Marker*>());

    virtual bool visible() const;
    virtual bool overlapping() const;


    optional<TimeRange> const& source_range () const;
    void set_source_range(optional<TimeRange> const& source_range);

    std::vector<Retainer<Effect>>& effects();
    std::vector<Retainer<Effect>> const& effects() const;

    std::vector<Retainer<Marker>>& markers();
    std::vector<Retainer<Marker>> const& markers() const;

protected:
    virtual ~Item();

    virtual bool read_from(Reader&);
    virtual void write_to(Writer&) const;

private:
    optional<TimeRange> _source_range;
    std::vector<Retainer<Effect>> _effects;
    std::vector<Retainer<Marker>> _markers;
};

#endif
