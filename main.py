from aqt import mw, gui_hooks
from aqt.browser import Browser
from aqt.qt import *
from aqt.utils import showInfo, tooltip
from anki.notes import Note
from anki.collection import Collection
from anki.decks import DeckId
import random
import os
from .dialog import QuizCardCreatorDialog

# Biến toàn cục để theo dõi menu đã được thêm chưa
_menu_added = False

def setup_addon():
    """Thiết lập addon"""
    gui_hooks.browser_menus_did_init.append(add_menu_to_browser)
    
    # Thêm vào menu Tools của Anki
    if mw:
        setup_main_menu()

def setup_main_menu():
    """Thêm menu vào Tools của Anki chính"""
    action = QAction("Create Quiz Card Notes...", mw)
    action.triggered.connect(lambda: open_dialog_from_main())
    mw.form.menuTools.addAction(action)

def add_menu_to_browser(browser: Browser):
    """Thêm menu vào Browser"""
    global _menu_added
    
    # Đảm bảo chỉ thêm một lần
    if _menu_added:
        return
    
    # Tạo action
    action = QAction("Create Quiz Card Note...", browser)
    action.triggered.connect(lambda: open_dialog_from_browser(browser))
    
    # Thêm vào menu Edit
    browser.form.menuEdit.addSeparator()
    browser.form.menuEdit.addAction(action)
    
    _menu_added = True

def open_dialog_from_browser(browser: Browser):
    """Mở dialog từ Browser"""
    try:
        # Lấy các thẻ được chọn trong browser
        selected_nids = browser.selectedNotes()
        
        if selected_nids:
            # Lấy note đầu tiên để xác định deck
            note = browser.col.get_note(selected_nids[0])
            cards = browser.col.db.list("SELECT id FROM cards WHERE nid = ?", note.id)
            if cards:
                first_card = browser.col.get_card(cards[0])
                deck_id = first_card.did
            else:
                deck_id = browser.col.decks.selected()
        else:
            deck_id = browser.col.decks.selected()
        
        # Mở dialog
        dialog = QuizCardCreatorDialog(browser.col, deck_id, browser)
        dialog.exec()
        
    except Exception as e:
        showInfo(f"Error opening dialog: {str(e)}")

def open_dialog_from_main():
    """Mở dialog từ menu Tools chính"""
    if not mw or not mw.col:
        showInfo("Please open a collection first")
        return
    
    try:
        deck_id = mw.col.decks.selected()
        dialog = QuizCardCreatorDialog(mw.col, deck_id, mw)
        dialog.exec()
        
    except Exception as e:
        showInfo(f"Error: {str(e)}")

def check_for_existing_quiz_cards(col: Collection, vocab: str, deck_id: DeckId, quiz_field_name: str) -> bool:
    """Kiểm tra xem từ vựng đã có quiz card chưa"""
    try:
        # Lấy tất cả card trong deck
        cids = col.decks.cids(deck_id, children=True)
        if not cids:
            return False
        
        for cid in cids:
            card = col.get_card(cid)
            note = col.get_note(card.nid)
            
            # Kiểm tra tag quiz_generated
            if 'tags' in note and 'quiz_generated' in note.tags:
                # Kiểm tra nội dung quiz field
                if quiz_field_name in note:
                    quiz_content = note[quiz_field_name]
                    # Tìm từ vựng trong quiz content
                    if f"[{vocab}]" in quiz_content:
                        return True
        
        return False
        
    except Exception as e:
        print(f"Error checking existing quiz cards: {str(e)}")
        return False