from pathlib import Path
import importlib.util
import tempfile

ROOT = Path(__file__).resolve().parent.parent

agents_path = ROOT / 'AGENTS.md'
handoff_ref_path = ROOT / 'references' / 'chatgpt-codex-handoff.md'
skill_path = ROOT / 'SKILL.md'
init_script = ROOT / 'scripts' / 'init_project.py'

checks = {
    'root AGENTS exists': agents_path.exists(),
    'handoff reference exists': handoff_ref_path.exists(),
}

agents = agents_path.read_text(encoding='utf-8').lower() if agents_path.exists() else ''
handoff_ref = handoff_ref_path.read_text(encoding='utf-8').lower() if handoff_ref_path.exists() else ''
skill = skill_path.read_text(encoding='utf-8').lower() if skill_path.exists() else ''

checks.update({
    'agents defines chatgpt git codex flow': all(term in agents for term in ['chatgpt', 'git', 'codex']),
    'agents points to detailed contract': 'references/chatgpt-codex-handoff.md' in agents,
    'handoff defines git as system of record': 'system of record' in handoff_ref and 'git' in handoff_ref,
    'handoff separates director and implementation authority': 'director contract' in handoff_ref and 'implementation' in handoff_ref,
    'handoff forbids codex semantic downgrade': 'must not' in handoff_ref and ('director intent' in handoff_ref or 'director contract' in handoff_ref),
    'skill routes to handoff contract': 'references/chatgpt-codex-handoff.md' in skill,
})

if init_script.exists():
    spec = importlib.util.spec_from_file_location('init_project', init_script)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        srt = root / 'handoff_test.srt'
        srt.write_text('1\n00:00:00,000 --> 00:00:02,000\nHello\n', encoding='utf-8')
        project = mod.initialize_project(root / 'factory', srt, project_id='handoff_test')
        task = project / 'handoff' / 'codex-task.md'
        checks['project initializes codex handoff task'] = task.exists()
        task_text = task.read_text(encoding='utf-8').lower() if task.exists() else ''
        checks['codex task preserves director boundary'] = 'director' in task_text and 'do not reinterpret' in task_text
else:
    checks['project initializes codex handoff task'] = False
    checks['codex task preserves director boundary'] = False

failed = [name for name, ok in checks.items() if not ok]
for name, ok in checks.items():
    print(('PASS' if ok else 'FAIL') + ': ' + name)

if failed:
    raise SystemExit('chatgpt-codex handoff regression: ' + '; '.join(failed))

print('PASS: ChatGPT -> Git -> Codex handoff contract')
