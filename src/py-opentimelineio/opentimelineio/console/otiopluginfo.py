#!/usr/bin/env python
#
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Print information about the OTIO plugin ecosystem."""

import argparse
import fnmatch
import textwrap
import opentimelineio as otio

# on some python interpreters, pkg_resources is not available
try:
    import pkg_resources
except ImportError:
    pkg_resources = None

OTIO_PLUGIN_TYPES = ['all'] + otio.plugins.manifest.OTIO_PLUGIN_TYPES


def _parsed_args():
    """ parse commandline arguments with argparse """

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '-p',
        '--plugin-types',
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
        '-l',
        '--long-docs',
        default=False,
        action="store_true",
        help="Print full docstring instead of just the summary line.",
    )
    parser.add_argument(
        'plugpattern',
        type=str,
        default='*',
        nargs='?',
        help='Only print information about plugins that match this glob.'
    )
    parser.add_argument(
        '--version',
        default=False,
        action="store_true",
        help=(
            "Print the otio and pkg_resource installed plugin version "
            "information to the commandline."
        ),
    )

    return parser.parse_args()


def _supported_features_formatted(feature_map, _):
    if feature_map:
        print("    explicit supported features:")
    for thing, args in feature_map.items():
        print("      {} args: {}".format(thing, args['args']))
    extra_features = []
    for kind in ["read", "write"]:
        if (
            f"{kind}_from_string" in feature_map
            and f"{kind}_from_file" not in feature_map
        ):
            extra_features.append(
                "{0}_from_file (calls: {0}_from_string)".format(kind)
            )

    if extra_features:
        print("    implicit supported features:")
        for feat in extra_features:
            print(f"      {feat}")


def _schemadefs_formatted(feature_map, args):
    print("    SchemaDefs:")
    for sd in feature_map.keys():
        print(f"      {sd}")
        _docs_formatted(feature_map[sd]['doc'], args, indent=8)


def _docs_formatted(docstring, arg_map, indent=4):
    long_docs = arg_map.get('long_docs')

    if long_docs:
        prefix = " " * indent + "doc (long): "
    else:
        prefix = " " * indent + "doc (short): "

    initial_indent = prefix
    subsequent_indent = " " * len(prefix)

    try:
        block = docstring.split("\n")
    except AttributeError:
        raise RuntimeError(
            "Plugin: '{}' is missing a docstring.  Make sure the doctring is "
            "assigned to the __doc__ variable name.".format(arg_map['plugname'])
        )

    fmt_block = []
    for line in block:
        line = textwrap.fill(
            line,
            initial_indent=initial_indent,
            subsequent_indent=subsequent_indent,
            width=len(subsequent_indent) + 80,
        )
        initial_indent = subsequent_indent
        fmt_block.append(line)

    if long_docs:
        text = "\n".join(fmt_block)
    else:
        text = fmt_block[0]

    print(text)


_FORMATTER = {
    "supported features": _supported_features_formatted,
    "SchemaDefs": _schemadefs_formatted,
    "doc": _docs_formatted,
}

_FIELDS_TO_SKIP = frozenset(["name"])


def _print_field(key, val, **args):
    # if attribute doesn't hit any of the user specified patterns
    if (
        not any(fnmatch.filter([key], pt) for pt in args['attribs'])
        or key in _FIELDS_TO_SKIP
    ):
        return

    if key in _FORMATTER:
        _FORMATTER[key](val, args)
        return

    print(f"    {key}: {val}")


def main():
    """  main entry point  """
    args = _parsed_args()

    plugin_types = args.plugin_types

    if 'all' in plugin_types:
        # all means the full list of built in plugins
        plugin_types = otio.plugins.manifest.OTIO_PLUGIN_TYPES

    # load all the otio plugins
    active_plugin_manifest = otio.plugins.ActiveManifest()

    # print version information to the shell
    if args.version:
        print(f"OpenTimelineIO version: {otio.__version__}")

        if pkg_resources:
            pkg_resource_plugins = list(
                pkg_resources.iter_entry_points("opentimelineio.plugins")
            )
            if pkg_resource_plugins:
                print("Plugins from pkg_resources:")
                for plugin in pkg_resource_plugins:
                    print(f"   {plugin.dist}")
            else:
                print("No pkg_resource plugins installed.")

    # list the loaded manifests
    print("Manifests loaded:")
    for mf in active_plugin_manifest.source_files:
        print(f"  {mf}")

    for pt in plugin_types:
        # hooks have special code (see below)
        if pt == "hooks":
            continue

        # header
        print("")
        print(f"{pt}:")

        # filter plugins by the patterns passed in on the command line
        plugin_by_type = getattr(active_plugin_manifest, pt)
        plugins = [
            p for p in plugin_by_type
            if fnmatch.filter([p.name], args.plugpattern)
        ]

        # if nothing is found of that type that matches the filter
        if not plugins:
            print("    (none found)")

        for plug in plugins:
            print(f"  {plug.name}")

            try:
                info = plug.plugin_info_map()
            except Exception as err:
                print(
                    "    ERROR: plugin {} couldn't generate its information"
                    " map: {}\n".format(
                        plug.name,
                        err
                    )
                )
                continue

            for key, val in info.items():
                _print_field(
                    key,
                    val,
                    long_docs=args.long_docs,
                    attribs=args.attribs,
                    plugname=plug.name,
                )

    # hooks aren't really plugin objects, instead they're a mapping of hook
    # to list of hookscripts that will run on that hook
    if "hooks" in plugin_types:
        print("")
        print("hooks:")
        hooknames = fnmatch.filter(
            active_plugin_manifest.hooks.keys(),
            args.plugpattern
        )
        for hookname in hooknames:
            print(f"  {hookname}")
            for hook_script in active_plugin_manifest.hooks[hookname]:
                print(f"    {hook_script}")
            if not active_plugin_manifest.hooks[hookname]:
                print("    (no hook scripts attached)")

        if not hooknames:
            print("  (none found)")


if __name__ == '__main__':
    main()
