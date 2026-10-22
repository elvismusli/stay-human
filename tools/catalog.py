#!/usr/bin/env python3
"""Portable recipe validation and planning; Python standard library only."""
import argparse
from datetime import date
import json
import math
from pathlib import Path
import re
import sys
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def valid_date(value):
    if value is not None:
        require(isinstance(value, str), 'date must be a string or null')
        require(date.fromisoformat(value).isoformat() == value, 'use YYYY-MM-DD dates')


def evidence_exists(value, root):
    if not nonempty(value):
        return False
    if urlparse(value).scheme in ('https', 'http'):
        return bool(urlparse(value).netloc)
    path = (root / value).resolve()
    return path.is_relative_to(root.resolve()) and path.is_file()


def validate_recipe(data, folder, root):
    require(isinstance(data, dict), 'recipe must be an object')
    require(data.get('schema_version') == 1, 'unsupported recipe schema_version')
    require(data.get('id') == folder.name, 'recipe id must match its directory')
    require(bool(re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', data['id'])), 'invalid recipe id')
    for key in ('title', 'category', 'summary'):
        require(nonempty(data.get(key)), f'missing {key}')
    require(data.get('status') in ('experimental', 'reported', 'tested'), 'invalid recipe status')
    require((folder / 'README.md').is_file(), 'missing recipe README.md')
    components = data.get('components')
    require(isinstance(components, list) and components, 'components must be a nonempty list')
    ids = set()
    for component in components:
        require(isinstance(component, dict), 'component must be an object')
        cid = component.get('id')
        require(isinstance(cid, str) and re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', cid), 'invalid component id')
        require(cid not in ids, f'duplicate component {cid}')
        ids.add(cid)
        require(nonempty(component.get('name')), 'component name missing')
        require(isinstance(component.get('required'), bool), 'required must be boolean')
        reqs = component.get('requirements')
        require(isinstance(reqs, list) and reqs and all(nonempty(r) for r in reqs), 'component requirements missing')
    evidence = data.get('evidence')
    require(isinstance(evidence, list), 'evidence must be a list')
    require(all(evidence_exists(e, root) for e in evidence), 'invalid evidence URL or missing local file')
    if data['status'] != 'experimental':
        require(bool(evidence), 'reported/tested recipes need evidence')
    return ids


def validate_sourcing(data, ids, root):
    require(isinstance(data, dict), 'sourcing must be an object')
    require(data.get('schema_version') == 1, 'unsupported sourcing schema_version')
    require(bool(re.fullmatch('[A-Z]{2}', str(data.get('country', '')))), 'country must be a two-letter code')
    require(bool(re.fullmatch('[A-Z]{3}', str(data.get('currency', '')))), 'currency must be a three-letter code')
    require(nonempty(data.get('city')), 'city missing')
    valid_date(data.get('checked_on'))
    require(isinstance(data.get('items'), list), 'items must be a list')
    for item in data['items']:
        require(isinstance(item, dict), 'item must be an object')
        require(item.get('component_id') in ids, 'unknown component_id')
        require(item.get('status') in ('candidate', 'purchased', 'tested'), 'invalid item status')
        for key in ('model', 'url', 'price', 'checked_on', 'evidence'):
            require(key in item, f'item missing {key}; use null if unknown')
        valid_date(item['checked_on'])
        if item['model'] is not None:
            require(nonempty(item['model']), 'model must be text or null')
        if item['url'] is not None:
            parsed = urlparse(item['url'])
            require(parsed.scheme in ('http', 'https') and parsed.netloc, 'invalid product URL')
        price = item['price']
        require(price is None or (type(price) in (int, float) and math.isfinite(price) and price >= 0), 'price must be nonnegative or null')
        if price is not None or item['url'] is not None:
            require(item['checked_on'] is not None, 'listing/price needs a check date')
        if item['status'] != 'candidate':
            require(nonempty(item['model']) and item['checked_on'] is not None, 'purchased/tested item needs model and date')
            require(evidence_exists(item['evidence'], root), 'purchased/tested item needs evidence')


def validate(root=ROOT):
    files = sorted((root / 'recipes').glob('*/recipe.json'))
    require(bool(files), 'no recipes found')
    for path in files:
        data = json.loads(path.read_text())
        ids = validate_recipe(data, path.parent, root)
        for sourcing in sorted((path.parent / 'sourcing').glob('*.json')):
            try:
                validate_sourcing(json.loads(sourcing.read_text()), ids, root)
            except (ValueError, TypeError, KeyError) as exc:
                raise ValueError(f'{sourcing.relative_to(root)}: {exc}') from exc
        for report in sorted((path.parent / 'reports').glob('*.json')):
            d = json.loads(report.read_text())
            require(d.get('schema_version') == 1, 'unsupported report schema_version')
            require(d.get('recipe_id') == data['id'], 'report recipe_id mismatch')
            require(d.get('status') in ('draft', 'reported', 'tested'), 'invalid report status')
            valid_date(d.get('date'))
            if d['status'] != 'draft':
                require(d.get('date') is not None, 'published report needs a date')
                for key in ('configuration', 'actual_use', 'limitations'):
                    require(nonempty(d.get(key)), f'published report needs {key}')
    return files


def plan(data, country, city, budget, currency):
    lines = [f"# {data['title']}: local adaptation brief", '',
             f'location: {city}, {country}', f'budget ceiling: {budget:g} {currency}',
             f"recipe status: {data['status']}", '',
             'this is a research brief, not a product recommendation or quotation.',
             'no live prices, availability, shipping, taxes, or compatibility have been checked.', '',
             '## clarify before sourcing', '',
             '- available space, access needs, and existing equipment',
             '- device masses, mounting surfaces, dimensions, and intended positions',
             '- delivery constraints and whether the budget includes devices, shipping, and taxes', '',
             '## component requirements', '']
    for component in data['components']:
        optional = '' if component['required'] else ' (optional)'
        lines += [f"### {component['name']}{optional}", '']
        lines += [f'- {r}' for r in component['requirements']]
        lines += ['- product / source / price / delivery / date: unknown', '- compatibility: not verified', '']
    lines += ['## deliverable', '',
              '- local model options with public sources, check dates, and explicit currency',
              '- known subtotal and all excluded or unknown costs; do not count unknown as zero',
              '- compatibility gaps and measurements to resolve before purchase',
              '- manufacturer-based assembly sequence and acceptance checks',
              '- buy or contact sellers only with separate user authorization',
              '- after actual use, contribute a build report through a fork and pull request']
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('validate')
    sub.add_parser('list')
    p = sub.add_parser('plan')
    p.add_argument('recipe')
    p.add_argument('--country', required=True)
    p.add_argument('--city', required=True)
    p.add_argument('--budget', required=True, type=float)
    p.add_argument('--currency', required=True)
    args = parser.parse_args()
    try:
        files = validate()
        if args.command == 'validate':
            print(f'valid: {len(files)} recipe(s); evidence links checked for shape/local existence, not remote truth')
        elif args.command == 'list':
            for path in files:
                d = json.loads(path.read_text())
                print(f"{d['id']}\t{d['status']}\t{d['title']}")
        else:
            require(re.fullmatch('[A-Z]{2}', args.country), 'use an uppercase two-letter country code')
            require(re.fullmatch('[A-Z]{3}', args.currency), 'use an uppercase three-letter currency code')
            require(math.isfinite(args.budget) and args.budget > 0, 'budget must be finite and positive')
            require(nonempty(args.city) and '\n' not in args.city, 'city must be a nonempty single line')
            matches = [p for p in files if p.parent.name == args.recipe]
            require(bool(matches), 'unknown recipe; run list')
            print(plan(json.loads(matches[0].read_text()), args.country, args.city, args.budget, args.currency), end='')
    except (ValueError, TypeError, KeyError, OSError) as exc:
        parser.exit(2, f'error: {exc}\n')


if __name__ == '__main__':
    main()
