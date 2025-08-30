import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,  # 布局控件
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,  # 基础控件
    QDialog, QFormLayout, QMessageBox, QInputDialog  # 交互控件
)
from PyQt5.QtCore import Qt  # Qt常量（如对齐方式）
from PyQt5.QtGui import QFont  # 字体设置

# 导入核心业务逻辑（与UI分离，通过接口调用）
from Core import KeyWordNoteBook


class LoginDialog(QDialog):
    """登录对话框：程序启动时的第一道安全验证，仅验证主密码"""

    def __init__(self, parent=None):
        super().__init__(parent)
        # -------------------------- 窗口基础设置 --------------------------
        self.setWindowTitle("密码本登录")  # 窗口标题
        self.setFixedSize(300, 150)  # 固定窗口大小（防止拉伸导致布局错乱）
        self.main_key = None  # 存储用户输入的主密码（验证后传递给核心类）

        # -------------------------- 布局初始化 --------------------------
        # 垂直布局：控件自上而下排列（适合表单类界面）
        main_layout = QVBoxLayout()

        # -------------------------- 表单布局（密码输入） --------------------------
        # 表单布局：标签与输入框成对排列，自动对齐
        form_layout = QFormLayout()

        # 密码输入框：设置为密码模式（输入内容隐藏为*）
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)  # 关键：密码隐藏显示
        self.password_input.setPlaceholderText("请输入主密码")  # 提示文本
        form_layout.addRow("主密码：", self.password_input)  # 标签+输入框成对添加

        # -------------------------- 按钮布局（登录/取消） --------------------------
        # 水平布局：按钮自左向右排列（适合操作按钮组）
        btn_layout = QHBoxLayout()

        # 登录按钮：触发密码验证逻辑
        self.login_btn = QPushButton("登录")
        self.login_btn.clicked.connect(self._on_login_click)  # 绑定点击事件

        # 取消按钮：关闭登录窗口，退出程序
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)  # 调用QDialog自带的"取消"逻辑

        btn_layout.addWidget(self.login_btn)
        btn_layout.addWidget(self.cancel_btn)

        # -------------------------- 组装布局 --------------------------
        main_layout.addLayout(form_layout)  # 先加表单
        main_layout.addLayout(btn_layout)  # 再加按钮组
        self.setLayout(main_layout)  # 设置窗口的主布局

    def _on_login_click(self):
        """登录按钮点击事件：验证密码非空后传递结果"""
        password = self.password_input.text().strip()  # 获取输入并去除首尾空格
        if not password:  # 空密码校验
            QMessageBox.warning(self, "警告", "请输入主密码，不能为空！")
            return
        # 密码非空则存储并关闭登录窗口（返回"确认"状态）
        self.main_key = password
        self.accept()  # 调用QDialog自带的"确认"逻辑，关闭窗口并返回Accepted


class SecondaryVerifyDialog(QDialog):
    """二级验证对话框：执行敏感操作前的二次密码验证（防误触/盗操作）"""

    def __init__(self, action_name: str, parent=None):
        """
        :param action_name: 要执行的操作名称（如"添加条目"），用于提示用户
        :param parent: 父窗口（主界面），确保对话框居中显示在父窗口上
        """
        super().__init__(parent)
        # -------------------------- 窗口基础设置 --------------------------
        self.setWindowTitle(f"安全验证 - {action_name}")  # 动态标题（明确操作场景）
        self.setFixedSize(300, 150)
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
            QMessageBox.warning(self, "警告", "请输入验证密码！")
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
        super().__init__(parent)
        # -------------------------- 窗口基础设置 --------------------------
        self.setWindowTitle("修改密码条目" if item_data else "添加新密码条目")
        self.setFixedSize(450, 320)  # 足够大的空间容纳所有表单字段
        self.item_data = item_data.copy() if item_data else {}  # 存储编辑后的条目数据

        # -------------------------- 布局初始化 --------------------------
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)  # 窗口内边距（避免控件贴边）

        # -------------------------- 表单布局（条目字段） --------------------------
        form_layout = QFormLayout()
        form_layout.setSpacing(12)  # 表单字段之间的间距

        # 1. 条目名称输入框（必填：用于标识条目，如"B站账号"）
        self.name_input = QLineEdit(self.item_data.get("name", ""))
        self.name_input.setPlaceholderText("请输入条目名称（如：B站账号）")
        form_layout.addRow("条目名称：", self.name_input)

        # 2. 网址输入框（可选：存储对应网站的URL）
        self.url_input = QLineEdit(self.item_data.get("url", ""))
        self.url_input.setPlaceholderText("可选：输入网站URL（如https://www.bilibili.com）")
        form_layout.addRow("网址：", self.url_input)

        # 3. 用户名输入框（必填：账号的用户名/邮箱/手机号）
        self.username_input = QLineEdit(self.item_data.get("username", ""))
        self.username_input.setPlaceholderText("请输入用户名/邮箱/手机号")
        form_layout.addRow("用户名：", self.username_input)

        # 4. 密码输入框（必填：存储明文密码，后续由核心类加密）
        self.password_input = QLineEdit(self.item_data.get("password", ""))
        self.password_input.setEchoMode(QLineEdit.Password)  # 密码隐藏
        self.password_input.setPlaceholderText("请输入密码（明文，将自动加密存储）")
        form_layout.addRow("密码：", self.password_input)

        # 5. 备注输入框（可选：存储额外信息，如"2024年5月修改"）
        self.note_input = QLineEdit(self.item_data.get("note", ""))
        self.note_input.setPlaceholderText("可选：输入备注信息（如：工作账号）")
        form_layout.addRow("备注：", self.note_input)

        # -------------------------- 按钮布局（保存/取消） --------------------------
        btn_layout = QHBoxLayout()

        self.save_btn = QPushButton("保存条目")
        self.save_btn.clicked.connect(self._save_item)  # 绑定保存逻辑

        self.cancel_btn = QPushButton("取消编辑")
        self.cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)

        # -------------------------- 组装布局 --------------------------
        main_layout.addLayout(form_layout)
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

    def _save_item(self):
        """保存按钮点击事件：收集表单数据并关闭窗口"""
        # 收集输入的表单数据（去除首尾空格）
        self.item_data = {
            "name": self.name_input.text().strip(),
            "url": self.url_input.text().strip(),
            "username": self.username_input.text().strip(),
            "password": self.password_input.text().strip(),
            "note": self.note_input.text().strip()
        }
        # 简单校验：条目名称和用户名不能为空（核心类可再做二次校验）
        if not self.item_data["name"]:
            QMessageBox.warning(self, "警告", "条目名称不能为空！")
            return
        if not self.item_data["username"]:
            QMessageBox.warning(self, "警告", "用户名不能为空！")
            return
        # 保存成功，关闭窗口并返回"确认"状态
        self.accept()


class PasswordManagerMainWindow(QMainWindow):
    """密码本主窗口：程序的核心交互界面，整合所有功能入口"""

    def __init__(self, password_book: KeyWordNoteBook):
        super().__init__()
        # -------------------------- 核心依赖初始化 --------------------------
        self.password_book = password_book  # 持有核心类实例（调用业务逻辑）
        self.init_ui()  # 初始化界面控件

    def init_ui(self):
        """初始化主界面的所有控件和布局"""
        # -------------------------- 窗口基础设置 --------------------------
        self.setWindowTitle("安全密码本管理器")  # 主窗口标题
        self.setGeometry(150, 100, 900, 600)  # 窗口位置（x,y）和大小（宽,高）
        self.setMinimumSize(800, 500)  # 最小窗口大小（防止拉伸过小导致控件错乱）

        # -------------------------- 中心部件与主布局 --------------------------
        # QMainWindow必须通过centralWidget承载布局（固定用法）
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        # 主布局：垂直布局（标题 → 按钮组 → 表格 → 状态栏）
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)  # 主布局内边距
        main_layout.setSpacing(20)  # 主布局内控件间距

        # -------------------------- 1. 标题标签 --------------------------
        title_label = QLabel("密码条目管理")
        # 设置标题字体（加粗、放大，提升视觉层级）
        title_font = QFont()
        title_font.setPointSize(18)  # 字体大小
        title_font.setBold(True)  # 加粗
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)  # 标题居中
        main_layout.addWidget(title_label)

        # -------------------------- 2. 功能按钮组（水平布局） --------------------------
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)  # 按钮之间的间距

        # 2.1 添加条目按钮：打开添加条目对话框
        self.add_btn = QPushButton("1. 添加条目")
        self.add_btn.setFixedSize(120, 40)  # 固定按钮大小（统一视觉）
        self.add_btn.clicked.connect(self._on_add_item_click)  # 绑定点击事件

        # 2.2 修改条目按钮：打开修改条目对话框（需先选中条目）
        self.edit_btn = QPushButton("2. 修改条目")
        self.edit_btn.setFixedSize(120, 40)
        self.edit_btn.clicked.connect(self._on_edit_item_click)

        # 2.3 删除条目按钮：删除选中的条目（需二次确认）
        self.delete_btn = QPushButton("3. 删除条目")
        self.delete_btn.setFixedSize(120, 40)
        self.delete_btn.clicked.connect(self._on_delete_item_click)

        # 2.4 显示密码按钮：查看选中条目的解密后密码（需二次验证）
        self.show_pwd_btn = QPushButton("4. 显示密码")
        self.show_pwd_btn.setFixedSize(120, 40)
        self.show_pwd_btn.clicked.connect(self._on_show_password_click)

        # 将按钮添加到按钮布局（自左向右排列）
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.show_pwd_btn)
        # 设置按钮布局的对齐方式（居左，避免按钮拉伸）
        btn_layout.setAlignment(Qt.AlignLeft)
        main_layout.addLayout(btn_layout)

        # -------------------------- 3. 条目表格（核心展示控件） --------------------------
        self.item_table = QTableWidget()
        # 3.1 设置表格列数和列标题（仅显示非敏感字段，密码不显示）
        self.table_columns = ["条目ID", "条目名称", "网址", "用户名", "备注"]  # 列定义
        self.item_table.setColumnCount(len(self.table_columns))
        self.item_table.setHorizontalHeaderLabels(self.table_columns)
        # 3.2 表格样式优化
        self.item_table.horizontalHeader().setStretchLastSection(True)  # 最后一列拉伸填充
        # self.item_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # 第2列（名称）拉伸
        self.item_table.setSelectionBehavior(QTableWidget.SelectRows)  # 选中时整行选中（优化操作）
        self.item_table.setEditTriggers(QTableWidget.NoEditTriggers)  # 禁止表格直接编辑（需通过对话框）
        # 3.3 隐藏"条目ID"列（内部使用，用户无需看到）
        self.item_table.setColumnHidden(0, True)
        main_layout.addWidget(self.item_table)

        # -------------------------- 4. 状态栏（底部信息提示） --------------------------
        self.status_bar = self.statusBar()  # QMainWindow自带状态栏
        self.status_bar.showMessage("就绪：已登录，可执行操作", 5000)  # 显示5秒后消失的提示

        # -------------------------- 初始化：加载条目到表格 --------------------------
        self._load_items_to_table()

    def _load_items_to_table(self):
        """从核心类获取条目数据，加载到表格中（仅显示非敏感字段）"""
        # 1. 清空表格现有数据（避免重复加载）
        self.item_table.setRowCount(0)  # 重置行数为0
        # 2. 从核心类获取非敏感条目数据（核心类已处理解密和字段筛选）
        items = self.password_book.get_non_secret_items()  # 假设核心类提供该方法
        if not items:  # 无数据时显示提示
            self.status_bar.showMessage("提示：当前无密码条目，可点击「添加条目」创建", 3000)
            return
        # 3. 遍历数据，填充表格
        for row_idx, item in enumerate(items):
            # 添加新行（行索引=row_idx）
            self.item_table.insertRow(row_idx)
            # 为每行的每列设置数据（与table_columns对应）
            self.item_table.setItem(row_idx, 0, QTableWidgetItem(item["id"]))  # 条目ID（隐藏）
            self.item_table.setItem(row_idx, 1, QTableWidgetItem(item["name"]))  # 条目名称
            self.item_table.setItem(row_idx, 2, QTableWidgetItem(item["url"]))  # 网址
            self.item_table.setItem(row_idx, 3, QTableWidgetItem(item["username"]))  # 用户名
            self.item_table.setItem(row_idx, 4, QTableWidgetItem(item["note"]))  # 备注
        # 4. 状态栏提示加载结果
        self.status_bar.showMessage(f"成功加载 {len(items)} 条密码条目", 3000)

    def _show_secondary_verify(self, action_name: str) -> bool:
        """
        显示二级验证对话框，统一处理二次验证逻辑
        :param action_name: 操作名称（如"添加条目"）
        :return: True=验证通过，False=验证失败/取消
        """
        verify_dialog = SecondaryVerifyDialog(action_name, self)
        if verify_dialog.exec_() != QDialog.Accepted:  # 用户点击取消
            return False
        # 调用核心类验证密码是否正确
        return self.password_book.verify_main_key(verify_dialog.input_password)

    def _get_selected_item_id(self) -> str | None:
        """
        获取表格中选中条目的ID（仅支持选中一行）
        :return: 选中条目的ID，无选中/多选时返回None
        """
        # 获取所有选中的单元格，提取对应的行索引
        selected_items = self.item_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "选择错误", "请先选中一条密码条目！")
            return None
        # 确保只选中一行（避免多行动作混乱）
        selected_rows = {item.row() for item in selected_items}
        if len(selected_rows) > 1:
            QMessageBox.warning(self, "选择错误", "仅支持选中一条条目，请重新选择！")
            return None
        # 获取选中行的第0列（条目ID）数据
        selected_row = selected_rows.pop()
        return self.item_table.item(selected_row, 0).text()

    # -------------------------- 按钮点击事件处理 --------------------------
    def _on_add_item_click(self):
        """添加条目按钮点击事件：二次验证→打开添加对话框→保存数据"""
        # 1. 二次验证（不通过则终止）
        if not self._show_secondary_verify("添加密码条目"):
            QMessageBox.warning(self, "验证失败", "主密码不正确，无法添加条目！")
            return
        # 2. 打开添加对话框
        add_dialog = ItemEditDialog(parent=self)
        if add_dialog.exec_() != QDialog.Accepted:  # 用户取消添加
            return
        # 3. 调用核心类添加条目（核心类会自动加密密码）
        item_data = add_dialog.item_data
        success = self.password_book.add_item(item_data)
        if success:
            QMessageBox.information(self, "添加成功", f"「{item_data['name']}」条目已添加！")
            self._load_items_to_table()  # 重新加载表格
        else:
            QMessageBox.error(self, "添加失败", "条目添加失败，请重试！")

    def _on_edit_item_click(self):
        """修改条目按钮点击事件：二次验证→获取选中条目→打开修改对话框→更新数据"""
        # 1. 二次验证
        if not self._show_secondary_verify("修改密码条目"):
            QMessageBox.warning(self, "验证失败", "主密码不正确，无法修改条目！")
            return
        # 2. 获取选中条目的ID
        item_id = self._get_selected_item_id()
        if not item_id:
            return
        # 3. 从核心类获取该条目的完整数据（含解密后的密码）
        item_data = self.password_book.get_item_by_id(item_id)
        if not item_data:
            QMessageBox.error(self, "获取失败", f"未找到ID为「{item_id}」的条目！")
            return
        # 4. 打开修改对话框（传入现有数据）
        edit_dialog = ItemEditDialog(item_data, self)
        if edit_dialog.exec_() != QDialog.Accepted:  # 用户取消修改
            return
        # 5. 调用核心类更新条目
        updated_data = edit_dialog.item_data
        success = self.password_book.update_item(item_id, updated_data)
        if success:
            QMessageBox.information(self, "修改成功", f"「{updated_data['name']}」条目已更新！")
            self._load_items_to_table()  # 重新加载表格
        else:
            QMessageBox.error(self, "修改失败", "条目修改失败，请重试！")

    def _on_delete_item_click(self):
        """删除条目按钮点击事件：二次验证→获取选中条目→确认删除→调用核心类删除"""
        # 1. 二次验证
        if not self._show_secondary_verify("删除密码条目"):
            QMessageBox.warning(self, "验证失败", "主密码不正确，无法删除条目！")
            return
        # 2. 获取选中条目的ID
        item_id = self._get_selected_item_id()
        if not item_id:
            return
        # 3. 额外确认（防止误删，重要操作需双重确认）
        item_name = self.item_table.item(self.item_table.selectedItems()[0].row(), 1).text()
        confirm = QMessageBox.question(
            self, "确认删除",
            f"确定要删除「{item_name}」条目吗？删除后不可恢复！",
            QMessageBox.Yes | QMessageBox.No  # 提供"是/否"选项
        )
        if confirm != QMessageBox.Yes:  # 用户选择"否"
            return
        # 4. 调用核心类删除条目
        success = self.password_book.delete_item(item_id)
        if success:
            QMessageBox.information(self, "删除成功", f"「{item_name}」条目已删除！")
            self._load_items_to_table()  # 重新加载表格
        else:
            QMessageBox.error(self, "删除失败", "条目删除失败，请重试！")

    def _on_show_password_click(self):
        """显示密码按钮点击事件：二次验证→获取选中条目→调用核心类解密并显示密码"""
        # 1. 二次验证
        if not self._show_secondary_verify("查看密码"):
            QMessageBox.warning(self, "验证失败", "主密码不正确，无法查看密码！")
            return
        # 2. 获取选中条目的ID
        item_id = self._get_selected_item_id()
        if not item_id:
            return
        # 3. 从核心类获取解密后的密码
        item_data = self.password_book.get_item_by_id(item_id)
        if not item_data or "password" not in item_data:
            QMessageBox.error(self, "获取失败", "无法获取该条目的密码！")
            return
        # 4. 显示密码（使用信息对话框，密码居中显示）
        QMessageBox.information(
            self,
            f"「{item_data['name']}」的密码",
            f"<center>用户名：{item_data['username']}</center><br>"
            f"<center>密码：<b>{item_data['password']}</b></center><br>"
            f"<center>（请妥善保管，关闭后无法再次查看）</center>",
            QMessageBox.Ok
        )




if __name__ == "__main__":
    pass
