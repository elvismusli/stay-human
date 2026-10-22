# contributing

welcome. a small useful correction is a real contribution. you do not need to own premium gear, speak perfect english, or use an ai agent.

## easiest route: open an issue

use [setup proposal](https://github.com/matskevich/stay-human/issues/new?template=setup.yml) for a recipe or local variant, or [build report](https://github.com/matskevich/stay-human/issues/new?template=report.yml) for actual experience. explain what you know and what is still uncertain. maintainers can help turn it into files.

## contribute files

1. fork this repository on github, clone your fork, and create a branch.
2. copy `templates/recipe/` to `recipes/your-recipe-id/` for a new recipe. replace placeholders and give it a unique lowercase hyphenated id. add it to the README when ready.
3. for a local variant, add `recipes/<id>/sourcing/<country>-<city>.json` using `templates/sourcing.json`. use ISO 3166-1 alpha-2 country codes, ISO 4217 currency codes, metric units, and dates such as `2026-10-22`.
4. for actual experience, copy `templates/build-report.md` into `recipes/<id>/reports/`. include limitations and failures as well as successes.
5. run the checks below, commit your files, push your branch, and open a pull request against `main`. explain what changed and link supporting public sources. the maintainer reviews and merges it.

```sh
python3 sh.py validate
python3 -m unittest discover -s tests
```

for an existing file, github's edit button can also create a fork and pull request. no direct write access is needed. maintainers should merge only after the checks pass and the evidence, rights, and privacy review is complete.

## evidence vocabulary

- `experimental`: requirements or an idea; not a validated build.
- `reported`: a contributor reports assembling it; the report explains the scope.
- `tested`: there is a linked build report describing actual use, duration, configuration, and limitations. this means field-tested, not clinically validated or universally safe.

individual sourcing records use `candidate`, `purchased`, or `tested`. `purchased` and `tested` require an evidence link or a repository report path. a different product or a different mounting geometry needs its own check.

health-related recipes must separate personal observations from published evidence, cite sources for health claims, and avoid diagnosis or treatment instructions. describe where a protocol may not fit rather than making universal promises.

## attribution and privacy

submit your own words and media, or clearly identify the source and its compatible license. obtain permission before publishing other people's photos or text. omit addresses, private messages, order numbers, contact details, and medical records. acknowledge contributors using the public name or handle they choose.

by submitting original material, you agree to license code under MIT and content under CC BY 4.0, as described in README.md. disclose any third-party license exceptions and affiliate relationships. no mandatory copyright assignment.
