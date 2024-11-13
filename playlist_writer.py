# playlist_writer.py
import os
from pydub import AudioSegment

class PlaylistWriter:
    @staticmethod
    def create_m3u_playlist(save_path, files, extended=False):
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write("#EXTM3U\n")
            for file in files:
                if extended:
                    duration = PlaylistWriter.get_audio_duration(file)
                    title = os.path.basename(file)
                    f.write(f"#EXTINF:{duration},{title}\n")
                f.write(os.path.relpath(file, os.path.dirname(save_path)) + "\n")

    @staticmethod
    def create_pls_playlist(save_path, files):
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write("[playlist]\n")
            f.write(f"NumberOfEntries={len(files)}\n\n")
            for i, file in enumerate(files, 1):
                f.write(f"File{i}={os.path.relpath(file, os.path.dirname(save_path))}\n")
                f.write(f"Title{i}={os.path.basename(file)}\n")
                duration = PlaylistWriter.get_audio_duration(file)
                f.write(f"Length{i}={duration}\n\n")
            f.write("Version=2\n")

    @staticmethod
    def create_wpl_playlist(save_path, files):
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write('<?wpl version="1.0"?>\n<smil>\n<head>\n')
            f.write('<meta name="Generator" content="Playlist Creator"/>\n')
            f.write('<title>Playlist</title>\n</head>\n<body>\n<seq>\n')
            for file in files:
                rel_path = os.path.relpath(file, os.path.dirname(save_path))
                f.write(f'<media src="{rel_path}"/>\n')
            f.write('</seq>\n</body>\n</smil>')

    @staticmethod
    def get_audio_duration(file_path):
        try:
            audio = AudioSegment.from_file(file_path)
            return int(len(audio) / 1000)  # Duration in seconds
        except:
            return 0
