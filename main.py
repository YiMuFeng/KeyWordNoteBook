# Copyright (c) 2025 Y.MF. All rights reserved.
#
# 本代码及相关文档受著作权法保护，未经授权，禁止任何形式的复制、分发、修改或商业使用。
# 如需使用或修改本代码，请联系版权所有者获得书面许可（联系方式：1428483061@qq.com）。
#
# 免责声明：本代码按"原样"提供，不提供任何明示或暗示的担保，包括但不限于对适销性、特定用途适用性的担保。
# 在任何情况下，版权所有者不对因使用本代码或本代码的衍生作品而导致的任何直接或间接损失承担责任。
#
# 项目名称：main.py
# 项目仓库：https://github.com/YiMuFeng/KeyWordNoteBook.git
# 创建时间：2025/8/26 22:36
# 版权所有者：Y.MF
# 联系方式：1428483061@qq.com
# 许可协议：Apache License 2.0

"""
"""
__version__ = "0.0.1.1"

import sys
from PyQt5.QtWidgets import QApplication, QDialog

from UI import LoginDialog,MainWindow,ErrorDialog
from Core import KeyWordNoteBook


def main():
    """程序入口：初始化应用→登录→启动主界面"""
    # 1. 初始化PyQt应用（固定用法，管理事件循环）
    app = QApplication(sys.argv)

    # 设置全局深色样式表
    app.setStyle("Fusion")
    app.setStyleSheet("""
            QMainWindow {
               background-color: #2d2d2d;  
            }
            QMainWindow > QWidget {  
                background-color: #2d2d2d;
            }
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
            QTableWidget {
                background-color: #333333;
                color: #ffffff;
                gridline-color: #444444;
            }
            QHeaderView::section {
                background-color: #333333;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 5px;
            }
            QTableWidget QHeaderView::section:vertical {
                width: 10px;                /* 固定行号列宽度（避免序号显示不全） */
                text-align: center;         /* 行号居中显示（默认左对齐，居中更协调） */
            }
            QTableWidget::item {
                background-color: #2d2d2d
                border: 1px solid #444444;
            }
            QTableWidget::item:selected {
                background-color: #4da6ff;  /* 选中时蓝色高亮 */
                color: #ffffff;
            }
            QStatusBar {
                background-color: #333333;
                color: #ffffff;
                border-top: 1px solid #444444;
            }
        }
       """)

    # 2. 显示登录对话框
    while True:
        login_dialog = LoginDialog()
        if login_dialog.exec_() != QDialog.Accepted:  # 用户取消登录
            sys.exit(0)  # 退出程序

        # 3. 初始化核心类（传入登录成功的主密码）
        try:
            password_book = KeyWordNoteBook(mainKey=login_dialog.main_key)#login_dialog.main_key
            break
        except UnicodeError as e:
            error_msg = ErrorDialog(msg=f"文件损坏：{str(e)}",button="退出")
            error_msg.exec_()
            sys.exit(1)
        except ValueError as e:
            # 密码错误：提示用户并重新显示登录界面
            error_msg = ErrorDialog(msg=str(e),button="重新输入")
            error_msg.exec_()  # 显示错误提示，用户确认后继续循环（重新登录）
        except Exception as e:
            # 其他致命错误（如文件损坏、权限问题）：提示后退出
            error_msg = ErrorDialog(msg=f"初始化失败.系统错误：{str(e)}", button="退出")
            error_msg.exec_()
            sys.exit(1)

    # 4. 启动主界面
    main_window = MainWindow(password_book)
    main_window.show()  # 显示主窗口
    # 5. 运行应用的事件循环（程序阻塞在此，直到关闭）
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
