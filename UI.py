
# Copyright (c) 2025 Y.MF. All rights reserved.
# 基于PyQt实现用户界面（简洁、可用的实现，连接 Core.py 提供的 API）
__version__ = "0.0.1.4"

import os
import sys
import time
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QDialog, QFormLayout,
    QListWidget, QListWidgetItem, QTextEdit, QApplication, QScrollArea, QSizePolicy, QToolButton, QGridLayout
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont

# Import shared/custom widgets from the local module
from CustomWidgets import ModernButton, ModernInput, ModernLabel, ModernCard, ListItem

# Simple color palette used across the UI
COLORS = {
    'background': '#f5f7fb',
    'surface': '#ffffff',
    'primary': '#1a73e8',
    'outline': '#e6e9ee',
    'text': {
        'primary': '#202124',
        'secondary': '#5f6368'
    }
}


class ErrorDialog(QDialog):
    def __init__(self, parent=None, msg="", button="确认"):
        super().__init__(parent, Qt.FramelessWindowHint | Qt.Dialog)
        self.setWindowModality(Qt.ApplicationModal)
        self.setFixedSize(360, 140)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['surface']};
                border-radius: 8px;
                border: 1px solid {COLORS['outline']};
            }}
            QLabel {{ color: {COLORS['text']['primary']}; font-size: 14px; }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        label = QLabel(msg)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        btn = ModernButton(button)
        btn.setFixedSize(140, 36)
        btn.clicked.connect(self.accept)
        layout.addWidget(btn, alignment=Qt.AlignCenter)


class ConfirmDialog(QDialog):
    def __init__(self, parent=None, msg="", ok_text="确认", cancel_text="取消"):
        super().__init__(parent, Qt.FramelessWindowHint | Qt.Dialog)
        self.setWindowModality(Qt.ApplicationModal)
        self.setFixedSize(460, 160)
        layout = QVBoxLayout(self)
        label = QLabel(msg)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        btns = QHBoxLayout()
        ok = ModernButton(ok_text, primary=True)
        ok.clicked.connect(self.accept)
        cancel = ModernButton(cancel_text, primary=False)
        cancel.clicked.connect(self.reject)
        btns.addWidget(ok)
        btns.addWidget(cancel)
        layout.addLayout(btns)


class SecondaryVerifyDialog(QDialog):
    def __init__(self, action_name: str, parent=None):
        super().__init__(parent, Qt.FramelessWindowHint | Qt.Dialog)
        self.setWindowModality(Qt.ApplicationModal)
        self.setFixedSize(360, 180)
        self.input_password = None
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        tip = ModernLabel(f'执行 "{action_name}" 需要验证主密码')
        tip.setAlignment(Qt.AlignCenter)
        layout.addWidget(tip)
        self.password_input = ModernInput()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText('请输入主密码')
        layout.addWidget(self.password_input)
        # 按回车键触发确认
        try:
            self.password_input.returnPressed.connect(self._on_ok)
        except Exception:
            pass
        btns = QHBoxLayout()
        ok = ModernButton('确认', primary=True)
        ok.clicked.connect(self._on_ok)
        cancel = ModernButton('取消', primary=False)
        cancel.clicked.connect(self.reject)
        btns.addWidget(ok)
        btns.addWidget(cancel)
        layout.addLayout(btns)

    def _on_ok(self):
        pw = self.password_input.text().strip()
        if not pw:
            ErrorDialog(self, '请输入主密码').exec_()
            return
        self.input_password = pw
        self.accept()


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.FramelessWindowHint | Qt.Dialog)
        self.setWindowModality(Qt.ApplicationModal)
        self.setFixedSize(520, 240)
        self.main_key = None
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        title_row = QHBoxLayout()
        logo = QLabel('🔒')
        logo.setStyleSheet('font-size:28px;')
        title = ModernLabel('密码本管理器')
        title.setStyleSheet('font-size:18px; font-weight:700;')
        title_row.addStretch()
        title_row.addWidget(logo)
        title_row.addWidget(title)
        title_row.addStretch()
        layout.addLayout(title_row)
        self.password_input = ModernInput()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText('请输入主密码')
        layout.addWidget(self.password_input)
        btns = QHBoxLayout()
        login = ModernButton('登录', primary=True)
        login.clicked.connect(self._on_login)
        # make the login button the dialog's default so Enter triggers it
        try:
            login.setDefault(True)
            login.setAutoDefault(True)
        except Exception:
            pass
        cancel = ModernButton('退出', primary=False)
        cancel.clicked.connect(self.reject)
        try:
            cancel.setAutoDefault(False)
        except Exception:
            pass
        # also bind Return on the password input to trigger login
        try:
            self.password_input.returnPressed.connect(self._on_login)
        except Exception:
            pass
        btns.addStretch()
        btns.addWidget(cancel)
        btns.addWidget(login)
        layout.addLayout(btns)

    def _on_login(self):
        pw = self.password_input.text().strip()
        if not pw:
            ErrorDialog(self, '请输入主密码').exec_()
            return
        self.main_key = pw
        self.accept()


class MainWindow(QMainWindow):
    """现代化三栏布局（左侧导航、中间卡片列表、右侧详情）"""
    def __init__(self, password_book):
        super().__init__()
        self.password_book = password_book
        # cache for short-term verified main password to avoid repeated prompts
        self._cached_pw = None
        self._last_verified_at = 0.0
        self._verify_ttl = 120  # seconds
        # debug: 当为 True 时使用文本列表渲染（便于调试可见性问题）
        self._debug_text_render = False
        self.current_item_id = None
        self.window_width = 1280
        self.window_height = 820
        self.setFont(QFont('Segoe UI', 10))

        # 全局样式（轻量化 Material 风格）
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {COLORS['background']}; }}
            QWidget#navBar {{ background-color: {COLORS['surface']}; border-right: 1px solid {COLORS['outline']}; }}
            QListWidget {{ background: transparent; border: none; outline: none; padding: 8px; }}
            QListWidget::item {{ color: {COLORS['text']['secondary']}; padding: 10px 12px; margin: 4px 8px; border-radius: 8px; }}
            QListWidget::item:selected {{ background-color: {COLORS['primary']}; color: white; }}
        """)

        self._init_ui()
        self.center_window()

    def _init_ui(self):
        self.setWindowTitle('密码本管理器')
        self.setMinimumSize(900, 600)
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # 左侧导航
        left = QWidget(objectName='navBar')
        left.setFixedWidth(220)
        l_layout = QVBoxLayout(left)
        l_layout.setContentsMargins(0, 18, 0, 18)
        l_layout.setSpacing(6)
        title_left = ModernLabel('密码管理')
        title_left.setStyleSheet('font-size:18px; font-weight:700; padding: 0 16px 12px 16px;')
        l_layout.addWidget(title_left)
        self.category_list = QListWidget()
        categories = [('所有密码', '📑'), ('收藏', '⭐'), ('安全检查', '🔒'), ('回收站', '🗑️')]
        for label, icon in categories:
            self.category_list.addItem(QListWidgetItem(f'{icon} {label}'))
        self.category_list.currentRowChanged.connect(self._on_category_changed)
        l_layout.addWidget(self.category_list)
        l_layout.addStretch()

        # 中间主内容
        center = QWidget(objectName='contentArea')
        c_layout = QVBoxLayout(center)
        c_layout.setContentsMargins(20, 20, 20, 20)
        c_layout.setSpacing(12)
        top_row = QHBoxLayout()
        self.search_input = ModernInput()
        self.search_input.setPlaceholderText('搜索 URL / 用户名 / 备注')
        self.search_input.textChanged.connect(self._on_search_changed)
        new_btn = ModernButton('+ 新建密码', primary=True)
        new_btn.clicked.connect(self._on_new_item)
        top_row.addWidget(self.search_input, 1)
        top_row.addWidget(new_btn, 0)
        c_layout.addLayout(top_row)

        # 列表滚动区
        list_scroll = QScrollArea()
        list_scroll.setWidgetResizable(True)
        list_scroll.setFrameShape(QScrollArea.NoFrame)
        from PyQt5.QtWidgets import QSizePolicy
        self.list_container = QWidget()
        self.list_container.setMinimumHeight(1)
        self.list_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # use a vertical layout so each card occupies a full row
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(10)
        list_scroll.setWidget(self.list_container)
        c_layout.addWidget(list_scroll)

        # 右侧详情卡（默认收起）
        right = ModernCard()
        right.setVisible(False)
        self.right_panel = right
        r_layout = QVBoxLayout(right)
        r_layout.setContentsMargins(18, 18, 18, 18)
        r_layout.setSpacing(12)
        header = QHBoxLayout()
        icon = QLabel('🔑')
        icon.setStyleSheet('font-size:20px;')
        hdr = ModernLabel('密码详情')
        hdr.setStyleSheet('font-size:16px; font-weight:600;')
        header.addWidget(icon)
        header.addWidget(hdr)
        header.addStretch()
        # close button for collapsing panel
        from PyQt5.QtWidgets import QToolButton
        close_btn = QToolButton()
        close_btn.setText('✖')
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet('background: transparent; border: none;')
        close_btn.clicked.connect(lambda: self._animate_right_panel(False))
        header.addWidget(close_btn)
        r_layout.addLayout(header)
        form = QFormLayout()
        form.setSpacing(12)
        self.detail_url = ModernInput()
        self.detail_username = ModernInput()
        self.detail_password = ModernInput()
        self.detail_password.setEchoMode(QLineEdit.Password)
        self.detail_link = ModernInput()
        self.detail_note = QTextEdit()
        self.detail_note.setFixedHeight(110)
        self.detail_note.setStyleSheet(f"background-color: white; border:1px solid {COLORS['outline']}; border-radius:6px; padding:8px;")
        form.addRow(ModernLabel('URL:'), self.detail_url)
        form.addRow(ModernLabel('用户名:'), self.detail_username)
        form.addRow(ModernLabel('密码:'), self.detail_password)
        form.addRow(ModernLabel('关联地址:'), self.detail_link)
        form.addRow(ModernLabel('备注:'), self.detail_note)
        r_layout.addLayout(form)
        btns = QHBoxLayout()
        btns.setSpacing(8)
        self.reveal_btn = ModernButton('👁️ 显示', primary=False)
        self.reveal_btn.clicked.connect(self._reveal_password)
        self.copy_btn = ModernButton('📋 复制', primary=False)
        self.copy_btn.clicked.connect(self._copy_password)
        self.save_btn = ModernButton('💾 保存', primary=True)
        self.save_btn.clicked.connect(self._save_item)
        self.delete_btn = ModernButton('🗑️ 删除', primary=False)
        self.delete_btn.clicked.connect(self._delete_item)
        btns.addWidget(self.reveal_btn)
        btns.addWidget(self.copy_btn)
        btns.addWidget(self.save_btn)
        btns.addWidget(self.delete_btn)
        btns.addStretch()
        r_layout.addLayout(btns)

        root.addWidget(left)
        root.addWidget(center, 2)
        # set initial collapsed max width for animation
        right.setMaximumWidth(0)
        root.addWidget(right, 1)

        self.status = self.statusBar()
        self.status.showMessage('就绪：已登录', 3000)

        # 初始化列表
        # 默认选择左侧第一个类别（所有密码）并设置为深色选中
        try:
            self.category_list.setCurrentRow(0)
        except Exception:
            pass

        self._load_items()

        # 首次打开（新初始化的密码本）要求设置主密码：如果 ARGON2_PARAMS.integrity_check 为占位字符串，则认为是新建
        try:
            params = getattr(self.password_book, 'load_dict', {}).get('ARGON2_PARAMS', {})
            if params.get('integrity_check', '').startswith('123'):
                # 弹出设置主密码对话（简化为要求用户输入并重-hash）
                dlg = LoginDialog(self)
                dlg.setWindowTitle('设置主密码')
                dlg.password_input.setPlaceholderText('请设置主密码（将用于加密）')
                res = dlg.exec_()
                if res == QDialog.Accepted and dlg.main_key:
                    # 重写保存在文件中的 verify_hash 使用新的主密码
                    # 这里我们简单地替换 KeyWordNoteBook 的 MainKey 并重新初始化文件头
                    self.password_book.MainKey = dlg.main_key
                    # 重新初始化并同步文件
                    self.password_book._initialize_new_book()
                    self.status.showMessage('主密码已设置', 3000)
        except Exception:
            pass

        # animation for right panel (width + opacity)
        from PyQt5.QtCore import QPropertyAnimation
        from PyQt5.QtWidgets import QGraphicsOpacityEffect
        self._right_anim = QPropertyAnimation(self.right_panel, b"maximumWidth")
        self._right_anim.setDuration(220)
        # opacity effect and animation
        self._right_opacity_effect = QGraphicsOpacityEffect(self.right_panel)
        self.right_panel.setGraphicsEffect(self._right_opacity_effect)
        from PyQt5.QtCore import QVariantAnimation
        # use QPropertyAnimation on opacity through the effect
        self._right_opacity_anim = QPropertyAnimation(self._right_opacity_effect, b"opacity")
        self._right_opacity_anim.setDuration(220)
        # when width animation finishes and panel is collapsed, hide the panel for input pass-through
        def _on_right_anim_finished():
            try:
                if self.right_panel.maximumWidth() == 0:
                    self.right_panel.setVisible(False)
            except Exception:
                pass
        try:
            self._right_anim.finished.connect(_on_right_anim_finished)
        except Exception:
            pass

    def center_window(self):
        screen = self.screen()
        geom = screen.availableGeometry()
        x = (geom.width() - self.window_width) // 2
        y = (geom.height() - self.window_height) // 2
        self.setGeometry(x, y, self.window_width, self.window_height)

    def _load_items(self, filter_text: str = ''):
        # 在加载时先尝试清理回收站中超过5天的条目
        try:
            purge = getattr(self.password_book, 'purge_recycle_bin_older_than', None)
            if callable(purge):
                purge(5)
        except Exception:
            pass

        items = self.password_book.get_non_secret_items() or []
        print('调试: get_non_secret_items 返回:', items)
        # debug 模式：将所有条目渲染为文本，便于快速确认数据在 UI 中可见
        if self._debug_text_render:
            try:
                # 清空原有布局
                for i in reversed(range(self.list_layout.count())):
                    w = self.list_layout.itemAt(i).widget()
                    if w:
                        w.setParent(None)
                from PyQt5.QtWidgets import QTextEdit
                txt = QTextEdit()
                txt.setReadOnly(True)
                lines = []
                for it in items:
                    lines.append(f"[{it.get('Index','')}] {it.get('URL','')} | {it.get('UserName','')} | {it.get('Note','')}")
                txt.setPlainText('\n'.join(lines))
                self.list_layout.addWidget(txt)
                self.list_container.update()
                self.list_container.repaint()
                return
            except Exception as e:
                print('调试渲染失败:', e)
        q = filter_text.lower().strip()
        # 清空
        for i in reversed(range(self.list_layout.count())):
            w = self.list_layout.itemAt(i).widget()
            if w:
                w.setParent(None)
        # 根据左侧分类决定显示内容
        cur_idx = self.category_list.currentRow() if hasattr(self, 'category_list') else 0
        if cur_idx == 0:
            source = items
        elif cur_idx == 1:
            # 收藏
            source = [it for it in items if bool(it.get('Favorite', False))]
        elif cur_idx == 3:
            # 回收站：从 Core 中读取 RecycleBin 并显示其中的 Item 的元信息
            rb = getattr(self.password_book, 'load_dict', {}).get('RecycleBin', {})
            source = []
            for k, v in rb.items():
                entry = dict(v.get('Item', {}))
                entry['Index'] = k
                entry['DeletedAt'] = v.get('DeletedAt')
                # 标记为已删除，UI 可根据无 Password 显示
                source.append(entry)
        else:
            source = items

        if not q:
            filtered = source
        else:
            filtered = [it for it in source if q in it.get('URL', '').lower() or q in it.get('UserName', '').lower() or q in it.get('Note', '').lower()]
        import os
        icons_dir = os.path.join(os.path.dirname(__file__), 'assets', 'icons')
        # add each item as a single full-width card (one per row)
        for it in filtered:
            item = ListItem()
            url = it.get('URL', '')
            username = it.get('UserName', '')
            note = it.get('Note', '')
            idx = it.get('Index', '')
            modified = it.get('Modified', '未知')
            item.title.setText(url)
            subtitle_lines = []
            if username:
                subtitle_lines.append(f"用户: {username}")
            if note:
                subtitle_lines.append(f"备注: {note}")
            subtitle_lines.append(f"编号: {idx}")
            subtitle_lines.append(f"更新时间: {modified}")
            item.subtitle.setText('  |  '.join(subtitle_lines))
            url_l = url.lower()
            username_l = username.lower()
            icon_path = os.path.join(icons_dir, 'default.png')
            if 'bank' in url_l or 'bank' in username_l or 'card' in url_l:
                icon_path = os.path.join(icons_dir, 'bank.png')
            elif '@' in username_l or 'mail' in url_l or 'email' in username_l:
                icon_path = os.path.join(icons_dir, 'email.png')
            else:
                icon_path = os.path.join(icons_dir, 'site.png')
            try:
                item.set_icon(icon_path)
            except Exception:
                pass
            star_icon = os.path.join(icons_dir, 'star.svg')
            edit_icon = os.path.join(icons_dir, 'edit.svg')
            del_icon = os.path.join(icons_dir, 'delete.svg')
            view_icon = os.path.join(icons_dir, 'view.svg')
            fav_btn = item.add_action_button(icon_path=star_icon, tooltip='收藏')
            edit_btn = item.add_action_button(icon_path=edit_icon, tooltip='编辑')
            del_btn = item.add_action_button(icon_path=del_icon, tooltip='删除')
            view_btn = item.add_action_button(icon_path=view_icon, tooltip='查看')
            # 若当前为回收站类别，替换删除为恢复按钮
            if cur_idx == 3:
                # 创建一个恢复按钮替代删除动作，避免断开信号导致异常
                restore_icon = os.path.join(icons_dir, 'restore.svg')
                # 检查图标文件是否存在，否则用文字
                import os
                if os.path.exists(restore_icon):
                    restore_btn = item.add_action_button(icon_path=restore_icon, tooltip='恢复')
                else:
                    restore_btn = item.add_action_button(text='恢复', tooltip='恢复')
                # 移除原来的删除按钮（简单隐藏）
                try:
                    del_btn.setVisible(False)
                except Exception:
                    pass
                # 用默认参数绑定 index，避免闭包 bug
                restore_btn.clicked.connect(lambda checked=False, idx=index: self._on_restore_item(idx))
            # attach non-secret data to item for edit without secondary verification
            item._data = it
            index = it.get('Index', '')
            fav_btn.clicked.connect(lambda checked=False, idx=index, itm=item: self._on_favorite_toggle(idx, itm))
            # edit will populate the right-side form using non-secret fields
            # Use a wrapper so we can detect keyboard modifiers (Shift) at click time
            edit_btn.clicked.connect(lambda checked=False, itm=item: self._edit_click_handler(itm))
            del_btn.clicked.connect(lambda checked=False, idx=index: self._on_delete_item_by_idx(idx))
            view_btn.clicked.connect(lambda checked=False, idx=index: self._on_view_item(idx))
            # connect card click to expand right panel and show non-sensitive info
            try:
                item.clicked.connect(lambda itm=item: self._on_card_clicked(itm))
            except Exception:
                pass
            # add as a full-width row
            try:
                self.list_layout.addWidget(item)
            except Exception:
                # fallback (shouldn't happen for QVBoxLayout)
                pass
            print(f'调试: 添加 ListItem, Index={idx}, URL={url}')
            anim = QPropertyAnimation(item, b"maximumHeight")
            anim.setDuration(200)
            anim.setStartValue(0)
            anim.setEndValue(item.sizeHint().height())
            anim.setEasingCurve(QEasingCurve.OutCubic)
            anim.start()
        self.list_container.update()
        self.list_container.repaint()
        self.status.showMessage(f'成功加载 {len(filtered)} 条', 3000)

    def _on_restore_item(self, item_id: str):
        # 恢复回收站条目
        ok = getattr(self.password_book, 'restore_from_recycle', None)
        if callable(ok):
            res = self.password_book.restore_from_recycle(item_id)
            if res:
                ErrorDialog(self, '已恢复条目').exec_()
                self._load_items(self.search_input.text())
            else:
                ErrorDialog(self, '恢复失败').exec_()

    def _on_search_changed(self, text: str):
        self._load_items(filter_text=text)

    def _on_category_changed(self, idx: int):
        # “所有密码”显示全部条目
        if idx == 0:
            self._load_items(filter_text='')
        else:
            self._load_items(filter_text=self.search_input.text())

    def _on_view_item(self, item_id: str):
        self.current_item_id = item_id
        pw = self._get_verified_password('查看密码')
        if not pw:
            return
        data = self.password_book.get_item_by_id(item_id, upw=pw)
        if data:
            self.detail_url.setText(data.get('URL', ''))
            self.detail_username.setText(data.get('UserName', ''))
            self.detail_password.setText(data.get('Password', ''))
            self.detail_password.setEchoMode(QLineEdit.Password)
            self.detail_link.setText(data.get('LinkURL', ''))
            self.detail_note.setPlainText(data.get('Note', ''))

    def _on_card_clicked(self, list_item: ListItem):
        """Expand the right-side panel and populate with non-sensitive information from the card."""
        # ensure right panel visible
        try:
            self.right_panel.setVisible(True)
        except Exception:
            pass
        data = getattr(list_item, '_data', None)
        if not data:
            return
        # populate non-sensitive fields
        url = data.get('URL', '') if isinstance(data, dict) else getattr(data, 'URL', '')
        username = data.get('UserName', '') if isinstance(data, dict) else getattr(data, 'UserName', '')
        note = data.get('Note', '') if isinstance(data, dict) else getattr(data, 'Note', '')
        link = data.get('LinkURL', '') if isinstance(data, dict) else getattr(data, 'LinkURL', '')
        item_id = data.get('Index') if isinstance(data, dict) else getattr(data, 'Index', None)
        self.current_item_id = item_id
        self.detail_url.setText(url)
        self.detail_username.setText(username)
        self.detail_password.setText('')
        self.detail_password.setEchoMode(QLineEdit.Password)
        self.detail_link.setText(link)
        self.detail_note.setPlainText(note)
        # compute adaptive width based on window width
        try:
            win_w = max(600, self.width())
            adaptive = int(min(480, win_w * 0.36))
        except Exception:
            adaptive = 380
        self._animate_right_panel(True, target_width=adaptive)

    def _animate_right_panel(self, show: bool, target_width: int = None):
        """Animate the right panel sliding in or out by changing its maximumWidth."""
        # determine adaptive target width if not provided
        if target_width is None:
            try:
                win_w = max(600, self.width())
                target_width = int(min(480, win_w * 0.36))
            except Exception:
                target_width = 380

        if show:
            # ensure widget visible and animate width->target and opacity->1
            try:
                self.right_panel.setVisible(True)
            except Exception:
                pass
            start_w = self.right_panel.maximumWidth()
            end_w = target_width
            start_o = getattr(self, '_right_opacity_effect', None).opacity() if getattr(self, '_right_opacity_effect', None) else 0.0
            end_o = 1.0
        else:
            start_w = self.right_panel.maximumWidth()
            end_w = 0
            start_o = getattr(self, '_right_opacity_effect', None).opacity() if getattr(self, '_right_opacity_effect', None) else 1.0
            end_o = 0.0

        try:
            # width animation
            self._right_anim.stop()
            self._right_anim.setStartValue(start_w)
            self._right_anim.setEndValue(end_w)
            # opacity animation (if available)
            if getattr(self, '_right_opacity_anim', None):
                self._right_opacity_anim.stop()
                self._right_opacity_anim.setStartValue(start_o)
                self._right_opacity_anim.setEndValue(end_o)
                self._right_opacity_anim.start()
            self._right_anim.start()
        except Exception:
            # fallback
            self.right_panel.setMaximumWidth(end_w)
            if end_o <= 0:
                try:
                    self.right_panel.setVisible(False)
                except Exception:
                    pass

    def _toggle_right_panel(self):
        # toggle based on current max width
        cur = self.right_panel.maximumWidth()
        self._animate_right_panel(cur == 0)

    def _get_verified_password(self, action_name: str) -> str:
        """Return a verified main password, using cached value if within TTL, otherwise prompt.

        Returns the password string when verified, or empty string / None on cancel/failure.
        """
        now = time.time()
        if self._cached_pw and (now - self._last_verified_at) < self._verify_ttl:
            return self._cached_pw

        dlg = SecondaryVerifyDialog(action_name, self)
        if dlg.exec_() != QDialog.Accepted:
            return ''
        if not self.password_book.verify_main_key(dlg.input_password):
            ErrorDialog(self, '密码验证失败').exec_()
            return ''
        # cache and return
        try:
            self._cached_pw = dlg.input_password
            self._last_verified_at = now
        except Exception:
            pass
        return self._cached_pw

    def _reveal_password(self):
        if not self.current_item_id:
            ErrorDialog(self, '请先选择一个条目').exec_()
            return
        # require secondary verification to reveal the password
        pw = self._get_verified_password('查看密码')
        if not pw:
            return
        data = self.password_book.get_item_by_id(self.current_item_id, upw=pw)
        if data:
            self.detail_password.setText(data.get('Password', ''))
            self.detail_password.setEchoMode(QLineEdit.Normal)

    def _on_favorite_toggle(self, item_id: str, list_item_widget):
        # 切换收藏字段并保存
        pw = self._get_verified_password('收藏/取消收藏')
        if not pw:
            return
        # 读取当前条目数据
        data = self.password_book.get_item_by_id(item_id, upw=pw)
        if not data:
            ErrorDialog(self, '无法读取条目数据').exec_()
            return
        # 切换 Favorite 字段（可能为布尔或字符串）
        fav = data.get('Favorite', False)
        data['Favorite'] = not bool(fav)
        res = self.password_book.update_item(item_id, data=data, upw=pw)
        if res:
            self.status.showMessage('收藏状态已更新', 3000)
            self._load_items(self.search_input.text())
        else:
            ErrorDialog(self, '更新收藏失败').exec_()

    def _on_edit_item(self, item_id: str):
        # 打开右侧详情并加载（与查看类似，但不需要二次验证）
        data = self.password_book.get_item_by_id(item_id, upw='') or {}
        self.current_item_id = item_id
        self.detail_url.setText(data.get('URL', ''))
        self.detail_username.setText(data.get('UserName', ''))
        self.detail_password.setText(data.get('Password', ''))
        self.detail_password.setEchoMode(QLineEdit.Password)
        self.detail_link.setText(data.get('LinkURL', ''))
        self.detail_note.setPlainText(data.get('Note', ''))

    def _on_edit_item_from_data(self, data):
        """Populate the right-side detail form using a non-secret data dict attached to the list item.

        The list items attach a lightweight representation (non-secret) as `item._data`.
        This method uses that to quickly populate the editing form without performing
        a secondary password verification. It still sets `current_item_id` so subsequent
        save/delete operations operate on the correct item.
        """
        if not data:
            ErrorDialog(self, '无法读取条目数据').exec_()
            return
        # data may be a KeyItem or a plain dict
        try:
            # prefer explicit key 'Index' for identifier
            item_id = data.get('Index') if isinstance(data, dict) else getattr(data, 'Index', None)
        except Exception:
            item_id = None
        if not item_id:
            # Fall back to any available id-like keys
            if isinstance(data, dict):
                item_id = data.get('Id') or data.get('id') or data.get('index')
        # set current id (if still None, leave as None — saving will treat as new)
        self.current_item_id = item_id
        # Fill fields with available non-secret fields
        url = data.get('URL', '') if isinstance(data, dict) else getattr(data, 'URL', '')
        username = data.get('UserName', '') if isinstance(data, dict) else getattr(data, 'UserName', '')
        note = data.get('Note', '') if isinstance(data, dict) else getattr(data, 'Note', '')
        link = data.get('LinkURL', '') if isinstance(data, dict) else getattr(data, 'LinkURL', '')
        # Password likely not included in non-secret data; leave it blank to require verification on save
        self.detail_url.setText(url)
        self.detail_username.setText(username)
        self.detail_password.setText('')
        self.detail_password.setEchoMode(QLineEdit.Password)
        self.detail_link.setText(link)
        self.detail_note.setPlainText(note)

    def _edit_click_handler(self, list_item_widget):
        """Handle click on edit button: check if Shift is pressed to reveal secrets on edit.

        If Shift is held, perform a secondary verification and fetch full item data (including password).
        Otherwise, populate using non-secret data attached to the list item.
        """
        modifiers = QApplication.keyboardModifiers()
        shift_pressed = bool(modifiers & Qt.ShiftModifier)
        data = getattr(list_item_widget, '_data', None)
        if shift_pressed:
            # attempt to get full item data requiring secondary verification
            # determine id from data
            item_id = None
            if isinstance(data, dict):
                item_id = data.get('Index') or data.get('Id') or data.get('id')
            else:
                item_id = getattr(data, 'Index', None)
            if not item_id:
                ErrorDialog(self, '无法识别条目编号以执行查看').exec_()
                return
            # use cached verification helper
            pw = self._get_verified_password('查看并编辑（显示密码）')
            if not pw:
                return
            full = self.password_book.get_item_by_id(item_id, upw=pw)
            if not full:
                ErrorDialog(self, '无法读取条目数据').exec_()
                return
            # populate full data including password
            self.current_item_id = item_id
            self.detail_url.setText(full.get('URL', ''))
            self.detail_username.setText(full.get('UserName', ''))
            self.detail_password.setText(full.get('Password', ''))
            self.detail_password.setEchoMode(QLineEdit.Password)
            self.detail_link.setText(full.get('LinkURL', ''))
            self.detail_note.setPlainText(full.get('Note', ''))
        else:
            # normal behavior: populate from non-secret data
            self._on_edit_item_from_data(data)

    def _on_delete_item_by_idx(self, item_id: str):
        # 设 current_item_id 然后调用删除流程
        self.current_item_id = item_id
        self._delete_item()

    def _copy_password(self):
        pwd = self.detail_password.text().strip()
        if not pwd:
            ErrorDialog(self, '当前无可复制密码').exec_()
            return
        QApplication.clipboard().setText(pwd)
        # 状态栏提示
        self.status.showMessage('已复制密码到剪贴板', 3000)
        # 弹出短暂浮层提示（类似 toast）
        try:
            self._show_toast('复制成功')
        except Exception:
            pass

    def _show_toast(self, text: str, timeout: int = 1500):
        # 简单实现：在主窗口右下角创建一个无边框 QLabel 然后淡出
        from PyQt5.QtWidgets import QLabel
        lbl = QLabel(text, self)
        lbl.setStyleSheet('background: rgba(0,0,0,0.75); color: white; padding: 8px 12px; border-radius: 6px;')
        lbl.adjustSize()
        x = max(0, self.width() - lbl.width() - 40)
        y = max(0, self.height() - lbl.height() - 80)
        lbl.move(x, y)
        lbl.show()
        # 自动隐藏
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(timeout, lbl.deleteLater)

    def _on_new_item(self):
        self.current_item_id = None
        self.detail_url.clear()
        self.detail_username.clear()
        self.detail_password.clear()
        self.detail_link.clear()
        self.detail_note.clear()
        # 打开右侧详情面板以便新建
        try:
            # 计算合适宽度由 _animate_right_panel 处理
            self._animate_right_panel(True)
            # 将光标放到 URL 输入以便快速输入
            try:
                self.detail_url.setFocus()
            except Exception:
                pass
        except Exception:
            pass

    def _save_item(self):
        data = {
            'URL': self.detail_url.text().strip(),
            'UserName': self.detail_username.text().strip(),
            'Password': self.detail_password.text().strip(),
            'LinkURL': self.detail_link.text().strip(),
            'Note': self.detail_note.toPlainText().strip()
        }
        if not data['URL'] or not data['UserName'] or not data['Password']:
            ErrorDialog(self, 'URL/用户名/密码为必填项').exec_()
            return
        pw = self._get_verified_password('保存条目')
        if not pw:
            return
        if self.current_item_id:
            res = self.password_book.update_item(self.current_item_id, data=data, upw=pw)
            if res:
                ErrorDialog(self, f'修改条目 {res} 成功').exec_()
                self._load_items(self.search_input.text())
            else:
                ErrorDialog(self, '修改失败').exec_()
        else:
            new_id = self.password_book.add_item(data, upw=pw)
            if new_id != '-1':
                ErrorDialog(self, f'添加条目 {new_id} 成功').exec_()
                self._load_items(self.search_input.text())
            else:
                ErrorDialog(self, '添加失败').exec_()

    def _delete_item(self):
        if not self.current_item_id:
            ErrorDialog(self, '请先选择要删除的条目').exec_()
            return
        pw = self._get_verified_password('删除密码条目')
        if not pw:
            return
        confirm = ConfirmDialog(self, '确定要删除该条目吗？删除后不可恢复！')
        if confirm.exec_() != QDialog.Accepted:
            return
        ok = self.password_book.delete_item(self.current_item_id, upw=pw)
        if ok:
            ErrorDialog(self, '删除成功').exec_()
            self.current_item_id = None
            self._load_items(self.search_input.text())
        else:
            ErrorDialog(self, '删除失败').exec_()


if __name__ == '__main__':
    pass

