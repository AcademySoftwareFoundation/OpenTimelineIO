#pragma once

#include "opentimelineio/composable.h"
#include "opentimelineio/version.h"
#include "opentimelineio/track.h"
#include <functional>
#include <vector>

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {

class Stack;

// track_clip_visual_diff
//
// Given an old track and a new track, the clips on both are compared using
// Meyer's diffing algorithm, which is used to do source code diffs in programs like git.
// The resulting Stack has a first track containing clips that are new in new_track,
// the second track contains a copy of new_track, and any subsequent tracks contain
// clips that are in old_track but not in new_track.
// If this Stack is added to a Timeline and saved, it can be opened in otioviewer as
// a convenient visual diff showing how new_track was obtained from old_track.
//
// a typical invocation, detecting the insertion or removal of a clip is:
//
// Stack* diff_stack = track_clip_visual_diff(t1, t2,
//                          [](Composable const*const a, Composable const*const b) ->
//                          bool { return (a != nullptr) && (b != nullptr) &&
//                                         (a->name() == b->name()); });
//
Stack* track_clip_visual_diff(Track* old_track, Track* new_track,
                              std::function<bool(Composable const*const,
                                                 Composable const*const)>
                                                            comparison_func);

// track_clip_diff
//
// Given an old track and a new track, the clips on both are compared using
// Meyer's diffing algorithm.
//
// The result will be a vector<TrackDiffResult> which can be iterated to
// discover the series of operations that turns the old track into the new track.
//
// a typical invocation, detecting the insertion or removal of a clip is:
//
// auto diff = track_clip_visual_diff(t1, t2,
//                          [](Composable const*const a, Composable const*const b) ->
//                          bool { return (a != nullptr) && (b != nullptr) &&
//                                         (a->name() == b->name()); });
//
// another example, detecting changed duration in addition to insertion or removal:
//
// auto diff = track_clip_visual_diff(t1, t2,
//                          [](Composable const*const a, Composable const*const b) ->
//                          bool { return (a != nullptr) && (b != nullptr) &&
//                                         (a->name() == b->name()) &&
//                                         (a->duration() == b->duration() });

typedef enum
{
    TrackDiffAdded,     // an element that appears only in new
    TrackDiffRemoved,   // an element that appears only in old
    TrackDiffCommon     // an element that appears in both
} TrackDiffOp;

typedef struct
{
    int before_index;       // if an element was added before_index should be ignored
    int after_index;        // if an element was removed, after_index should be ignored
    TrackDiffOp edit_type;
} TrackDiffResult;

std::vector<TrackDiffResult>
track_clip_diff(Track const*const before_track, Track const*const after_track,
                std::function<bool(Composable const*const, Composable const*const)> comparison_func);

} }

