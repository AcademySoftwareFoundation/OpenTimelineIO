#!/usr/bin/env python
#
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project


"""Generate the OpenTimelineIO Core Specification.

The specification is assembled from two sources:

1. The *code* -- every serializable schema object, its fields, field types,
   default values, inheritance, and the semantic docstrings carried by the
   bindings.  This half is produced by reusing the model builder from
   :mod:`autogen_serialized_datamodel`.

2. A curated markdown *overlay* -- the human-authored narrative (introduction,
   conventions, metadata conventions, root objects, JSON serialization) and the
   per-object integrator usage guidance that does not belong in terse API
   docstrings.

The overlay declares the ordering and grouping of the object model via
HTML-comment directives, e.g.::

    <!-- @preamble -->
    # OpenTimelineIO Core Specification
    ...narrative...

    <!-- @section Object Model -->
    ...section intro...

    <!-- @object Timeline -->
    ...usage guidance for Timeline...

    <!-- @appendix -->
    ## JSON Serialization
    ...

Every data-model schema object must be referenced by exactly one ``@object``
directive and every ``@object`` must name a real schema object; otherwise
generation fails.  This keeps the specification honest: adding a new schema to
the code forces a matching entry in the overlay.

Run with ``make spec`` (dryrun) or ``make spec-update`` (write the baseline).
The generated document is verified by the unit test suite.
"""

import argparse
import os
import re
import sys

from opentimelineio.console import autogen_serialized_datamodel as asd


# Plugin-infrastructure classes are not part of the editorial data model and
# are intentionally excluded from the specification (the spec, like the
# serialized-schema doc, omits SchemaDef plugins).
SPEC_SKIP_OBJECTS = {
    "Adapter",
    "HookScript",
    "MediaLinker",
    "PluginManifest",
    "SchemaDef",
}

# Default locations, relative to the repository root.
DEFAULT_OVERLAY = os.path.join(
    "docs", "spec", "core-specification-overlay.md"
)
DEFAULT_OUTPUT = os.path.join(
    "docs", "spec", "otio-core-specification.md"
)

_DIRECTIVE_RE = re.compile(r"^<!--\s*@(\S+)(?:\s+(.*?))?\s*-->\s*$")

# RST roles that leak in from C++/python docstrings; rewrite to plain markdown
# inline code so the specification reads cleanly.
_RST_ROLE_RE = re.compile(r":[a-z:]+:`~?\.?([^`]+)`")

# RST inline literals (``text``) -> markdown inline code (`text`).
_RST_LITERAL_RE = re.compile(r"``([^`]+)``")


def _parsed_args():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-i",
        "--overlay",
        default=DEFAULT_OVERLAY,
        help="Path to the curated markdown overlay.",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-d",
        "--dryrun",
        action="store_true",
        default=False,
        help="Print the generated specification instead of writing it.",
    )
    group.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="Write the generated specification to this path.",
    )
    return parser.parse_args()


def _clean_docstring(text):
    """Rewrite RST inline markup to markdown: roles (``:class:`~Foo```) and
    inline literals (````text````) both become `` `text` ``."""
    if not text:
        return ""
    text = _RST_ROLE_RE.sub(r"`\1`", text)
    text = _RST_LITERAL_RE.sub(r"`\1`", text)
    return text.strip()


def _parse_overlay(text):
    """Parse the overlay into an ordered list of ``(directive, arg, body)``.

    Content appearing before the first directive is treated as a file header
    (e.g. license, authoring instructions) and is not emitted.
    """
    segments = []
    directive, arg, body = "header", None, []
    for line in text.splitlines():
        match = _DIRECTIVE_RE.match(line)
        if match:
            segments.append((directive, arg, "\n".join(body).strip()))
            directive, arg = match.group(1), match.group(2)
            body = []
        else:
            body.append(line)
    segments.append((directive, arg, "\n".join(body).strip()))
    return segments


def _index_model(model):
    """Map each schema object's base name (e.g. ``Clip``) to ``(class, entry,
    module path)``."""
    index = {}
    for cl, entry in model.items():
        base = entry["OTIO_SCHEMA"].rsplit(".", 1)[0]
        modobj = cl.__module__
        if modobj in ("opentimelineio._opentime", "opentimelineio._otio"):
            modobj = asd._remap_to_python_modules(cl)
        modpath = ".".join(modobj.split(".")[:2]) + "." + cl.__name__
        index[base] = (cl, entry, modpath)
    return index


def _render_object(name, index, prose):
    """Render the reference block for a single schema object.

    Layout: heading, code-derived metadata (schema/module/inheritance), the
    semantic definition (from the code docstring), the curated usage guidance
    (``prose`` from the overlay), then the field reference.
    """
    cl, entry, modpath = index[name]

    lines = ["### {}".format(name), ""]
    lines.append("- *schema*: `{}`".format(entry["OTIO_SCHEMA"]))
    lines.append("- *module*: `{}`".format(modpath))

    chain = asd._inheritance_chain(cl)
    if chain:
        lines.append(
            "- *inherits from*: {}".format(
                " -> ".join("`{}`".format(c) for c in chain)
            )
        )
    lines.append("")

    docstring = _clean_docstring(cl.__doc__)
    if docstring:
        lines.append(docstring)
        lines.append("")

    if prose:
        lines.append(prose.strip())
        lines.append("")

    fields = sorted(
        (k, v) for k, v in entry.items()
        if k not in asd.SKIP_KEYS and isinstance(v, dict)
    )
    if fields:
        lines.append("#### Fields")
        lines.append("")
        for key, field in fields:
            typeinfo = asd._format_typeinfo(field, include_default=True)
            helpstr = _clean_docstring(field["help"])
            lines.append(
                "- *{key}*{typeinfo}{sep}{help}".format(
                    key=key,
                    typeinfo=typeinfo,
                    sep=": " if helpstr else "",
                    help=helpstr,
                )
            )
        lines.append("")

    return "\n".join(lines)


def generate_specification(overlay_text):
    """Assemble the full specification markdown from the overlay + the model."""
    model = asd._generate_model()
    index = _index_model(model)
    segments = _parse_overlay(overlay_text)

    documented = [
        arg for directive, arg, _ in segments if directive == "object"
    ]

    # Validate the overlay against the code, in both directions.
    unknown = [name for name in documented if name not in index]
    if unknown:
        raise ValueError(
            "overlay documents unknown schema object(s): "
            + ", ".join(sorted(unknown))
        )

    expected = {
        name for name in index
        if name not in SPEC_SKIP_OBJECTS
    }
    missing = sorted(expected - set(documented))
    if missing:
        raise ValueError(
            "the following schema object(s) have no overlay @object entry "
            "(add them to {} or to SPEC_SKIP_OBJECTS): {}".format(
                DEFAULT_OVERLAY, ", ".join(missing)
            )
        )

    out = []
    for directive, arg, body in segments:
        if directive == "header":
            continue  # file header / authoring instructions; not emitted
        elif directive == "preamble":
            if body:
                out.append(body)
        elif directive == "section":
            out.append("## {}".format(arg))
            if body:
                out.append(body)
        elif directive == "object":
            out.append(_render_object(arg, index, body))
        elif directive == "appendix":
            if body:
                out.append(body)
        else:
            raise ValueError(
                "unknown overlay directive: @{}".format(directive)
            )

    # single trailing newline, blank line between blocks
    return "\n\n".join(block.strip() for block in out if block.strip()) + "\n"


def generate_and_write_specification(overlay_path=None):
    """Read the overlay and return the generated specification text."""
    overlay_path = overlay_path or DEFAULT_OVERLAY
    with open(overlay_path) as fi:
        return generate_specification(fi.read())


def main():
    args = _parsed_args()
    spec = generate_and_write_specification(args.overlay)

    if args.dryrun:
        sys.stdout.write(spec)
        return

    if not args.output:
        sys.stderr.write(
            "ERROR: specify --output PATH or --dryrun\n"
        )
        sys.exit(1)

    with open(args.output, "w") as fo:
        fo.write(spec)
    print("wrote specification to {}".format(args.output))


if __name__ == "__main__":
    main()
