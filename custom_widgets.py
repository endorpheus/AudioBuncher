# custom_widgets.py
from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QStyle
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize
from file_manager import FileManager

class ThumbnailListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIconSize(QSize(32, 32))
        self.setSpacing(2)

    def add_audio_item(self, file_path, text=None):
        if text is None:
            text = os.path.basename(file_path)
            
        item = QListWidgetItem(text)
        item.setData(Qt.ItemDataRole.UserRole, file_path)
        
        # Try to get thumbnail
        thumbnail = FileManager.extract_thumbnail(file_path)
        if thumbnail:
            item.setIcon(QIcon(QPixmap.fromImage(thumbnail)))
        else:
            # Use default music icon from system theme
            item.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
            
        self.addItem(item)
        return item
