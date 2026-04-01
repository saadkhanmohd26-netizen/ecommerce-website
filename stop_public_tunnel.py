import signal
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
INSTANCE_DIR = REPO_ROOT / 'instance'
PUBLIC_URL_FILE = INSTANCE_DIR / 'public_base_url.txt'
PID_FILE = INSTANCE_DIR / 'cloudflared.pid'


def main():
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text(encoding='utf-8').strip())
            try:
                import os
                os.kill(pid, signal.SIGTERM)
            except OSError:
                pass
        except Exception:
            pass
        PID_FILE.unlink(missing_ok=True)

    PUBLIC_URL_FILE.unlink(missing_ok=True)
    print('Public tunnel stopped.')


if __name__ == '__main__':
    main()
