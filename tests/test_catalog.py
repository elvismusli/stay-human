import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('catalog', ROOT / 'tools/catalog.py')
catalog = importlib.util.module_from_spec(spec)
spec.loader.exec_module(catalog)


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.folder = ROOT / 'recipes/zero-gravity'
        self.recipe = json.loads((self.folder / 'recipe.json').read_text())
        self.sourcing = json.loads((self.folder / 'sourcing/ID-bali.json').read_text())
        self.ids = {c['id'] for c in self.recipe['components']}

    def test_catalog_is_valid(self):
        self.assertTrue(catalog.validate())

    def test_unsubstantiated_tested_build_is_rejected(self):
        self.recipe['status'] = 'tested'
        with self.assertRaises(ValueError):
            catalog.validate_recipe(self.recipe, self.folder, ROOT)

    def test_wrong_component_and_false_evidence_are_rejected(self):
        for patch in ({'component_id': 'missing'}, {'status': 'tested'}, {'price': -1}, {'price': 10}, {'url': 'javascript:alert(1)'}, {'price': float('nan')}):
            with self.subTest(patch=patch):
                data = copy.deepcopy(self.sourcing)
                data['items'][0].update(patch)
                with self.assertRaises(ValueError):
                    catalog.validate_sourcing(data, self.ids, ROOT)

    def test_local_evidence_cannot_escape_repository(self):
        self.assertFalse(catalog.evidence_exists('../dima-ops/README.md', ROOT))

    def test_unknown_prices_remain_unknown_in_plan(self):
        result = catalog.plan(self.recipe, 'KE', 'Nairobi', 50000, 'KES')
        self.assertIn('Nairobi, KE', result)
        self.assertIn('50000 KES', result)
        self.assertIn('not verified', result)
        self.assertIn('do not count unknown as zero', result)

    def test_cli_rejects_invalid_budget_and_recipe(self):
        for recipe, budget in [('zero-gravity', 'nan'), ('zero-gravity', '-1'), ('../other', '100')]:
            result = subprocess.run([sys.executable, str(ROOT / 'tools/catalog.py'), 'plan', recipe, '--country', 'ID', '--city', 'Bali', '--budget', budget, '--currency', 'IDR'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertNotIn('Traceback', result.stderr)


if __name__ == '__main__':
    unittest.main()
