
# main.py
import os
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QCheckBox, 
    QListWidget, QProgressBar, QFileDialog, QMessageBox, QFrame, QListWidgetItem,
    QAbstractItemView, QDialog, QDialogButtonBox, QRadioButton, QStyle, QMenuBar, QMenu)
from PyQt6.QtCore import Qt, QFileSystemWatcher, QSize
from PyQt6.QtGui import QIcon, QPixmap, QAction
from audio_thread import AudioCombinerThread
from playlist_writer import PlaylistWriter
from file_manager import FileManager
from config import PlaylistFormats
from AboutDialog import AboutDialog
from id3_editor import edit_id3_tags

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

class PlaylistCreator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Playlist Creator")
        self.setMinimumSize(1000, 700)
        self.fs_watcher = QFileSystemWatcher()
        self.fs_watcher.directoryChanged.connect(self.update_available_files)
        self.create_menu()
        self.setup_ui()

    def create_menu(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        # Edit ID3 Tags action
        edit_tags_action = QAction('Edit ID3 Tags', self)
        edit_tags_action.setShortcut('Ctrl+T')
        edit_tags_action.triggered.connect(self.edit_id3_tags)
        file_menu.addAction(edit_tags_action)

        # Export Album Art action
        export_art_action = QAction('Export Album Art', self)
        export_art_action.setShortcut('Ctrl+E')
        export_art_action.triggered.connect(self.export_album_art)
        file_menu.addAction(export_art_action)
        
        file_menu.addSeparator()
        
        # Quit action
        quit_action = QAction('Quit', self)
        quit_action.setShortcut('Ctrl+Q')
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        # About action
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def edit_id3_tags(self):
        # Get the selected files
        selected_files = self.get_selected_files_paths()
        if not selected_files:
            QMessageBox.warning(self, "Warning", "Please select files to edit tags!")
            return
            
        if edit_id3_tags(selected_files, self):
            # Refresh the displays
            self.update_available_files()

    def export_album_art(self):
        selected_files = self.get_selected_files_paths()
        if not selected_files:
            QMessageBox.warning(self, "Warning", "Please select a file to export album art from!")
            return
        
        # For now, just handle the first selected file
        file_path = selected_files[0]
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Album Art",
            "",
            "Images (*.jpg *.jpeg *.png)"
        )
        
        if save_path:
            if FileManager.export_thumbnail(file_path, save_path):
                QMessageBox.information(self, "Success", "Album art exported successfully!")
            else:
                QMessageBox.warning(self, "Error", "No album art found or error saving!")

    def show_about(self):
        about = AboutDialog(self)
        about.exec()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Directory selection
        dir_layout = QHBoxLayout()
        dir_label = QLabel("Select Directory:")
        self.dir_entry = QLineEdit()
        self.dir_entry.textChanged.connect(self.handle_directory_change)
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_directory)
        dir_layout.addWidget(dir_label)
        dir_layout.addWidget(self.dir_entry)
        dir_layout.addWidget(browse_btn)
        main_layout.addLayout(dir_layout)

        # Options
        options_frame = QFrame()
        options_frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        options_layout = QHBoxLayout(options_frame)
        
        self.recursive_check = QCheckBox("Include Subdirectories")
        self.recursive_check.setChecked(True)
        self.recursive_check.stateChanged.connect(self.update_available_files)
        
        sort_label = QLabel("Sort by:")
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["name", "date", "size"])
        self.sort_combo.currentTextChanged.connect(self.update_available_files)
        
        options_layout.addWidget(self.recursive_check)
        options_layout.addWidget(sort_label)
        options_layout.addWidget(self.sort_combo)
        options_layout.addStretch()
        
        main_layout.addWidget(options_frame)

        # Lists and controls
        lists_layout = QHBoxLayout()
        
        # Available files list
        available_layout = QVBoxLayout()
        available_label = QLabel("Available Files:")
        self.available_list = ThumbnailListWidget()
        self.available_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        available_layout.addWidget(available_label)
        available_layout.addWidget(self.available_list)
        
        # Control buttons
        control_layout = QVBoxLayout()
        add_btn = QPushButton("Add →")
        add_btn.clicked.connect(self.add_selected_files)
        remove_btn = QPushButton("← Remove")
        remove_btn.clicked.connect(self.remove_selected_files)
        add_all_btn = QPushButton("Add All →")
        add_all_btn.clicked.connect(self.add_all_files)
        remove_all_btn = QPushButton("← Remove All")
        remove_all_btn.clicked.connect(self.remove_all_files)
        
        control_layout.addStretch()
        control_layout.addWidget(add_btn)
        control_layout.addWidget(remove_btn)
        control_layout.addWidget(add_all_btn)
        control_layout.addWidget(remove_all_btn)
        control_layout.addStretch()
        
        # Selected files list
        selected_layout = QVBoxLayout()
        selected_label = QLabel("Selected Files:")
        self.selected_list = ThumbnailListWidget()
        self.selected_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.selected_list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        selected_layout.addWidget(selected_label)
        selected_layout.addWidget(self.selected_list)
        
        lists_layout.addLayout(available_layout)
        lists_layout.addLayout(control_layout)
        lists_layout.addLayout(selected_layout)
        main_layout.addLayout(lists_layout)

        # Playlist type selection
        type_layout = QHBoxLayout()
        type_label = QLabel("Playlist Type:")
        self.playlist_combo = QComboBox()
        self.playlist_combo.addItems(PlaylistFormats.FORMATS.keys())
        
        # Action buttons
        create_btn = QPushButton("Create Playlist")
        combine_btn = QPushButton("Combine Selected Audio")
        
        create_btn.clicked.connect(self.create_playlist)
        combine_btn.clicked.connect(self.combine_audio)
        
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.playlist_combo)
        type_layout.addStretch()
        type_layout.addWidget(create_btn)
        type_layout.addWidget(combine_btn)
        
        main_layout.addLayout(type_layout)

        # Progress bar and status
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_label = QLabel()
        
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.status_label)

    def handle_directory_change(self):
        watched_dirs = self.fs_watcher.directories()
        if watched_dirs:
            self.fs_watcher.removePaths(watched_dirs)
        
        new_dir = self.dir_entry.text()
        if os.path.exists(new_dir):
            self.fs_watcher.addPath(new_dir)
            if self.recursive_check.isChecked():
                for root, dirs, _ in os.walk(new_dir):
                    for dir in dirs:
                        self.fs_watcher.addPath(os.path.join(root, dir))
        
        self.update_available_files()

    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.dir_entry.setText(directory)

    def update_available_files(self):
        current_files = set(self.get_selected_files_paths())
        self.available_list.clear()
        
        for file in FileManager.get_audio_files(
            self.dir_entry.text(), 
            self.recursive_check.isChecked(),
            self.sort_combo.currentText()
        ):
            if file not in current_files:
                self.available_list.add_audio_item(file)

    def get_selected_files_paths(self):
        return [self.selected_list.item(i).data(Qt.ItemDataRole.UserRole)
                for i in range(self.selected_list.count())]

    def add_selected_files(self):
        for item in self.available_list.selectedItems():
            file_path = item.data(Qt.ItemDataRole.UserRole)
            self.selected_list.add_audio_item(file_path)
            self.available_list.takeItem(self.available_list.row(item))

    def remove_selected_files(self):
        for item in self.selected_list.selectedItems():
            file_path = item.data(Qt.ItemDataRole.UserRole)
            self.available_list.add_audio_item(file_path)
            self.selected_list.takeItem(self.selected_list.row(item))
        self.update_available_files()

    def add_all_files(self):
        while self.available_list.count() > 0:
            item = self.available_list.item(0)
            file_path = item.data(Qt.ItemDataRole.UserRole)
            self.selected_list.add_audio_item(file_path)
            self.available_list.takeItem(0)

    def remove_all_files(self):
        self.selected_list.clear()
        self.update_available_files()

    def create_playlist(self):
        files = self.get_selected_files_paths()
        if not files:
            QMessageBox.warning(self, "Warning", "No files selected for the playlist!")
            return

        playlist_info = PlaylistFormats.FORMATS[self.playlist_combo.currentText()]
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Playlist",
            "",
            f"{self.playlist_combo.currentText()} (*{playlist_info['ext']})"
        )

        if not save_path:
            return

        try:
            if playlist_info["ext"] in [".m3u", ".m3u8"]:
                PlaylistWriter.create_m3u_playlist(save_path, files, playlist_info["extended"])
            elif playlist_info["ext"] == ".pls":
                PlaylistWriter.create_pls_playlist(save_path, files)
            elif playlist_info["ext"] == ".wpl":
                PlaylistWriter.create_wpl_playlist(save_path, files)

            QMessageBox.information(self, "Success", "Playlist created successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create playlist: {str(e)}")

    def combine_audio(self):
        files = self.get_selected_files_paths()
        if not files:
            QMessageBox.warning(self, "Warning", "No files selected for combining!")
            return

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Combined Audio",
            "",
            "MP3 files (*.mp3)"
        )

        if not save_path:
            return

        # Select thumbnail source
        thumbnail_source = self.select_thumbnail_source(files)

        self.progress_bar.setVisible(True)
        self.combiner_thread = AudioCombinerThread(files, save_path, thumbnail_source)
        self.combiner_thread.progress.connect(self.progress_bar.setValue)
        self.combiner_thread.status.connect(self.status_label.setText)
        self.combiner_thread.finished.connect(self.handle_combine_finished)
        self.combiner_thread.start()

    def handle_combine_finished(self, success, message):
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)
        self.status_label.clear()
        
        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.critical(self, "Error", f"Failed to combine audio: {message}")

    def select_thumbnail_source(self, files):
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Thumbnail Source")
        layout = QVBoxLayout(dialog)
        
        layout.addWidget(QLabel("Choose thumbnail source for combined file:"))
        
        buttons = []
        for file in files:
            rb = QRadioButton(os.path.basename(file))
            rb.setProperty("file_path", file)
            thumbnail = FileManager.extract_thumbnail(file)
            if thumbnail:
                rb.setIcon(QIcon(QPixmap.fromImage(thumbnail)))
            buttons.append(rb)
            layout.addWidget(rb)
        
        if buttons:
            buttons[0].setChecked(True)
        
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            for button in buttons:
                if button.isChecked():
                    return button.property("file_path")
        return None

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = PlaylistCreator()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()