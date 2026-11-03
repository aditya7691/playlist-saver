"""Install Deno from its official release when no supported runtime is present."""
import io
import platform
import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path


def main():
    if shutil.which('deno'):
        return
    if sys.platform != 'win32' or platform.machine().lower() not in ('amd64', 'x86_64'):
        raise RuntimeError('Install Deno from https://deno.com/ and run Start.cmd again.')
    print('Setting up the YouTube JavaScript runtime from the official Deno release…')
    url = 'https://github.com/denoland/deno/releases/latest/download/deno-x86_64-pc-windows-msvc.zip'
    with urllib.request.urlopen(url, timeout=90) as response:
        data = response.read(150 * 1024 * 1024)
    target = Path(__file__).resolve().parent / 'tools'
    target.mkdir(exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        exe = archive.read('deno.exe')
    temporary = target / 'deno.exe.tmp'
    temporary.write_bytes(exe)
    temporary.replace(target / 'deno.exe')
    print('Runtime ready.')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print('Runtime setup failed:', exc)
        sys.exit(1)
