# file_manager.py
import os
from PyQt6.QtGui import QImage
from mutagen import File
from mutagen.id3 import ID3, APIC
from mutagen.mp3 import MP3
from config import AudioFormats

class FileManager:
    @staticmethod
    def get_audio_files(directory, recursive=True, sort_by="name"):
        files = []
        if not directory or not os.path.exists(directory):
            return files

        if recursive:
            for root, _, filenames in os.walk(directory):
                for filename in filenames:
                    if any(filename.lower().endswith(ext) for ext in AudioFormats.SUPPORTED_FORMATS):
                        files.append(os.path.join(root, filename))
        else:
            files = [os.path.join(directory, f) for f in os.listdir(directory)
                    if os.path.isfile(os.path.join(directory, f)) and 
                    any(f.lower().endswith(ext) for ext in AudioFormats.SUPPORTED_FORMATS)]

        if sort_by == "name":
            files.sort()
        elif sort_by == "date":
            files.sort(key=lambda x: os.path.getmtime(x))
        elif sort_by == "size":
            files.sort(key=lambda x: os.path.getsize(x))

        return files

    @staticmethod
    def extract_thumbnail(file_path):
        try:
            audio = File(file_path)
            if audio is None:
                return None
                
            # Handle MP3
            if isinstance(audio.tags, ID3):
                for tag in audio.tags.values():
                    if tag.FrameID in ('APIC', 'PIC'):
                        return QImage.fromData(tag.data)
                
            # Handle FLAC
            if hasattr(audio, 'pictures'):
                if audio.pictures:
                    return QImage.fromData(audio.pictures[0].data)
                
            # Handle other formats with embedded images
            if hasattr(audio.tags, 'images'):
                images = audio.tags.images
                if images:
                    return QImage.fromData(images[0].data)
                    
        except Exception as e:
            print(f"Error extracting thumbnail: {e}")
        return None

    @staticmethod
    def save_thumbnail(source_file, target_file):
        try:
            # Extract thumbnail from source
            source_audio = File(source_file)
            if source_audio is None:
                return
                
            # For MP3 files (most common case)
            if isinstance(source_audio.tags, ID3):
                for tag in source_audio.tags.values():
                    if tag.FrameID == 'APIC':
                        # Create new ID3 tags for target
                        id3 = ID3()
                        id3.add(
                            APIC(
                                encoding=tag.encoding,
                                mime=tag.mime,
                                type=tag.type,
                                desc=tag.desc,
                                data=tag.data
                            )
                        )
                        # Save the ID3 tags to the target file
                        id3.save(target_file, v2_version=3)
                        return True
                        
            # Handle FLAC
            elif hasattr(source_audio, 'pictures'):
                if source_audio.pictures:
                    target_audio = File(target_file)
                    if hasattr(target_audio, 'pictures'):
                        target_audio.pictures = source_audio.pictures
                        target_audio.save()
                        return True
                        
            # Handle other formats
            elif hasattr(source_audio.tags, 'images'):
                if source_audio.tags.images:
                    target_audio = File(target_file)
                    if hasattr(target_audio.tags, 'images'):
                        target_audio.tags.images = source_audio.tags.images
                        target_audio.save()
                        return True
                        
        except Exception as e:
            print(f"Error saving thumbnail: {e}")
            raise  # Re-raise the exception to see what's going wrong
        return False
