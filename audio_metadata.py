# audio_metadata.py
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
import os
from datetime import datetime

class AudioMetadata:
    @staticmethod
    def get_file_info(file_path):
        """Get comprehensive file information"""
        try:
            file_stats = os.stat(file_path)
            audio = MP3(file_path)
            
            info = {
                'file_size': AudioMetadata.format_size(file_stats.st_size),
                'modified_date': datetime.fromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'duration': AudioMetadata.format_duration(audio.info.length),
                'bitrate': f"{int(audio.info.bitrate / 1000)}kbps",
                'sample_rate': f"{int(audio.info.sample_rate / 1000)}kHz",
                'channels': 'Stereo' if audio.info.channels == 2 else 'Mono',
                'format': 'MP3',
                'mode': audio.info.mode
            }
            return info
            
        except Exception as e:
            return {
                'error': str(e)
            }

    @staticmethod
    def format_size(size_bytes):
        """Convert bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f}{unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f}TB"

    @staticmethod
    def format_duration(seconds):
        """Convert seconds to MM:SS format"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"

    @staticmethod
    def get_formatted_metadata(file_path):
        """Get formatted metadata string for display"""
        try:
            info = AudioMetadata.get_file_info(file_path)
            if 'error' in info:
                return f"Error reading file: {info['error']}"
                
            return (f"File Information:\n"
                   f"Size: {info['file_size']}\n"
                   f"Modified: {info['modified_date']}\n"
                   f"\nAudio Properties:\n"
                   f"Duration: {info['duration']}\n"
                   f"Bitrate: {info['bitrate']}\n"
                   f"Sample Rate: {info['sample_rate']}\n"
                   f"Channels: {info['channels']}\n"
                   f"Format: {info['format']}")
        except Exception as e:
            return f"Error formatting metadata: {str(e)}"
