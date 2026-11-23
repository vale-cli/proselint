# proselint [![Build + Test](https://github.com/vale-cli/proselint/actions/workflows/main.yml/badge.svg)](https://github.com/vale-cli/proselint/actions/workflows/main.yml) ![Vale version](https://img.shields.io/badge/vale-%3E%3D%20v3.28.1-blue.svg) ![license](https://img.shields.io/github/license/mashape/apistatus.svg)

> [`proselint`](https://github.com/amperser/proselint/) places the world’s greatest writers and editors by your side, where they whisper suggestions on how to improve your prose.

This repository contains a [Vale-compatible](https://github.com/vale-cli/vale) implementation of the guidelines enforced by the `proselint` ([LICENSE](https://github.com/amperser/proselint/blob/master/LICENSE.md)) linter.

## Getting Started

To get started, add the package to your configuration file (as shown below) and then run `vale sync`.

```ini
StylesPath = styles
MinAlertLevel = suggestion

Packages = proselint

[*]
BasedOnStyles = proselint
```

## Rules

The rules are generated from the checks that `proselint` 0.16.0 ships, with
the same word lists, patterns, and messages. Each check path becomes one
rule, or more when its lists differ in message, case, or matching:

- A `Nested` rule holds the phrases that contain another phrase of the same
  check, or repeat one. `proselint` reports both, and a Vale rule reports one
  match per position.
- `Spelling`, `SentenceSpacingMixed`, and `Exclamation` are `script` rules
  that read the whole file, since they count what the file uses.
- Text in double quotes, or in single quotes on one line, is not reported,
  as in `proselint`. `CurlyQuotes` is the exception there too.

`proselint` leaves its `restricted` checks off, and they have no rules here.

| `proselint` check | Rules |
| ----------------- | ----- |
| `annotations.misc` | `Annotations` |
| `archaism` | `Archaisms` |
| `cliches.hell` | `ClichesHell` |
| `cliches.misc.garner` | `ClichesGarner` |
| `cliches.misc.write_good` | `Cliches`, `ClichesNested` |
| `cliches.misc.gnu_diction` | `ClichesDiction` |
| `dates_times.am_pm.lowercase_periods` | `DateCase` |
| `dates_times.am_pm.spacing` | `DateSpacing` |
| `dates_times.am_pm.midnight_noon` | `DateMidnight`, `DateRedundancy` |
| `dates_times.dates.decade_apostrophes` | `DateDecades`, `DateDecadesFull` |
| `dates_times.dates.dash_and_from` | `DateRange` |
| `dates_times.dates.month_year_comma` | `DateMonthComma` |
| `dates_times.dates.month_of_year` | `DateMonthOf` |
| `hedging` | `Hedging` |
| `industrial_language.airlinese` | `Airlinese` |
| `industrial_language.bureaucratese` | `Bureaucratese` |
| `industrial_language.chatspeak` | `Chatspeak`, `ChatspeakNested` |
| `industrial_language.commercialese` | `Commercialese`, `CommercialeseNested` |
| `industrial_language.corporate_speak` | `CorporateSpeak` |
| `industrial_language.jargon` | `Jargon` |
| `lexical_illusions` | `LexicalIllusions` |
| `malapropisms` | `Malapropisms` |
| `misc.apologizing` | `Apologizing` |
| `misc.back_formations` | `BackFormations` |
| `misc.but` | `But` |
| `misc.capitalization.terms` | `Capitalization` |
| `misc.capitalization.seasons` | `CapitalizationSeasons` |
| `misc.capitalization.months` | `CapitalizationMonths` |
| `misc.capitalization.days` | `CapitalizationDays` |
| `misc.composition` | `Composition`, `CompositionNested`, `CompositionPatterns` |
| `misc.currency` | `Currency` |
| `misc.debased` | `Debased` |
| `misc.false_plurals.misc` | `FalsePlurals` |
| `misc.false_plurals.kudos` | `Kudos` |
| `misc.greylist` | `Greylist` |
| `misc.illogic` | `Illogic` |
| `misc.illogic.coin` | `IllogicCoin` |
| `misc.illogic.collusion` | `IllogicCollusion` |
| `misc.inferior_superior` | `InferiorSuperior` |
| `misc.institution_name` | `InstitutionName` |
| `misc.latin` | `Latin` |
| `misc.many_a` | `ManyA` |
| `misc.metadiscourse` | `Metadiscourse` |
| `misc.narcissism` | `Narcissism` |
| `misc.not_guilty` | `NotGuilty` |
| `misc.phrasal_adjectives.ly` | `PhrasalAdjectivesLy` |
| `misc.phrasal_adjectives.examples` | `PhrasalAdjectives` |
| `misc.preferred_forms` | `PreferredForms`, `PreferredFormsMeantime`, `PreferredFormsMeantimeInner` |
| `misc.pretension` | `Pretension` |
| `misc.professions` | `Professions` |
| `misc.scare_quotes` | `ScareQuotes` |
| `misc.suddenly` | `Suddenly` |
| `misc.tense_present` | `TensePresent` |
| `misc.waxed` | `Waxed` |
| `misc.whence` | `Whence` |
| `mixed_metaphors.bottleneck` | `MixedMetaphorsBottleneck` |
| `mixed_metaphors.misc` | `MixedMetaphors` |
| `mondegreens` | `Mondegreens` |
| `needless_variants` | `Needless` |
| `nonwords` | `Nonwords` |
| `oxymorons` | `Oxymorons` |
| `psychology.lie_detector` | `LieDetector` |
| `psychology.p_equals_zero` | `P-Value` |
| `psychology.mental_telepathy` | `MentalTelepathy` |
| `redundancy.misc.wallace` | `RedundancyWallace` |
| `redundancy.misc.garner` | `RedundancyGarner`, `RedundancyGarnerPatterns` |
| `redundancy.misc.nordquist` | `RedundancyNordquist` |
| `redundancy.misc.after_the_deadline` | `Redundancy`, `RedundancyNested` |
| `redundancy.ras_syndrome` | `RASSyndrome` |
| `skunked_terms` | `Skunked` |
| `social_awareness.lgbtq.terms` | `LGBTTerms` |
| `social_awareness.lgbtq.offensive` | `LGBTOffensive` |
| `social_awareness.nword` | `NWord` |
| `social_awareness.sexism` | `GenderBias`, `GenderBiasForms` |
| `spelling.able_atable` | `SpellingAbleAtable` |
| `spelling.able_ible` | `SpellingAbleIble` |
| `spelling.ally_ly` | `SpellingAllyLy` |
| `spelling.ance_ence` | `SpellingAnceEnce` |
| `spelling.athletes` | `SpellingAthletes` |
| `spelling.consistency` | `Spelling` |
| `spelling.ely_ly` | `SpellingElyLy` |
| `spelling.em_im_en_in` | `SpellingEmIm` |
| `spelling.er_or` | `SpellingErOr` |
| `spelling.in_un` | `SpellingInUn` |
| `spelling.misc` | `SpellingMisc`, `SpellingTill` |
| `spelling.ve_of` | `SpellingVeOf` |
| `terms.animal_adjectives` | `AnimalLabels` |
| `terms.denizen_labels.garner` | `DenizenLabels` |
| `terms.denizen_labels.norris` | `DenizenLabelsNorris` |
| `terms.eponymous_adjectives` | `EponymousAdjectives` |
| `terms.venery` | `GroupTerms` |
| `typography.diacritical_marks` | `Diacritical` |
| `typography.punctuation.misplaced` | `EtAl`, `EtAlNested` |
| `typography.punctuation.exclamation` | `Exclamation` |
| `typography.punctuation.hyperbole` | `Hyperbole` |
| `typography.punctuation.spacing` | `SentenceSpacingMixed` |
| `typography.symbols.ellipsis` | `Ellipsis` |
| `typography.symbols.copyright` | `Copyright` |
| `typography.symbols.trademark` | `Trademark`, `RegisteredTrademark` |
| `typography.symbols.sentence_spacing` | `SentenceSpacing` |
| `typography.symbols.multiplication` | `Multiplication` |
| `typography.symbols.curly_quotes` | `CurlyQuotes` |
| `uncomparables` | `Uncomparables`, `UncomparablesMost` |
| `weasel_words.very` | `Very` |

## Differences from proselint

On plain text the style reports what `proselint` reports, at the same line
and column, except:

- `proselint` reads every file as plain text. In Markdown and the other
  formats Vale understands, the style skips code, URLs, and front matter.
- `proselint` finds a listed word inside a longer one (`TODO` in `TODOS`)
  whenever the word also stands alone somewhere in the file. The style
  matches whole words only.
- `proselint` cannot match a phrase that is split across two lines. The
  style can.
- `proselint` pairs quotes across the whole file, so a quote left open in
  one paragraph hides findings in the next. The style looks for the nearest
  quotes, and for single quotes only within a line. The three `script` rules
  do not look at quotes.
- `proselint` stops after 1,000 findings. The style does not.
- Where a list entry is a pattern, `proselint` prints `None` as the preferred
  form. The style prints the form.

## Development

```console
$ cd script
$ uv venv .venv
$ uv pip install --python .venv/bin/python -r requirements.txt
$ .venv/bin/python generate.py   # rewrite proselint/*.yml
$ .venv/bin/python fixture.py    # rewrite fixtures/phrases.txt
$ cd ..
$ ./test.sh                      # compare with the golden file, then with proselint itself
```

To move to a newer `proselint`, change its version in
`script/requirements.txt` and run the same steps. A new check stops the
generator until it has a name in `NAMES`. `script/compare.py` takes any files,
reads each as plain text, and prints every finding the two tools disagree on.
