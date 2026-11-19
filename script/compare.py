"""Runs proselint and this style over the same files and reports where they
disagree.

    .venv/bin/python compare.py [-v] <file>...

Set VALE to test a particular binary. Exits 1 on any difference.

proselint reads every file as plain text, so pass plain text: a Markdown
file is copied to a `.txt` first, which keeps Vale from skipping its code.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

from proselint.checks import __register__
from proselint.config import DEFAULT, Config
from proselint.registry import CheckRegistry
from proselint.tools import LintFile

from generate import NAMES

HERE = Path(__file__).parent
PATHS = {
    name + suffix: path
    for path, names in NAMES.items()
    for name in names
    for suffix in ("", "Nested")
}

CheckRegistry().register_many(__register__)

# proselint stops at 1,000 findings by default.
CONFIG = Config(max_errors=10**9, checks=DEFAULT["checks"])


def squash(text: str) -> str:
    return " ".join(text.split()).lower()


def original(path: Path) -> tuple[list[tuple], LintFile]:
    lint = LintFile(path)
    found = []
    for result in lint.lint(CONFIG):
        start, end = result.check_result.span
        found.append(
            (
                result.pos[0],
                result.pos[1],
                result.check_result.check_path,
                squash(lint.content[start:end]),
            )
        )
    return found, lint


def offset(lint: LintFile, line: int, col: int) -> int:
    """Where a line and column sit in the text proselint read."""
    return lint.line_bounds[line - 1] + col


def vale(paths: list[Path]) -> dict[Path, list[tuple]]:
    with tempfile.TemporaryDirectory() as tmp:
        config = Path(tmp) / ".vale.ini"
        config.write_text(
            f"StylesPath = {HERE.parent}\nMinAlertLevel = suggestion\n\n"
            "[*]\nBasedOnStyles = proselint\n"
        )
        run = subprocess.run(
            [
                os.environ.get("VALE", "vale"),
                "--no-global",
                "--no-exit",
                "--output=JSON",
                f"--config={config}",
                *map(str, paths),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
    if not run.stdout.strip().startswith("{"):
        sys.exit(run.stderr or run.stdout)

    found: dict[Path, list[tuple]] = {}
    for name, alerts in json.loads(run.stdout).items():
        found[Path(name).resolve()] = [
            (
                a["Line"],
                a["Span"][0],
                PATHS[a["Check"].split(".", 1)[1]],
                a["Match"],
            )
            for a in alerts
        ]
    return found


def embedded(lines: list[str], finding: tuple) -> bool:
    """Whether a finding starts or ends in the middle of a word."""
    line, col, _path, text = finding
    row = lines[line - 1]
    start, end = col - 1, col - 1 + len(text)
    word = re.compile(r"\w")
    before = start > 0 and word.match(row[start - 1]) and word.match(row[start])
    after = end < len(row) and word.match(row[end - 1]) and word.match(row[end])
    return bool(before or after)


def main() -> None:
    args = sys.argv[1:]
    verbose = bool(args) and args[0] == "-v"
    sources = [Path(a).resolve() for a in args[verbose:]]

    with tempfile.TemporaryDirectory() as tmp:
        files = []
        for index, source in enumerate(sources):
            if source.suffix == ".txt":
                files.append(source)
                continue
            copy = Path(tmp).resolve() / f"{index}-{source.stem}.txt"
            shutil.copyfile(source, copy)
            files.append(copy)

        ours = vale(files)
        total = Counter()
        failed = False

        for source, file in zip(sources, files):
            lines = file.read_text().splitlines()
            found, lint = original(file)
            want = Counter(found)
            raw = {}
            for line, col, path, text in ours.get(file, []):
                raw.setdefault((line, col, path, squash(text)), text)
            got = Counter(
                (line, col, path, squash(text))
                for line, col, path, text in ours.get(file, [])
            )
            missing = sorted((want - got).elements())
            extra = sorted((got - want).elements())

            # proselint finds a listed word inside a longer one whenever the
            # word also stands alone somewhere in the file.
            inside = [m for m in missing if embedded(lines, m)]
            # A phrase split across lines: Vale reads it, proselint cannot.
            wrapped = [e for e in extra if "\n" in raw[e]]
            # proselint pairs quotes across the whole file, single ones too,
            # and drops what falls between them.
            quoted = [
                e
                for e in extra
                if e not in wrapped
                and lint.is_quoted_pos(offset(lint, e[0], e[1]))
            ]
            missing = [m for m in missing if m not in inside]
            extra = [e for e in extra if e not in wrapped and e not in quoted]
            bad = bool(missing or extra)
            failed = failed or bad

            total["proselint"] += sum(want.values())
            total["vale"] += sum(got.values())
            total["missing"] += len(missing)
            total["extra"] += len(extra)
            total["wrapped"] += len(wrapped)
            total["inside"] += len(inside)
            total["quoted"] += len(quoted)

            if bad or verbose:
                try:
                    name = source.relative_to(Path.cwd())
                except ValueError:
                    name = source
                print(
                    f"{'FAIL' if bad else 'ok  '} {name}: proselint"
                    f" {sum(want.values())}, vale {sum(got.values())},"
                    f" missing {len(missing)}, extra {len(extra)},"
                    f" wrapped {len(wrapped)}, inside a word {len(inside)},"
                    f" quoted {len(quoted)}"
                )
            for sign, items in (("-", missing), ("+", extra)):
                for line, col, path, text in items:
                    print(f'  {sign} {line}:{col} {path} "{text}"')
            if verbose:
                for line, col, path, text in inside:
                    print(f'  ^ {line}:{col} {path} "{text}"')
                for line, col, path, text in wrapped:
                    print(f'  ~ {line}:{col} {path} "{text}"')
                for line, col, path, text in quoted:
                    print(f'  q {line}:{col} {path} "{text}"')

    print(
        f"{len(sources)} files: proselint {total['proselint']}, vale"
        f" {total['vale']}, missing {total['missing']}, extra"
        f" {total['extra']}, wrapped {total['wrapped']}, inside a word"
        f" {total['inside']}, quoted {total['quoted']}"
    )
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
