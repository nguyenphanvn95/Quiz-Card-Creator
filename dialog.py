from aqt.qt import *
from aqt.utils import showInfo, tooltip
from anki.notes import Note
from anki.collection import Collection
from anki.decks import DeckId, DeckManager
from anki.models import ModelManager
import random
import json
from typing import Set, List, Dict, Tuple

class QuizCardCreatorDialog(QDialog):
    def __init__(self, col: Collection, default_deck_id: DeckId, parent=None):
        super().__init__(parent)
        self.col = col
        self.default_deck_id = default_deck_id
        self.deck_manager = DeckManager(col)
        self.model_manager = ModelManager(col)
        self.setup_ui()
        self.load_decks()
        self.load_note_types()
        self.connect_signals()
        
    def setup_ui(self):
        """Thiết lập giao diện"""
        self.setWindowTitle("Quiz Card Creator")
        
        # Layout chính với kích thước linh hoạt
        main_layout = QVBoxLayout(self)
        
        # Tạo scroll area để hỗ trợ nội dung dài
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        # Widget nội dung
        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        self.content_layout.setSpacing(8)
        
        # 1. Deck lấy dữ liệu
        self.content_layout.addWidget(self.create_section_header("1. Source Deck"))
        self.source_deck_combo = QComboBox()
        self.source_deck_combo.setMinimumWidth(300)
        self.content_layout.addWidget(self.source_deck_combo)
        self.content_layout.addSpacing(15)
        
        # 2. Note type lấy dữ liệu
        self.content_layout.addWidget(self.create_section_header("2. Source Note Type"))
        self.source_notetype_combo = QComboBox()
        self.content_layout.addWidget(self.source_notetype_combo)
        self.content_layout.addSpacing(15)
        
        # 3. Trường chứa từ vựng
        self.content_layout.addWidget(self.create_section_header("3. Vocabulary Field"))
        self.vocab_field_combo = QComboBox()
        self.content_layout.addWidget(self.vocab_field_combo)
        self.content_layout.addSpacing(15)
        
        # 4. Trường chứa nghĩa
        self.content_layout.addWidget(self.create_section_header("4. Meaning Field"))
        self.meaning_field_combo = QComboBox()
        self.content_layout.addWidget(self.meaning_field_combo)
        self.content_layout.addSpacing(20)
        
        # 5. Note type thẻ xuất ra
        self.content_layout.addWidget(self.create_section_header("5. Target Note Type"))
        self.target_notetype_combo = QComboBox()
        self.content_layout.addWidget(self.target_notetype_combo)
        self.content_layout.addSpacing(15)
        
        # 6. Nơi lưu thẻ quiz
        self.content_layout.addWidget(self.create_section_header("6. Save to Deck"))
        
        # Checkbox tạo deck mới
        self.new_deck_checkbox = QCheckBox("Create new deck: 'Quiz Notes'")
        self.new_deck_checkbox.setChecked(True)
        self.content_layout.addWidget(self.new_deck_checkbox)
        
        # Combo chọn deck có sẵn
        self.target_deck_combo = QComboBox()
        self.target_deck_combo.setEnabled(False)
        self.content_layout.addWidget(self.target_deck_combo)
        self.content_layout.addSpacing(20)
        
        # 7. Cấu hình nâng cao
        self.content_layout.addWidget(self.create_section_header("7. Advanced Options"))
        
        # Option: Skip existing quiz cards
        self.skip_existing_checkbox = QCheckBox("Skip notes that already have quiz cards")
        self.skip_existing_checkbox.setChecked(True)
        self.skip_existing_checkbox.setToolTip("Prevent creating duplicate quiz cards for the same vocabulary")
        self.content_layout.addWidget(self.skip_existing_checkbox)
        
        # Option: Number of random cards
        random_layout = QHBoxLayout()
        random_layout.addWidget(QLabel("Number of random cards:"))
        self.random_count_spin = QSpinBox()
        self.random_count_spin.setRange(1, 10)
        self.random_count_spin.setValue(3)
        self.random_count_spin.setMinimumWidth(60)
        random_layout.addWidget(self.random_count_spin)
        random_layout.addStretch()
        self.content_layout.addLayout(random_layout)
        
        self.content_layout.addSpacing(20)
        
        # 8. Thanh tiến trình
        self.progress_label = QLabel("Ready")
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.content_layout.addWidget(self.progress_label)
        self.content_layout.addWidget(self.progress_bar)
        self.content_layout.addSpacing(20)
        
        # 9. Nút hành động
        button_layout = QHBoxLayout()
        self.create_btn = QPushButton("Create Quiz Cards")
        self.create_btn.setMinimumWidth(120)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setMinimumWidth(120)
        button_layout.addStretch()
        button_layout.addWidget(self.create_btn)
        button_layout.addSpacing(10)
        button_layout.addWidget(self.cancel_btn)
        button_layout.addStretch()
        self.content_layout.addLayout(button_layout)
        
        # Thêm stretch để đẩy nội dung lên trên
        self.content_layout.addStretch()
        
        # Thiết lập scroll area
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
        
        # Thiết lập kích thước cửa sổ
        self.setMinimumSize(500, 600)
        
    def create_section_header(self, text: str) -> QLabel:
        """Tạo tiêu đề section"""
        label = QLabel(f"<b>{text}</b>")
        label.setStyleSheet("QLabel { color: #2c3e50; margin-top: 5px; }")
        return label
    
    def load_decks(self):
        """Tải danh sách deck"""
        try:
            decks = self.col.decks.all_names_and_ids()
            self.deck_map = {}
            
            for deck in decks:
                self.deck_map[str(deck.id)] = deck.name
                self.source_deck_combo.addItem(deck.name, deck.id)
                self.target_deck_combo.addItem(deck.name, deck.id)
            
            # Chọn deck mặc định
            default_deck_name = self.deck_manager.name_if_exists(self.default_deck_id)
            if default_deck_name:
                index = self.source_deck_combo.findText(default_deck_name)
                if index >= 0:
                    self.source_deck_combo.setCurrentIndex(index)
                    self.target_deck_combo.setCurrentIndex(index)
            
        except Exception as e:
            showInfo(f"Error loading decks: {str(e)}")
    
    def load_note_types(self):
        """Tải danh sách note type"""
        try:
            note_types = self.col.models.all_names_and_ids()
            self.model_map = {}
            
            for model in note_types:
                self.model_map[str(model.id)] = model.name
                self.source_notetype_combo.addItem(model.name, model.id)
                self.target_notetype_combo.addItem(model.name, model.id)
            
        except Exception as e:
            showInfo(f"Error loading note types: {str(e)}")
    
    def connect_signals(self):
        """Kết nối các tín hiệu"""
        # Khi chọn source deck, tải note types của deck đó
        self.source_deck_combo.currentIndexChanged.connect(self.on_source_deck_changed)
        
        # Khi chọn source note type, tải các trường
        self.source_notetype_combo.currentIndexChanged.connect(self.on_source_notetype_changed)
        
        # Khi chọn target note type, kiểm tra trường Quiz
        self.target_notetype_combo.currentIndexChanged.connect(self.on_target_notetype_changed)
        
        # Checkbox tạo deck mới
        self.new_deck_checkbox.toggled.connect(
            lambda checked: self.target_deck_combo.setEnabled(not checked)
        )
        
        # Nút hành động
        self.create_btn.clicked.connect(self.create_quiz_cards)
        self.cancel_btn.clicked.connect(self.reject)
        
        # Tải dữ liệu ban đầu
        self.on_source_deck_changed()
    
    def get_unique_note_ids_from_deck(self, deck_id: DeckId, model_id: int) -> List[int]:
        """Lấy danh sách note ID duy nhất từ deck, không trùng lặp"""
        try:
            cids = self.col.decks.cids(deck_id, children=True)
            if not cids:
                return []
            
            # Sử dụng set để loại bỏ trùng lặp
            note_ids = set()
            for cid in cids:
                card = self.col.get_card(cid)
                note = self.col.get_note(card.nid)
                if note.mid == model_id:
                    note_ids.add(note.id)
            
            return list(note_ids)
            
        except Exception as e:
            showInfo(f"Error getting unique notes: {str(e)}")
            return []
    
    def on_source_deck_changed(self):
        """Khi thay đổi deck nguồn - tối ưu hiệu suất"""
        try:
            deck_id = self.source_deck_combo.currentData()
            if not deck_id:
                return
            
            # Lấy tất cả card trong deck
            cids = self.col.decks.cids(deck_id, children=True)
            if not cids:
                self.source_notetype_combo.clear()
                return
            
            # Sử dụng set để lấy note type duy nhất
            note_type_ids = set()
            
            # Batch processing để tăng hiệu suất
            batch_size = 100
            for i in range(0, len(cids), batch_size):
                batch_cids = cids[i:i+batch_size]
                
                # Lấy note IDs từ card IDs
                placeholders = ','.join('?' for _ in batch_cids)
                query = f"SELECT nid FROM cards WHERE id IN ({placeholders})"
                nids = self.col.db.list(query, *batch_cids)
                
                if nids:
                    # Lấy model IDs từ note IDs
                    nid_placeholders = ','.join('?' for _ in nids)
                    model_query = f"SELECT mid FROM notes WHERE id IN ({nid_placeholders})"
                    mids = self.col.db.list(model_query, *nids)
                    note_type_ids.update(mids)
                
                QApplication.processEvents()
            
            # Cập nhật combo box
            self.source_notetype_combo.clear()
            
            for model_id, model_name in self.model_map.items():
                if int(model_id) in note_type_ids:
                    self.source_notetype_combo.addItem(model_name, int(model_id))
            
            if self.source_notetype_combo.count() > 0:
                self.source_notetype_combo.setCurrentIndex(0)
                self.on_source_notetype_changed()
            
        except Exception as e:
            showInfo(f"Error loading deck notes: {str(e)}")
    
    def on_source_notetype_changed(self):
        """Khi thay đổi note type nguồn"""
        try:
            model_id = self.source_notetype_combo.currentData()
            if not model_id:
                return
            
            model = self.col.models.get(model_id)
            if not model:
                return
            
            # Cập nhật combo box trường
            self.vocab_field_combo.clear()
            self.meaning_field_combo.clear()
            
            for field in model['flds']:
                field_name = field['name']
                self.vocab_field_combo.addItem(field_name, field_name)
                self.meaning_field_combo.addItem(field_name, field_name)
            
            if self.vocab_field_combo.count() > 0:
                self.vocab_field_combo.setCurrentIndex(0)
            
            if self.meaning_field_combo.count() > 1:
                self.meaning_field_combo.setCurrentIndex(1)
            elif self.meaning_field_combo.count() > 0:
                self.meaning_field_combo.setCurrentIndex(0)
            
        except Exception as e:
            showInfo(f"Error loading fields: {str(e)}")
    
    def on_target_notetype_changed(self):
        """Khi thay đổi note type đích"""
        # Ở đây chúng ta có thể thêm kiểm tra trường Quiz
        pass
    
    def get_config(self):
        """Đọc cấu hình từ file"""
        import os
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        default_config = {
            "default_quiz_deck_name": "Quiz Notes",
            "quiz_field_name": "Quiz",
            "max_random_cards": 3,
            "skip_existing_cards": True,
            "prevent_duplicates": True
        }
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return default_config
    
    def ensure_quiz_field(self, model_id):
        """Đảm bảo note type có trường Quiz"""
        try:
            config = self.get_config()
            quiz_field_name = config['quiz_field_name']
            
            model = self.col.models.get(model_id)
            if not model:
                return False
            
            # Kiểm tra xem trường Quiz đã tồn tại chưa
            for field in model['flds']:
                if field['name'] == quiz_field_name:
                    return True
            
            # Thêm trường Quiz mới
            field = self.col.models.new_field(quiz_field_name)
            self.col.models.add_field(model, field)
            self.col.models.save(model, updateReqs=False)
            
            return True
            
        except Exception as e:
            showInfo(f"Error adding quiz field: {str(e)}")
            return False
    
    def get_existing_quiz_notes(self, target_deck_id: DeckId, target_model_id: int, 
                               vocab_field: str, source_note_ids: List[int]) -> Set[str]:
        """Lấy danh sách từ vựng đã có quiz card"""
        try:
            existing_vocabs = set()
            
            # Lấy tất cả note trong deck đích
            cids = self.col.decks.cids(target_deck_id, children=True)
            if not cids:
                return existing_vocabs
            
            for cid in cids:
                card = self.col.get_card(cid)
                note = self.col.get_note(card.nid)
                
                # Chỉ kiểm tra note có cùng model
                if note.mid != target_model_id:
                    continue
                
                # Kiểm tra tag để xác định đây là quiz card
                if hasattr(note, 'tags') and 'quiz_generated' in note.tags:
                    # Tìm từ vựng gốc từ quiz card
                    config = self.get_config()
                    quiz_field_name = config['quiz_field_name']
                    
                    if quiz_field_name in note:
                        quiz_content = note[quiz_field_name]
                        # Quiz content có dạng: [vocab1][meaning1]|[vocab2][meaning2]
                        # Chúng ta cần lấy vocab1, vocab2, vocab3
                        parts = quiz_content.split('|')
                        for part in parts:
                            if part.startswith('[') and '][' in part:
                                # Lấy phần từ vựng (giữa [ và ][)
                                vocab_start = part.find('[') + 1
                                vocab_end = part.find('][')
                                if vocab_end > vocab_start:
                                    vocab = part[vocab_start:vocab_end]
                                    existing_vocabs.add(vocab)
            
            return existing_vocabs
            
        except Exception as e:
            print(f"Error getting existing quiz notes: {str(e)}")
            return set()
    
    def get_vocab_from_note(self, note: Note, vocab_field: str) -> str:
        """Lấy từ vựng từ note"""
        try:
            return note[vocab_field] if vocab_field in note else ""
        except:
            return ""
    
    def create_quiz_cards(self):
        """Tạo thẻ quiz với kiểm tra trùng lặp"""
        try:
            # Lấy thông tin từ giao diện
            source_deck_id = self.source_deck_combo.currentData()
            source_model_id = self.source_notetype_combo.currentData()
            target_model_id = self.target_notetype_combo.currentData()
            vocab_field = self.vocab_field_combo.currentData()
            meaning_field = self.meaning_field_combo.currentData()
            skip_existing = self.skip_existing_checkbox.isChecked()
            random_count = self.random_count_spin.value()
            
            if not all([source_deck_id, source_model_id, target_model_id, vocab_field, meaning_field]):
                showInfo("Please fill all required fields")
                return
            
            # Đảm bảo trường Quiz tồn tại trong note type đích
            if not self.ensure_quiz_field(target_model_id):
                showInfo("Failed to add Quiz field to target note type")
                return
            
            # Xác định deck đích
            if self.new_deck_checkbox.isChecked():
                config = self.get_config()
                deck_name = config['default_quiz_deck_name']
                
                # Tìm hoặc tạo deck mới
                deck_id = self.deck_manager.id_for_name(deck_name)
                if not deck_id:
                    deck_id = self.deck_manager.id(deck_name, create=True)
            else:
                deck_id = self.target_deck_combo.currentData()
            
            # Lấy danh sách note duy nhất (không trùng lặp)
            unique_note_ids = self.get_unique_note_ids_from_deck(source_deck_id, source_model_id)
            if not unique_note_ids:
                showInfo("No unique notes found in source deck")
                return
            
            # Nếu skip existing, lấy danh sách từ vựng đã có quiz
            existing_vocabs = set()
            if skip_existing:
                existing_vocabs = self.get_existing_quiz_notes(
                    deck_id, target_model_id, vocab_field, unique_note_ids
                )
            
            # Hiển thị thanh tiến trình
            self.progress_bar.setVisible(True)
            self.progress_bar.setMaximum(len(unique_note_ids))
            self.progress_label.setText(f"Processing 0/{len(unique_note_ids)} notes")
            QApplication.processEvents()
            
            config = self.get_config()
            quiz_field_name = config['quiz_field_name']
            
            created_count = 0
            skipped_count = 0
            failed_count = 0
            
            # Lấy tất cả note để dùng cho việc lấy ngẫu nhiên
            all_source_notes = []
            all_vocab_meaning_map = {}  # vocab -> meaning
            
            for note_id in unique_note_ids:
                try:
                    note = self.col.get_note(note_id)
                    vocab = self.get_vocab_from_note(note, vocab_field)
                    meaning = note[meaning_field] if meaning_field in note else ""
                    
                    if vocab and meaning:
                        all_source_notes.append(note)
                        all_vocab_meaning_map[vocab] = meaning
                except:
                    pass
            
            # Tạo quiz cards
            for i, note_id in enumerate(unique_note_ids):
                try:
                    note = self.col.get_note(note_id)
                    vocab = self.get_vocab_from_note(note, vocab_field)
                    meaning = note[meaning_field] if meaning_field in note else ""
                    
                    if not vocab or not meaning:
                        skipped_count += 1
                        continue
                    
                    # Kiểm tra xem đã có quiz card cho từ vựng này chưa
                    if skip_existing and vocab in existing_vocabs:
                        skipped_count += 1
                        continue
                    
                    # Lấy các note ngẫu nhiên (trừ note hiện tại)
                    available_notes = [n for n in all_source_notes 
                                     if n.id != note_id and self.get_vocab_from_note(n, vocab_field) != vocab]
                    
                    if len(available_notes) < random_count:
                        # Không đủ note để lấy ngẫu nhiên
                        skipped_count += 1
                        continue
                    
                    # Chọn ngẫu nhiên
                    random_notes = random.sample(available_notes, random_count)
                    
                    # Tạo chuỗi quiz
                    quiz_parts = []
                    for random_note in random_notes:
                        random_vocab = self.get_vocab_from_note(random_note, vocab_field)
                        random_meaning = random_note[meaning_field] if meaning_field in random_note else ""
                        
                        if random_vocab and random_meaning:
                            quiz_parts.append(f"[{random_vocab}][{random_meaning}]")
                    
                    if not quiz_parts:
                        failed_count += 1
                        continue
                    
                    # Tạo note mới
                    target_model = self.col.models.get(target_model_id)
                    new_note = Note(self.col, target_model)
                    
                    # Sao chép tất cả các trường từ note gốc
                    for field in note.keys():
                        if field in new_note:
                            new_note[field] = note[field]
                    
                    # Thêm dữ liệu quiz
                    new_note[quiz_field_name] = "|".join(quiz_parts)
                    
                    # Thêm tag để nhận biết
                    new_note.tags.append("quiz_generated")
                    
                    # Thêm note
                    self.col.add_note(new_note, deck_id)
                    created_count += 1
                    
                    # Thêm vào danh sách từ vựng đã tạo
                    existing_vocabs.add(vocab)
                    
                except Exception as e:
                    failed_count += 1
                    print(f"Error processing note {note_id}: {str(e)}")
                
                # Cập nhật tiến trình
                self.progress_bar.setValue(i + 1)
                self.progress_label.setText(f"Processing: {i + 1}/{len(unique_note_ids)} - "
                                          f"Created: {created_count}, Skipped: {skipped_count}")
                QApplication.processEvents()
            
            # Hoàn thành
            self.progress_label.setText(
                f"Complete! Created: {created_count}, Skipped: {skipped_count}, Failed: {failed_count}"
            )
            
            if created_count > 0:
                tooltip(f"Successfully created {created_count} quiz cards\n"
                       f"Skipped {skipped_count} duplicate/existing cards")
                self.accept()
            else:
                showInfo("No quiz cards were created. Check if cards already exist.")
            
        except Exception as e:
            showInfo(f"Error creating quiz cards: {str(e)}")
        finally:
            self.progress_bar.setVisible(False)