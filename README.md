# stay human

an agent-first, open library of reproducible workspaces, movement, rest, and recovery setups. the first recipe is an experimental zero-gravity workspace, starting in bali and open to local adaptations anywhere.

## one link to give your agent

https://github.com/matskevich/stay-human/tree/main/recipes/zero-gravity

ask it to adapt the recipe to your location, document what actually works, and contribute improvements. [AGENTS.md](AGENTS.md) is the short entrypoint. agents should not ingest the entire repository.

## cli

python 3.10+. standard library only. no account, dependency installation, model vendor, or central service required.

```sh
git clone https://github.com/matskevich/stay-human.git
cd stay-human
python3 sh.py capabilities
python3 sh.py list
python3 sh.py show zero-gravity
python3 sh.py show zero-gravity --section sourcing --country ID --city Bali
python3 sh.py plan zero-gravity --country ID --city Bali --budget 5000000 --currency IDR
```

compact JSON by default. errors are structured. reads are offline. `list` is a small index, `show` returns only the requested section, and `plan` prepares requirements without claiming live shopping results. unknown prices remain null. [interface details](docs/agent-contract.md).

## contributions

```sh
# in a fork, on a new branch
python3 sh.py init sourcing --recipe zero-gravity --id ke-nairobi --country KE --city Nairobi --currency KES --write
python3 sh.py init report --recipe zero-gravity --id my-first-build --write
# fill supported facts; keep unknowns null
python3 sh.py validate
python3 -m unittest discover -s tests
# review diff, commit intended files, push fork branch, open pull request
```

`init recipe --id my-setup --write` adds a new recipe. omit `--write` to preview. existing files are never overwritten. anyone can contribute through a fork and pull request, or [an issue](https://github.com/matskevich/stay-human/issues/new/choose). maintainers review merges. [contribution details](CONTRIBUTING.md) · [community standards](CODE_OF_CONDUCT.md).

english is the shared language; imperfect english and translations are welcome. use metric measurements and explicit local currencies. no particular country, budget, body type, or agent subscription is assumed.

## status and licenses

the zero-gravity recipe is a functional specification, **not a verified shopping list**. original build details and local product checks are pending. field experience is not clinical evidence. no private conversations or third-party photos are published.

code (`sh.py`, `tools/`, tests, automation): [MIT](LICENSE). original recipe data, guides, templates and media: [CC BY 4.0](LICENSE-CONTENT.md). only contribute material you have the right to share.
