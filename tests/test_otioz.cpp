// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "utils.h"

#include <opentimelineio/bundle.h>
#include <opentimelineio/clip.h>
#include <opentimelineio/externalReference.h>
#include <opentimelineio/timeline.h>
#include <opentimelineio/track.h>

#include <fstream>

using namespace OTIO_NS;
using namespace OTIO_NS::bundle;

void create_file(std::filesystem::path const& path)
{
    std::ofstream fs(path);
}

SerializableObject::Retainer<Timeline> create_simple_timeline()
{
    SerializableObject::Retainer<Timeline> tl(new Timeline);

    SerializableObject::Retainer<Track> tr = new Track();
    tl->tracks()->append_child(tr);

    SerializableObject::Retainer<Clip> cl = new Clip();
    tr->append_child(cl);

    return tl;
}

void compare_filenames(Timeline* a, Timeline* b)
{
    const auto a_clips = a->find_clips();
    const auto b_clips = b->find_clips();
    assertEqual(a_clips.size(), b_clips.size());

    for (size_t i = 0; i < a_clips.size(); ++i)
    {
        auto a_ref = dynamic_cast<ExternalReference*>(a_clips[i]->media_reference());
        auto b_ref = dynamic_cast<ExternalReference*>(b_clips[i]->media_reference());
        assertNotNull(a_ref);
        assertNotNull(b_ref);

        assertEqual(
            std::filesystem::u8path(a_ref->target_url()).filename(),
            std::filesystem::u8path(b_ref->target_url()).filename());
    }
}

int
main(int argc, char** argv)
{
    Tests tests;

    tests.add_test("test_otioz_round_trip", [] {
        auto tl = create_simple_timeline();
        SerializableObject::Retainer<ExternalReference> ref =
            new ExternalReference("video.mov");
        tl->find_clips().front()->set_media_reference(ref);
        
        TempDir temp;
        create_file(temp.path() / ref->target_url());
        
        std::string const otioz_path =
            (temp.path() / "round_trip.otioz").u8string();
        WriteOptions options;
        options.relative_media_path = temp.path().u8string();
        assertTrue(write_otioz(tl, otioz_path, options));
        
        auto result = dynamic_cast<Timeline*>(read_otioz(otioz_path));
        assertNotNull(result);
        compare_filenames(tl, result);
    });

    tests.run(argc, argv);
    return 0;
}
