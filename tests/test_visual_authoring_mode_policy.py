from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent.parent
skill = (ROOT / 'SKILL.md').read_text(encoding='utf-8').lower()
failure = (ROOT / 'references' / 'failure-regression.md').read_text(encoding='utf-8').lower()
standard = (ROOT / 'references' / 'production-standard.md').read_text(encoding='utf-8').lower()
readme = (ROOT / 'tests' / 'fixtures' / 'srt-regression' / 'README.md').read_text(encoding='utf-8').lower()
cases = json.loads((ROOT / 'tests' / 'fixtures' / 'srt-regression' / 'cases.json').read_text(encoding='utf-8'))
honghao = next(item for item in cases['cases'] if item['case_id'] == 'honghao-0914-argument-turn')

checks = {
    'failure class exists': 'fr-11' in failure and 'ui-first' in failure,
    'skill says visual-first': 'visual-first' in skill and 'ui-first' in skill,
    'standard covers container-first': 'container-first' in standard and 'visual relationship' in standard,
    'honghao covers fr-11': 'FR-11' in honghao['primary_failure_classes'],
    'library documents mode regression': 'ui-first' in readme and 'visual-first' in readme,
}

failed = [name for name, ok in checks.items() if not ok]
for name, ok in checks.items():
    print(('PASS' if ok else 'FAIL') + ': ' + name)
if failed:
    raise SystemExit('visual authoring mode regression: ' + '; '.join(failed))
print('PASS: visual authoring mode policy')
