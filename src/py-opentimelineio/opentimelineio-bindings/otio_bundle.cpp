// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include <pybind11/pybind11.h>
#include <pybind11/operators.h>
#include <pybind11/stl.h>

#include "otio_errorStatusHandler.h"

#include <opentimelineio/bundle.h>

using namespace OTIO_NS;
using namespace OTIO_NS::bundle;

namespace py = pybind11;

void otio_bundle_bindings(pybind11::module m)
{
    auto mbundle = m.def_submodule("bundle");
    
    py::enum_<MediaReferencePolicy>(mbundle, "MediaReferencePolicy",
R"docstring(
This enumeration provides the bundle media reference policy.
)docstring")
        .value(
            "error_if_not_file",
            MediaReferencePolicy::error_if_not_file,
            "Return an error if there are any non-file media references.")
        .value(
            "missing_if_not_file",
            MediaReferencePolicy::missing_if_not_file,
            "Replace non-file media references with missing references.")
        .value(
            "all_missing",
            MediaReferencePolicy::all_missing,
            "Replace all media references with missing references.");
    
    py::class_<WriteOptions>(mbundle, "WriteOptions",
R"docstring(
Options for writing bundles.
)docstring")
        .def(py::init<>())
        .def_readwrite(
            "relative_media_path",
            &WriteOptions::relative_media_path,
            "Base directory for resolving relative media reference paths. "
            "If a media reference URL resolves to a relative path, it is resolved "
            "against this directory before being added to the bundle.")
        .def_readwrite(
            "policy",
            &WriteOptions::policy,
            "The media reference policy.")
        .def_readwrite(
            "indent",
            &WriteOptions::indent,
            "Number of spaces for JSON indentation.");
    
    py::class_<ReadOptions>(mbundle, "ReadOptions",
R"docstring(
Options for reading bundles.
)docstring")
        .def(py::init<>())
        .def_readwrite(
            "extract_path",
            &ReadOptions::extract_path,
            "Extract the contents of the otioz bundle to this directory, "
            "which must not already exist.")
        .def_readwrite(
            "absolute_media_reference_paths",
            &ReadOptions::absolute_media_reference_paths,
            "Convert the media reference paths to absolute paths. "
            "If this is set to true for otioz files, an extract_path must also be set.");

    mbundle.def(
        "dry_run",
        [](
            Timeline const*     timeline,
            WriteOptions const& options = WriteOptions())
        {
            return dry_run(timeline, options, ErrorStatusHandler());
        },
        "Calculate the total uncompressed size of the files that would be "
        "written to a bundle, without actually writing it. This is useful for "
        "estimating the disk space required.",
        py::arg("timeline"),
        py::arg("options") = WriteOptions());

    mbundle.def(
        "write_otioz",
        [](
            Timeline const*     timeline,
            std::string const&  path,
            WriteOptions const& options = WriteOptions())
        {
            return write_otioz(timeline, path, options, ErrorStatusHandler());
        },
        "Write a timeline and it's referenced media to an .otioz bundle.",
        py::arg("timeline"),
        py::arg("path"),
        py::arg("options") = WriteOptions());

    mbundle.def(
        "read_otioz",
        [](
            std::string const& path,
            ReadOptions const& options = ReadOptions())
        {
            return read_otioz(path, options, ErrorStatusHandler());
        },
        "Read a timeline from an .otioz bundle.",
        py::arg("path"),
        py::arg("options") = ReadOptions());

    mbundle.def(
        "write_otiod",
        [](
            Timeline const*     timeline,
            std::string const&  path,
            WriteOptions const& options = WriteOptions())
        {
            return write_otiod(timeline, path, options, ErrorStatusHandler());
        },
        "Write a timeline and it's referenced media to an .otiod bundle.",
        py::arg("timeline"),
        py::arg("path"),
        py::arg("options") = WriteOptions());

    mbundle.def(
        "read_otiod",
        [](std::string const& path,
            ReadOptions const& options = ReadOptions())
        {
            return read_otiod(path, options, ErrorStatusHandler());
        },
        "Read a timeline from an .otiod bundle.",
        py::arg("path"),
        py::arg("options") = ReadOptions());
}
