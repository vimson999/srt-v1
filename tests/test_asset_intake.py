import importlib.util
import json
import subprocess
import tempfile
from hashlib import sha256
from pathlib import Path
from shutil import copy2


ROOT = Path(__file__).resolve().parent.parent
INTAKE_SCRIPT = ROOT / 'scripts' / 'intake_assets.py'
INDEX_SCRIPT = Path('/Users/v9/Downloads/report-video/asset-library/catalog/build-index.mjs')

if not INTAKE_SCRIPT.exists():
    raise SystemExit('FAIL: scripts/intake_assets.py does not exist')

spec = importlib.util.spec_from_file_location('intake_assets', INTAKE_SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

with tempfile.TemporaryDirectory() as td:
    root = Path(td) / 'factory'
    inbox = root / 'asset-library' / 'inbox' / 'episode_a'
    (inbox / 'video').mkdir(parents=True)
    (inbox / 'reports').mkdir(parents=True)
    (inbox / 'video' / 'factory_line.mp4').write_bytes(b'video-bytes')
    (inbox / 'reports' / 'goldman.png').write_bytes(b'report-bytes')

    first = mod.intake_assets(root, 'episode_a', run_index=False)
    if first['imported_count'] != 2 or first['duplicate_count'] != 0:
        raise SystemExit(f'FAIL first intake summary: {first}')
    if not (root / 'asset-library' / 'raw' / 'video' / 'factory_line.mp4').exists():
        raise SystemExit('FAIL video was not copied into raw/video')
    if not (root / 'asset-library' / 'raw' / 'reports' / 'goldman.png').exists():
        raise SystemExit('FAIL report was not copied into raw/reports')

    second = mod.intake_assets(root, 'episode_a', run_index=False)
    if second['imported_count'] != 0 or second['duplicate_count'] != 2:
        raise SystemExit(f'FAIL duplicate intake summary: {second}')
    raw_files = list((root / 'asset-library' / 'raw').rglob('*'))
    if len([path for path in raw_files if path.is_file()]) != 2:
        raise SystemExit('FAIL duplicate files were created')

if not INDEX_SCRIPT.exists():
    raise SystemExit(f'FAIL: missing index builder at {INDEX_SCRIPT}')

with tempfile.TemporaryDirectory() as td:
    root = Path(td) / 'factory'
    library = root / 'asset-library'
    catalog = library / 'catalog'
    raw_video = library / 'raw' / 'video' / 'factory_line.mp4'
    raw_video.parent.mkdir(parents=True)
    raw_video.write_bytes(b'video-bytes')
    catalog.mkdir(parents=True)
    projects = root / 'projects' / 'episode_a' / 'manifest'
    projects.mkdir(parents=True)
    (catalog / 'project_roots.json').write_text(
        json.dumps({'roots': [{'path': '../projects'}]}), encoding='utf-8'
    )
    (projects / 'assets.json').write_text(
        json.dumps(
            {
                'assets': [
                    {
                        'asset_id': 'factory_line',
                        'type': 'video',
                        'category': 'context_broll',
                        'path': 'raw/video/factory_line.mp4',
                        'description': '机器生产线',
                        'tags': ['factory'],
                        'status': 'keep',
                        'usage': ['shot-1'],
                    }
                ]
            }
        ),
        encoding='utf-8',
    )
    (catalog / 'metadata.json').write_text(
        json.dumps(
            {
                'schema_version': 1,
                'library_id': 'report-video-asset-library',
                'assets': {
                    'factory_line': {
                        'description': '电子制造工厂自动化生产线广角镜头',
                        'tags': ['electronics', 'wide', 'low_motion'],
                        'status': 'backup',
                        'license_status': 'unverified',
                        'notes': '人工确认：可作为制造业语境背景。',
                    }
                },
            },
            ensure_ascii=False,
        ),
        encoding='utf-8',
    )
    builder = catalog / 'build-index.mjs'
    copy2(INDEX_SCRIPT, builder)
    subprocess.run(['node', str(builder)], check=True, capture_output=True, text=True)
    index = json.loads((catalog / 'assets.json').read_text(encoding='utf-8'))
    record = next(asset for asset in index['assets'] if asset['asset_id'] == 'factory_line')
    if record['description'] != '电子制造工厂自动化生产线广角镜头':
        raise SystemExit('FAIL manual description was not merged')
    if record['tags'] != ['electronics', 'wide', 'low_motion']:
        raise SystemExit('FAIL manual tags were not merged')
    if record['status'] != 'backup' or record['notes'] != '人工确认：可作为制造业语境背景。':
        raise SystemExit('FAIL manual review fields were not preserved')
    if record['file_exists'] is not True or record['file_size_bytes'] != len(b'video-bytes'):
        raise SystemExit('FAIL computed fields were not refreshed')

print('PASS: asset intake is idempotent and metadata survives index rebuild')
