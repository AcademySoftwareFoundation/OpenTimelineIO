#include "opentimelineio/trackAlgorithm.h"
#include "opentimelineio/transition.h"

#include "opentimelineio/composable.h"
#include "opentimelineio/gap.h"
#include "opentimelineio/item.h"
#include "opentimelineio/stack.h"
#include "dtl/dtl.hpp"
#include "trackDiff.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {

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

