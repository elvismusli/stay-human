import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class AgentCliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        shutil.copytree(ROOT / 'recipes', self.root / 'recipes')

    def tearDown(self):
        self.tmp.cleanup()

    def cli(self, *args, code=0):
        proc = subprocess.run([sys.executable, str(ROOT / 'sh.py'), '--root', str(self.root), *args], capture_output=True, text=True)
        self.assertEqual(proc.returncode, code, proc.stdout + proc.stderr)
        value = json.loads(proc.stdout)
        self.assertEqual(value['api_version'], 1)
        self.assertEqual(value['ok'], code == 0)
        return value

    def test_discovery_show_plan(self):
        self.assertIn('commands', self.cli('capabilities')['data'])
        self.assertEqual(self.cli('list')['data']['recipes'][0]['id'], 'zero-gravity')
        shown = self.cli('show', 'zero-gravity')['data']
        self.assertEqual(shown['recipe']['id'], 'zero-gravity')
        self.assertNotIn('guide', shown)
        self.assertNotIn('sourcing', shown)
        self.assertNotIn('components', self.cli('list')['data']['recipes'][0])
        self.assertEqual(self.cli('show', 'zero-gravity', '--section', 'sourcing', '--country', 'KE')['data']['sourcing'], [])
        d = self.cli('plan', 'zero-gravity', '--country', 'KE', '--city', 'Nairobi', '--budget', '50000', '--currency', 'KES')['data']
        self.assertIsNone(d['known_total'])
        self.assertFalse(d['purchase_ready'])
        self.assertEqual(d['local_candidates'], [])

    def test_contribution_workflow_and_no_overwrite(self):
        args = ('init', 'sourcing', '--recipe', 'zero-gravity', '--id', 'ke-nairobi', '--country', 'KE', '--city', 'Nairobi', '--currency', 'KES')
        target = self.root / 'recipes/zero-gravity/sourcing/ke-nairobi.json'
        self.assertFalse(self.cli(*args)['data']['written'])
        self.assertFalse(target.exists())
        self.cli(*args, '--write')
        before = target.read_bytes()
        self.assertEqual(self.cli(*args, '--write', code=2)['error']['code'], 'already_exists')
        self.assertEqual(target.read_bytes(), before)
        self.cli('init', 'report', '--recipe', 'zero-gravity', '--id', 'first-build', '--write')
        self.cli('init', 'recipe', '--id', 'movement-breaks', '--write')
        self.cli('validate')

    def test_invalid_input_returns_json_and_cannot_escape(self):
        for args in [('show', '../private'), ('show', 'missing'), ('init', 'recipe', '--id', '../escape', '--write'), ('plan',), ('bogus',)]:
            self.assertIsNotNone(self.cli(*args, code=2)['error']['code'])

    def test_false_report_and_corrupt_data_rejected(self):
        self.cli('init', 'report', '--recipe', 'zero-gravity', '--id', 'false-report', '--write')
        target = self.root / 'recipes/zero-gravity/reports/false-report.json'
        data = json.loads(target.read_text());data['status'] = 'tested'
        target.write_text(json.dumps(data))
        self.cli('validate', code=2)
        target.write_text('{')
        self.cli('show', 'zero-gravity', '--section', 'reports', code=2)


if __name__ == '__main__':
    unittest.main()
