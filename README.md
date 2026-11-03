# Playlist Saver

**[Open Playlist Saver](https://aditya7691.github.io/playlist-saver/)**

Download a YouTube playlist directly into a folder on your Windows PC.

## First time

1. [Download the helper ZIP](https://github.com/aditya7691/playlist-saver/archive/refs/heads/main.zip) and extract it.
2. Open the extracted folder and double-click **Start.cmd**. Python 3.10+ is required. If needed, install it from [python.org](https://www.python.org/downloads/) with **Add Python to PATH** enabled.
3. First launch installs yt-dlp and FFmpeg into an isolated environment in the extracted folder, plus Deno from its official release for YouTube extraction. Internet is required.
4. Your browser opens the downloader. Choose a folder, paste a playlist link, choose quality, and click **Download playlist**.

## Every time after

Open **Start.cmd**, then use the page it opens or the link on your GitHub profile. Keep the helper window open until downloads finish. Closing the browser does not stop the helper. Use **Stop download** before closing the helper window.

The GitHub page carries your link and quality to the helper page. Confirm **Download playlist** there to begin. No GitHub password, access token, or cloud server is needed.

Videos are numbered in playlist order inside a playlist subfolder. Quality is an upper limit; the source may be lower. Merged video/audio uses MKV; combined source files may retain their original extension. VLC can play these files.

Run again with the same folder to resume. Completed video IDs are remembered in `.playlist-saver-history.txt`. To download completed videos at another quality, choose a new destination. The destination resets to Downloads/Playlists when the helper restarts.

## Troubleshooting

- **Can't reach the page:** open Start.cmd and keep its window open. Local address: http://127.0.0.1:17869/
- **YouTube changes:** close the helper, run Update.cmd, then reopen Start.cmd.
- **Runtime setup failed:** check the internet connection and reopen Start.cmd, or install [Deno](https://deno.com/) yourself. The automatic runtime setup supports 64-bit Intel/AMD Windows.
- **Unavailable videos:** private, deleted, age-restricted, or sign-in-required videos can fail. Expand Download activity to see details. The helper does not sign in or bypass restrictions.
- **Folder window hidden:** check behind the browser or use Alt+Tab.

The helper listens only on your own PC, checks requests with a per-session token, and does not expose a public download service. Download only videos you own or have permission to save.

Built with [yt-dlp](https://github.com/yt-dlp/yt-dlp) and [imageio-ffmpeg](https://github.com/imageio/imageio-ffmpeg).
