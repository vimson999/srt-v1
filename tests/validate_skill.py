from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
skill = (ROOT / 'SKILL.md').read_text(encoding='utf-8')
workflow = (ROOT / 'references' / 'workflow.md').read_text(encoding='utf-8')
asset_library = (ROOT / 'references' / 'asset-library.md').read_text(encoding='utf-8')

checks = {
    'skill mentions automatic project initialization': 'project initialization' in skill.lower(),
    'workflow has explicit initialization phase': 'Project initialization' in workflow,
    'workflow creates projects/<project_id>': 'projects/<project_id>/' in workflow,
    'workflow creates project.json': 'project.json' in workflow,
    'workflow creates script.txt from SRT': 'script.txt' in workflow and 'SRT' in workflow,
    'workflow protects existing projects from overwrite': 'overwrite' in workflow.lower() or 'existing project' in workflow.lower(),
    'workflow gives the user a single asset-ready handoff': '素材已准备好' in workflow or 'assets are ready' in workflow.lower(),
    'workflow makes intake agent-owned': 'intake_assets.py' in workflow and 'do not ask the user to run' in workflow.lower(),
    'asset library has a project drop zone': 'inbox/<project_id>' in asset_library,
    'asset descriptions use a persistent metadata sidecar': 'metadata.json' in asset_library,
    'asset intake is incremental and hash based': 'hash' in asset_library.lower() and 'incremental' in asset_library.lower(),
}

failed = [name for name, ok in checks.items() if not ok]
for name, ok in checks.items():
    print(('PASS' if ok else 'FAIL') + ': ' + name)

if failed:
    raise SystemExit(1)
