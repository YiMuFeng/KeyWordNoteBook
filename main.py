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
__version__ = "0.0.1.2"

import sys
import argparse
import logging
from PyQt5.QtWidgets import QApplication, QDialog

from UI import LoginDialog, MainWindow, ErrorDialog
from Core import KeyWordNoteBook


def setup_logging(debug: bool = False):
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def get_stylesheet() -> str:
    """Return the global stylesheet used by the application.

    Keeping the stylesheet in a function makes it easy to test and
    to swap themes later (dark mode, user themes, etc.).
    """
    return """
        QWidget { background-color: #f3f6f9; color: #222222; }
        QMainWindow { background-color: #f3f6f9; }
        QDialog { background-color: #ffffff; }

        QWidget[card="true"] { background-color: #ffffff; border-radius: 8px; }

        QLabel { color: #2b2b2b; }
        QLineEdit {
            background-color: #ffffff;
            color: #2b2b2b;
            border: 1px solid #e6e9ee;
            border-radius: 6px;
            padding: 8px;
        }
        QLineEdit:focus { border: 1px solid #3b82f6; }

        QPushButton {
            background-color: #0f1724;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 6px;
        }
        QPushButton.secondary {
            background-color: transparent; color: #475569; border: 1px solid transparent;
        }
        QPushButton#newBtn {
            background-color: #0f1724; color: white; font-weight: 600; padding: 8px 14px; border-radius: 6px;
        }

        QTableWidget { background-color: transparent; gridline-color: #eef2f7; }
        QHeaderView::section { background-color: transparent; color: #475569; padding: 8px; }
        QTableWidget::item { background-color: #ffffff; border: 1px solid #eef2f7; }
        QTableWidget::item:selected { background-color: #eef6ff; }

        QStatusBar { background-color: transparent; color: #6b7280; }
    """


def run_app(argv=None) -> int:
    """Run the GUI application. Returns process exit code.

    This function is split out to make it easier to test programmatically.
    """
    parser = argparse.ArgumentParser(prog="KeyWordNoteBook")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args, _ = parser.parse_known_args(argv)

    setup_logging(debug=args.debug)
    log = logging.getLogger("main")

    app = QApplication(sys.argv if argv is None else argv)
    app.setStyle("Fusion")
    app.setStyleSheet(get_stylesheet())

    # 显示登录对话框并尝试初始化核心类
    while True:
        login_dialog = LoginDialog()
        if login_dialog.exec_() != QDialog.Accepted:
            log.info("User cancelled login. Exiting.")
            return 0

        try:
            password_book = KeyWordNoteBook(mainKey=login_dialog.main_key)
            break
        except UnicodeError as e:
            log.exception("UnicodeError while initializing KeyWordNoteBook")
            error_msg = ErrorDialog(msg=f"文件损坏：{str(e)}", button="退出")
            error_msg.exec_()
            return 1
        except ValueError as e:
            # 密码错误：提示用户并重新显示登录界面
            log.warning("Authentication failed: %s", e)
            error_msg = ErrorDialog(msg=str(e), button="重新输入")
            error_msg.exec_()
            # loop back to re-show login
        except Exception as e:
            log.exception("Fatal error while initializing KeyWordNoteBook")
            error_msg = ErrorDialog(msg=f"初始化失败.系统错误：{str(e)}", button="退出")
            error_msg.exec_()
            return 1

    main_window = MainWindow(password_book)
    main_window.show()

    exit_code = app.exec_()
    log.info("Application exited with code %s", exit_code)
    return int(exit_code)


def main():
    code = run_app()
    sys.exit(code)


if __name__ == '__main__':
    main()
