import yt_dlp
import os

def get_ffmpeg_path():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ffmpeg_path = os.path.join(script_dir, "ffmpeg.exe")
    if os.path.exists(ffmpeg_path):
        return ffmpeg_path
    else:
        return None

def download_media(url, format_type='mp4'):
    if format_type == 'mp3':
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'postprocessor_args': ['-ar', '44100'],
            'prefer_ffmpeg': True,
            'overwrites': True,
        }
    elif format_type == 'mp4':
        ydl_opts = {
            'format': 'best',
            'overwrites': True,
        }
    else:
        print("Format non supporté. Choisissez 'mp3' ou 'mp4'.")
        return

    ffmpeg_path = get_ffmpeg_path()
    if ffmpeg_path:
        ydl_opts['ffmpeg_location'] = ffmpeg_path

    def my_hook(d):
        if d['status'] == 'finished':
            filename = d.get('filename', 'inconnu')
            print(f"Téléchargé : {os.path.basename(filename)}")

    ydl_opts['progress_hooks'] = [my_hook]

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

        extractor = info.get('extractor_key', 'Autre')
        uploader = info.get('uploader', 'Inconnu')

        if extractor.lower() == 'youtube':
            if 'music.youtube.com' in url:
                base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "YouTube Music")
            else:
                base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "YouTube Videos")
        elif extractor.lower() == 'tiktok':
            safe_uploader = "".join(c for c in uploader if c.isalnum() or c in " _-").rstrip()
            base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), safe_uploader)
        else:
            safe_extractor = "".join(c for c in extractor if c.isalnum() or c in " _-").rstrip()
            base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), safe_extractor)

        os.makedirs(base_dir, exist_ok=True)

        if 'entries' in info:
            playlist_title = info.get('title', 'Playlist')
            safe_title = "".join(c for c in playlist_title if c.isalnum() or c in " _-").rstrip()
            playlist_dir = os.path.join(base_dir, safe_title)
            os.makedirs(playlist_dir, exist_ok=True)
            ydl_opts['outtmpl'] = os.path.join(playlist_dir, '%(title)s.%(ext)s')
            print(f"Playlist détectée : {playlist_title}")
            print(f"Téléchargement dans : {playlist_dir}")
        else:
            ydl_opts['outtmpl'] = os.path.join(base_dir, '%(title)s.%(ext)s')

        with yt_dlp.YoutubeDL(ydl_opts) as ydl_final:
            ydl_final.download([url])

if __name__ == "__main__":
    url = input("Entrez l'URL : ").strip()
    format_choisi = input("Souhaitez-vous télécharger en 'mp3' ou 'mp4' ? ").strip().lower()

    if format_choisi not in ['mp3', 'mp4']:
        print("Format invalide. Utilisez 'mp3' ou 'mp4'.")
        exit()

    download_media(url, format_type=format_choisi)