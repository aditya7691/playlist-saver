"""Playlist Saver: loopback-only web interface and download worker."""
import json
import os
import secrets
import subprocess
import sys
import threading
import webbrowser
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

BASE = Path(__file__).resolve().parent
PORT = 17869
ORIGIN = f'http://127.0.0.1:{PORT}'
TOKEN = secrets.token_urlsafe(32)
LOCK = threading.RLock()
STATE = {'running': False, 'status': 'Ready', 'folder': str(Path.home() / 'Downloads' / 'Playlists'), 'percent': 0, 'current': '', 'completed': 0, 'errors': 0}
LOG = deque(maxlen=200)
PROCESS = None
CANCEL = threading.Event()


def canonical_url(value):
    p = urlparse(str(value).strip())
    if p.scheme != 'https' or p.hostname not in {'youtube.com', 'www.youtube.com', 'm.youtube.com', 'music.youtube.com'}:
        raise ValueError('Enter an HTTPS YouTube playlist link.')
    playlist = parse_qs(p.query).get('list', [''])[0]
    if not playlist or len(playlist) > 200 or not all(c.isalnum() or c in '-_' for c in playlist):
        raise ValueError('Copy the full playlist link, including list=…')
    return 'https://www.youtube.com/playlist?list=' + playlist


def download_args(url, folder, quality, ffmpeg):
    if quality not in {'360', '480', '720', '1080', 'best'}:
        raise ValueError('Choose a supported video quality.')
    cap = '' if quality == 'best' else f'[height<={quality}]'
    return [sys.executable, '-m', 'yt_dlp', '--ignore-config', '--yes-playlist', '--newline', '--no-color',
            '--progress', '--no-simulate', '--ignore-errors', '--continue', '--windows-filenames',
            '--no-overwrites', '--ffmpeg-location', ffmpeg,
            '--download-archive', str(folder / '.playlist-saver-history.txt'),
            '--progress-template', 'download:PS_PROGRESS:%(progress._percent_str)s|%(info.title)s',
            '--print', 'after_move:PS_DONE:%(filepath)s',
            '-f', f'bv*{cap}+ba/b{cap}', '--merge-output-format', 'mkv',
            '-o', str(folder / '%(playlist_title).120B' / '%(playlist_index)03d - %(title).120B [%(id)s].%(ext)s'),
            '--', url]


def worker(url, folder, quality):
    global PROCESS
    try:
        import imageio_ffmpeg
        args = download_args(url, folder, quality, imageio_ffmpeg.get_ffmpeg_exe())
        if CANCEL.is_set():
            return
        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                encoding='utf-8', errors='replace', creationflags=0x08000000 if os.name == 'nt' else 0)
        with LOCK:
            PROCESS = proc
            if CANCEL.is_set():
                proc.terminate()
        for line in proc.stdout:
            line = line.rstrip()
            with LOCK:
                if line.startswith('PS_PROGRESS:'):
                    percent, _, title = line[len('PS_PROGRESS:'):].partition('|')
                    try:
                        STATE['percent'] = float(percent.strip().rstrip('%'))
                    except ValueError:
                        pass
                    STATE['current'] = title
                elif line.startswith('PS_DONE:'):
                    STATE['completed'] += 1
                    STATE['percent'] = 100
                    LOG.append('Saved: ' + line[len('PS_DONE:'):])
                else:
                    LOG.append(line)
                    if 'ERROR:' in line:
                        STATE['errors'] += 1
        code = proc.wait()
        with LOCK:
            if CANCEL.is_set():
                STATE['status'] = 'Stopped — click Download to resume.'
            elif code or STATE['errors']:
                STATE['status'] = 'Finished with errors — see activity for details.'
            else:
                STATE['status'] = 'Complete — videos are saved in your folder.'
    except Exception as exc:
        with LOCK:
            LOG.append(str(exc))
            STATE['status'] = 'Download failed — see activity for details.'
            STATE['errors'] += 1
    finally:
        with LOCK:
            PROCESS = None
            STATE['running'] = False
            if CANCEL.is_set():
                STATE['status'] = 'Stopped — click Download to resume.'


def choose_folder():
    # This runs on the helper's main thread, which owns Tk.
    from tkinter import Tk, filedialog
    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    try:
        return filedialog.askdirectory(parent=root, title='Save your playlists here')
    finally:
        root.destroy()


FOLDER_REQUESTS = __import__('queue').Queue()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def valid_host(self):
        return self.headers.get('Host') == f'127.0.0.1:{PORT}'

    def reply(self, data, code=200, kind='application/json; charset=utf-8'):
        body = json.dumps(data).encode() if isinstance(data, dict) else data.encode()
        self.send_response(code)
        self.send_header('Content-Type', kind)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if not self.valid_host():
            return self.reply({'error': 'Invalid host'}, 403)
        if self.path == '/':
            page = (BASE / 'docs' / 'index.html').read_text(encoding='utf-8')
            return self.reply(page.replace('"__LOCAL_CONFIG__"', json.dumps({'token': TOKEN})), kind='text/html; charset=utf-8')
        if self.path == '/api/status':
            if self.headers.get('X-Playlist-Token') != TOKEN:
                return self.reply({'error': 'Reopen the downloader page.'}, 403)
            with LOCK:
                return self.reply({**STATE, 'log': list(LOG)})
        return self.reply({'error': 'Not found'}, 404)

    def do_POST(self):
        if (not self.valid_host() or self.headers.get('Origin') != ORIGIN
                or self.headers.get('X-Playlist-Token') != TOKEN):
            return self.reply({'error': 'Reopen the downloader page.'}, 403)
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if not 0 <= size <= 8192:
                raise ValueError('Request is too large.')
            data = json.loads(self.rfile.read(size) or b'{}')
            if not isinstance(data, dict):
                raise ValueError('Invalid request.')
            if self.path == '/api/start':
                url = canonical_url(data.get('url', ''))
                quality = str(data.get('quality', '720'))
                if quality not in {'360', '480', '720', '1080', 'best'}:
                    raise ValueError('Choose a supported video quality.')
                with LOCK:
                    if STATE['running']:
                        return self.reply({'error': 'A download is already running.'}, 409)
                    folder = Path(STATE['folder']).expanduser().resolve()
                    folder.mkdir(parents=True, exist_ok=True)
                    CANCEL.clear()
                    LOG.clear()
                    STATE.update(running=True, status='Connecting to YouTube…', percent=0, current='', completed=0, errors=0)
                    threading.Thread(target=worker, args=(url, folder, quality), daemon=True).start()
                return self.reply({'ok': True})
            if self.path == '/api/stop':
                with LOCK:
                    if STATE['running']:
                        CANCEL.set()
                        if PROCESS and PROCESS.poll() is None:
                            PROCESS.terminate()
                        STATE['status'] = 'Stopping…'
                return self.reply({'ok': True})
            if self.path == '/api/folder':
                with LOCK:
                    if STATE['running']:
                        return self.reply({'error': 'Stop the download before changing folders.'}, 409)
                event, result = threading.Event(), {}
                FOLDER_REQUESTS.put((event, result))
                if not event.wait(180):
                    raise ValueError('Folder selection timed out. Try again.')
                with LOCK:
                    if result.get('folder') and not STATE['running']:
                        STATE['folder'] = result['folder']
                    return self.reply({'folder': STATE['folder']})
            if self.path == '/api/open':
                with LOCK:
                    folder = Path(STATE['folder'])
                folder.mkdir(parents=True, exist_ok=True)
                os.startfile(str(folder))
                return self.reply({'ok': True})
            return self.reply({'error': 'Not found'}, 404)
        except (ValueError, OSError) as exc:
            return self.reply({'error': str(exc)}, 400)


def main():
    try:
        server = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
    except OSError:
        print('A helper may already be running. Opening the downloader…')
        webbrowser.open(ORIGIN)
        return
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print('Playlist Saver is ready. Keep this window open while downloading.\n' + ORIGIN)
    webbrowser.open(ORIGIN)
    try:
        while True:
            try:
                event, result = FOLDER_REQUESTS.get(timeout=.25)
            except __import__('queue').Empty:
                continue
            try:
                result['folder'] = choose_folder()
            except Exception as exc:
                print('Could not open folder picker:', exc)
            finally:
                event.set()
    except KeyboardInterrupt:
        CANCEL.set()
        with LOCK:
            if PROCESS and PROCESS.poll() is None:
                PROCESS.terminate()
        server.shutdown()


if __name__ == '__main__':
    main()
