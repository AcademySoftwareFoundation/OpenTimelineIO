#include "opentimelineio/trackAlgorithm.h"
#include "opentimelineio/transition.h"

#include "opentimelineio/composable.h"
#include "opentimelineio/gap.h"
#include "opentimelineio/item.h"
#include "opentimelineio/stack.h"
#include "dtl/dtl.hpp"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {
/*

Stack *Stack_create(
        const char *name,
        std::optional<TimeRange> source_range,
        AnyDictionary *metadata,
        EffectVector *effects,
        MarkerVector *markers) 
{
    nonstd::optional<opentime::TimeRange> timeRangeOptional = nonstd::nullopt;
    if (source_range.valid)
        timeRangeOptional = nonstd::optional<opentime::TimeRange>(
                CTimeRange_to_CppTimeRange(source_range.value));

    std::string name_str = std::string();
    if (name != NULL) name_str = name;

    OTIO_NS::AnyDictionary metadataDictionary = OTIO_NS::AnyDictionary();
    if (metadata != NULL) {
        metadataDictionary =
                *reinterpret_cast<OTIO_NS::AnyDictionary *>(metadata);
    }

    EffectVectorDef effectsVector = EffectVectorDef();
    if (effects != NULL) { effectsVector = *reinterpret_cast<EffectVectorDef *>(effects); }

    MarkerVectorDef markersVector = MarkerVectorDef();
    if (markers != NULL) { markersVector = *reinterpret_cast<MarkerVectorDef *>(markers); }

    return reinterpret_cast<Stack *>(new OTIO_NS::Stack(
            name_str,
            timeRangeOptional,
            metadataDictionary,
            effectsVector,
            markersVector));
}

*/



Track* track_trimmed_to_range(Track* in_track, TimeRange trim_range, ErrorStatus* error_status) {
    Track* new_track = dynamic_cast<Track*>(in_track->clone(error_status));
    if (is_error(error_status) || !new_track) {
        return nullptr;
    }
    
    auto track_map = new_track->range_of_all_children(error_status);
    if (is_error(error_status)) {
        return nullptr;
    }
    
    std::vector<Composable*> children_copy (new_track->children().begin(),
                                            new_track->children().end());
    
    for (size_t i = children_copy.size(); i--; ) {
        Composable* child = children_copy[i];
        auto child_range_it = track_map.find(child);
        if (child_range_it == track_map.end()) {
            if (error_status) {
                *error_status = ErrorStatus(ErrorStatus::CANNOT_COMPUTE_AVAILABLE_RANGE,
                        "failed to find child in track_map map");
            }
            return nullptr;
        }

        auto child_range = child_range_it->second;
        if (!trim_range.intersects(child_range)) {
            new_track->remove_child(static_cast<int>(i), error_status);
            if (is_error(error_status)) {
                return nullptr;
            }
        }
        else if (!trim_range.contains(child_range)) {
            if (dynamic_cast<Transition*>(child)) {
                if (error_status) {
                    *error_status = ErrorStatus(ErrorStatus::CANNOT_TRIM_TRANSITION,
                                                "Cannot trim in the middle of a transition");
                }
                return nullptr;
            }
            
            Item* child_item = dynamic_cast<Item*>(child);
            if (!child_item) {
                if (error_status) {
                    *error_status = ErrorStatus(ErrorStatus::TYPE_MISMATCH,
                                                "Expected child of type Item*", child);
                }
                return nullptr;
            }
            auto child_source_range = child_item->trimmed_range(error_status);
            if (is_error(error_status)) {
                return nullptr;
            }
            
            if (trim_range.start_time() > child_range.start_time()) {
                auto trim_amount = trim_range.start_time() - child_range.start_time();
                child_source_range = TimeRange(child_source_range.start_time() + trim_amount,
                                               child_source_range.duration() - trim_amount);
            }
            
            auto trim_end = trim_range.end_time_exclusive();
            auto child_end = child_range.end_time_exclusive();
            if (trim_end < child_end) {
                auto trim_amount = child_end - trim_end;
                child_source_range = TimeRange(child_source_range.start_time(),
                                               child_source_range.duration() - trim_amount);
            }
            
            child_item->set_source_range(child_source_range);
        }
    }
    
    return new_track;
}


typedef SerializableObject::Retainer<Composable> Obj;

struct Comparator {
    explicit Comparator(std::function<bool(Composable const*const, Composable const*const)> cmp)
    : cmp(cmp) {}
    
    Comparator() = delete;
    
    bool impl(const Obj& a, const Obj& b) const
    { return cmp(a, b); }

    std::function<bool(Composable const*const, Composable const*const)> cmp;
};

struct TrackCmp
{
    explicit TrackCmp(TrackCmp&& rh)
    {
        std::swap(rh.items, items);
    }

    explicit TrackCmp(const TrackCmp& rh)
    {
        items = rh.items;
    }

    explicit TrackCmp(std::vector<Obj>::iterator b,
                      std::vector<Obj>::iterator e)
    : items(b, e)
    {
    }

    explicit TrackCmp(std::vector<Obj>::const_iterator b,
                      std::vector<Obj>::const_iterator e)
    : items(b, e)
    {
    }

    explicit TrackCmp(Track const*const track)
    : items(track->children().begin(), track->children().end())
    {
    }

    TrackCmp& operator=(const TrackCmp& rh)
    {
        items = rh.items;
        return *this;
    }

    TrackCmp& operator=(TrackCmp&& rh)
    {
        std::swap(rh.items, items);
        return *this;
    }

    std::vector<Obj> items;

    typedef std::vector<Obj>::iterator iterator;
    typedef std::vector<Obj>::const_iterator const_iterator;
    const Obj& operator[](size_t i) const { return items[i]; }

    std::vector<Obj>::const_iterator begin() {
        return items.begin();
    }
    std::vector<Obj>::const_iterator end() {
        return items.end();
    }
};

void swap(TrackCmp& a, TrackCmp& b)
{
    TrackCmp t(std::move(a));
    a = std::move(b);
    b = std::move(t);
}

std::ostream& operator<<(std::ostream& os, const Obj& o)
{
    os << "Name:" << o->name();
    return os;
}


std::vector<TrackDiffResult>
track_clip_diff(Track const*const before_track, Track const*const after_track,
                std::function<bool(Composable const*const, Composable const*const)> comparison_func)
{
    if (!before_track && !after_track)
        return {};

    std::vector<TrackDiffResult> result;
    if (!before_track) {
        auto& children = after_track->children();
        result.reserve(children.size());
        for (int i = 0; i < children.size(); ++i)
            result.push_back({ -1, i, TrackDiffAdded });
        return result;
    }
    if (!after_track) {
        auto& children = before_track->children();
        result.reserve(children.size());
        for (int i = 0; i < children.size(); ++i)
            result.push_back({ -1, i, TrackDiffRemoved });
        return result;
    }
    
    TrackCmp A { before_track };
    TrackCmp B { after_track };
    Comparator cmp(comparison_func);
    dtl::Diff<Obj, TrackCmp, Comparator> d(A, B, cmp);
    d.compose();

    result.reserve(A.items.size() + B.items.size());
    auto session = d.getSes();
    auto sequence = session.getSequence();
    for (auto& i : sequence)
    {
        TrackDiffOp e;
        switch (i.second.type) {
            case dtl::SES_DELETE: e = TrackDiffRemoved; break;
            case dtl::SES_ADD:    e = TrackDiffAdded; break;
            case dtl::SES_COMMON: e = TrackDiffCommon; break;
        }
        result.push_back({(int) i.second.beforeIdx, (int) i.second.afterIdx, e });
    }

    return result;
}


// Given an old track, and a new track, the clips on both are compared using
// Meyer's diffing algorithm, which is used to do source code diffs in programs like git.
// The resulting Stack has a first track containing clips that are new in new_track,
// the second track contains a copy of new_track, and any subsequent tracks contain
// clips that are in old_track but not in new_track.
// If this Stack is added to a Timeline and saved, it can be opened in otioviewer as
// a convenient visual diff showing how new_track was obtained from old_track.
//
Stack* track_clip_visual_diff(Track* before_track, Track* after_track,
                              std::function<bool(Composable const*const,
                                                 Composable const*const)>
                                                            comparison_func)
{
    ErrorStatus* err = nullptr;
    Stack* ret = new Stack("diff");
 
    if (!before_track && !after_track) {
        Track* t1 = new Track("added");
        Track* t2 = new Track("new");
        Track* t3 = new Track("removed");
        ret->append_child(t1);
        ret->append_child(t2);
        ret->append_child(t3);
        return ret;
    }
    if (!after_track) {
        Track* t1 = new Track("added");
        Track* t2 = new Track("new");
        Track* t3 = dynamic_cast<Track*>(before_track->clone(err));
        t3->set_name("removed");
        ret->append_child(t1);
        ret->append_child(t2);
        ret->append_child(t3);
        return ret;
    }
    if (!before_track) {
        Track* t1 = dynamic_cast<Track*>(after_track->clone(err)); 
        t1->set_name("added");
        Track* t2 = dynamic_cast<Track*>(after_track->clone(err));
        t2->set_name("new");
        Track* t3 = new Track("removed");
        ret->append_child(t1);
        ret->append_child(t2);
        ret->append_child(t3);
        return ret;
    }

    TrackCmp A { before_track };
    TrackCmp B { after_track };
    Comparator cmp(comparison_func);

    dtl::Diff<Obj, TrackCmp, Comparator> d(A, B, cmp);
    d.compose();

    Track* t1 = new Track("added");
    Track* t2 = dynamic_cast<Track*>(after_track->clone(err));
    t2->set_name("new");
    Track* t3 = new Track("removed");

    opentime::RationalTime added_add_time(0, 24);
    opentime::RationalTime added_remove_time(0, 24);

    auto before_children = before_track->children();
    auto after_children = t2->children();
    
    auto session = d.getSes();
    auto sequence = session.getSequence();
    for (auto& i : sequence)
    {
        if (i.second.type == dtl::SES_ADD) {
            auto& composable = after_children[i.second.afterIdx];
            Item* item = dynamic_cast<Item*>(composable.value);
            optional<TimeRange> t = item->trimmed_range_in_parent(err);
            auto dt = t.value().start_time() - added_add_time;
            if (dt.value() > 0) {
                t1->append_child(new Gap(dt, "gap"));
                added_add_time += t.value().duration() + dt;
            }
            t1->append_child(B.items[i.second.afterIdx]);
        }
        else if (i.second.type == dtl::SES_DELETE) {
            auto& composable = before_children[i.second.beforeIdx];
            Item* item = dynamic_cast<Item*>(composable.value);
            optional<TimeRange> t = item->trimmed_range_in_parent(err);
            auto dt = t.value().start_time() - added_remove_time;
            if (dt.value() > 0) {
                t3->append_child(new Gap(dt, "gap"));
                added_remove_time += t.value().duration() + dt;
            }
            t3->append_child(B.items[i.second.beforeIdx]);
        }
    }
    
    ret->append_child(t1);
    ret->append_child(t2);
    ret->append_child(t3);
    return ret;
}

} }

