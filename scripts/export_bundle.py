"""Export tracked project files plus pinned upstream source as a portable ZIP.

Excludes Git metadata, secrets, environments and downloaded model/data caches.
Run after staging files so newly added artifacts appear in git ls-files.
"""
import hashlib
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def tracked(directory):
    output = subprocess.check_output(['git', '-C', str(directory), 'ls-files', '-z'])
    return [directory / name.decode() for name in output.split(b'\0') if name]


def main():
    paths = tracked(ROOT)
    destination = ROOT / 'dist/d2r-rag-reproduction.zip'
    destination.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(set(paths)):
            if path.is_file() and not path.is_symlink():
                archive.write(path, 'd2r-rag-reproduction/' + str(path.relative_to(ROOT)))
    with zipfile.ZipFile(destination) as archive:
        if archive.testzip() is not None:
            raise RuntimeError('ZIP integrity check failed')
    digest = hashlib.sha256(destination.read_bytes()).hexdigest()
    destination.with_suffix('.zip.sha256').write_text(digest + '  ' + destination.name + '\n')
    print(destination)
    print('SHA256:', digest)


if __name__ == '__main__':
    main()
