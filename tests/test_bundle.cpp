// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "utils.h"

#include <opentimelineio/bundle.h>
#include <opentimelineio/clip.h>
#include <opentimelineio/externalReference.h>
#include <opentimelineio/generatorReference.h>
#include <opentimelineio/imageSequenceReference.h>
#include <opentimelineio/missingReference.h>
#include <opentimelineio/timeline.h>
#include <opentimelineio/track.h>

#include <fstream>
#include <sstream>

using namespace OTIO_NS;
using namespace OTIO_NS::bundle;

// Utility for creating a simple timeline
SerializableObject::Retainer<Timeline> create_simple_timeline()
{
    SerializableObject::Retainer<Timeline> tl(new Timeline);

    SerializableObject::Retainer<Track> tr = new Track(
        "video",
        TimeRange(0, 48, 24),
        Track::Kind::video);
    tl->tracks()->append_child(tr);

    SerializableObject::Retainer<Clip> cl = new Clip(
        "video clip 1",
        nullptr,
        TimeRange(0, 24, 24));
    tr->append_child(cl);

    cl = new Clip(
        "video clip 2",
        nullptr,
        TimeRange(0, 24, 24));
    tr->append_child(cl);

    tr = new Track(
        "autio",
        TimeRange(0, 48, 24),
        Track::Kind::audio);
    tl->tracks()->append_child(tr);

    cl = new Clip(
        "audio clip 1",
        nullptr,
        TimeRange(0, 24, 48));
    tr->append_child(cl);

    return tl;
}

// Utility to find a clip by name
Clip* find_clip_by_name(Timeline* timeline, std::string const& name)
{
    for (auto clip : timeline->find_clips())
    {
        if (name == clip->name())
        {
            return clip;
        }
    }
    return nullptr;
}

// Utility for creating an empty file
void create_file(std::filesystem::path const& path)
{
    std::filesystem::create_directories(path.parent_path());
    std::ofstream fs(path);
}

// Utility for creating empty files for each media reference
void create_refs(Timeline* timeline, std::filesystem::path const& path)
{
    for (auto const& clip : timeline->find_clips())
    {
        for (auto const& ref : clip->media_references())
        {
            if (auto ext = dynamic_cast<ExternalReference*>(ref.second))
            {
                if (auto const file = file_from_url(ext->target_url()))
                {
                    auto const file_path = std::filesystem::u8path(*file);
                    create_file(file_path.is_relative() ?
                        path / file_path :
                        file_path);
                }
            }
            else if (auto seq = dynamic_cast<ImageSequenceReference*>(ref.second))
            {
                auto const base = file_from_url(seq->target_url_base());
                for (int frame = seq->start_frame();
                    frame <= seq->end_frame();
                    frame += seq->frame_step())
                {
                    std::string file;
                    if (base)
                    {
                        file += *base;
                    }
                    file += seq->target_url_for_image_number(frame);
                    auto const file_path = std::filesystem::u8path(file);
                    create_file(file_path.is_relative() ?
                        path / file_path :
                        file_path);
                }
            }
        }
    }
}

// Utility to compare media reference filenames between timeline
void compare_filenames(Timeline* a, Timeline* b)
{
    const auto a_clips = a->find_clips();
    const auto b_clips = b->find_clips();
    assertEqual(a_clips.size(), b_clips.size());
    for (size_t i = 0; i < a_clips.size(); ++i)
    {
        auto a_ext = dynamic_cast<ExternalReference*>(a_clips[i]->media_reference());
        auto b_ext = dynamic_cast<ExternalReference*>(b_clips[i]->media_reference());
        if (a_ext && b_ext)
        {
            auto const a_file = file_from_url(a_ext->target_url());
            auto const b_file = file_from_url(b_ext->target_url());
            if (a_file && b_file)
            {
                assertEqual(
                    std::filesystem::u8path(*a_file).filename(),
                    std::filesystem::u8path(*b_file).filename());
            }
        }
        auto a_seq = dynamic_cast<ImageSequenceReference*>(a_clips[i]->media_reference());
        auto b_seq = dynamic_cast<ImageSequenceReference*>(b_clips[i]->media_reference());
        if (a_seq && b_seq)
        {
            assertEqual(a_seq->name_prefix(), b_seq->name_prefix());
            assertEqual(a_seq->name_suffix(), b_seq->name_suffix());
        }
    }
}

int
main(int argc, char** argv)
{
    Tests tests;

    tests.add_test("test_otioz_round_trip", [] {
        
        // Create a temp directory
        TempDir temp;

        // Create a timeline and media references
        auto tl = create_simple_timeline();
        find_clip_by_name(tl, "video clip 1")->set_media_reference(
            new ExternalReference("video1.mov"));
        find_clip_by_name(tl, "video clip 2")->set_media_reference(
            new ImageSequenceReference(
                "",
                "render.",
                ".exr",
                0, 1, 24, 0,
                ImageSequenceReference::MissingFramePolicy::error,
                TimeRange(0, 24, 24)));
        find_clip_by_name(tl, "audio clip 1")->set_media_references(
            {
                { "wav", new ExternalReference("audio.wav") },
                { "absolute_path", new ExternalReference(temp.path() / "audio.mp3") },
                { "sub_dir", new ExternalReference("sub_dir/audio.ogg") }
            },
            "wav");
        create_refs(tl, temp.path());
        
        // Write the otioz
        std::string const otioz_path =
            (temp.path() / "round_trip.otioz").u8string();
        WriteOptions write_options;
        write_options.relative_media_path = temp.path().u8string();
        OTIO_NS::ErrorStatus error;
        assertTrue(write_otioz(tl, otioz_path, write_options, &error));
        
        // Read the otioz and compare with the original
        ReadOptions read_options;
        auto const extract_path = temp.path() / "extract";
        read_options.extract_path = extract_path.u8string();
        auto result = dynamic_cast<Timeline*>(read_otioz(
            otioz_path,
            read_options,
            &error));
        assertNotNull(result);
        compare_filenames(tl, result);
        auto const media_path = extract_path / media_dir;
        assertTrue(std::filesystem::exists(media_path / "video1.mov"));
        for (int i = 0; i < 24; ++i)
        {
            std::stringstream ss;
            ss << "render." << i << ".exr";
            assertTrue(std::filesystem::exists(media_path / ss.str()));
        }
        assertTrue(std::filesystem::exists(media_path / "audio.wav"));
        assertTrue(std::filesystem::exists(media_path / "audio.mp3"));
        assertTrue(std::filesystem::exists(media_path / "audio.ogg"));
    });

    tests.add_test("test_otiod_round_trip", [] {
        
        // Create a temp directory
        TempDir temp;

        // Create a timeline and media references
        auto tl = create_simple_timeline();
        find_clip_by_name(tl, "video clip 1")->set_media_reference(
            new ExternalReference("video1.mov"));
        find_clip_by_name(tl, "video clip 2")->set_media_reference(
            new ImageSequenceReference(
                "",
                "render.",
                ".exr",
                0, 1, 24, 0,
                ImageSequenceReference::MissingFramePolicy::error,
                TimeRange(0, 24, 24)));
        find_clip_by_name(tl, "audio clip 1")->set_media_references(
            {
                { "wav", new ExternalReference("audio.wav") },
                { "absolute_path", new ExternalReference(temp.path() / "audio.mp3") },
                { "sub_dir", new ExternalReference("sub_dir/audio.ogg") }
            },
            "wav");
        create_refs(tl, temp.path());
        
        // Write the otiod
        std::string const otiod_path =
            (temp.path() / "round_trip.otiod").u8string();
        WriteOptions options;
        options.relative_media_path = temp.path().u8string();
        OTIO_NS::ErrorStatus error;
        assertTrue(write_otiod(tl, otiod_path, options, &error));
        
        // Read the otiod and compare with the original
        auto result = dynamic_cast<Timeline*>(read_otiod(
            otiod_path,
            ReadOptions(),
            &error));
        assertNotNull(result);
        compare_filenames(tl, result);
    });

    tests.add_test("test_otioz_media_policy", [] {

        // Create a timeline with file and non-file references
        auto tl = create_simple_timeline();
        find_clip_by_name(tl, "video clip 1")->set_media_reference(
            new ExternalReference("video1.mov"));
        find_clip_by_name(tl, "video clip 2")->set_media_reference(
            new GeneratorReference(
                "gradient",
                "gradient",
                TimeRange(0, 24, 24),
                {},
                {
                    { "meta", "data" }
                }));
        
        // error_if_not_file
        {
            TempDir temp;
            create_refs(tl, temp.path());

            std::string const otioz_path =
                (temp.path() / "missing.otioz").u8string();
            WriteOptions options;
            options.relative_media_path = temp.path().u8string();
            options.policy = MediaReferencePolicy::error_if_not_file;
            OTIO_NS::ErrorStatus error;
            assertFalse(write_otioz(tl, otioz_path, options, &error));
        }

        // missing_if_not_file
        {
            TempDir temp;
            create_refs(tl, temp.path());

            std::string const otioz_path =
                (temp.path() / "missing.otioz").u8string();
            WriteOptions options;
            options.relative_media_path = temp.path().u8string();
            options.policy = MediaReferencePolicy::missing_if_not_file;
            OTIO_NS::ErrorStatus error;
            assertTrue(write_otioz(tl, otioz_path, options, &error));
            
            auto result = dynamic_cast<Timeline*>(read_otioz(
                otioz_path,
                ReadOptions(),
                &error));
            assertNotNull(result);
            assertNotNull(dynamic_cast<MissingReference*>(
                find_clip_by_name(result, "video clip 2")->media_reference()));
        }
        
        // all_missing
        {
            TempDir temp;
            create_refs(tl, temp.path());

            std::string const otioz_path =
                (temp.path() / "missing.otioz").u8string();
            WriteOptions options;
            options.relative_media_path = temp.path().u8string();
            options.policy = MediaReferencePolicy::all_missing;
            OTIO_NS::ErrorStatus error;
            assertTrue(write_otioz(tl, otioz_path, options, &error));
            
            auto result = dynamic_cast<Timeline*>(read_otioz(
                otioz_path,
                ReadOptions(),
                &error));
            assertNotNull(result);
            assertNotNull(dynamic_cast<MissingReference*>(
                find_clip_by_name(result, "video clip 1")->media_reference()));
            assertNotNull(dynamic_cast<MissingReference*>(
                find_clip_by_name(result, "video clip 2")->media_reference()));
        }
    });

    tests.add_test("test_otioz_error", [] {

        // Create a temp directory
        TempDir temp;

        // Create a timeline
        auto tl = create_simple_timeline();

        // Write the otioz
        std::string otioz_path =
            (temp.path() / "error.otioz").u8string();
        OTIO_NS::ErrorStatus error;
        assertTrue(write_otioz(tl, otioz_path, WriteOptions(), &error));

        // Write the otioz (error on overwrite)
        assertFalse(write_otioz(tl, otioz_path, WriteOptions(), &error));
        std::filesystem::remove(otioz_path);

        // Write the otioz (error on missing media)
        find_clip_by_name(tl, "video clip 1")->set_media_reference(
            new ExternalReference("video1.mov"));
        assertFalse(write_otioz(tl, otioz_path, WriteOptions(), &error));
        std::filesystem::remove(otioz_path);

        // Write the otioz (error on overwrite media)
        find_clip_by_name(tl, "video clip 2")->set_media_reference(
            new ExternalReference("video2.mov"));
        create_refs(tl, temp.path());
        assertFalse(write_otioz(tl, otioz_path, WriteOptions(), &error));
        std::filesystem::remove(otioz_path);

        // Write the otioz (error on input path)
        otioz_path = (temp.path() / "subdir" / "error.otioz").u8string();
        assertFalse(write_otioz(tl, otioz_path, WriteOptions(), &error));
        std::filesystem::remove(otioz_path);
    });

    tests.add_test("test_otiod_error", [] {

        // Create a temp directory
        TempDir temp;

        // Create a timeline
        auto tl = create_simple_timeline();

        // Write the otiod
        std::string otiod_path =
            (temp.path() / "error.otiod").u8string();
        OTIO_NS::ErrorStatus error;
        assertTrue(write_otiod(tl, otiod_path, WriteOptions(), &error));

        // Write the otiod (error on overwrite)
        assertFalse(write_otiod(tl, otiod_path, WriteOptions(), &error));
        std::filesystem::remove_all(otiod_path);

        // Write the otiod (missing media)
        find_clip_by_name(tl, "video clip 1")->set_media_reference(
            new ExternalReference("video1.mov"));
        assertFalse(write_otiod(tl, otiod_path, WriteOptions(), &error));
        std::filesystem::remove_all(otiod_path);

        // Write the otiod (error on overwrite media)
        find_clip_by_name(tl, "video clip 2")->set_media_reference(
            new ExternalReference("video2.mov"));
        create_refs(tl, temp.path());
        assertFalse(write_otioz(tl, otiod_path, WriteOptions(), &error));
        std::filesystem::remove(otiod_path);

        // Write the otiod (error on input path)
        otiod_path = (temp.path() / "subdir" / "error.otiod").u8string();
        assertFalse(write_otiod(tl, otiod_path, WriteOptions(), &error));
        std::filesystem::remove_all(otiod_path);
    });

    tests.run(argc, argv);
    return 0;
}
