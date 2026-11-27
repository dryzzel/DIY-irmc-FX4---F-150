"""Run permanent and historical suites in separate interpreters. No device I/O."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    for label, cwd, directory in (
        ('Permanent firmware', ROOT, 'tests'),
        ('Historical regressions', ROOT / 'legacy', '.'),
    ):
        print('\n' + label, flush=True)
        result = subprocess.run(
            [sys.executable, '-B', '-m', 'unittest', 'discover', '-s', directory,
             '-p', 'test_*.py'], cwd=cwd,
        )
        if result.returncode:
            return result.returncode
    return 0


if __name__ == '__main__':
    sys.exit(main())
