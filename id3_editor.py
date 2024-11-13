# id3_editor.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFileDialog, QGroupBox, QFormLayout, QDialogButtonBox,
    QListWidget, QCheckBox, QSplitter, QWidget, QMessageBox, QApplication,
    QMenu, QTextEdit)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QAction
from mutagen.id3 import ID3, APIC
from mutagen.mp3 import MP3
import os
from tag_definitions import TagDefinitions
from audio_metadata import AudioMetadata
from id3_tag_copy import TagCopyDialog
from file_manager import FileManager

class ID3BatchEditor(QDialog):
    def __init__(self, file_paths, parent=None):
        super().__init__(parent)
        self.file_paths = file_paths
        self.setWindowTitle("Batch ID3 Tag Editor")
        self.setMinimumSize(900, 700)
        
        # Dictionary to store original tags for each file
        self.file_tags = {}
        self.load_all_tags()
        
        # Initialize UI elements
        self.tag_inputs = {}
        self.tag_checkboxes = {}
        
        self.setup_ui()
        self.setup_connections()
        
        # Store the new art path for batch operations
        self.new_art_path = None
        self.clear_art_flag = False

    def load_all_tags(self):
        for file_path in self.file_paths:
            try:
                audio = MP3(file_path)
                if not audio.tags:
                    audio.tags = ID3()
                self.file_tags[file_path] = audio.tags
            except Exception as e:
                print(f"Error loading tags for {file_path}: {e}")
                self.file_tags[file_path] = ID3()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Create splitter for file list and editing panel
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - File list and file info
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # File list section
        file_list_layout = QVBoxLayout()
        file_list_layout.addWidget(QLabel("Files to edit:"))
        self.file_list = QListWidget()
        self.file_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.show_file_context_menu)
        self.file_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        
        for file_path in self.file_paths:
            self.file_list.addItem(os.path.basename(file_path))
        file_list_layout.addWidget(self.file_list)
        
        # Add select/deselect all buttons
        select_buttons = QHBoxLayout()
        select_all = QPushButton("Select All")
        deselect_all = QPushButton("Deselect All")
        select_all.clicked.connect(lambda: self.file_list.selectAll())
        deselect_all.clicked.connect(lambda: self.file_list.clearSelection())
        select_buttons.addWidget(select_all)
        select_buttons.addWidget(deselect_all)
        file_list_layout.addLayout(select_buttons)
        
        left_layout.addLayout(file_list_layout)
        
        # File info section
        info_group = QGroupBox("File Information")
        info_layout = QVBoxLayout(info_group)
        self.info_label = QTextEdit()
        self.info_label.setReadOnly(True)
        info_layout.addWidget(self.info_label)
        left_layout.addWidget(info_group)
        
        splitter.addWidget(left_widget)
        
        # Right side - Tag editing
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Tag selection group
        tag_select_group = QGroupBox("Tags to Update")
        tag_select_layout = QVBoxLayout(tag_select_group)
        
        for tag_name in list(TagDefinitions.TAG_FRAMES.keys()) + ["Album Art"]:
            self.tag_checkboxes[tag_name] = QCheckBox(TagDefinitions.get_display_name(tag_name))
            tag_select_layout.addWidget(self.tag_checkboxes[tag_name])
        
        right_layout.addWidget(tag_select_group)
        
        # Tag editing group
        tag_group = QGroupBox("New Tag Values")
        form_layout = QFormLayout(tag_group)

        # Create input fields for all text-based tags
        for tag_name in TagDefinitions.TAG_FRAMES.keys():
            if tag_name == "Comment":
                self.tag_inputs[tag_name] = QTextEdit()
                self.tag_inputs[tag_name].setMaximumHeight(60)
                self.tag_inputs[tag_name].setEnabled(False)
            else:
                self.tag_inputs[tag_name] = QLineEdit()
                self.tag_inputs[tag_name].setEnabled(False)
            form_layout.addRow(f"{TagDefinitions.get_display_name(tag_name)}:", 
                             self.tag_inputs[tag_name])

        right_layout.addWidget(tag_group)

        # Album art group
        art_group = QGroupBox("Album Art")
        art_layout = QHBoxLayout(art_group)
        
        self.art_label = QLabel()
        self.art_label.setFixedSize(150, 150)
        self.art_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.art_label.setText("No Album Art")
        art_layout.addWidget(self.art_label)

        art_buttons = QVBoxLayout()
        self.load_art_btn = QPushButton("Load Art")
        self.clear_art_btn = QPushButton("Clear Art")
        self.load_art_btn.setEnabled(False)
        self.clear_art_btn.setEnabled(False)
        art_buttons.addWidget(self.load_art_btn)
        art_buttons.addWidget(self.clear_art_btn)
        art_buttons.addStretch()
        art_layout.addLayout(art_buttons)

        right_layout.addWidget(art_group)
        
        splitter.addWidget(right_widget)
        
        layout.addWidget(splitter)

        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Apply | 
            QDialogButtonBox.StandardButton.Close
        )
        apply_button = button_box.button(QDialogButtonBox.StandardButton.Apply)
        apply_button.clicked.connect(self.apply_changes)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def setup_connections(self):
        self.load_art_btn.clicked.connect(self.load_art)
        self.clear_art_btn.clicked.connect(self.clear_art)
        self.file_list.currentItemChanged.connect(self.update_file_info)
        self.file_list.itemSelectionChanged.connect(self.update_selection_info)
        
        # Connect tag checkboxes to enable/disable corresponding inputs
        for tag_name, checkbox in self.tag_checkboxes.items():
            if tag_name in self.tag_inputs:
                checkbox.toggled.connect(lambda checked, tn=tag_name: self.tag_inputs[tn].setEnabled(checked))
            elif tag_name == "Album Art":
                checkbox.toggled.connect(self.load_art_btn.setEnabled)
                checkbox.toggled.connect(self.clear_art_btn.setEnabled)

    def update_selection_info(self):
        selected_items = self.file_list.selectedItems()
        if len(selected_items) > 1:
            self.info_label.setText(f"{len(selected_items)} files selected")
            self.clear_tag_inputs()
        elif len(selected_items) == 1:
            self.update_file_info(selected_items[0], None)

    def clear_tag_inputs(self):
        for input_widget in self.tag_inputs.values():
            if isinstance(input_widget, QLineEdit):
                input_widget.clear()
            elif isinstance(input_widget, QTextEdit):
                input_widget.clear()

    def show_file_context_menu(self, position):
        current_item = self.file_list.currentItem()
        if not current_item:
            return

        menu = QMenu()
        
        copy_from_action = QAction("Copy Tags From This File", self)
        copy_from_action.triggered.connect(self.copy_tags_from_selected)
        menu.addAction(copy_from_action)
        
        export_art_action = QAction("Export Album Art...", self)
        export_art_action.triggered.connect(self.export_current_art)
        menu.addAction(export_art_action)
        
        menu.exec(self.file_list.mapToGlobal(position))

    def export_current_art(self):
        current_item = self.file_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Warning", "Please select a file first!")
            return

        file_path = self.file_paths[self.file_list.row(current_item)]
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

    def copy_tags_from_selected(self):
        current_item = self.file_list.currentItem()
        if not current_item:
            return
            
        source_file = self.file_paths[self.file_list.row(current_item)]
        
        # Get other selected files as targets
        target_files = []
        for item in self.file_list.selectedItems():
            if item != current_item:
                target_files.append(self.file_paths[self.file_list.row(item)])
        
        if not target_files:
            QMessageBox.warning(self, "Warning", 
                              "Please select additional files to copy tags to!")
            return
        
        dialog = TagCopyDialog(source_file, target_files, self)
        if dialog.exec():
            selected_tags = dialog.get_selected_tags()
            self.copy_tags_between_files(source_file, target_files, selected_tags)

    def copy_tags_between_files(self, source_file, target_files, selected_tags):
        source_tags = self.file_tags[source_file]
        errors = []
        
        for target_file in target_files:
            try:
                target_tags = self.file_tags[target_file]
                
                # Copy selected text tags
                for tag_name in selected_tags:
                    if tag_name in TagDefinitions.TAG_FRAMES:
                        frame_id = TagDefinitions.TAG_FRAMES[tag_name][0]
                        if frame_id in source_tags:
                            target_tags.add(source_tags[frame_id])
                
                # Handle album art separately
                if "Album Art" in selected_tags:
                    # Remove existing art
                    target_tags.delall("APIC")
                    # Copy art if present
                    for tag in source_tags.values():
                        if tag.FrameID == "APIC":
                            target_tags.add(tag)
                
                target_tags.save()
                
            except Exception as e:
                errors.append(f"{os.path.basename(target_file)}: {str(e)}")
        
        if errors:
            QMessageBox.warning(
                self,
                "Errors Occurred",
                "Errors while copying tags:\n" + "\n".join(errors)
            )
        else:
            QMessageBox.information(
                self,
                "Success",
                f"Tags copied successfully to {len(target_files)} files!"
            )
        
        # Refresh the file info display
        self.update_file_info(self.file_list.currentItem(), None)

    def update_file_info(self, current, previous):
        if not current:
            self.info_label.setText("")
            return
            
        file_path = self.file_paths[self.file_list.row(current)]
        tags = self.file_tags[file_path]
        
        # Get file and audio metadata
        metadata = AudioMetadata.get_formatted_metadata(file_path)
        
        # Get current tags
        tag_info = "\nCurrent Tags:\n"
        for tag_name in TagDefinitions.TAG_FRAMES.keys():
            value = TagDefinitions.get_tag_value(tags, tag_name)
            if value:
                tag_info += f"{TagDefinitions.get_display_name(tag_name)}: {value}\n"
        
        # Check for album art
        has_art = any(tag.FrameID == 'APIC' for tag in tags.values())
        tag_info += f"Album Art: {'Present' if has_art else 'None'}\n"
        
        # Update info display
        self.info_label.setText(metadata + tag_info)
        
        # Update album art preview
        if has_art:
            for tag in tags.values():
                if tag.FrameID == 'APIC':
                    pixmap = QPixmap()
                    pixmap.loadFromData(tag.data)
                    self.art_label.setPixmap(pixmap.scaled(
                        self.art_label.size(), 
                        Qt.AspectRatioMode.KeepAspectRatio, 
                        Qt.TransformationMode.SmoothTransformation
                    ))
                    break
        else:
            self.art_label.setText("No Album Art")

    def load_art(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Album Art",
            "",
            "Images (*.png *.jpg *.jpeg)"
        )
        if file_path:
            self.new_art_path = file_path
            pixmap = QPixmap(file_path)
            self.art_label.setPixmap(pixmap.scaled(
                self.art_label.size(), 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            ))
            self.clear_art_flag = False

    def clear_art(self):
        self.art_label.setText("No Album Art")
        self.new_art_path = None
        self.clear_art_flag = True

    def apply_changes(self):
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select files to update!")
            return

        # Confirm batch operation if multiple files selected
        if len(selected_items) > 1:
            result = QMessageBox.question(
                self,
                "Confirm Batch Operation",
                f"Are you sure you want to apply these changes to {len(selected_items)} files?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if result != QMessageBox.StandardButton.Yes:
                return

        # Get the tags that should be updated
        updates = {}
        for tag_name, checkbox in self.tag_checkboxes.items():
            if checkbox.isChecked() and tag_name in self.tag_inputs:
                if isinstance(self.tag_inputs[tag_name], QLineEdit):
                    value = self.tag_inputs[tag_name].text()
                else:  # QTextEdit for comments
                    value = self.tag_inputs[tag_name].toPlainText()
                    
                if value:
                    tag = TagDefinitions.create_tag(tag_name, value)
                    if tag:
                        updates[TagDefinitions.TAG_FRAMES[tag_name][0]] = tag
        
        # Process each selected file
        errors = []
        processed = 0
        
        for item in selected_items:
            file_path = self.file_paths[self.file_list.row(item)]
            try:
                tags = self.file_tags[file_path]
                
                # Update text tags
                for frame_id, frame in updates.items():
                    tags.add(frame)
                
                # Handle album art
                if self.tag_checkboxes['Album Art'].isChecked():
                    tags.delall("APIC")  # Remove existing art
                    if self.new_art_path:  # Add new art if provided
                        with open(self.new_art_path, 'rb') as art:
                            tags.add(
                                APIC(
                                    encoding=3,
                                    mime=f'image/{os.path.splitext(self.new_art_path)[1][1:]}',
                                    type=3,
                                    desc='Cover',
                                    data=art.read()
                                )
                            )
                
                # Save changes
                tags.save(file_path)
                processed += 1
                
            except Exception as e:
                errors.append(f"{os.path.basename(file_path)}: {str(e)}")
        
        # Show results
        if errors:
            QMessageBox.warning(
                self,
                "Errors Occurred",
                f"Processed {processed} files successfully.\n\nErrors:\n" + "\n".join(errors)
            )
        else:
            QMessageBox.information(
                self,
                "Success",
                f"Successfully updated {processed} files!"
            )
            
        # Refresh the file info display
        self.update_file_info(self.file_list.currentItem(), None)


def edit_id3_tags(file_paths, parent=None):
    dialog = ID3BatchEditor(file_paths, parent)
    return dialog.exec()