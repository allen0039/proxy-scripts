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
# The publisher serves these Loon resources to versioned Loon clients.
USER_AGENT = 'Loon/962 CFNetwork/3860.500.111.2.2 Darwin/25.0.0'

OUTPUTS = ['Scripts/Surge/RedPaperSurge.js', 'Surge/Modules/RedPaper_remove_ads.sgmodule',
           'RedPaperSurge.js', 'RedPaper_remove_ads.sgmodule']


def fetch(url):
    with urlopen(Request(url, headers={'User-Agent': USER_AGENT}), timeout=60) as response:
        data = response.read(2_000_001)
    if not data or len(data) > 2_000_000:
        raise ValueError('Empty or oversized upstream response')
    text = data.decode('utf-8-sig')
    if '<html' in text.lower() or '<!doctype html' in text.lower():
        raise ValueError('Upstream returned an HTML error/challenge page')
    return data


def main():
    downloaded = {name: fetch(url) for name, url in SOURCES.items()}
    unchanged = all((ROOT / 'upstream/redpaper' / name).read_bytes() == data for name, data in downloaded.items())
    # Publish an initial receipt even if the first live fetch matches the snapshot.
    if unchanged and (ROOT / 'upstream/redpaper/sync.json').exists():
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
        print('Upstream verified; Surge conversion and regression checks passed.')


if __name__ == '__main__':
    main()
