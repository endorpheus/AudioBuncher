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
            # Create new ID3 tag for target
            audio = MP3(target_file)
            if not audio.tags:
                audio.tags = ID3()
            
            # Extract thumbnail from source
            source_audio = File(source_file)
            if source_audio is None:
                return False

            # Handle MP3 source
            if isinstance(source_audio.tags, ID3):
                for tag in source_audio.tags.values():
                    if tag.FrameID == 'APIC':
                        # Remove existing art
                        audio.tags.delall('APIC')
                        # Add new art
                        audio.tags.add(
                            APIC(
                                encoding=tag.encoding,
                                mime=tag.mime,
                                type=tag.type,
                                desc=tag.desc,
                                data=tag.data
                            )
                        )
                        audio.save()
                        return True

            # Handle FLAC source
            if hasattr(source_audio, 'pictures') and source_audio.pictures:
                pic = source_audio.pictures[0]
                audio.tags.delall('APIC')
                audio.tags.add(
                    APIC(
                        encoding=3,
                        mime=pic.mime,
                        type=3,
                        desc='Cover',
                        data=pic.data
                    )
                )
                audio.save()
                return True

            # Handle other formats
            if hasattr(source_audio.tags, 'images') and source_audio.tags.images:
                img = source_audio.tags.images[0]
                audio.tags.delall('APIC')
                audio.tags.add(
                    APIC(
                        encoding=3,
                        mime=f'image/{img.mime_type}',
                        type=3,
                        desc='Cover',
                        data=img.data
                    )
                )
                audio.save()
                return True
                
        except Exception as e:
            print(f"Error saving thumbnail: {e}")
        return False

    @staticmethod
    def export_thumbnail(file_path, save_path):
        """Extract and save album art to a file"""
        try:
            audio = File(file_path)
            if audio is None:
                return False

            # Handle MP3
            if isinstance(audio.tags, ID3):
                for tag in audio.tags.values():
                    if tag.FrameID in ('APIC', 'PIC'):
                        with open(save_path, 'wb') as img_file:
                            img_file.write(tag.data)
                        return True

            # Handle FLAC
            if hasattr(audio, 'pictures') and audio.pictures:
                with open(save_path, 'wb') as img_file:
                    img_file.write(audio.pictures[0].data)
                return True

            # Handle other formats
            if hasattr(audio.tags, 'images') and audio.tags.images:
                with open(save_path, 'wb') as img_file:
                    img_file.write(audio.tags.images[0].data)
                return True

        except Exception as e:
            print(f"Error exporting thumbnail: {e}")
        return False