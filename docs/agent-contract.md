# agent interface v1

start with `python3 sh.py capabilities`. stdout contains exactly one compact JSON object by default, including on an error. exit 0 means success; exit 2 means a usage, validation, or data error. `--help` is the normal text help exception. `plan --format markdown` opts into a human-readable brief. commands do not prompt, use the network, need credentials, invoke a model, or purchase anything.

```json
{"api_version":1,"ok":true,"data":{},"error":null}
```

errors have `ok: false`, `data: null`, and `error: {"code": "...", "message": "..."}`. error codes include `usage_error`, `invalid_id`, `not_found`, `already_exists`, `invalid_path`, `invalid_country`, `invalid_city`, `invalid_currency`, `invalid_budget`, and `invalid_data`. inspect `ok` and the exit code, not prose. unknown optional fields may be added within v1; incompatible changes require a new api/schema version.

## identity and source of truth

`recipes/<id>/recipe.json` is the machine source of truth for component requirements and status. ids are lowercase hyphenated strings and must match directory names. recipe ids must not be reused for unrelated recipes. guides explain the data; they must not silently contradict it. `show` returns requirements only. `show --section sourcing|reports|guide` loads one other section on demand. `list` is a summary index. never load guides as part of routine discovery.

share `https://github.com/matskevich/stay-human/tree/main/recipes/zero-gravity` for the current recipe. replace `main` with a full git commit for an immutable reference. `checkout_commit` describes the checkout base, not a promise that local edits are absent. check `git status` and `git diff` before contributing.

## structured files

all JSON content uses `schema_version: 1`. the templates define the starting shape; `validate` is the executable validator. recipe fields are id, title, category, summary, status, components, evidence. components have id, name, required, and a nonempty list of requirements. category is an open string so contributors can add routines as well as physical workspaces.

sourcing fields are country, city, currency, checked_on, notes, items. each item has component_id, model, url, price, status, checked_on, evidence, notes. unknown facts are null, never fabricated zero values. a price or listing needs its check date. purchased/tested items need a model, date, and evidence. country/currency validation checks code shape, not membership in an externally maintained registry.

structured report fields are recipe_id, status, date, country, city, configuration, actual_use, limitations, costs, changes, sources, credits. reports begin as draft; reported/tested reports require a date, configuration, actual_use and limitations. recipe-level reported/tested status requires evidence references. maintainers must check that these substantiate the claim: the validator checks presence, not scientific truth. markdown reports are also welcome and manually reviewed; use JSON for agent-readable reports.

all local evidence paths are relative to the repository root and must remain inside it. remote evidence URLs are syntax-checked, not fetched. validation does not prove stock availability, physical safety, engineering load ratings, health benefits, copyright ownership, or absence of personal data.

## mutation and contribution

`init` previews complete proposed files by default. add `--write` to create them. existing files are never overwritten; a repeat returns `already_exists`. edit existing JSON files on a branch and inspect the diff. no command commits, pushes, merges, installs software, or contacts a seller. `--root PATH` can target another local checkout for content operations.

```sh
# run in your fork's checkout
git switch -c add-local-variant
python3 sh.py init sourcing --recipe zero-gravity --id ke-nairobi --country KE --city Nairobi --currency KES --write
python3 sh.py init report --recipe zero-gravity --id nairobi-first-build --write
# fill the generated JSON files with supported facts; retain unknowns
python3 sh.py validate
python3 -m unittest discover -s tests
git diff
# commit only intended files, push your fork branch, and open a pull request
```

use `prompts/contribute-zero-gravity.md` for the initial builder handoff. if your agent lacks git hosting credentials, prepare a patch or issue draft instead of claiming publication. submitting an issue is a valid starting point; maintainers can help turn it into structured data.
