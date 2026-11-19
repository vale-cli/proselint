"""Generates the rules in ../proselint from the checks proselint ships.

    uv venv .venv && uv pip install --python .venv/bin/python -r requirements.txt
    .venv/bin/python generate.py

The version comes from requirements.txt, so the rules track whatever
proselint release is pinned there.
"""

from __future__ import annotations

import json
import re
import sys
from importlib.metadata import version
from pathlib import Path

import yaml
from proselint.checks import __register__ as REGISTER
from proselint.checks.misc import but
from proselint.config import DEFAULT
from proselint.registry.checks import Check, Padding, types

HERE = Path(__file__).parent
OUT = HERE.parent / "proselint"
VERSION = version("proselint")

# Each proselint check path and the rules it becomes. A path needs a second
# name when its checks differ in message, case, or padding.
NAMES = {
    "annotations.misc": ["Annotations"],
    "archaism": ["Archaisms"],
    "cliches.hell": ["ClichesHell"],
    "cliches.misc.garner": ["ClichesGarner"],
    "cliches.misc.write_good": ["Cliches"],
    "cliches.misc.gnu_diction": ["ClichesDiction"],
    "dates_times.am_pm.lowercase_periods": ["DateCase"],
    "dates_times.am_pm.spacing": ["DateSpacing"],
    "dates_times.am_pm.midnight_noon": ["DateMidnight", "DateRedundancy"],
    "dates_times.dates.decade_apostrophes": ["DateDecades", "DateDecadesFull"],
    "dates_times.dates.dash_and_from": ["DateRange"],
    "dates_times.dates.month_year_comma": ["DateMonthComma"],
    "dates_times.dates.month_of_year": ["DateMonthOf"],
    "hedging": ["Hedging"],
    "industrial_language.airlinese": ["Airlinese"],
    "industrial_language.bureaucratese": ["Bureaucratese"],
    "industrial_language.chatspeak": ["Chatspeak"],
    "industrial_language.commercialese": ["Commercialese"],
    "industrial_language.corporate_speak": ["CorporateSpeak"],
    "industrial_language.jargon": ["Jargon"],
    "lexical_illusions": ["LexicalIllusions"],
    "malapropisms": ["Malapropisms"],
    "misc.apologizing": ["Apologizing"],
    "misc.back_formations": ["BackFormations"],
    "misc.but": ["But"],
    "misc.capitalization.terms": ["Capitalization"],
    "misc.capitalization.seasons": ["CapitalizationSeasons"],
    "misc.capitalization.months": ["CapitalizationMonths"],
    "misc.capitalization.days": ["CapitalizationDays"],
    "misc.composition": ["Composition", "CompositionPatterns"],
    "misc.currency": ["Currency"],
    "misc.debased": ["Debased"],
    "misc.false_plurals.misc": ["FalsePlurals"],
    "misc.false_plurals.kudos": ["Kudos"],
    "misc.greylist": ["Greylist"],
    "misc.illogic": ["Illogic"],
    "misc.illogic.coin": ["IllogicCoin"],
    "misc.illogic.collusion": ["IllogicCollusion"],
    "misc.inferior_superior": ["InferiorSuperior"],
    "misc.institution_name": ["InstitutionName"],
    "misc.latin": ["Latin"],
    "misc.many_a": ["ManyA"],
    "misc.metadiscourse": ["Metadiscourse"],
    "misc.narcissism": ["Narcissism"],
    "misc.not_guilty": ["NotGuilty"],
    "misc.phrasal_adjectives.ly": ["PhrasalAdjectivesLy"],
    "misc.phrasal_adjectives.examples": ["PhrasalAdjectives"],
    "misc.preferred_forms": [
        "PreferredForms",
        "PreferredFormsMeantime",
        "PreferredFormsMeantimeInner",
    ],
    "misc.pretension": ["Pretension"],
    "misc.professions": ["Professions"],
    "misc.scare_quotes": ["ScareQuotes"],
    "misc.suddenly": ["Suddenly"],
    "misc.tense_present": ["TensePresent"],
    "misc.waxed": ["Waxed"],
    "misc.whence": ["Whence"],
    "mixed_metaphors.bottleneck": ["MixedMetaphorsBottleneck"],
    "mixed_metaphors.misc": ["MixedMetaphors"],
    "mondegreens": ["Mondegreens"],
    "needless_variants": ["Needless"],
    "nonwords": ["Nonwords"],
    "oxymorons": ["Oxymorons"],
    "psychology.lie_detector": ["LieDetector"],
    "psychology.p_equals_zero": ["P-Value"],
    "psychology.mental_telepathy": ["MentalTelepathy"],
    "redundancy.misc.wallace": ["RedundancyWallace"],
    "redundancy.misc.garner": ["RedundancyGarner", "RedundancyGarnerPatterns"],
    "redundancy.misc.nordquist": ["RedundancyNordquist"],
    "redundancy.misc.after_the_deadline": ["Redundancy"],
    "redundancy.ras_syndrome": ["RASSyndrome"],
    "skunked_terms": ["Skunked"],
    "social_awareness.lgbtq.terms": ["LGBTTerms"],
    "social_awareness.lgbtq.offensive": ["LGBTOffensive"],
    "social_awareness.nword": ["NWord"],
    "social_awareness.sexism": ["GenderBias", "GenderBiasForms"],
    "spelling.able_atable": ["SpellingAbleAtable"],
    "spelling.able_ible": ["SpellingAbleIble"],
    "spelling.ally_ly": ["SpellingAllyLy"],
    "spelling.ance_ence": ["SpellingAnceEnce"],
    "spelling.athletes": ["SpellingAthletes"],
    "spelling.consistency": ["Spelling"],
    "spelling.ely_ly": ["SpellingElyLy"],
    "spelling.em_im_en_in": ["SpellingEmIm"],
    "spelling.er_or": ["SpellingErOr"],
    "spelling.in_un": ["SpellingInUn"],
    "spelling.misc": ["SpellingMisc", "SpellingTill"],
    "spelling.ve_of": ["SpellingVeOf"],
    "terms.animal_adjectives": ["AnimalLabels"],
    "terms.denizen_labels.garner": ["DenizenLabels"],
    "terms.denizen_labels.norris": ["DenizenLabelsNorris"],
    "terms.eponymous_adjectives": ["EponymousAdjectives"],
    "terms.venery": ["GroupTerms"],
    "typography.diacritical_marks": ["Diacritical"],
    "typography.punctuation.misplaced": ["EtAl"],
    "typography.punctuation.exclamation": ["Exclamation"],
    "typography.punctuation.hyperbole": ["Hyperbole"],
    "typography.punctuation.spacing": ["SentenceSpacingMixed"],
    "typography.symbols.ellipsis": ["Ellipsis"],
    "typography.symbols.copyright": ["Copyright"],
    "typography.symbols.trademark": ["Trademark", "RegisteredTrademark"],
    "typography.symbols.sentence_spacing": ["SentenceSpacing"],
    "typography.symbols.multiplication": ["Multiplication"],
    "typography.symbols.curly_quotes": ["CurlyQuotes"],
    "uncomparables": ["Uncomparables", "UncomparablesMost"],
    "weasel_words.very": ["Very"],
}

# Rules that were not `error` before keep their level.
LEVELS = {
    "Currency": "warning",
    "DenizenLabels": "warning",
    "GroupTerms": "warning",
    "LGBTOffensive": "warning",
    "LGBTTerms": "warning",
    "Needless": "warning",
    "P-Value": "suggestion",
}

# ---------------------------------------------------------------------------
# Quotes
#
# proselint drops a finding that starts inside a quotation: an opening quote
# after a separator and a closing quote before one. Single quotes only count
# within a line, where an apostrophe is less likely to pass for one.

SEP = r"[ ,.!?:;\r\n-]"
QUOTED = (
    rf'(?!(?<=(?:^|{SEP})["“][^"“”]*)[^"“”]*["”](?={SEP}|$)'
    rf"|(?<=(?:^|{SEP})'[^'\n]*)[^'\n]*'(?={SEP}|$))"
)

# ---------------------------------------------------------------------------
# Reading the checks


def units() -> list[dict]:
    """Flatten every enabled check into the lists and patterns it runs."""
    found: list[dict] = []
    enabled = {k for k, v in DEFAULT["checks"].items() if v}

    def add(kind: str, spec, check: Check) -> None:
        found.append(
            {
                "path": check.path,
                "kind": kind,
                "spec": spec,
                "message": check.message,
                "insensitive": check.engine.opts.case_insensitive,
                "fancy": type(check.engine).__name__ == "Fancy",
                "quotes": check.flags.allow_quotes,
                "ppm": check.flags.ppm_threshold,
                "offset": check.offset[0],
            }
        )

    # A check written as a function builds its lists when it runs, so run it
    # and note what it asks for.
    def record(kind):
        def check(self, _text, check):
            add(kind, self, check)
            return iter(())

        return check

    for cls, kind in (
        (types.Existence, "existence"),
        (types.ExistenceSimple, "simple"),
        (types.PreferredForms, "forms"),
        (types.PreferredFormsSimple, "forms"),
        (types.Consistency, "consistency"),
    ):
        cls.check = record(kind)

    probe = "group bunch wax waxes waxed waxing"
    for check in REGISTER:
        if check.path.split(".")[0] not in enabled:
            continue
        if check.check_type is but._check_but_paragraphs:
            add("but", but.PATTERN, check)
        elif isinstance(check.check_type, tuple):
            check.check_type.check(probe, check)
        else:
            before = len(found)
            list(check.check_type(probe, check))
            if len(found) == before:
                sys.exit(f"{check.path}: a check this script cannot read")

    return found


# ---------------------------------------------------------------------------
# Patterns


def literal(pattern: str) -> bool:
    """Words and spaces only: nothing a wrapped line could change."""
    return re.fullmatch(r"[\w ',-]+", pattern) is not None


def keep_spaces(pattern: str) -> str:
    """Stop Vale from letting a space in a regex match a line break."""
    if literal(pattern):
        return pattern
    out, in_class, i = [], False, 0
    while i < len(pattern):
        c = pattern[i]
        if c == "\\":
            out.append(pattern[i : i + 2])
            i += 2
            continue
        if c == "[":
            in_class = True
        elif c == "]":
            in_class = False
        out.append("[ ]" if c == " " and not in_class else c)
        i += 1
    return "".join(out)


def unicode_words(pattern: str) -> str:
    r"""Python's `\w` is Unicode; Vale's is ASCII."""
    return pattern.replace(r"\w", r"[\pL\pN_]")


# What a check skips at the start of a match, by `offset`.
SKIPPED = {1: [r"\s"], 2: [r"\b[;,] "]}


def lookbehind(pattern: str, offset: int) -> str:
    """Move the part of a match proselint skips into a lookbehind."""
    if offset == 0:
        return pattern
    for prefix in SKIPPED.get(offset, []):
        if pattern.startswith(prefix):
            return f"(?<={prefix}){pattern[len(prefix):]}"
    sys.exit(f"cannot apply offset {offset} to {pattern}")


def pad(pattern: str, padding: Padding) -> str:
    return pattern if padding in WORDS else padding.format(pattern)


WORDS = (Padding.WORDS_IN_TEXT,)


def message(text: str, *, replace: bool = False) -> str:
    """Turn a `str.format` message into the one Vale fills in."""
    text = text.replace("%", "%%")
    count = iter(range(1, 10))

    def slot(match: re.Match) -> str:
        index = int(match.group(1)) + 1 if match.group(1) else next(count)
        return f"%[{index}]s"

    text = re.sub(r"\{(\d?)\}", slot, text)
    if replace:
        # Vale quotes the replacement itself.
        text = text.replace("'%[1]s'", "%[1]s")
    return text


# ---------------------------------------------------------------------------
# Rules


def base(name: str, extends: str, text: str) -> dict:
    return {
        "extends": extends,
        "message": text,
        "link": "https://github.com/amperser/proselint",
        "level": LEVELS.get(name, "error"),
    }


def nested(items: list[str], insensitive: bool, words: bool) -> set[str]:
    """The items that hold another item, or repeat one.

    proselint reports every item that matches and Vale one per position, so
    these go in a rule of their own.
    """
    fold = (lambda s: s.lower()) if insensitive else (lambda s: s)
    plain = [fold(i) for i in items]
    out = set()
    for index, item in enumerate(plain):
        for other_index, other in enumerate(plain):
            if index == other_index:
                continue
            repeat = item == other and other_index < index
            edge = r"\b" if words else ""
            inside = item != other and re.search(
                edge + re.escape(other) + edge, item
            )
            if repeat or inside:
                out.add(items[index])
    return out


def split(rule: dict, key: str) -> list[dict]:
    """Split a rule in two when some of its items overlap others."""
    items = rule[key]
    names = list(items)
    words = not rule.get("nonword")
    inner = nested([strip_guard(n) for n in names], rule["ignorecase"], words)
    inner = {n for n in names if strip_guard(n) in inner}
    repeats = rule.pop("repeats", [])
    if len(set(repeats)) != len(repeats):
        sys.exit(f"items repeated more than twice: {repeats}")
    if not inner and not repeats:
        return [rule]
    if nested([strip_guard(n) for n in inner], rule["ignorecase"], words):
        sys.exit(f"items nested too deeply: {sorted(inner)[:3]}")
    keep = lambda pick: (  # noqa: E731
        {k: v for k, v in items.items() if pick(k)}
        if isinstance(items, dict)
        else [k for k in items if pick(k)]
    )
    return [
        {**rule, key: keep(lambda k: k not in inner)},
        {**rule, key: keep(lambda k: k in inner or k in repeats)},
    ]


def strip_guard(key: str) -> str:
    return key.removesuffix(QUOTED)


def existence(name: str, group: list[dict]) -> dict:
    first = group[0]
    tokens: list[str] = []
    repeats: list[str] = []
    padding = Padding.RAW
    exceptions: list[str] = []
    for unit in group:
        spec = unit["spec"]
        if unit["kind"] == "simple":
            items = [spec.pattern]
        else:
            items, padding = list(spec.items), spec.padding
        exceptions += getattr(spec, "exceptions", ())
        for item in items:
            item = lookbehind(item, unit["offset"])
            if unit["fancy"]:
                item = unicode_words(item)
            token = keep_spaces(pad(item, padding))
            # An item listed twice is reported twice.
            (repeats if token in tokens else tokens).append(token)

    rule = base(name, "existence", message(first["message"]))
    rule["ignorecase"] = first["insensitive"]
    if padding not in WORDS:
        rule["nonword"] = True
    if not first["quotes"]:
        rule["append"] = True
        rule["raw"] = [QUOTED]
    if exceptions:
        rule["exceptions"] = [
            ("(?i)" if first["insensitive"] else "") + e.strip("^$")
            for e in exceptions
        ]
    rule["tokens"] = tokens
    rule["repeats"] = repeats
    return rule


def substitution(name: str, group: list[dict]) -> dict:
    first = group[0]
    swap: dict[str, str] = {}
    padding = first["spec"].padding
    for unit in group:
        for key, value in unit["spec"].items.items():
            key = keep_spaces(pad(lookbehind(key, unit["offset"]), padding))
            if "|" in key:
                key = f"(?:{key})"
            swap[key + QUOTED] = value.replace("|", r"\|")

    rule = base(name, "substitution", message(first["message"], replace=True))
    rule["ignorecase"] = first["insensitive"]
    if padding not in WORDS:
        rule["nonword"] = True
    rule["action"] = {"name": "replace"}
    rule["swap"] = swap
    return rule


def explained(name: str, group: list[dict]) -> dict:
    """One rule for terms that each carry their own message."""
    rule = base(name, "substitution", "%s")
    rule["ignorecase"] = group[0]["insensitive"]
    rule["nonword"] = True
    rule["swap"] = {
        u["spec"].pattern + QUOTED: u["message"].replace("%", "%%")
        for u in group
    }
    return rule


def paragraph_start(name: str, unit: dict) -> dict:
    if unit["spec"] != r"(^|^\n|\n\n)But\b":
        sys.exit("misc.but has changed; update paragraph_start")
    rule = base(name, "existence", message(unit["message"]))
    rule["scope"] = "paragraph"
    rule["nonword"] = True
    rule["tokens"] = [r"\ABut\b"]
    return rule


def script(name: str, text: str, body: str) -> dict:
    rule = base(name, "script", text)
    rule["scope"] = "raw"
    rule["script"] = Block(body)
    return rule


def consistency(name: str, unit: dict) -> dict:
    """Report whichever spelling of a pair the document uses less."""
    flag = "(?i)" if unit["insensitive"] else ""
    pairs = json.dumps([list(p) for p in unit["spec"].term_pairs], ensure_ascii=False)
    parts = unit["message"].split("{}")
    if len(parts) == 3:
        text = f'{json.dumps(parts[0])} + pair[1 - minor] + {json.dumps(parts[1])} + m[0].text + {json.dumps(parts[2])}'
    elif len(parts) == 1:
        text = json.dumps(parts[0])
    else:
        sys.exit(f"{unit['path']}: unexpected message")
    body = f"""text := import("text")

pairs := {pairs}

matches := []
for pair in pairs {{
  a := text.re_find("{flag}" + pair[0], scope, -1)
  b := text.re_find("{flag}" + pair[1], scope, -1)
  if is_undefined(a) || is_undefined(b) {{
    continue
  }}
  // A tie goes against the first spelling.
  minor := len(b) < len(a) ? 1 : 0
  for m in (minor == 1 ? b : a) {{
    matches = append(matches, {{begin: m[0].begin, end: m[0].end, message: {text}}})
  }}
}}
"""
    return script(name, unit["message"].replace("{}", "%s"), body)


def threshold(name: str, unit: dict) -> dict:
    """Report the match that takes the document past a parts-per-million cap."""
    ppm = unit["ppm"]
    text = f"{unit['message']} Surpassed {ppm} ppm."
    flag = "(?i)" if unit["insensitive"] else ""
    body = f"""text := import("text")
math := import("math")

matches := []
found := text.re_find(`{flag}{unit["spec"].pattern}`, scope, -1)
size := len(scope) + 2
if size < 1000 {{
  size = 1000
}}
need := int(math.ceil({ppm} * size / 1000000.0))
if need < 2 {{
  need = 2
}}
if !is_undefined(found) && len(found) >= need {{
  m := found[need - 1][0]
  matches = [{{begin: m.begin, end: m.end}}]
}}
"""
    return script(name, text, body)


def signature(unit: dict) -> tuple:
    spec = unit["spec"]
    padding = getattr(spec, "padding", Padding.RAW)
    # Checks of different types can match the same text, and each reports it.
    single = spec.pattern if unit["kind"] == "simple" else None
    return (
        type(spec).__name__ if unit["kind"] == "forms" else "existence",
        single,
        unit["message"],
        unit["insensitive"],
        padding in WORDS,
        padding,
        unit["quotes"],
        unit["offset"],
    )


def build() -> dict[str, dict]:
    by_path: dict[str, list[dict]] = {}
    for unit in units():
        by_path.setdefault(unit["path"], []).append(unit)

    rules: dict[str, dict] = {}
    for path, found in by_path.items():
        if path not in NAMES:
            sys.exit(f"{path}: new check, add it to NAMES")
        names = list(NAMES[path])
        kind = found[0]["kind"]

        if kind == "but":
            rules[names[0]] = paragraph_start(names[0], found[0])
        elif kind == "consistency":
            rules[names[0]] = consistency(names[0], found[0])
        elif found[0]["ppm"]:
            rules[names[0]] = threshold(names[0], found[0])
        elif path == "misc.greylist":
            rules[names[0]] = explained(names[0], found)
        else:
            groups: dict[tuple, list[dict]] = {}
            for unit in found:
                groups.setdefault(signature(unit), []).append(unit)
            if len(groups) != len(names):
                sys.exit(f"{path}: {len(groups)} rules but {len(names)} names")
            for name, group in zip(names, groups.values()):
                forms = group[0]["kind"] == "forms"
                rule = (substitution if forms else existence)(name, group)
                parts = split(rule, "swap" if forms else "tokens")
                for suffix, part in zip(("", "Nested"), parts):
                    rules[name + suffix] = part

    return rules


class Block(str):
    """A string YAML writes as a literal block."""


yaml.add_representer(
    Block,
    lambda dumper, data: dumper.represent_scalar(
        "tag:yaml.org,2002:str", data, style="|"
    ),
)


def main() -> None:
    rules = build()
    for old in OUT.glob("*.yml"):
        old.unlink()

    header = (
        f"# Generated by script/generate.py from proselint {VERSION}."
        " Do not edit.\n"
    )
    for name, rule in rules.items():
        body = yaml.dump(
            rule, sort_keys=False, allow_unicode=True, width=10**6
        )
        (OUT / f"{name}.yml").write_text(header + body)

    print(f"wrote {len(rules)} rules from proselint {VERSION}")


if __name__ == "__main__":
    main()
