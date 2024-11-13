# id3_tag_copy.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QListWidget, QCheckBox, QGroupBox, QMessageBox)
from PyQt6.QtCore import Qt
from tag_definitions import TagDefinitions

class TagCopyDialog(QDialog):
    def __init__(self, source_file, target_files, parent=None):
        super().__init__(parent)
        self.source_file = source_file
        self.target_files = target_files
        self.selected_tags = set()
        
        self.setWindowTitle("Copy Tags")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Source file info
        source_group = QGroupBox("Source")
        source_layout = QVBoxLayout(source_group)
        source_layout.addWidget(QLabel(f"Copy tags from: {self.source_file}"))
        layout.addWidget(source_group)

        # Tag selection
        tag_group = QGroupBox("Select Tags to Copy")
        tag_layout = QVBoxLayout(tag_group)
        
        # Add checkboxes for each tag type
        self.tag_checkboxes = {}
        for tag_name in TagDefinitions.TAG_FRAMES.keys():
            checkbox = QCheckBox(TagDefinitions.get_display_name(tag_name))
            checkbox.toggled.connect(self.update_selected_tags)
            self.tag_checkboxes[tag_name] = checkbox
            tag_layout.addWidget(checkbox)
        
        # Add Album Art checkbox separately
        art_checkbox = QCheckBox("Album Art")
        art_checkbox.toggled.connect(self.update_selected_tags)
        self.tag_checkboxes["Album Art"] = art_checkbox
        tag_layout.addWidget(art_checkbox)
        
        layout.addWidget(tag_group)

        # Target files list
        target_group = QGroupBox("Target Files")
        target_layout = QVBoxLayout(target_group)
        
        self.file_list = QListWidget()
        for file_path in self.target_files:
            self.file_list.addItem(file_path)
        target_layout.addWidget(self.file_list)
        
        layout.addWidget(target_group)

        # Buttons
        button_layout = QHBoxLayout()
        select_all = QPushButton("Select All Tags")
        deselect_all = QPushButton("Deselect All Tags")
        select_all.clicked.connect(self.select_all_tags)
        deselect_all.clicked.connect(self.deselect_all_tags)
        
        ok_button = QPushButton("Copy Tags")
        cancel_button = QPushButton("Cancel")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(select_all)
        button_layout.addWidget(deselect_all)
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)

    def update_selected_tags(self):
        self.selected_tags = {tag_name for tag_name, checkbox 
                            in self.tag_checkboxes.items() 
                            if checkbox.isChecked()}

    def select_all_tags(self):
        for checkbox in self.tag_checkboxes.values():
            checkbox.setChecked(True)

    def deselect_all_tags(self):
        for checkbox in self.tag_checkboxes.values():
            checkbox.setChecked(False)

    def get_selected_tags(self):
        return self.selected_tags
