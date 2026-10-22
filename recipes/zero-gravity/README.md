# zero-gravity workspace

**status: experimental · first location: bali, indonesia · exact products: pending**

a recipe for arranging a reclining chair, adjustable desk or support structure, and device arms into a workspace that can be adapted to a person's body, room, and equipment. “zero gravity” is a common name for a reclined configuration; it is not a literal absence of gravity or a health claim.

## agent entrypoint

from the repository root:

```sh
python3 sh.py show zero-gravity
python3 sh.py plan zero-gravity --country ID --city Bali --budget 5000000 --currency IDR
```

read [the agent contract](../../docs/agent-contract.md). create a local variant or report with `init`, edit supported facts, validate, and open a pull request from a fork. this recipe id stays `zero-gravity`; pin a git commit for reproducibility.

## what is ready

- functional [component requirements](recipe.json), independent of brands or stores
- a [bali sourcing record](sourcing/ID-bali.json) with explicit unknowns
- an [assembly and acceptance checklist](assembly.md)
- a [contribution handoff](../../prompts/contribute-zero-gravity.md) for the original builder and their agents

## what is not ready

there is no verified product list, measured geometry, load assessment, or public build report yet. do not treat this as a ready-to-buy package. the original builder has been invited to contribute their own publishable account; no private messages or photographs are included.

## fit matters more than product names

an arm can support the right weight yet fail to reach the required height. record the lowest usable tray position and the monitor position with the chair actually reclined. include mounting height, arm reach, room clearance, and the ability to get in and out. do not assume arms designed for upright screens support every tilt or suspended orientation.

this recipe does not require wall mounting. desk clamps or a separate support may be considered only after checking their ratings, stability, and surface compatibility. the existing laptop or display can be reused when compatible; list additional devices separately from furniture costs.

## evidence and use

comfort is individual. describe an actual trial and its limitations in a build report; do not claim that reclining treats pain or makes long uninterrupted sessions healthy. include how the setup fits into breaks and changes of activity. if a configuration causes discomfort, stop the trial and adjust it rather than forcing the recipe.

## next contribution

the original or another builder can supply model names, public shopping links, measured dimensions, authorized photos, the assembly sequence, things that failed, and changes made after use. keep unknown products as candidates. add other countries as sourcing variants instead of overwriting the bali file.
