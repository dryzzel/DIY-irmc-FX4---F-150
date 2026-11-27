"""Offline syntax, local-link, and targeted publication checks. No board access."""
import re
import sys
from urllib.parse import unquote, urlsplit

from release_files import ROOT, FIRMWARE, source_paths

PRIVATE_PATTERNS = tuple(re.compile(pattern) for pattern in (
    r'[A-Za-z]:[\\/]Users[\\/][^\s]+',
    r'/(?:home|Users)/[A-Za-z0-9_.-]+/',
    r'gh[pousr]_[A-Za-z0-9]{20,}',
    r'github_pat_[A-Za-z0-9_]{20,}',
    r'sk-[A-Za-z0-9]{20,}',
    r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
))


def check():
    paths = source_paths()
    selected = set(paths)
    errors = []
    for name in (*FIRMWARE, 'main.py'):
        if ROOT / 'pico_final' / name not in selected:
            errors.append('Missing firmware file: ' + name)
    license_path = ROOT / 'LICENSE'
    if not license_path.is_file() or 'GNU GENERAL PUBLIC LICENSE' not in license_path.read_text(encoding='utf-8'):
        errors.append('Missing GPL license text')
    for path in paths:
        relative = path.relative_to(ROOT).as_posix()
        if path.suffix.lower() in {'.png', '.pdf'}:
            continue
        content = path.read_text(encoding='utf-8-sig')
        if path.suffix == '.py':
            try:
                compile(content, relative, 'exec')
            except SyntaxError as exc:
                errors.append('{}: {}'.format(relative, exc))
        if any(pattern.search(content) for pattern in PRIVATE_PATTERNS):
            errors.append('Review possible private data in ' + relative)
        if path.suffix != '.md':
            continue
        for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', content):
            target = target.strip().strip('<>')
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            destination = (path.parent / unquote(parsed.path)).resolve()
            if not destination.is_relative_to(ROOT) or not destination.exists():
                errors.append('{}: missing local link {}'.format(relative, target))
            elif destination.is_file() and destination not in selected:
                errors.append('{}: link excluded from release {}'.format(relative, target))
    for error in errors:
        print('ERROR:', error)
    if not errors:
        print('Checked {} public files: syntax, local links, license and targeted privacy scan OK.'.format(len(paths)))
    return not errors


if __name__ == '__main__':
    sys.exit(0 if check() else 1)
