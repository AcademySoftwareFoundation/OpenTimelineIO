#!/usr/bin/env python
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Run Ruff formatting followed by the project's quote and comma fixes."""

import argparse
import ast
import io
import shutil
import subprocess
import tempfile
import tokenize
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def remove_list_trailing_commas(source):
    """Remove commas before list closers, preserving tuples and subscript syntax."""
    lines = source.splitlines(keepends=True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    tokens = [
        token
        for token in tokenize.generate_tokens(io.StringIO(source).readline)
        if token.type
        not in {
            tokenize.COMMENT,
            tokenize.NL,
            tokenize.NEWLINE,
            tokenize.INDENT,
            tokenize.DEDENT,
            tokenize.ENDMARKER,
        }
    ]
    by_end = {token.end: index for index, token in enumerate(tokens)}
    remove = set()
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.List):
            continue
        # AST columns are UTF-8 byte offsets; tokenize columns are characters.
        end_column = len(
            lines[node.end_lineno - 1]
            .encode("utf-8")[: node.end_col_offset]
            .decode("utf-8")
        )
        index = by_end.get((node.end_lineno, end_column))
        if index is None or index == 0 or tokens[index].string != "]":
            continue
        comma = tokens[index - 1]
        if comma.string == ",":
            remove.add(offsets[comma.start[0] - 1] + comma.start[1])
    for offset in sorted(remove, reverse=True):
        source = source[:offset] + source[offset + 1 :]
    return source


def python_files(root, ruff):
    selected = subprocess.check_output(
        [ruff, "check", "--show-files", "."], cwd=root, text=True
    ).splitlines()
    return [Path(name).resolve().relative_to(root.resolve()) for name in selected]


def format_tree(root, ruff):
    # The comma rule intentionally runs after formatting. Disable the formatter's
    # compatibility warning for this step, without disabling the final lint rule.
    subprocess.run(
        [ruff, "format", "--config", 'lint.ignore = ["Q000", "COM819"]', "."],
        cwd=root,
        check=True,
    )
    for name in python_files(root, ruff):
        if name.suffix in {".py", ".pyi"}:
            path = root / name
            source = path.read_text(encoding="utf-8")
            formatted = remove_list_trailing_commas(source)
            if source != formatted:
                path.write_text(formatted, encoding="utf-8")
    subprocess.run([ruff, "check", "--fix", "."], cwd=root, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="Check without editing files"
    )
    args = parser.parse_args()
    ruff = shutil.which("ruff")
    if ruff is None:
        parser.error("Ruff is required; run this command with uv run --only-group lint")

    if not args.check:
        format_tree(ROOT, ruff)
        return 0

    # Check the combined result, not the formatter's intermediate trailing commas.
    # Use Ruff's own file selection so exclusions match local formatting exactly.
    files = python_files(ROOT, ruff)
    with tempfile.TemporaryDirectory(prefix="otio-format-") as folder:
        staged = Path(folder)
        for name in [Path("pyproject.toml"), Path(".gitignore"), *files]:
            target = staged / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        format_tree(staged, ruff)
        changed = [
            name
            for name in files
            if (ROOT / name).read_bytes() != (staged / name).read_bytes()
        ]

    if changed:
        for name in changed:
            print(f"Would reformat: {name}")
        print("Run make format-python to apply the project formatting pipeline.")
        return 1
    print("Python formatting is up to date.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
