// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include <pybind11/pybind11.h>

#include <opentimelineio/urlUtils.h>

using namespace opentimelineio::OPENTIMELINEIO_VERSION;

namespace py = pybind11;

void otio_url_utils_bindings(pybind11::module m)
{
    m.def(
        "url_from_filepath",
        &url_from_filepath,
        "Convert a filesystem path to a file URL.\n"
        "\n"
        "For example:\n"
        "* '/var/tmp/thing.otio' -> 'file:///var/tmp/thing.otio'\n"
        "* 'subdir/thing.otio' -> 'tmp/thing.otio'",
        py::arg("url"));

    m.def(
        "filepath_from_url",
        &filepath_from_url,
        "Convert a file URL to a filesystem path.\n"
        "\n"
        "URLs can either be encoded according to the `RFC 3986` standard or "
        "not. Additionally, Windows mapped drive letter and UNC paths need to "
        "be accounted for when processing URLs.\n"
        "\n"
        "RFC 3986: https://tools.ietf.org/html/rfc3986",
        py::arg("filepath"));
}
