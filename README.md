# Playlist Saver

**[Open Playlist Saver](https://aditya7691.github.io/playlist-saver/)**

Download a YouTube or YouTube Music playlist as videos or MP3 audio directly into a folder on your Windows PC.

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

## YouTube Music and audio-only downloads

Paste the playlist's Share link (music.youtube.com/playlist?list=… works), select **Audio only · MP3**, choose 128, 192, or 320 kbps or best variable bitrate, then download. Tracks are numbered in playlist order under **Audio / playlist name** inside your selected folder. Higher MP3 settings cannot improve the original source quality.

Audio and video use separate download histories, so a previously saved video can also be downloaded as audio. Audio quality changes still skip completed tracks; choose another destination to download them again. Public and accessible unlisted playlists work; private and sign-in-required playlists are not supported.

After updating helper.py, close the running helper and reopen Start.cmd, then refresh the page.

## Troubleshooting

- **Audio selected but MKV video saved:** an older helper process can keep running after its files are updated. Stop the download, close its command window, reopen the updated Start.cmd, and refresh the page. The page now checks helper capabilities and confirms the selected download type before starting.

- **Access denied / WinError 5:** the helper now checks that it can create files and subfolders before starting. Choose a writable folder. If the helper was launched from the chat, close that helper and open Start.cmd yourself from File Explorer so it runs with your normal Windows folder access. Administrator access is not needed.
- **Can't reach the page:** open Start.cmd and keep its window open. Local address: http://127.0.0.1:17869/
- **YouTube changes:** close the helper, run Update.cmd, then reopen Start.cmd.
- **Runtime setup failed:** check the internet connection and reopen Start.cmd, or install [Deno](https://deno.com/) yourself. The automatic runtime setup supports 64-bit Intel/AMD Windows.
- **Unavailable videos:** private, deleted, age-restricted, or sign-in-required videos can fail. Expand Download activity to see details. The helper does not sign in or bypass restrictions.
- **Folder window hidden:** check behind the browser or use Alt+Tab.

The helper listens only on your own PC, checks requests with a per-session token, and does not expose a public download service. Download only videos you own or have permission to save.

Built with [yt-dlp](https://github.com/yt-dlp/yt-dlp) and [imageio-ffmpeg](https://github.com/imageio/imageio-ffmpeg).
