"""Explicit source-package inventory; excludes workstation and device artifacts."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOP_LEVEL = (
    '.gitignore', '.gitattributes', '.editorconfig', 'README.md', 'README.es.md',
    'CHANGELOG.md', 'CONTRIBUTING.md', 'LICENSE',
)
DIRECTORIES = ('pico_final', 'tests', 'tools', 'docs', 'legacy', 'examples', '.github')
SUFFIXES = {'.py', '.md', '.svg', '.png', '.pdf', '.yml', '.yaml'}
EXCLUDED_PARTS = {
    '__pycache__', '.git', '.venv-pico', 'pico_backups', 'logs_cmcv', 'dist',
    'build', '.pytest_cache',
}
FIRMWARE = ('__init__.py', 'config.py', 'controller.py', 'hardware.py', 'runtime.py')


def source_paths():
    selected = {ROOT / name for name in TOP_LEVEL if (ROOT / name).is_file()}
    for directory in DIRECTORIES:
        for path in (ROOT / directory).rglob('*'):
            relative = path.relative_to(ROOT)
            if (path.is_file() and not path.is_symlink()
                    and not EXCLUDED_PARTS.intersection(relative.parts)
                    and path.suffix.lower() in SUFFIXES):
                selected.add(path)
    return sorted(selected)
