"""
Author:G W
Date  :2022.04.12
"""
import sys
import win32gui, win32api, win32con
import win32process
import images
from PySide2.QtWidgets import QWidget, QApplication, QSystemTrayIcon, \
    QMenu, QAction
from PySide2.QtGui import QIcon
from PySide2.QtCore import Qt, QEvent
from TopOnWindow import Ui_Form


class ControlBoard(QWidget, Ui_Form):
    def __init__(self):  # 设置UI界面的信号与槽函数
        super(ControlBoard, self).__init__()
        self.setupUi(self)
        self.pushButton_1.clicked.connect(self.refresh_text)
        self.pushButton_3.clicked.connect(self.set_toponwindow)
        self.pushButton_4.clicked.connect(self.cancel_set_toponwindow)
        self.setWindowIcon(QIcon(':laptop.ico'))

    def get_hwnd_dict(self, hwnd, hwnd_title):  # 获取所有窗口的名称
        self.textEdit.clear()
        self.comboBox.clear()
        if (win32gui.IsWindow(hwnd)
                and win32gui.IsWindowEnabled(hwnd)
                and win32gui.IsWindowVisible(hwnd)
                and win32gui.GetWindowText(hwnd)):
            hwnd_title[f"{hwnd}"] = win32gui.GetWindowText(hwnd)

    def get_hwnd(self):  # 获取所有窗口的句柄与名称
        hwnd_title = {}
        win32gui.EnumWindows(self.get_hwnd_dict, hwnd_title)
        return hwnd_title

    def refresh_text(self):  # 将窗口信息打印在textEdit和comboBox中
        hwnd_title = self.get_hwnd()
        del_handle = ''
        for handle, string in hwnd_title.items():
            if string == '窗口置顶':
                del_handle = handle
        del hwnd_title[del_handle]
        hwnd_key = list(hwnd_title)
        hwnd_value = list(hwnd_title.values())
        for i in range(0, len(hwnd_key) - 1):
            self.textEdit.append(str(hwnd_value[i]))
            self.comboBox.addItem(str(hwnd_value[i]))

    def return_key(self, val, dict):  # 根据窗口文本返回窗口键值
        for key, value in dict.items():
            if value == val:
                return key
        return 'Key Not Found'

    def set_toponwindow(self, hwnd):  # 窗口置顶
        combobox_text = self.comboBox.currentText()
        hwnd_title = self.get_hwnd()
        form_ui_key = self.return_key('窗口置顶', hwnd_title)
        combobox_key = self.return_key(combobox_text, hwnd_title)
        dwForeID = win32process.GetWindowThreadProcessId(combobox_key)
        dwCurID = win32api.GetCurrentThreadId()
        win32process.AttachThreadInput(dwForeID[0], dwCurID, 1)
        win32gui.SetWindowPos(combobox_key, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                              win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        win32gui.SetWindowPos(form_ui_key, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                              win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        win32process.AttachThreadInput(dwForeID[0], dwCurID, 0)
        self.refresh_text()

    def cancel_set_toponwindow(self):
        combobox_text = self.comboBox.currentText()
        hwnd_title = self.get_hwnd()
        combobox_key = self.return_key(combobox_text, hwnd_title)
        win32gui.SetWindowPos(combobox_key, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                              win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        self.refresh_text()

    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            if self.windowState() and Qt.WindowMinimized:
                event.ignore()
                self.setWindowFlags(Qt.SplashScreen | Qt.FramelessWindowHint)
                self.showMinimized()
                self.show()
                return


class TrayIcon(QSystemTrayIcon, QWidget, Qt):
    def __init__(self,Widget,parent=None):  # 设置UI界面的信号与槽函数
        super(TrayIcon, self).__init__()
        self.activated.connect(self.onIconClicked)
        self.ui = Widget
        self.createMenu()

    def createMenu(self):
        self.menu = QMenu()
        self.showAction = QAction("显示主界面", self, triggered=self.show_window)
        self.quitAction = QAction("退出", self, triggered=self.quit)
        self.menu.addAction(self.showAction)
        self.menu.addAction(self.quitAction)
        self.setContextMenu(self.menu)
        self.setIcon(QIcon(":laptop.ico"))
        self.icon = self.MessageIcon()

    def show_window(self):
        self.ui.showNormal()
        self.ui.activateWindow()
        self.ui.setWindowFlags(self.Widget)
        self.ui.show()

    def quit(self):
        QApplication.quit()

    # 鼠标点击icon传递的信号会带有一个整形的值，1是表示单击右键，2是双击，3是单击左键，4是用鼠标中键点击
    def onIconClicked(self, reason):
        if reason == 2 or reason == 3:
            if self.ui.isMinimized() or not self.ui.isVisible():
                # 若是最小化，则先正常显示窗口，再变为活动窗口（暂时显示在最前面）
                self.ui.showNormal()
                self.ui.activateWindow()
                self.ui.setWindowFlags(self.Widget)
                self.ui.show()
            else:
                # 若不是最小化，则最小化
                self.ui.setWindowFlags(self.SplashScreen | self.FramelessWindowHint)
                self.ui.showMinimized()
                self.ui.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ControlBoard()
    win.show()
    win.refresh_text()
    tray = TrayIcon(win)
    tray.show()
    sys.exit(app.exec_())
