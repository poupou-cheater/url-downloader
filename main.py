import yt_dlp
import os
import sys

def get_ffmpeg_path():
    """Retourne le chemin vers ffmpeg.exe dans le même dossier que le script exécutable."""
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))  # Utilise sys.argv[0] pour le .exe
    ffmpeg_path = os.path.join(script_dir, "ffmpeg.exe")
    if os.path.exists(ffmpeg_path):
        return ffmpeg_path
    else:
        return None  # yt-dlp cherchera dans le PATH

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
            'overwrites': True,  # Écrase les fichiers existants
        }
    elif format_type == 'mp4':
        ydl_opts = {
            'format': 'best',
            'overwrites': True,  # Écrase les fichiers existants
        }
    else:
        print("Format not supported. chose 'mp3' or 'mp4'please.")
        return

    # Ajouter le chemin de ffmpeg s'il est présent dans le même dossier que le .exe
    ffmpeg_path = get_ffmpeg_path()
    if ffmpeg_path:
        ydl_opts['ffmpeg_location'] = ffmpeg_path
    else:
        print("WARNING: ffmpeg.exe not found please read the README.")

    def my_hook(d):
        if d['status'] == 'finished':
            filename = d.get('filename', 'inconnu')
            print(f"Téléchargé : {os.path.basename(filename)}")

    ydl_opts['progress_hooks'] = [my_hook]

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

        # Déterminer le nom de la plateforme ou site
        extractor = info.get('extractor_key', 'Autre')  # Ex: 'youtube', 'tiktok', 'instagram', etc.
        uploader = info.get('uploader', 'Inconnu')

        # Créer un dossier en fonction de la plateforme ou uploader
        script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))  # Dossier du script/.exe
        if extractor.lower() == 'youtube':
            if 'music.youtube.com' in url:
                base_dir = os.path.join(script_dir, "YouTube Music")
            else:
                base_dir = os.path.join(script_dir, "YouTube Videos")
        elif extractor.lower() == 'tiktok':
            safe_uploader = "".join(c for c in uploader if c.isalnum() or c in " _-").rstrip()
            base_dir = os.path.join(script_dir, safe_uploader)
        else:
            # Pour les autres plateformes, créer un dossier nommé d'après l'extractor
            safe_extractor = "".join(c for c in extractor if c.isalnum() or c in " _-").rstrip()
            base_dir = os.path.join(script_dir, safe_extractor)

        os.makedirs(base_dir, exist_ok=True)

        # Gérer les playlists
        if 'entries' in info:  # C’est une playlist
            playlist_title = info.get('title', 'Playlist')
            safe_title = "".join(c for c in playlist_title if c.isalnum() or c in " _-").rstrip()
            playlist_dir = os.path.join(base_dir, safe_title)
            os.makedirs(playlist_dir, exist_ok=True)
            ydl_opts['outtmpl'] = os.path.join(playlist_dir, '%(title)s.%(ext)s')
            print(f"Playlist détectée : {playlist_title}")
            print(f"Téléchargement dans : {playlist_dir}")
        else:  # Vidéo seule
            ydl_opts['outtmpl'] = os.path.join(base_dir, '%(title)s.%(ext)s')

        # Télécharger
        with yt_dlp.YoutubeDL(ydl_opts) as ydl_final:
            ydl_final.download([url])

if __name__ == "__main__":
    url = input("ENTER URL : ").strip()
    format_choisi = input("you want download 'mp3' or 'mp4' ? ").strip().lower()

    if format_choisi not in ['mp3', 'mp4']:
        print("Format invalide. Use 'mp3' ou 'mp4'.")
        input("press enter to leave ...")  # Empêche la fermeture immédiate
        exit()

    download_media(url, format_type=format_choisi)
