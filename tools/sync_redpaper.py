"""Fetch both upstream files, validate in isolation, then update tracked outputs."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
SOURCES = {
    'RedPaper_remove_ads.lpx': 'https://kelee.one/Tool/Loon/Lpx/RedPaper_remove_ads.lpx',
    'RedPaper_remove_ads.js': 'https://kelee.one/Resource/JavaScript/RedPaper/RedPaper_remove_ads.js',
}
OUTPUTS = ['Scripts/Surge/RedPaperSurge.js', 'Surge/Modules/RedPaper_remove_ads.sgmodule',
           'RedPaperSurge.js', 'RedPaper_remove_ads.sgmodule']


def fetch(url):
    with urlopen(Request(url, headers={'User-Agent': 'proxy-scripts-upstream-sync/1.0'}), timeout=60) as response:
        data = response.read(2_000_001)
    if not data or len(data) > 2_000_000:
        raise ValueError('Empty or oversized upstream response')
    text = data.decode('utf-8-sig')
    if '<html' in text.lower() or '<!doctype html' in text.lower():
        raise ValueError('Upstream returned an HTML error/challenge page')
    return data


def main():
    downloaded = {name: fetch(url) for name, url in SOURCES.items()}
    if all((ROOT / 'upstream/redpaper' / name).read_bytes() == data for name, data in downloaded.items()):
        print('Upstream unchanged; nothing to publish.')
        return
    with tempfile.TemporaryDirectory(prefix='redpaper-sync-') as directory:
        stage = Path(directory)
        for folder in ['tools', 'tests', 'upstream/redpaper']:
            shutil.copytree(ROOT / folder, stage / folder)
        for name, data in downloaded.items():
            (stage / 'upstream/redpaper' / name).write_bytes(data)
        for command in [['python3', 'tools/build_redpaper.py'],
                        ['node', '--check', 'Scripts/Surge/RedPaperSurge.js'],
                        ['node', 'tests/redpaper.cjs']]:
            subprocess.run(command, cwd=stage, check=True, timeout=60)
        # No tracked file is changed until the full candidate passes.
        for relative in OUTPUTS + ['upstream/redpaper/' + name for name in SOURCES]:
            destination = ROOT / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(stage / relative, destination)
        metadata = {'synced_at': datetime.now(timezone.utc).isoformat(), 'sources': {
            name: {'url': SOURCES[name], 'sha256': hashlib.sha256(data).hexdigest()}
            for name, data in downloaded.items()}}
        (ROOT / 'upstream/redpaper/sync.json').write_text(json.dumps(metadata, indent=2) + '\n')
        print('Upstream changed; Surge conversion and regression checks passed.')


if __name__ == '__main__':
    main()
