import importlib.util
import json
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / 'scripts' / 'init_project.py'
if not SCRIPT.exists():
    raise SystemExit('FAIL: scripts/init_project.py does not exist')

spec = importlib.util.spec_from_file_location('init_project', SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    srt = root / 'my_test.srt'
    srt.write_text('1\n00:00:00,000 --> 00:00:02,000\nHello world\n', encoding='utf-8')
    project = mod.initialize_project(root / 'report-video', srt, project_id='my_test')

    expected = [
        project / 'input' / 'subtitles.srt',
        project / 'input' / 'script.txt',
        project / 'project.json',
        project / 'storyboard',
        project / 'data' / 'motion_cues.json',
        root / 'report-video' / 'asset-library' / 'raw' / 'video',
        root / 'report-video' / 'asset-library' / 'processed' / 'thumbnails',
        root / 'report-video' / 'asset-library' / 'catalog',
        root / 'report-video' / 'asset-library' / 'catalog' / 'assets.json',
        root / 'report-video' / 'asset-library' / 'catalog' / 'metadata.json',
        root / 'report-video' / 'asset-library' / 'catalog' / 'review_queue.json',
        root / 'report-video' / 'asset-library' / 'catalog' / 'usage.json',
        root / 'report-video' / 'asset-library' / 'inbox' / 'my_test',
        project / 'manifest',
        project / 'output' / 'preview',
        project / 'output' / 'final',
    ]
    missing = [str(p) for p in expected if not p.exists()]
    if missing:
        raise SystemExit('FAIL missing: ' + ', '.join(missing))

    script_text = (project / 'input' / 'script.txt').read_text(encoding='utf-8').strip()
    if script_text != 'Hello world':
        raise SystemExit('FAIL script extraction: ' + repr(script_text))

    project_json = json.loads((project / 'project.json').read_text(encoding='utf-8'))
    if project_json.get('asset_library', {}).get('resolution') != 'asset_id':
        raise SystemExit('FAIL shared asset library contract')

    jsonl_path = project / 'storyboard' / 'storyboard.jsonl'
    csv_path = project / 'storyboard' / 'storyboard.csv'
    summary_path = project / 'storyboard' / 'director_summary.md'
    if not jsonl_path.exists() or jsonl_path.read_text(encoding='utf-8') != '':
        raise SystemExit('FAIL canonical storyboard.jsonl should start empty')
    if csv_path.read_text(encoding='utf-8').splitlines()[0] != mod.STORYBOARD_CSV_HEADER:
        raise SystemExit('FAIL storyboard.csv header contract')
    if 'pending phase 1' not in summary_path.read_text(encoding='utf-8').lower():
        raise SystemExit('FAIL director summary initialization')
    if project_json.get('storyboard_contract', {}).get('path') != 'storyboard/storyboard.jsonl':
        raise SystemExit('FAIL storyboard contract pointer')

    motion_cues = json.loads((project / 'data' / 'motion_cues.json').read_text(encoding='utf-8'))
    if motion_cues != {'schema_version': 1, 'cues': []}:
        raise SystemExit('FAIL motion cue placeholder contract')

    metadata = json.loads(
        (root / 'report-video' / 'asset-library' / 'catalog' / 'metadata.json').read_text(
            encoding='utf-8'
        )
    )
    if metadata.get('library_id') != 'report-video-asset-library' or metadata.get('assets') != {}:
        raise SystemExit('FAIL metadata sidecar contract')

    try:
        mod.initialize_project(root / 'report-video', srt, project_id='my_test')
    except FileExistsError:
        pass
    else:
        raise SystemExit('FAIL existing project should not be overwritten')

print('PASS: init_project behavior')
