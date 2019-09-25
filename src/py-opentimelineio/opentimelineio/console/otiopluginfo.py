#!/usr/bin/env python
#
# copyright 2019 pixar animation studios
#
# licensed under the apache license, version 2.0 (the "apache license")
# with the following modification; you may not use this file except in
# compliance with the apache license and the following modification to it:
# section 6. trademarks. is deleted and replaced with:
#
# 6. trademarks. this license does not grant permission to use the trade
#    names, trademarks, service marks, or product names of the licensor
#    and its affiliates, except as required to comply with section 4(c) of
#    the license and to reproduce the content of the notice file.
#
# you may obtain a copy of the apache license at
#
#     http://www.apache.org/licenses/license-2.0
#
# unless required by applicable law or agreed to in writing, software
# distributed under the apache license with the above modification is
# distributed on an "as is" basis, without warranties or conditions of any
# kind, either express or implied. see the apache license for the specific
# language governing permissions and limitations under the apache license.
#

"""Print information about the OTIO plugin ecosystem."""

import argparse
import fnmatch
import opentimelineio as otio


OTIO_PLUGIN_TYPES = [
    'all',
    'adapters',
    'media_linkers',
    'schemadefs',
    'hook_scripts'
]


def _parsed_args():
    """ parse commandline arguments with argparse """

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '-l',
        '--list',
        type=str,
        default='all',
        nargs='+',
        choices=OTIO_PLUGIN_TYPES,
        help=(
            'Comma separated list of which kinds of plugins to print info on.'
        )
    )
    parser.add_argument(
        '-a',
        '--attribs',
        type=str,
        default=['*'],
        nargs='+',
        help=(
            'Comma separated list of globs of which attributes to print info'
            ' on.'
        )

    )
    parser.add_argument(
        'plugpattern',
        type=str,
        default='*',
        help='Only print information about plugins that match this glob.'
    )

    return parser.parse_args()


def _supported_features_formatted(feature_map):
    print("    explicit supported features:")
    for thing, args in feature_map.items():
        print("      {} args: {}".format(thing, args['args']))
    extra_features = []
    for kind in ["read", "write"]:
        if (
            "{}_from_string".format(kind) in feature_map
            and "{}_from_file".format(kind) not in feature_map
        ):
            extra_features.append(
                "{0}_from_file (calls: {0}_from_string)".format(kind)
            )

    if extra_features:
        print("    implicit supported features:")
        for feat in extra_features:
            print("      {}".format(feat))


_FORMATTER = {
    "supported features": _supported_features_formatted
}

_FIELDS_TO_SKIP = frozenset(["name"])


def main():
    """  main entry point  """
    args = _parsed_args()

    plugin_types = args.list

    if 'all' in plugin_types:
        # all means all but 'all'
        plugin_types = OTIO_PLUGIN_TYPES[1:]

    # load all the otio plugins
    active_plugin_manifest = otio.plugins.ActiveManifest()

    # list the loaded manifests
    print("Manifests loaded:")
    for mf in active_plugin_manifest.source_files:
        print("  {}".format(mf))

    for pt in plugin_types:
        print("")
        print("{}:".format(pt))
        plugin_by_type = getattr(active_plugin_manifest, pt)
        for plug in plugin_by_type:
            if not fnmatch.filter([plug.name], args.plugpattern):
                continue

            print("  {}".format(plug.name))
            info = plug.plugin_info_map()
            for thing, val in info.items():
                if thing in _FIELDS_TO_SKIP:
                    continue
                if thing in _FORMATTER:
                    _FORMATTER[thing](val)
                    continue

                print("    {}: {}".format(thing, val))

        if not plugin_by_type:
            print("    (none found)")


if __name__ == '__main__':
    main()
