"""

"""
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,  # 布局控件
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,  # 基础控件
    QDialog, QFormLayout, QMessageBox, QInputDialog  # 交互控件
)
from PyQt5.QtCore import Qt  # Qt常量（如对齐方式）
from PyQt5.QtGui import QFont  # 字体设置

from UI import LoginDialog,PasswordManagerMainWindow
from Core import KeyWordNoteBook

def main():
    """程序入口：初始化应用→登录→启动主界面"""
    # 1. 初始化PyQt应用（固定用法，管理事件循环）
    app = QApplication(sys.argv)

    # 设置全局深色样式表
    app.setStyle("Fusion")
    app.setStyleSheet("""
           QDialog {
               background-color: #2d2d2d;
           }
           QLabel {
               color: #ffffff;
           }
           QLineEdit {
               background-color: #333333;
               color: #ffffff;
               border: 1px solid #555555;
               border-radius: 4px;
               padding: 5px;
           }
           QLineEdit:focus {
               border: 1px solid #4da6ff;
           }
           QPushButton {
               background-color: #555555;
               color: white;
               border: none;
               padding: 6px 12px;
               border-radius: 4px;
           }
           QPushButton:hover {
               background-color: #666666;
           }
           QPushButton:pressed {
               background-color: #444444;
           }
           QMessageBox {
               background-color: #2d2d2d;
               color: #ffffff;
           }
           QMessageBox QPushButton {
               background-color: #555555;
               color: white;
               border: none;
               padding: 5px 10px;
               border-radius: 3px;
           }
       """)



    # 2. 显示登录对话框
    login_dialog = LoginDialog()
    if login_dialog.exec_() != QDialog.Accepted:  # 用户取消登录
        sys.exit(0)  # 退出程序
    # 3. 初始化核心类（传入登录成功的主密码）
    try:
        password_book = KeyWordNoteBook(mainKey=login_dialog.main_key)
    except Exception as e:
        QMessageBox.critical(None, "初始化失败", f"密码本核心类初始化失败：{str(e)}")
        sys.exit(1)
    # 4. 启动主界面
    main_window = PasswordManagerMainWindow(password_book)
    main_window.show()  # 显示主窗口
    # 5. 运行应用的事件循环（程序阻塞在此，直到关闭）
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
