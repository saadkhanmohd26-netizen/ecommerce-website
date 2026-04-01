import os
import re
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
INSTANCE_DIR = REPO_ROOT / 'instance'
PUBLIC_URL_FILE = INSTANCE_DIR / 'public_base_url.txt'
PID_FILE = INSTANCE_DIR / 'cloudflared.pid'
LOG_FILE = INSTANCE_DIR / 'cloudflared.log'
PACKAGE_PATH = Path(os.environ.get('LOCALAPPDATA', '')) / 'Microsoft' / 'WinGet' / 'Packages' / 'Cloudflare.cloudflared_Microsoft.Winget.Source_8wekyb3d8bbwe' / 'cloudflared.exe'


def find_cloudflared():
    if PACKAGE_PATH.exists():
        return PACKAGE_PATH

    for candidate in os.environ.get('PATH', '').split(os.pathsep):
        exe = Path(candidate) / 'cloudflared.exe'
        if exe.exists():
            return exe

    raise FileNotFoundError('cloudflared.exe not found. Install it first with winget install --id Cloudflare.cloudflared --scope user')


def extract_public_url(text):
    match = re.search(r'https://[-a-zA-Z0-9]+\.trycloudflare\.com', text)
    return match.group(0) if match else ''


def main():
    INSTANCE_DIR.mkdir(exist_ok=True)
    cloudflared = find_cloudflared()

    with LOG_FILE.open('w', encoding='utf-8') as log_handle:
        process = subprocess.Popen(
            [str(cloudflared), 'tunnel', '--url', 'http://127.0.0.1:5000', '--no-autoupdate'],
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            text=True,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        )

    PID_FILE.write_text(str(process.pid), encoding='utf-8')
    deadline = time.time() + 30

    while time.time() < deadline:
        if process.poll() is not None:
            break

        try:
            log_text = LOG_FILE.read_text(encoding='utf-8', errors='ignore')
        except OSError:
            log_text = ''

        public_url = extract_public_url(log_text)
        if public_url:
            PUBLIC_URL_FILE.write_text(public_url, encoding='utf-8')
            print(public_url)
            return 0

        time.sleep(0.5)

    process.terminate()
    raise RuntimeError('Could not start Cloudflare tunnel. Check instance/cloudflared.log for details.')


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
