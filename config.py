# config.py
class PlaylistFormats:
    FORMATS = {
        "M3U (.m3u)": {
            "ext": ".m3u",
            "encoding": "utf-8",
            "relative_paths": True,
            "extended": False
        },
        "M3U Extended (.m3u8)": {
            "ext": ".m3u8",
            "encoding": "utf-8",
            "relative_paths": True,
            "extended": True
        },
        "PLS (.pls)": {
            "ext": ".pls",
            "encoding": "utf-8",
            "relative_paths": True
        },
        "Windows Media Player (.wpl)": {
            "ext": ".wpl",
            "encoding": "utf-8",
            "relative_paths": True
        }
    }

class AudioFormats:
    SUPPORTED_FORMATS = [".mp3", ".wav", ".ogg", ".flac", ".m4a", ".wma"]
