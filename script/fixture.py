"""Writes ../fixtures/phrases.txt: a match for every pattern proselint has,
one to a paragraph, so compare.py exercises all of them.
"""

from __future__ import annotations

import random
import re
from pathlib import Path

import exrex

from proselint.tools import QUOTE_PATTERN, SEPARATORS, check_matching_quotes

from generate import units

CLOSERS = {"“": "”", "”": "“", "‘": "’", "’": "‘"}


def balanced(paragraph: str) -> str:
    """Close a quote the paragraph leaves open, as proselint tracks them."""
    text = f"\n{paragraph}\n"
    pending = None
    for match in QUOTE_PATTERN.finditer(text):
        char, index = match.group(0), match.start()
        if pending is None:
            if text[index - 1] in SEPARATORS:
                pending = char
        elif check_matching_quotes((pending, char)) and text[index + 1] in SEPARATORS:
            pending = None
    if pending is None:
        return paragraph
    # On a line of its own, so it closes the quote without framing the match.
    return f"{paragraph}\n{CLOSERS.get(pending, pending)}"

HERE = Path(__file__).parent


def example(pattern: str) -> str:
    """One string the pattern matches."""
    pattern = re.sub(r"\\[bB]", "", pattern)
    pattern = pattern.replace(r"\x{2014}", "—").replace(r"\x{2013}", "–")
    pattern = re.sub(r"\(\?<?[=!][^)]*\)", "", pattern)
    pattern = pattern.replace(r"\s+", " ").replace(r"\s", " ")
    pattern = pattern.replace(r"\W?", "")
    return exrex.getone(pattern, limit=3)


def main() -> None:
    random.seed(0)
    out = ["Phrases", ""]
    for unit in units():
        spec, kind = unit["spec"], unit["kind"]
        if kind in ("but", "consistency") or unit["ppm"]:
            continue
        if kind == "simple":
            patterns = [spec.pattern]
        elif kind == "forms":
            patterns = list(spec.items)
        else:
            patterns = list(spec.items)
        for pattern in patterns:
            if "\\1" in pattern:
                continue
            out += [balanced(f"We saw {example(pattern).strip()} there."), ""]

    target = HERE.parent / "fixtures" / "phrases.txt"
    target.parent.mkdir(exist_ok=True)
    target.write_text("\n".join(out))
    print(f"wrote {target.name}: {len(out) // 2} paragraphs")


if __name__ == "__main__":
    main()
