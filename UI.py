# Copyright (c) 2025 Y.MF. All rights reserved.
#
# 本代码及相关文档受著作权法保护，未经授权，禁止任何形式的复制、分发、修改或商业使用。
# 如需使用或修改本代码，请联系版权所有者获得书面许可（联系方式：1428483061@qq.com）。
#
# 免责声明：本代码按"原样"提供，不提供任何明示或暗示的担保，包括但不限于对适销性、特定用途适用性的担保。
# 在任何情况下，版权所有者不对因使用本代码或本代码的衍生作品而导致的任何直接或间接损失承担责任。
#
# 项目名称：UI.py
# 项目仓库：https://github.com/YiMuFeng/KeyWordNoteBook.git
# 创建时间：2025/8/26 22:36
# 版权所有者：Y.MF
# 联系方式：1428483061@qq.com
# 许可协议：Apache License 2.0

"""
基于PyQt实现用户界面
"""
__version__ = "0.0.1.1"

import sys
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,  # 布局控件
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,  # 基础控件
    QDialog, QFormLayout,  QHeaderView, )# 交互控件
from PyQt5.QtCore import Qt  # Qt常量（如对齐方式）
from PyQt5.QtGui import QFont,QCursor  # 字体设置

from Core import KeyWordNoteBook,KeyItem


class ErrorDialog(QDialog):
    """
    处理Error信息的对话框
    msg="",对话框提示信息
    button="确认"，按钮提示信息
    """
    def __init__(self, parent=None,msg="",button="确认"):
        super().__init__(parent, Qt.FramelessWindowHint | Qt.Dialog)

        self.setWindowModality(Qt.ApplicationModal)  # 设置为应用程序级模态，确保在所有窗口上方显示
        self.setFixedSize(300, 150)  # 固定消息框大小
        self.setStyleSheet("""
                        QDialog {
                            background-color: #2d2d2d;
                            border-radius: 8px;
                            border: 1px solid #444;  /* 增加边框，确保可见性 */
                        }
                        QLabel {
                            color: #ffffff;
                            font-size: 14px;
                        }
                        QPushButton {
                            background-color: #4da6ff;
                            color: white;
                            border: none;
                            border-radius: 4px;
                            font-size: 14px;
                            font-weight: bold;
                        }
                        QPushButton:hover { background-color: #398ae5; }
                        QPushButton:pressed { background-color: #2a6dbb; }
                    """)
        # 消息框布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # 提示文本
        label = QLabel(msg)
        label.setAlignment(Qt.AlignCenter)  # 文本居中
        label.setWordWrap(True)  # 支持文本换行，避免长消息被截断
        layout.addWidget(label)
        # 放大的确认按钮
        confirm_btn = QPushButton(button)
        confirm_btn.setFixedSize(150, 40)  # 放大按钮尺寸
        confirm_btn.clicked.connect(self.accept)  # 点击关闭消息框
        layout.addWidget(confirm_btn, alignment=Qt.AlignCenter)  # 按钮居中

        self.setLayout(layout)

class ConfirmDialog(QDialog):
    """
    提供确认和取消按钮的确认对话框
    """
    def __init__(self, parent=None,msg="",button1="确认",button2="取消"):
        super().__init__(parent, Qt.FramelessWindowHint | Qt.Dialog)
        self.setWindowModality(Qt.ApplicationModal)  # 设置为应用程序级模态，确保在所有窗口上方显示
        self.setFixedSize(400, 200)  # 固定消息框大小
        # self.setAttribute(Qt.WA_TranslucentBackground)  # 背景透明，配合圆角
        # 消息框布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # 提示文本
        label = QLabel(msg)
        label.setAlignment(Qt.AlignCenter)  # 文本居中
        label.setWordWrap(True)  # 支持文本换行，避免长消息被截断
        main_layout.addWidget(label)

        # 按钮布局
        btn_layout = QHBoxLayout(self)
        btn_layout.setContentsMargins(20, 20, 20, 20)
        btn_layout.setSpacing(20)

        confirm_btn = QPushButton(button1)
        confirm_btn.setFixedSize(150, 40)  # 放大按钮尺寸
        confirm_btn.setStyleSheet("""
                                    QPushButton {
                                        background-color: #4da6ff;
                                        color: white;
                                        border: none;
                                        padding: 6px 12px;
                                        border-radius: 4px;
                                    }
                                    QPushButton:hover {
                                        background-color: #398ae5;
                                    }
                                    QPushButton:pressed {
                                        background-color: #2a6dbb;
                                    }
                                """)
        confirm_btn.clicked.connect(self.accept)  # 点击关闭消息框

        cancel_btn = QPushButton(button2)
        cancel_btn.setFixedSize(150, 40)  # 放大按钮尺寸
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(confirm_btn)
        btn_layout.addWidget(cancel_btn)
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

class LoginDialog(QDialog):
    """
    登录对话框：程序启动时验证登录
    TODO：在登录UI中添加选择密码本文件路径，将文件路径传给Core，以支持多用户
    # todo:添加自定义标题栏
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # 移除右上角问号按钮，只保留关闭按钮
        self.setWindowFlags(Qt.FramelessWindowHint)# 隐藏原生标题栏

        # -------------------------- 窗口基础设置 --------------------------
        self.setWindowTitle("登录")  # 窗口标题
        self.setFixedSize(500, 300)  # 固定窗口大小（防止拉伸导致布局错乱）
        self.main_key = None  # 存储用户输入的主密码（验证后传递给核心类）

        # -------------------------- 布局初始化 --------------------------
        # 主布局：控件自上而下排列
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)  # 增加内边距
        main_layout.setSpacing(15)  # 控件间距

        # -------------------------- 表单布局（密码输入） --------------------------
        # 表单布局：标签与输入框成对排列，自动对齐
        form_layout = QFormLayout()
        form_layout.setAlignment(Qt.AlignCenter)    #设置表单布局在父容器中居中对齐
        form_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)# 禁止标签和输入框自动换行（避免对齐错乱）
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignCenter)  # 标签居中对齐
        form_layout.setFormAlignment(Qt.AlignCenter)  # 整个表单内容居中
        form_layout.setHorizontalSpacing(15)    # 设置标签与输入框之间的间距（避免贴太近
        # 密码输入框：设置为密码模式（输入内容隐藏为*）
        self.password_input = QLineEdit()
        self.password_input.setFixedSize(200,50)
        self.password_input.setFont(QFont('Arial',10))
        self.password_input.setEchoMode(QLineEdit.Password)  # 关键：密码隐藏显示
        self.password_input.setPlaceholderText("请输入登录密码")  # 提示文本
        self.password_input.setAlignment(Qt.AlignCenter)

        # 表单标签设置为白色
        label = QLabel("登录密码：")
        label.setFixedSize(120,50)
        label.setFont(QFont('Arial', 14))
        label.setAlignment(Qt.AlignVCenter | Qt.AlignRight)  # 垂直居中+水平右对齐（视觉更协调）

        # 标签+输入框成对添加
        form_layout.addRow(label, self.password_input)

        # -------------------------- 按钮布局（登录/取消） --------------------------
        # 水平布局：按钮自左向右排列（适合操作按钮组）
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        # 登录按钮：触发密码验证逻辑
        self.login_btn = QPushButton("登录")
        self.login_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #4da6ff;
                        color: white;
                        border: none;
                        padding: 6px 12px;
                        border-radius: 4px;
                    }
                    QPushButton:hover {
                        background-color: #398ae5;
                    }
                    QPushButton:pressed {
                        background-color: #2a6dbb;
                    }
                """)
        self.login_btn.setFixedSize(200,50)
        self.login_btn.clicked.connect(self._on_login_click)  # 绑定点击事件

        # 取消按钮：关闭登录窗口，退出程序
        self.cancel_btn = QPushButton("退出")
        self.cancel_btn.setFixedSize(200, 50)
        self.cancel_btn.setFocus()
        self.cancel_btn.clicked.connect(self.reject)  # 调用QDialog自带的"取消"逻辑

        btn_layout.addWidget(self.login_btn)
        btn_layout.addWidget(self.cancel_btn)

        # -------------------------- 组装布局 --------------------------
        main_layout.addLayout(form_layout)  # 先加表单
        main_layout.addLayout(btn_layout)  # 再加按钮组
        self.setLayout(main_layout)  # 设置窗口的主布局

        self.cancel_btn.setFocus()  # 放在布局设置之后，避免被输入框抢占焦点

    def _on_login_click(self):
        """登录按钮点击事件：验证密码非空后传递结果"""
        password = self.password_input.text().strip()  # 获取输入并去除首尾空格
        if not password:  # 空密码校验
            msg_box = ErrorDialog(self,"请输入登录密码，不能为空！")
            # 确保窗口显示在最上层
            msg_box.setWindowFlags(
                msg_box.windowFlags() | Qt.WindowStaysOnTopHint
            )
            msg_box.raise_()  # 提升窗口层级
            msg_box.activateWindow()  # 激活窗口
            msg_box.exec_()  # 显示消息框
            return
        # 密码非空则存储并关闭登录窗口（返回"确认"状态）
        self.main_key = password
        self.accept()  # 调用QDialog自带的"确认"逻辑，关闭窗口并返回Accepted

class SecondaryVerifyDialog(QDialog):
    """
    二级验证对话框：执行敏感操作前的二次密码验证（防误触/盗操作）
    # todo:添加自定义标题栏
    """
    def __init__(self, action_name: str, parent=None):
        """
        :param action_name: 要执行的操作名称（如"添加条目"），用于提示用户
        :param parent: 父窗口（主界面），确保对话框居中显示在父窗口上
        """
        super().__init__(parent,Qt.FramelessWindowHint | Qt.Dialog)
        # -------------------------- 窗口基础设置 --------------------------
        self.setFixedSize(300, 160)
        self.verified = False  # 验证结果标记（True=验证通过）
        self.input_password = None  # 存储用户输入的验证密码

        # -------------------------- 布局初始化 --------------------------
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)  # 控件之间的间距（优化视觉体验）

        # -------------------------- 提示标签 --------------------------
        # 告知用户当前操作需要二次验证（增强安全性感知）
        tip_label = QLabel(f"执行「{action_name}」需要验证主密码")
        tip_label.setAlignment(Qt.AlignCenter)  # 文字居中
        main_layout.addWidget(tip_label)

        # -------------------------- 密码输入框 --------------------------
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("再次输入主密码")
        main_layout.addWidget(self.password_input)

        # -------------------------- 按钮布局（确认/取消） --------------------------
        btn_layout = QHBoxLayout()

        self.confirm_btn = QPushButton("确认验证")
        self.confirm_btn.clicked.connect(self._verify_password)  # 绑定验证逻辑
        self.confirm_btn.setStyleSheet("""
                            QPushButton {
                                background-color: #4da6ff;
                                color: white;
                                border: none;
                                padding: 6px 12px;
                                border-radius: 4px;
                            }
                            QPushButton:hover {
                                background-color: #398ae5;
                            }
                            QPushButton:pressed {
                                background-color: #2a6dbb;
                            }
                        """)
        self.cancel_btn = QPushButton("取消操作")
        self.cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(self.confirm_btn)
        btn_layout.addWidget(self.cancel_btn)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

    def _verify_password(self):
        """验证按钮点击事件：检查密码非空并标记验证结果"""
        password = self.password_input.text().strip()
        if not password:
            msg_box = ErrorDialog(self, "请输入登录密码，不能为空！")
            msg_box.exec_()  # 显示消息框
            return
        # 存储输入的密码并标记验证通过，关闭对话框
        self.input_password = password
        self.verified = True
        self.accept()

class ItemEditDialog(QDialog):
    """条目编辑对话框：添加/修改密码条目时的表单窗口（统一交互逻辑）"""
    def __init__(self, item_data: dict = None, parent=None):
        """
        :param item_data: 待修改的条目数据（None=添加新条目）
        :param parent: 父窗口
        """
        super().__init__(parent,Qt.FramelessWindowHint | Qt.Dialog)

        # -------------------------- 窗口基础设置 --------------------------
        self.dragging = None
        self.drag_start_position = None
        self.window_title = "修改密码条目" if item_data else "添加新密码条目"
        self.setFixedSize(450, 360)
        self.item_data = KeyItem(item_data) if item_data else KeyItem()        # 存储编辑后的条目数据

        # -------------------------- 主布局（包含标题栏和内容区） --------------------------
        main_container = QWidget()
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        # -------------------------- 1. 自定义标题栏 --------------------------
        self.title_bar = QWidget()
        self.title_bar.setFixedHeight(40)  # 标题栏高度
        self.title_bar.setStyleSheet("""
                    QWidget {
                        background-color: #1a1a1a;
                        border-top-left-radius: 6px;
                        border-top-right-radius: 6px;
                    }
                """)
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(15, 0, 10, 0)
        title_layout.setSpacing(0)
        # 标题文本
        title_label = QLabel(self.window_title)
        title_label.setStyleSheet("color: #ffffff; font-weight: bold;")
        title_layout.addWidget(title_label)

        # 占位符（推挤关闭按钮到右侧）
        title_layout.addStretch()
        # 关闭按钮
        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.setStyleSheet("""
                    QPushButton {
                        color: #ffffff;
                        background-color: transparent;
                        border-radius: 15px;
                        font-size: 16px;
                    }
                    QPushButton:hover {
                        background-color: #ff4444;
                    }
                    QPushButton:pressed {
                        background-color: #cc0000;
                    }
                """)
        self.close_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.close_btn.clicked.connect(self.reject)  # 关闭对话框
        title_layout.addWidget(self.close_btn)

        # -------------------------- 2. 内容区域（原有表单） --------------------------
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)

        # 表单布局（条目字段）
        form_layout = QFormLayout()
        form_layout.setSpacing(12)  # 表单字段之间的间距

        # 1. 条目名称输入框（必填）
        self.url_input = QLineEdit(self.item_data.get("URL", ""))
        self.url_input.setPlaceholderText("请输入条目网址")
        form_layout.addRow("网址：", self.url_input)
        # 3. 用户名输入框（必填）
        self.username_input = QLineEdit(self.item_data.get("UserName", ""))
        self.username_input.setPlaceholderText("请输入登录用的用户名")
        form_layout.addRow("用户名：", self.username_input)
        # 4. 密码输入框（必填）
        self.password_input = QLineEdit(self.item_data.get("Password", ""))
        self.password_input.setEchoMode(QLineEdit.Password)  # 密码隐藏
        self.password_input.setPlaceholderText("请输入密码（将自动加密存储）")
        form_layout.addRow("密码：", self.password_input)
        # 2. 关联输入框（可选）
        self.link_input = QLineEdit(self.item_data.get("LinkURL", ""))
        self.link_input.setPlaceholderText("可选：输入相关联的URL")
        form_layout.addRow("LinkURL：", self.link_input)
        # 5. 备注输入框（可选）
        self.note_input = QLineEdit(self.item_data.get("Note", ""))
        self.note_input.setPlaceholderText("可选：输入备注信息")
        form_layout.addRow("备注：", self.note_input)

        # -------------------------- 按钮布局（保存/取消） --------------------------
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.save_btn = QPushButton("保存")
        self.save_btn.setStyleSheet("""
                                    QPushButton {
                                        background-color: #4da6ff;
                                        color: white;
                                        border: none;
                                        padding: 6px 12px;
                                        border-radius: 4px;
                                    }
                                    QPushButton:hover {
                                        background-color: #398ae5;
                                    }
                                    QPushButton:pressed {
                                        background-color: #2a6dbb;
                                    }
                                """)
        self.save_btn.clicked.connect(self._save_item)# 绑定保存逻辑

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)

        # 组装内容布局
        content_layout.addLayout(form_layout)
        content_layout.addLayout(btn_layout)

        # -------------------------- 组装主布局 --------------------------
        main_layout.addWidget(self.title_bar)
        main_layout.addWidget(content_widget)
        # 设置主容器为对话框的主部件
        main_dialog_layout = QVBoxLayout()
        main_dialog_layout.setContentsMargins(0, 0, 0, 0)
        main_dialog_layout.addWidget(main_container)
        self.setLayout(main_dialog_layout)

    def _save_item(self):
        """保存按钮点击事件：收集表单数据并关闭窗口"""
        # 收集输入的表单数据（去除首尾空格）
        self.item_data = {
            "URL": self.url_input.text().strip(),
            "UserName": self.username_input.text().strip(),
            "Password": self.password_input.text().strip(),
            "LinkURL": self.link_input.text().strip(),
            "Note": self.note_input.text().strip()
        }
        # 简单校验：条目名称和用户名不能为空（核心类可再做二次校验）
        if not self.item_data["URL"]:
            msg_box = ErrorDialog(self, "警告：网址不能为空")
            msg_box.exec_()  # 显示消息框
            return
        if not self.item_data["UserName"]:
            msg_box = ErrorDialog(self, "警告：用户名不能为空")
            msg_box.exec_()  # 显示消息框
            return
        # 保存成功，关闭窗口并返回"确认"状态
        self.accept()

    # -------------------------- 窗口拖动功能实现 --------------------------
    def mousePressEvent(self, event):
        """鼠标按下时记录初始位置"""
        if event.button() == Qt.LeftButton and self.title_bar.underMouse():
            self.dragging = True
            self.drag_start_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    def mouseMoveEvent(self, event):
        """鼠标移动时拖动窗口"""
        if self.dragging and event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self.drag_start_position)
            event.accept()
    def mouseReleaseEvent(self, event):
        """鼠标释放时停止拖动"""
        self.dragging = False

class MainWindow(QMainWindow):
    """密码本主窗口：程序的核心交互界面，整合所有功能入口"""
    # todo：实现自定义标题栏
    def __init__(self, password_book: KeyWordNoteBook):
        super().__init__()
        # -------------------------- 核心依赖初始化 --------------------------
        self.password_book = password_book  # 持有核心类实例（调用业务逻辑）
        self.shown_password_row = -1    # 记录当前显示密码的行索引（-1表示无密码显示）

        self.item_table = None  # 主内容表单
        self.status_bar = None  # 状态栏
        self.table_columns = ["条目ID", "URL", "用户名", "密码","关联地址","密码等级", "备注","操作",]  # 列定义

        self.window_width = 1200  # 目标窗口宽度
        self.window_height = 800  # 目标窗口高度

        self.init_ui()  # 初始化界面控件
        self.center_window()  # 窗口居中显示（需在init_ui后调用，确保窗口已初始化）

    def init_ui(self):
        """
        初始化主界面的所有控件和布局
        优化布局：
        main_container:QWidget()
            main_layout:QVBoxLayout垂直布局
                title_bar:QWidget()
                    title_layout:QHBoxLayout 水平布局
                        title_label:QLabel
                        addStretch()
                        min_btn:QPushButton
                        close_btn:QPushButton
                content_widget:QWidget()
                    content_layout:QVBoxLayout
                        item_table:QTableWidget()
                        status_bar:self.statusBar()
        当前布局
        central_widget:QWidget()
            main_layout:QVBoxLayout垂直布局
                item_table:QTableWidget()
                status_bar:self.statusBar()
        """
        # -------------------------- 窗口基础设置 --------------------------
        self.setWindowTitle("密码本管理器")
        self.setMinimumSize(800, 500)  # 最小窗口大小（防止拉伸过小导致控件错乱）

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(20)

        # -------------------------- 3. 条目表格（核心展示控件） --------------------------
        self.item_table = QTableWidget()
        # 3.1 设置表格列数和列标题
        self.item_table.setColumnCount(len(self.table_columns))
        self.item_table.setHorizontalHeaderLabels(self.table_columns)
        self.item_table.verticalHeader().setVisible(False)  # 隐藏行号列
        # 3.2 表格样式优化
        header = self.item_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # 列1"URL"按内容自适应
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # 列2"用户名"按内容自适应
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # 列3"密码"按内容自适应
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # 列4"关联地址"按内容自适应
        header.setSectionResizeMode(5, QHeaderView.Fixed)  # 列5"密码等级"固定宽度
        header.setSectionResizeMode(6, QHeaderView.Stretch)  # 列6"备注"拉伸填充
        header.setSectionResizeMode(7, QHeaderView.Fixed)  # 列7"操作"按内容自适应
        header.resizeSection(5, 80)  # 列5"密码等级"固定100px宽
        header.resizeSection(7, 180)  # 列7（操作）固定120px宽（容下按钮）

        self.item_table.setSelectionBehavior(QTableWidget.SelectRows)  # 选中时整行选中（优化操作）
        self.item_table.setEditTriggers(QTableWidget.NoEditTriggers)  # 禁止表格直接编辑（需通过对话框）
        self.item_table.setColumnHidden(0, True) # 隐藏"条目ID"列
        self.item_table.setRowHeight(0, 35)  # 行高固定35px（适配按钮高度）
        # -------------------------- 4. 状态栏（底部信息提示） --------------------------
        self.status_bar = self.statusBar()  # QMainWindow自带状态栏
        self.status_bar.setStyleSheet("""
                    QStatusBar {
                        background-color: #2d2d2d;
                        color: #bbbbbb;
                        border-top: 1px solid #3d3d3d;
                        padding: 4px 10px;
                    }
                """)
        self.status_bar.showMessage("就绪：已登录，可执行操作", 5000)  # 显示5秒后消失的提示
        # -------------------------- 组装布局 --------------------------
        main_layout.addWidget(self.item_table)  # 表格添加到内容布局，而非主布局
        main_layout.addWidget(self.status_bar)
        # -------------------------- 初始化：加载条目到表格 --------------------------
        self._load_items_to_table()

    def center_window(self):
        """将窗口居中显示在桌面主屏幕"""
        # 1. 获取主屏幕的几何信息（分辨率）
        # 方式2：支持多屏幕，获取窗口所在屏幕（推荐，更精准）
        screen = self.screen()  # 获取窗口当前关联的屏幕
        screen_geometry = screen.availableGeometry()

        # 2. 计算窗口左上角的坐标（使窗口中心与屏幕中心对齐）
        x = (screen_geometry.width() - self.window_width) // 2  # 水平居中
        y = (screen_geometry.height() - self.window_height) // 2  # 垂直居中

        # 3. 设置窗口位置与大小（x,y为左上角坐标，width/height为窗口尺寸）
        self.setGeometry(x, y, self.window_width, self.window_height)

    def _load_items_to_table(self):
        """从核心类获取条目数据，加载到表格中（仅显示非敏感字段）"""
        # 1. 清空表格现有数据（避免重复加载）
        self.item_table.setRowCount(0)  # 重置行数为0
        # 2. 从核心类获取非敏感条目数据（核心类已处理解密和字段筛选）
        items = self.password_book.get_non_secret_items()  # 核心类提供该方法
        if not items:  # 无数据时显示提示
            self.status_bar.showMessage("提示：当前无密码条目，可点击「添加条目」创建", 3000)
            return
        # 3. 遍历数据，填充表格
        for row_idx, item in enumerate(items):
            # 添加新行（行索引=row_idx）
            self.item_table.insertRow(row_idx)
            self.item_table.setRowHeight(row_idx, 35)  # 行高适配按钮
            # 为每行的每列设置数据（与table_columns对应）
            self.item_table.setItem(row_idx, 0, QTableWidgetItem(item["Index"]))
            self.item_table.setItem(row_idx, 1, QTableWidgetItem(item["URL"]))
            self.item_table.setItem(row_idx, 2, QTableWidgetItem(item["UserName"]))
            self.item_table.setItem(row_idx, 3, QTableWidgetItem("  ********  "))
            self.item_table.setItem(row_idx, 4, QTableWidgetItem(item["LinkURL"]))
            self.item_table.setItem(row_idx, 5, QTableWidgetItem(item["PasswordLevel"]))
            self.item_table.setItem(row_idx, 6, QTableWidgetItem(item["Note"]))

            # 3.3 最后一列（列7）：添加操作按钮
            btn_container = QWidget()
            btn_layout = QHBoxLayout(btn_container)
            btn_layout.setContentsMargins(2, 2, 2, 2)  # 容器内边距（避免按钮贴边）
            btn_layout.setSpacing(5)  # 按钮之间的间距

            show_btn = QPushButton("显示")
            show_btn.setFixedSize(55, 30)  # 固定按钮大小（宽70px，高30px）
            # 绑定按钮点击事件（传递当前行索引，用于获取对应条目的密码）
            show_btn.clicked.connect(lambda _, r=row_idx: self._on_show_password_click(r))
            # 将按钮放入单元格（居中显示）
            btn_layout.addWidget(show_btn)

            edit_btn = QPushButton("修改")
            edit_btn.setFixedSize(55, 30)
            edit_btn.setStyleSheet("""
                                QPushButton {
                                    background-color: #4da6ff;
                                    color: white;
                                    border: none;
                                    padding: 6px 12px;
                                    border-radius: 4px;
                                }
                                QPushButton:hover {
                                    background-color: #398ae5;
                                }
                                QPushButton:pressed {
                                    background-color: #2a6dbb;
                                }
                            """)
            edit_btn.clicked.connect(lambda _, r=row_idx: self._on_edit_item_click(r))
            btn_layout.addWidget(edit_btn)

            delete_btn = QPushButton("删除")
            delete_btn.setStyleSheet("""
                                        QPushButton {
                                            background-color:  #e74c3c;
                                            color: #ffffff;
                                            border: none;
                                            padding: 6px 12px;
                                            border-radius: 4px;
                                        }
                                        QPushButton:hover {
                                            background-color: #c0392b;
                                        }
                                        QPushButton:pressed {
                                            background-color: #a52a1d;
                                        }
                                    """)
            delete_btn.setFixedSize(55, 30)
            delete_btn.clicked.connect(lambda _, r=row_idx: self._on_delete_item_click(r))
            btn_layout.addWidget(delete_btn)

            self.item_table.setCellWidget(row_idx, 7, btn_container)

        add_row_idx = len(items)
        self.item_table.insertRow(add_row_idx)
        self.item_table.setRowHeight(add_row_idx, 40)  # 略高于数据行，突出显示
        add_btn = QPushButton("添加")
        add_btn.setFixedSize(80, 35)
        add_btn.setStyleSheet("""
                            QPushButton {
                                background-color: #4da6ff;
                                color: white;
                                border: none;
                                padding: 6px 12px;
                                border-radius: 4px;
                            }
                            QPushButton:hover {
                                background-color: #398ae5;
                            }
                            QPushButton:pressed {
                                background-color: #2a6dbb;
                            }
                        """)
        add_btn.clicked.connect(self._on_add_item_click)
        self.item_table.setCellWidget(add_row_idx, 1, add_btn)

        # 4. 状态栏提示加载结果
        self.status_bar.showMessage(f"成功加载 {len(items)} 条密码条目", 3000)

    def _get_selected_item_id(self) -> str | None:
        """
        获取表格中选中条目的ID（仅支持选中一行）
        :return: 选中条目的ID，无选中/多选时返回None
        """
        # 获取所有选中的单元格，提取对应的行索引
        selected_items = self.item_table.selectedItems()
        if not selected_items:
            msg_box = ErrorDialog(self, "选择错误:请先选中一条密码条目")
            msg_box.exec_()  # 显示消息框
            return None
        # 确保只选中一行（避免多行动作混乱）
        selected_rows = {item.row() for item in selected_items}
        if len(selected_rows) > 1:
            msg_box = ErrorDialog(self, "选择错误:仅支持选中一条条目，请重新选择！")
            msg_box.exec_()  # 显示消息框
            return None
        # 获取选中行的第0列（条目ID）数据
        selected_row = selected_rows.pop()
        return self.item_table.item(selected_row, 0).text()

    def _hide_password(self):
        """隐藏当前显示的密码（恢复为星号）"""
        if self.shown_password_row != -1:  # 存在显示密码的行
            # 获取原始条目数据（用于重新生成星号）
            row_idx = self.shown_password_row
            # 重新设置为星号
            self.item_table.setItem(row_idx, 3, QTableWidgetItem("********"))
            self.shown_password_row = -1  # 重置记录

    # -------------------------- 按钮点击事件处理 --------------------------
    def _on_add_item_click(self):
        """添加条目按钮点击事件：二次验证→打开添加对话框→保存数据"""
        self._hide_password()
        # 1. 二次验证（不通过则终止）
        verify_dialog = SecondaryVerifyDialog("添加密码条目", self)
        if verify_dialog.exec_() != QDialog.Accepted:  # 用户点击取消
            return
        if not self.password_book.verify_main_key(verify_dialog.input_password):
            error_msg = ErrorDialog(msg=f"密码验证失败，无法添加条目")
            error_msg.exec_()
            return
        # 2. 打开添加对话框
        add_dialog = ItemEditDialog(parent=self)
        if add_dialog.exec_() != QDialog.Accepted:  # 用户取消添加
            return
        # 3. 调用核心类添加条目（核心类会自动加密密码）
        item_data = add_dialog.item_data
        print(item_data)
        success = self.password_book.add_item(item_data,upw=verify_dialog.input_password)
        if success != "-1":
            error_msg = ErrorDialog(msg=f"添加条目{success}成功")
            error_msg.exec_()
            self._load_items_to_table()  # 重新加载表格
        else:
            error_msg = ErrorDialog(msg=f"添加失败，请重试")
            error_msg.exec_()

    def _on_delete_item_click(self,row_idx:int):
        """删除条目按钮点击事件：二次验证→获取选中条目→确认删除→调用核心类删除"""
        self._hide_password()
        # 1. 二次验证
        verify_dialog = SecondaryVerifyDialog("删除密码条目", self)
        if verify_dialog.exec_() != QDialog.Accepted:  # 用户点击取消
            return
        if not self.password_book.verify_main_key(verify_dialog.input_password):
            error_msg = ErrorDialog(msg=f"密码验证失败，无法删除条目")
            error_msg.exec_()
            return
        # 2. 获取选中条目的ID
        print(row_idx)

        # 3. 额外确认（防止误删，重要操作需双重确认）
        item_id = self.item_table.item(row_idx, 0).text()
        item_url = self.item_table.item(row_idx, 1).text()

        confirm = ConfirmDialog(self, f"确定要删除「{item_url}」条目吗？删除后不可恢复！",)
        if confirm.exec_() != QDialog.Accepted:  # 用户点击取消
            return
        # 4. 调用核心类删除条目
        success = self.password_book.delete_item(item_id,upw=verify_dialog.input_password)
        if success:
            error_msg = ErrorDialog(msg=f"删除成功")
            error_msg.exec_()
            self._load_items_to_table()  # 重新加载表格
        else:
            error_msg = ErrorDialog(msg=f"删除失败，请重试")
            error_msg.exec_()

    def _on_show_password_click(self,row_idx:str):
        """显示密码按钮点击事件：二次验证→获取选中条目→调用核心类解密并显示密码"""
        self._hide_password()
        # 1. 二次验证（不通过则终止）
        verify_dialog = SecondaryVerifyDialog("查看密码条目", self)
        if verify_dialog.exec_() != QDialog.Accepted:  # 用户点击取消
            return
        if not self.password_book.verify_main_key(verify_dialog.input_password):
            error_msg = ErrorDialog(msg=f"密码验证失败，无法查看条目")
            error_msg.exec_()
            return
        # 2. 获取选中条目的ID

        item_id = self.item_table.item(row_idx, 0).text()
        print(row_idx,item_id)
        # 3. 从核心类获取解密后的密码
        item_data = self.password_book.get_item_by_id(item_id,upw=verify_dialog.input_password)

        if not item_data or "Password" not in item_data:
            error_msg = ErrorDialog(msg=f"错误:无法获取该条目的密码")
            error_msg.exec_()
            return
        # 4. 显示密码（使用信息对话框，密码居中显示）
        self.item_table.setItem(row_idx, 3, QTableWidgetItem(item_data["Password"]))
        self.shown_password_row = row_idx  # 记录密码显示的行

    def _on_edit_item_click(self,row_idx:str):
        """修改条目按钮点击事件：二次验证→获取选中条目→打开修改对话框→更新数据"""
        self._hide_password()
        # 1. 二次验证
        verify_dialog = SecondaryVerifyDialog("修改密码条目", self)
        if verify_dialog.exec_() != QDialog.Accepted:  # 用户点击取消
            return
        if not self.password_book.verify_main_key(verify_dialog.input_password):
            error_msg = ErrorDialog(msg=f"密码验证失败，无法修改条目" )
            error_msg.exec_()
            return

        # 3. 从核心类获取该条目的完整数据（含解密后的密码
        print(row_idx)
        item_id = self.item_table.item(row_idx, 0).text()
        item_data = self.password_book.get_item_by_id(item_id,upw=verify_dialog.input_password)

        if not item_data:
            error_msg = ErrorDialog(msg=f"获取条目{row_idx}失败，无法修改条目")
            error_msg.exec_()
            return
        print(item_data)#dict

        # 4. 打开修改对话框（传入现有数据）
        edit_dialog = ItemEditDialog(item_data, self)
        if edit_dialog.exec_() != QDialog.Accepted:  # 用户取消修改
            return
        # # 5. 调用核心类更新条目
        success = self.password_book.update_item(item_id, data=edit_dialog.item_data, upw=verify_dialog.input_password)
        if success:
            error_msg = ErrorDialog(msg=f"修改条目{success}成功")
            error_msg.exec_()
            self._load_items_to_table()  # 重新加载表格
        else:
            error_msg = ErrorDialog(msg=f"修改失败，请重试")
            error_msg.exec_()

if __name__ == "__main__":
    pass
