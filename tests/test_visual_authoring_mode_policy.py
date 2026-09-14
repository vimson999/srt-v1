from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent.parent
skill = (ROOT / 'SKILL.md').read_text(encoding='utf-8').lower()
failure = (ROOT / 'references' / 'failure-regression.md').read_text(encoding='utf-8').lower()
standard = (ROOT / 'references' / 'production-standard.md').read_text(encoding='utf-8').lower()
readme = (ROOT / 'tests' / 'fixtures' / 'srt-regression' / 'README.md').read_text(encoding='utf-8').lower()
cases = json.loads((ROOT / 'tests' / 'fixtures' / 'srt-regression' / 'cases.json').read_text(encoding='utf-8'))
honghao = next(item for item in cases['cases'] if item['case_id'] == 'honghao-0914-argument-turn')


def has_ui_first(text: str) -> bool:
    return 'ui-first' in text or 'ui_first' in text


checks = {
    'failure class exists': 'fr-11' in failure and has_ui_first(failure),
    'skill routes through production standard': 'references/production-standard.md' in skill,
    'standard is visual-first': 'visual-first' in standard and has_ui_first(standard),
    'standard covers container-first': 'container-first' in standard and 'visual relationship' in standard,
    'honghao covers fr-11': 'FR-11' in honghao['primary_failure_classes'],
    'library documents mode regression': has_ui_first(readme) and 'visual-first' in readme,
}

failed = [name for name, ok in checks.items() if not ok]
for name, ok in checks.items():
    print(('PASS' if ok else 'FAIL') + ': ' + name)
if failed:
    raise SystemExit('visual authoring mode regression: ' + '; '.join(failed))
print('PASS: visual authoring mode policy')
