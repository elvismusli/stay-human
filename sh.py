#!/usr/bin/env python3
"""stay-human: local, non-interactive, JSON-first agent interface."""
import argparse
import json
import math
from pathlib import Path
import re
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / 'tools'))
import catalog

ROOT = Path(__file__).resolve().parent


class CliError(Exception):
    def __init__(self, code, message):
        self.code, self.message = code, message


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise CliError('usage_error', message)


def emit(data=None, error=None):
    print(json.dumps({'api_version': 1, 'ok': error is None, 'data': data, 'error': error}, ensure_ascii=False, separators=(',', ':'), allow_nan=False))


def slug(value):
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', value):
        raise CliError('invalid_id', 'use a lowercase hyphenated identifier')
    return value


def load_recipe(root, recipe_id):
    slug(recipe_id)
    path = root / 'recipes' / recipe_id / 'recipe.json'
    if not path.is_file():
        raise CliError('not_found', f'unknown recipe: {recipe_id}')
    return path, json.loads(path.read_text())


def source(root, recipe_id):
    try:
        commit = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], stderr=subprocess.DEVNULL, text=True).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        commit = None
    return {'recipe_id': recipe_id, 'path': f'recipes/{recipe_id}/recipe.json',
            'url': f'https://github.com/matskevich/stay-human/tree/main/recipes/{recipe_id}',
            'checkout_commit': commit,
            'note': 'local files may include uncommitted changes; inspect git diff before publishing'}


def location(args):
    if not args.country or not re.fullmatch('[A-Z]{2}', args.country):
        raise CliError('invalid_country', 'supply --country with a two-letter uppercase country code')
    if not args.currency or not re.fullmatch('[A-Z]{3}', args.currency):
        raise CliError('invalid_currency', 'supply --currency with a three-letter uppercase currency code')
    if not args.city or '\n' in args.city:
        raise CliError('invalid_city', 'supply a nonempty single-line --city')


def parser():
    p = Parser(description=__doc__)
    p.add_argument('--root', type=Path, default=ROOT, help='local repository root; never a URL')
    sub = p.add_subparsers(dest='command', required=True, parser_class=Parser)
    sub.add_parser('capabilities')
    sub.add_parser('list')
    sub.add_parser('validate')
    show = sub.add_parser('show'); show.add_argument('recipe')
    show.add_argument('--section', choices=('requirements', 'sourcing', 'reports', 'guide'), default='requirements')
    show.add_argument('--country', help='filter sourcing by country code')
    show.add_argument('--city', help='filter sourcing by city')
    plan = sub.add_parser('plan'); plan.add_argument('recipe')
    for key in ('country', 'city', 'currency'):
        plan.add_argument('--' + key, required=True)
    plan.add_argument('--budget', type=float, required=True)
    plan.add_argument('--format', choices=('json', 'markdown'), default='json')
    init = sub.add_parser('init')
    init.add_argument('kind', choices=('recipe', 'sourcing', 'report'))
    init.add_argument('--id', required=True, help='new recipe id or local filename stem')
    init.add_argument('--recipe', help='existing parent recipe for sourcing/report')
    for key in ('country', 'city', 'currency'):
        init.add_argument('--' + key)
    init.add_argument('--write', action='store_true', help='create local files; otherwise preview only')
    return p


def run(args):
    root = args.root.resolve()
    if args.command == 'capabilities':
        return json.loads((ROOT / 'agent-api.json').read_text())
    if args.command == 'validate':
        files = catalog.validate(root)
        return {'valid': True, 'recipes': len(files), 'scope': 'structure, references, evidence presence; not remote truth, engineering certification, or health evidence'}
    if args.command == 'list':
        return {'recipes': [{k: d[k] for k in ('id', 'category', 'status', 'summary')} for p in sorted((root / 'recipes').glob('*/recipe.json')) for d in [json.loads(p.read_text())]]}
    if args.command in ('show', 'plan'):
        path, recipe = load_recipe(root, args.recipe)
        if args.command == 'show':
            if args.section == 'requirements':
                return {'source': source(root, args.recipe), 'recipe': recipe}
            if args.section == 'guide':
                return {'guide': (path.parent / 'README.md').read_text()}
            records = []
            for item in sorted((path.parent / args.section).glob('*.json')):
                data = json.loads(item.read_text())
                if args.country and data.get('country') != args.country:
                    continue
                if args.city and str(data.get('city', '')).casefold() != args.city.casefold():
                    continue
                records.append({'path': str(item.relative_to(root)), 'data': data})
            return {args.section: records}
        sourcing = [{'path': str(p.relative_to(root)), 'data': json.loads(p.read_text())} for p in sorted((path.parent / 'sourcing').glob('*.json'))]
        location(args)
        if not math.isfinite(args.budget) or args.budget <= 0:
            raise CliError('invalid_budget', 'budget must be finite and positive')
        brief = catalog.plan(recipe, args.country, args.city, args.budget, args.currency)
        if args.format == 'markdown':
            return brief
        return {'source': source(root, args.recipe), 'recipe_status': recipe['status'],
                'request': {'country': args.country, 'city': args.city, 'budget': args.budget, 'currency': args.currency},
                'components': recipe['components'],
                'local_candidates': [s for s in sourcing if s['data']['country'] == args.country and s['data']['city'].casefold() == args.city.casefold()],
                'known_total': None, 'purchase_ready': False,
                'unresolved': ['user measurements', 'current prices and delivery', 'whole-assembly compatibility', 'actual use verification']}
    slug(args.id)
    files = {}
    if args.kind == 'recipe':
        folder = root / 'recipes' / args.id
        if folder.exists():
            raise CliError('already_exists', 'recipe directory already exists; edit it on a branch')
        data = json.loads((ROOT / 'templates/recipe/recipe.json').read_text())
        data['id'] = args.id
        data['title'] = args.id.replace('-', ' ')
        files[folder / 'recipe.json'] = json.dumps(data, indent=2) + '\n'
        files[folder / 'README.md'] = (ROOT / 'templates/recipe/README.md').read_text().replace('your recipe title', data['title'])
    else:
        if not args.recipe:
            raise CliError('usage_error', '--recipe is required for sourcing/report')
        path, recipe = load_recipe(root, args.recipe)
        folder = path.parent
        if args.kind == 'sourcing':
            location(args)
            data = {'schema_version': 1, 'country': args.country, 'city': args.city, 'currency': args.currency,
                    'checked_on': None, 'notes': 'unverified local variant; fill in sources and check dates',
                    'items': [{'component_id': c['id'], 'model': None, 'url': None, 'price': None, 'status': 'candidate', 'checked_on': None, 'evidence': None, 'notes': 'compatibility not verified'} for c in recipe['components']]}
            target = folder / 'sourcing' / (args.id + '.json')
        else:
            data = json.loads((ROOT / 'templates/report.json').read_text())
            data['recipe_id'] = args.recipe
            data['country'], data['city'] = args.country, args.city
            target = folder / 'reports' / (args.id + '.json')
        files[target] = json.dumps(data, indent=2) + '\n'
    for target in files:
        if not target.resolve().is_relative_to(root):
            raise CliError('invalid_path', 'output path escapes repository')
        if target.exists():
            raise CliError('already_exists', f'refusing to overwrite {target.relative_to(root)}')
    created = []
    if args.write:
        try:
            for target, content in files.items():
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open('x') as stream:
                    created.append(target)
                    stream.write(content)
        except OSError:
            for target in created:
                target.unlink(missing_ok=True)
            raise
    return {'written': args.write, 'files': [{'path': str(t.relative_to(root)), 'content': c} for t, c in files.items()],
            'next': 'fill in facts and unknowns, run validate, review git diff, commit to a fork branch, open a pull request'}


def main(argv=None):
    try:
        args = parser().parse_args(argv)
        data = run(args)
        if args.command == 'plan' and args.format == 'markdown':
            print(data, end='')
        else:
            emit(data)
        return 0
    except CliError as exc:
        emit(error={'code': exc.code, 'message': exc.message})
        return 2
    except (ValueError, KeyError, TypeError, OSError) as exc:
        emit(error={'code': 'invalid_data', 'message': str(exc)})
        return 2


if __name__ == '__main__':
    sys.exit(main())
