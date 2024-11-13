# audio_thread.py
import os
from PyQt6.QtCore import QThread, pyqtSignal
from pydub import AudioSegment
from file_manager import FileManager

class AudioCombinerThread(QThread):
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, files, save_path, thumbnail_source=None):
        super().__init__()
        self.files = files
        self.save_path = save_path
        self.thumbnail_source = thumbnail_source

    def run(self):
        try:
            total_length = 0
            # First pass - calculate total length
            for file in self.files:
                self.status.emit(f"Analyzing: {os.path.basename(file)}")
                audio = AudioSegment.from_file(file)
                total_length += len(audio)

            combined = AudioSegment.empty()
            processed_length = 0
            # Second pass - combine files
            for file in self.files:
                self.status.emit(f"Combining: {os.path.basename(file)}")
                audio = AudioSegment.from_file(file)
                combined += audio
                processed_length += len(audio)
                self.progress.emit(int(processed_length * 100 / total_length))

            self.status.emit("Exporting combined audio...")
            # Export with parameters that ensure ID3 tag compatibility
            combined.export(
                self.save_path,
                format="mp3",
                tags={},  # Initialize empty tags
                id3v2_version='3'  # Use ID3v2.3
            )

            # Apply thumbnail if selected
            if self.thumbnail_source:
                self.status.emit("Applying thumbnail...")
                if not FileManager.save_thumbnail(self.thumbnail_source, self.save_path):
                    print("Failed to save thumbnail")

            self.finished.emit(True, "Audio files combined successfully!")
        except Exception as e:
            print(f"Error in audio combining: {e}")
            self.finished.emit(False, str(e))
