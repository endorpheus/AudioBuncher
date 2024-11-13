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
            combined = AudioSegment.empty()
            for i, file in enumerate(self.files):
                self.status.emit(f"Processing: {os.path.basename(file)}")
                audio = AudioSegment.from_file(file)
                combined += audio
                self.progress.emit(int((i + 1) / len(self.files) * 100))

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
            print(f"Error in audio combining: {e}")  # Add debug output
            self.finished.emit(False, str(e))
