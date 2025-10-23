from PyQt5.QtWidgets import (
    QWidget, QPushButton, QLineEdit, QLabel,
    QVBoxLayout, QHBoxLayout, QToolButton, QSizePolicy, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation
from PyQt5.QtGui import QColor, QPainter, QPainterPath, QIcon, QPixmap
from PyQt5.QtWidgets import QGraphicsOpacityEffect

class ModernCard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("modernCard")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("""
            QWidget#modernCard {
                background-color: white;
                border-radius: 8px;
            }
        """)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制白色背景（简化阴影以保持跨平台稳定）
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 8, 8)
        painter.fillPath(path, QColor(255, 255, 255))

class ModernButton(QPushButton):
    def __init__(self, text="", parent=None, primary=True):
        super().__init__(text, parent)
        self.primary = primary
        self.setObjectName("modernButton")
        self.setCursor(Qt.PointingHandCursor)
        self._updateStyle()
        
    def _updateStyle(self):
        if self.primary:
            self.setStyleSheet("""
                QPushButton#modernButton {
                    background-color: #1a73e8;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-weight: 600;
                }
                QPushButton#modernButton:hover { background-color: #1557b0; }
                QPushButton#modernButton:pressed { background-color: #0d47a1; }
            """)
        else:
            self.setStyleSheet("""
                QPushButton#modernButton {
                    background-color: #f8f9fa;
                    color: #3c4043;
                    border: 1px solid #dadce0;
                    border-radius: 6px;
                    padding: 8px 12px;
                }
                QPushButton#modernButton:hover { background-color: #f1f3f4; }
                QPushButton#modernButton:pressed { background-color: #e8eaed; }
            """)

class ModernInput(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("modernInput")
        self.setStyleSheet("""
            QLineEdit#modernInput {
                background-color: white;
                border: 1px solid #dadce0;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
            }
            QLineEdit#modernInput:focus { border-color: #1a73e8; }
        """)

class ModernLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setObjectName("modernLabel")
        self.setStyleSheet("""
            QLabel#modernLabel { color: #202124; font-size: 14px; }
        """)

class ListItem(ModernCard):
    # Emit when the card body is clicked
    clicked = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(12, 12, 12, 12)
        self.layout.setSpacing(12)

        # 图标占位（可替换为实际图标）
        self.icon = QLabel()
        self.icon.setFixedSize(36, 36)
        self.icon.setStyleSheet("background: #f1f3f4; border-radius: 18px;")

        # 主要内容：使用 header + body 的卡片样式
        self.content = QVBoxLayout()

        # header 区域（灰色背景）放置 icon + title
        self.header = QFrame()
        self.header.setObjectName('cardHeader')
        self.header.setStyleSheet("""
            QFrame#cardHeader { background-color: #f4f5f7; border-top-left-radius:8px; border-top-right-radius:8px; }
        """)
        self.header_layout = QHBoxLayout(self.header)
        self.header_layout.setContentsMargins(12, 8, 12, 8)
        self.header_layout.setSpacing(8)

        # 将原来的 icon 作为 header 的左侧头像
        # adjust icon size to be a bit larger for header
        self.icon.setFixedSize(40, 40)

        self.title = ModernLabel()
        self.title.setStyleSheet('font-weight:600; font-size:14px;')
        self.header_layout.addWidget(self.icon)
        self.header_layout.addWidget(self.title)
        self.header_layout.addStretch()

        # body 区域包含密码/网址/备注简要信息
        self.body = QWidget()
        self.body_layout = QVBoxLayout(self.body)
        self.body_layout.setContentsMargins(12, 10, 12, 12)
        self.body_layout.setSpacing(6)

        self.subtitle = QLabel()
        # allow subtitle to wrap to multiple lines to avoid truncation
        self.subtitle.setWordWrap(True)
        self.subtitle.setStyleSheet('color: #5f6368; font-size: 12px;')

        self.body_layout.addWidget(self.subtitle)

        self.content.addWidget(self.header)
        self.content.addWidget(self.body)

        # 操作按钮容器（使用单独的 widget 便于做淡入淡出动画）
        self.actions_widget = QWidget()
        self.actions = QHBoxLayout(self.actions_widget)
        self.actions.setContentsMargins(0, 0, 0, 0)
        self.actions.setSpacing(8)
        self._action_buttons = []
        # 淡入淡出效果
        self._opacity = QGraphicsOpacityEffect(self.actions_widget)
        self.actions_widget.setGraphicsEffect(self._opacity)
        self._opacity.setOpacity(0.0)
        self._fade_anim = QPropertyAnimation(self._opacity, b"opacity")
        self._fade_anim.setDuration(180)

        self.layout.addWidget(self.icon)
        self.layout.addLayout(self.content)
        self.layout.addStretch()
        self.layout.addWidget(self.actions_widget)

        # 卡片可见性风格（确保在浅色背景上可被看见）
        self.setStyleSheet("""
            QWidget#modernCard { background-color: white; border: 1px solid #e6e9ee; border-radius:8px; }
            QLabel#modernLabel { color: #202124 }
        """)
        # increase minimum height so multi-line subtitles are visible (cards look like boxed tiles)
        self.setMinimumHeight(160)
        # allow the title/subtitle area to expand vertically when needed
        self.title.setMinimumHeight(18)
        self.subtitle.setMinimumHeight(18)
        # prefer horizontal expansion so card fills available width in single-column layout
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

    def set_icon(self, path: str):
        """Set an icon from a file path. If path is falsy, leave the placeholder."""
        try:
            pix = QPixmap(path)
            if not pix.isNull():
                self.icon.setPixmap(pix.scaled(36, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        except Exception:
            # keep placeholder style if loading fails
            pass

    def add_action_button(self, icon_path: str = None, tooltip: str = '', text: str = ''):
        """Add a compact action button to the actions area. Returns the QToolButton."""
        btn = QToolButton()
        btn.setToolButtonStyle(Qt.ToolButtonIconOnly if icon_path else Qt.ToolButtonTextOnly)
        # use slightly smaller fixed size for inline action icons
        btn.setFixedSize(24, 24)
        btn.setCursor(Qt.PointingHandCursor)
        if icon_path:
            try:
                ico = QIcon(icon_path)
                btn.setIcon(ico)
                # consistent icon size (works for SVG and raster)
                btn.setIconSize(btn.size() - btn.rect().adjusted(4, 4, -4, -4).topLeft())
                # fallback explicit size
                btn.setIconSize(btn.size())
            except Exception:
                pass
        if tooltip:
            btn.setToolTip(tooltip)
        btn.setStyleSheet("""
            QToolButton { border: none; background: transparent; }
            QToolButton:hover { background: #eef3ff; border-radius: 4px; }
        """)
        self.actions.addWidget(btn)
        self._action_buttons.append(btn)
        return btn

    def enterEvent(self, event):
        # fade in the actions widget
        try:
            self._fade_anim.stop()
            self._fade_anim.setStartValue(self._opacity.opacity())
            self._fade_anim.setEndValue(1.0)
            self._fade_anim.start()
        except Exception:
            for b in self._action_buttons:
                b.setVisible(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        # fade out the actions widget
        try:
            self._fade_anim.stop()
            self._fade_anim.setStartValue(self._opacity.opacity())
            self._fade_anim.setEndValue(0.0)
            self._fade_anim.start()
        except Exception:
            for b in self._action_buttons:
                b.setVisible(False)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        # Emit a clicked signal so parent can react (e.g., expand detail pane)
        try:
            self.clicked.emit()
        except Exception:
            pass
        super().mousePressEvent(event)