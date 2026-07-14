#!/usr/bin/env python
#
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Example OTIO script that diffs two cuts of a timeline structurally:
which clips were added, removed, retimed, moved, or shifted between
cut A and cut B.

Because both inputs are parsed through OTIO adapters, the two cuts do not
need to be the same format — e.g. an EDL can be diffed against an FCP XML
export of a revised cut.

Approach: a cut is not positionally diffable (inserting one clip shifts
every downstream timecode), so clips are MATCHED BY IDENTITY first —
``(media target_url, source in-point)`` — then classified:

  added     in B, not in A
  removed   in A, not in B
  retimed   same clip, trimmed duration changed
  moved     relative order among matched clips changed
  shifted   only slid on the timeline (the ripple of an upstream edit)

Duration is compared as an attribute after matching, so an out-point trim
reads as "retimed" rather than removed+added. "moved" uses relative order
(longest increasing subsequence over the matched clips) rather than absolute
index, so a gap inserted by a lift-trim or a deleted event does not read as
every downstream clip having moved. Duplicate identities (same source used
twice) are paired as a multiset.

Scope is structural editorial only: clips, timing, order. Effects,
transitions, and retime curves are intentionally not diffed — they
serialize tool-specifically and don't round-trip across formats.

Exit codes follow diff(1): 0 = no structural changes, 1 = changes found,
2 = could not read an input.

This example is a lightweight, self-contained take on timeline diffing. For
a more full-featured, integrated tool — including a visual annotated-OTIO
output — see the proposed ``otiodiff`` feature for ``otiotool`` in
https://github.com/AcademySoftwareFoundation/OpenTimelineIO/pull/1922 and the
tracking issue https://github.com/AcademySoftwareFoundation/OpenTimelineIO/issues/26

A packaged version of this tool with tests and an MCP server for AI agents
lives at https://github.com/chaoz23/otio-diff
"""

from __future__ import annotations

import argparse
import bisect
import json
import sys
from collections import defaultdict
from dataclasses import dataclass, asdict
from typing import Optional

import opentimelineio as otio


# ---------------------------------------------------------------------------
# Flatten a Timeline into clip records
# ---------------------------------------------------------------------------

@dataclass
class ClipRecord:
    name: str
    media_url: Optional[str]          # target_url of the media reference
    src_start: Optional[float]        # source_range.start_time in seconds
    src_duration: Optional[float]     # source_range.duration in seconds
    timeline_start: Optional[float]   # position on the timeline in seconds
    track_index: int
    position_index: int               # clip-only ordinal within its track
    rate: Optional[float] = None      # clip frame rate, for frame output


def _seconds(rt) -> Optional[float]:
    if rt is None:
        return None
    try:
        return rt.to_seconds()
    except AttributeError:
        return rt.value / rt.rate if rt.rate else None


def flatten_timeline(tl: otio.schema.Timeline) -> list:
    """Flat, ordered list of ClipRecords; recurses into nested Stack/Track."""
    records = []

    def walk(container, track_index):
        pos = 0
        for item in container:
            if isinstance(item, otio.schema.Clip):
                src = item.source_range
                try:
                    tl_range = container.trimmed_range_of_child(item)
                    tl_start = _seconds(tl_range.start_time) if tl_range else None
                except Exception:
                    tl_start = None
                ref = item.media_reference
                records.append(ClipRecord(
                    name=item.name or "",
                    media_url=getattr(ref, "target_url", None) if ref else None,
                    src_start=_seconds(src.start_time) if src else None,
                    src_duration=_seconds(src.duration) if src else None,
                    timeline_start=tl_start,
                    track_index=track_index,
                    position_index=pos,
                    rate=(src.duration.rate if src and src.duration.rate else None),
                ))
                pos += 1
            elif isinstance(item, (otio.schema.Stack, otio.schema.Track)):
                walk(item, track_index)
            # Gaps: skipped entirely. position_index counts CLIPS only, so a
            # gap appearing (e.g. a lift-trim) doesn't read as downstream
            # clips having "moved". Transitions: out of scope.

    for t_idx, track in enumerate(tl.tracks):
        walk(track, t_idx)
    return records


# ---------------------------------------------------------------------------
# Match + classify
# ---------------------------------------------------------------------------

def clip_key(rec: ClipRecord) -> tuple:
    """Identity: (media url, source in-point). Duration is deliberately an
    attribute, not identity, so an out-point trim reads as retimed."""
    def r(x):
        return round(x, 4) if x is not None else None
    return (rec.media_url, r(rec.src_start))


@dataclass
class DiffResult:
    added: list
    removed: list
    retimed: list
    moved: list
    shifted: list
    unchanged_count: int


def diff(a: list, b: list) -> DiffResult:
    a_by_key = defaultdict(list)
    b_by_key = defaultdict(list)
    for r in a:
        a_by_key[clip_key(r)].append(r)
    for r in b:
        b_by_key[clip_key(r)].append(r)

    added, removed, retimed, moved, shifted = [], [], [], [], []

    # Pair matched clips (multiset for duplicates); surplus = added/removed.
    matched = []
    for key in set(a_by_key) | set(b_by_key):
        a_recs = a_by_key.get(key, [])
        b_recs = b_by_key.get(key, [])
        pairs = min(len(a_recs), len(b_recs))
        for i in range(pairs):
            matched.append((key, a_recs[i], b_recs[i]))
        removed.extend(asdict(r) for r in a_recs[pairs:])
        added.extend(asdict(r) for r in b_recs[pairs:])

    # moved = RELATIVE order of matched clips changed. LIS over A-ranks in B
    # order finds the clips that kept their order; the rest moved. A track
    # change is a move unconditionally.
    moved_idx = set()
    same_track = [i for i, (_, ra, rb) in enumerate(matched)
                  if ra.track_index == rb.track_index]
    moved_idx.update(i for i in range(len(matched)) if i not in same_track)

    order_a = sorted(same_track,
                     key=lambda i: (matched[i][1].track_index,
                                    matched[i][1].position_index))
    rank_a = {idx: n for n, idx in enumerate(order_a)}
    order_b = sorted(same_track,
                     key=lambda i: (matched[i][2].track_index,
                                    matched[i][2].position_index))
    seq = [rank_a[i] for i in order_b]

    tails, tails_pos = [], []
    prev = [-1] * len(seq)
    for pos, val in enumerate(seq):
        k = bisect.bisect_left(tails, val)
        if k == len(tails):
            tails.append(val)
            tails_pos.append(pos)
        else:
            tails[k] = val
            tails_pos[k] = pos
        prev[pos] = tails_pos[k - 1] if k > 0 else -1
    in_lis = set()
    if tails_pos:
        p = tails_pos[-1]
        while p != -1:
            in_lis.add(p)
            p = prev[p]
    moved_idx.update(order_b[pos] for pos in range(len(seq)) if pos not in in_lis)

    # Classify each matched pair.
    unchanged = 0
    for i, (key, ra, rb) in enumerate(matched):
        changed = False
        if ra.src_duration != rb.src_duration:
            retimed.append({"key": key, "before": asdict(ra), "after": asdict(rb)})
            changed = True
        if i in moved_idx:
            moved.append({"key": key, "before": asdict(ra), "after": asdict(rb)})
            changed = True
        if not changed and ra.timeline_start != rb.timeline_start:
            shifted.append({"key": key, "before": asdict(ra), "after": asdict(rb)})
            changed = True
        if not changed:
            unchanged += 1

    return DiffResult(added, removed, retimed, moved, shifted, unchanged)


# ---------------------------------------------------------------------------
# Output + CLI
# ---------------------------------------------------------------------------

def _label(rec: dict) -> str:
    if rec.get("name"):
        return rec["name"]
    url = rec.get("media_url")
    return url.rsplit("/", 1)[-1] if url else "<unnamed>"


def _fmt(seconds: Optional[float], rate: Optional[float]) -> str:
    if seconds is None:
        return "?"
    if rate:
        return "{}f".format(round(seconds * rate))
    return "{:.3f}s".format(seconds)


def human(result: DiffResult) -> str:
    counts = []
    for label, group in (("added", result.added), ("removed", result.removed),
                         ("retimed", result.retimed), ("moved", result.moved),
                         ("shifted", result.shifted)):
        if group:
            counts.append("{} {}".format(len(group), label))
    if not counts:
        return "No structural changes."

    lines = [", ".join(counts) + " ({} unchanged)".format(result.unchanged_count)]
    for rec in result.added:
        lines.append("  + {} added ({})".format(
            _label(rec), _fmt(rec["src_duration"], rec.get("rate"))))
    for rec in result.removed:
        lines.append("  - {} removed ({})".format(
            _label(rec), _fmt(rec["src_duration"], rec.get("rate"))))
    for item in result.retimed:
        ra, rb = item["before"], item["after"]
        rate = rb.get("rate") or ra.get("rate")
        da, db = ra["src_duration"], rb["src_duration"]
        if da is not None and db is not None:
            verb = "shortened" if db < da else "lengthened"
            lines.append("  ~ {} {} by {} ({} -> {})".format(
                _label(rb), verb, _fmt(abs(db - da), rate),
                _fmt(da, rate), _fmt(db, rate)))
        else:
            lines.append("  ~ {} retimed".format(_label(rb)))
    for item in result.moved:
        ra, rb = item["before"], item["after"]
        lines.append("  > {} moved (track {} pos {} -> track {} pos {})".format(
            _label(rb), ra["track_index"], ra["position_index"],
            rb["track_index"], rb["position_index"]))
    for item in result.shifted:
        ra, rb = item["before"], item["after"]
        rate = rb.get("rate") or ra.get("rate")
        ta, tb = ra["timeline_start"], rb["timeline_start"]
        if ta is not None and tb is not None:
            direction = "earlier" if tb < ta else "later"
            lines.append("  . {} shifted {} {}".format(
                _label(rb), _fmt(abs(tb - ta), rate), direction))
        else:
            lines.append("  . {} shifted".format(_label(rb)))
    return "\n".join(lines)


def load(path: str, rate: Optional[float] = None) -> list:
    """Read a timeline through the appropriate adapter. `rate` is forwarded
    to the EDL adapter (CMX 3600 EDLs don't carry their frame rate). If an
    adapter returns a SerializableCollection, the first Timeline is used."""
    kwargs = {}
    if rate is not None and path.lower().endswith(".edl"):
        kwargs["rate"] = rate
    tl = otio.adapters.read_from_file(path, **kwargs)
    if isinstance(tl, otio.schema.SerializableCollection):
        timelines = [t for t in tl if isinstance(t, otio.schema.Timeline)]
        if not timelines:
            raise ValueError("{}: collection contains no Timeline".format(path))
        if len(timelines) > 1:
            print("warning: {} contains {} timelines; diffing the first "
                  "({})".format(path, len(timelines),
                                timelines[0].name or "unnamed"),
                  file=sys.stderr)
        tl = timelines[0]
    return flatten_timeline(tl)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description="Structural editorial diff between two cuts of a timeline.")
    p.add_argument("a", help="baseline timeline (any format with an adapter)")
    p.add_argument("b", help="revised timeline (any format with an adapter)")
    p.add_argument("--json", action="store_true",
                   help="emit JSON instead of the human summary")
    p.add_argument("--rate", type=float, default=None,
                   help="frame rate hint for EDL inputs (EDLs don't carry it)")
    args = p.parse_args(argv)

    try:
        a = load(args.a, rate=args.rate)
        b = load(args.b, rate=args.rate)
    except Exception as e:
        print("error: could not read timelines: {}".format(e), file=sys.stderr)
        return 2

    result = diff(a, b)
    if args.json:
        print(json.dumps(asdict(result), indent=2))
    else:
        print(human(result))
    has_changes = bool(result.added or result.removed or result.retimed
                       or result.moved or result.shifted)
    return 1 if has_changes else 0


if __name__ == "__main__":
    sys.exit(main())
