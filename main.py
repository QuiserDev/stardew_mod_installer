import sys
import os
import json5
import zipfile
from datetime import datetime

from PySide6.QtWidgets import (QApplication, QListWidgetItem, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel, QPushButton, QTextEdit,
                               QFileDialog, QMessageBox, QProgressBar,
                               QGroupBox, QFrame, QListWidget, QDialog,
                               QScrollArea, QTextBrowser)
from PySide6.QtCore import Qt, QThread, Signal, QSettings, QTimer
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QIcon


def resource_path(relative_path):
    """获取资源文件的绝对路径，适用于开发环境和打包后的环境"""
    try:
        # PyInstaller 创建临时文件夹，并将路径存储在 _MEIPASS 中
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)


TUTORIAL_TEXT = """

<div style='background: linear-gradient(to right, #a8d8b9, #81c29c); padding: 10px; border-radius: 8px; margin: 10px 0;'>
<h2 style='color: #2e2e2e; font-size: 16px; margin: 0;'>1. 设置Mods文件夹</h2>
</div>
<ul style='color: #5d4037; font-size: 13px; line-height: 1.6;'>
<li><strong>首次启动</strong>会自动尝试查找Mods文件夹</li>
<li><strong>如果找不到</strong>，请手动选择，路径如下：</li>
<div style='background: rgba(139, 115, 85, 0.1); padding: 8px; border-radius: 4px; margin: 5px 0;'>
Steam → Stardew Valley → 齿轮图标(管理) → 浏览本地文件 → Mods子文件夹
</div>
</ul>

<div style='background: linear-gradient(to right, #ffd54f, #ffb74d); padding: 10px; border-radius: 8px; margin: 10px 0;'>
<h2 style='color: #2e2e2e; font-size: 16px; margin: 0;'>2. 安装Mod</h2>
</div>
<ul style='color: #5d4037; font-size: 13px; line-height: 1.6;'>
<li><strong>拖放安装</strong>：将zip文件拖放到窗口中的虚线框区域</li>
<li><strong>手动选择</strong>：点击"手动选择Mod文件"按钮</li>
<li><strong>自动解压</strong>：程序会自动解压到Mods文件夹</li>
</ul>

<div style='background: linear-gradient(to right, #90caf9, #64b5f6); padding: 10px; border-radius: 8px; margin: 10px 0;'>
<h2 style='color: #2e2e2e; font-size: 16px; margin: 0;'>3. 注意事项</h2>
</div>
<ul style='color: #5d4037; font-size: 13px; line-height: 1.6;'>
<li><strong>SMAPI要求</strong>：确保星露谷已安装SMAPI</li>
<li><strong>SMAPI安装</strong>：SMAPI也可以用本软件安装</li>
<li><strong>重启游戏</strong>：安装后需要重启游戏生效</li>
<li><strong>依赖项</strong>：某些Mod可能需要其他Mod支持</li>
</ul>

<div style='background: linear-gradient(to right, #ffab91, #ff8a65); padding: 10px; border-radius: 8px; margin: 10px 0;'>
<h2 style='color: #2e2e2e; font-size: 16px; margin: 0;'>4. 常见问题</h2>
</div>
<ul style='color: #5d4037; font-size: 13px; line-height: 1.6;'>
<li><strong>Mod不工作？</strong>检查是否解压正确，文件夹结构是否正确</li>
<li><strong>游戏崩溃？</strong>检查Mod兼容性，移除冲突的Mod</li>
<li><strong>需要更新？</strong>删除旧版再安装新版，避免文件冲突</li>
</ul>

<div style='background: linear-gradient(to right, #ce93d8, #ba68c8); padding: 10px; border-radius: 8px; margin: 10px 0;'>
<h2 style='color: #2e2e2e; font-size: 16px; margin: 0;'>💡 小贴士</h2>
</div>
<ul style='color: #5d4037; font-size: 13px; line-height: 1.6;'>
<li>定期备份Mods文件夹，避免意外丢失</li>
<li>安装新Mod时，建议逐个测试兼容性</li>
<li>查看Mod的说明文档，了解具体功能和使用方法</li>
</ul>


"""

class TutorialDialog(QDialog):
    """自定义教程对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📚 星露谷物语 Mod 安装器 - 使用教程")
        self.setModal(True)
        self.setMinimumSize(700, 600)
        self.setMaximumSize(900, 800)
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        # 主布局
        main_layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("📖 星露谷物语 Mod 安装器 使用教程")
        title_label.setStyleSheet("""
            font-size: 22px; 
            font-weight: bold; 
            color: #5d4037; 
            padding: 15px; 
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e6d4b3, stop:1 #c8b89d);
            border-radius: 8px;
            margin-bottom: 10px;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 2px solid #8b7355;
                border-radius: 8px;
                background-color: rgba(255, 255, 255, 0.9);
            }
            QScrollBar:vertical {
                background: #e6d4b3;
                width: 15px;
                border-radius: 7px;
            }
            QScrollBar::handle:vertical {
                background: #8b7355;
                border-radius: 7px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #6b5b47;
            }
        """)
        
        # 内容容器
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # 使用QTextBrowser来显示HTML格式的教程
        tutorial_browser = QTextBrowser()
        tutorial_browser.setHtml(TUTORIAL_TEXT)
        tutorial_browser.setStyleSheet("""
            QTextBrowser {
                background-color: rgba(255, 255, 255, 0.95);
                border: none;
                font-size: 13px;
                line-height: 1.6;
                padding: 15px;
            }
            QTextBrowser a {
                color: #81c29c;
                text-decoration: none;
            }
            QTextBrowser a:hover {
                color: #a8d8b9;
                text-decoration: underline;
            }
        """)
        tutorial_browser.setOpenExternalLinks(True)
        
        content_layout.addWidget(tutorial_browser)
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_button = QPushButton("关闭教程")
        close_button.setStyleSheet("""
            QPushButton {
                padding: 10px 25px;
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                                                 stop: 0 #a8d8b9, stop: 1 #81c29c);
                color: #2e2e2e;
                border: 2px solid #8b7355;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                                                 stop: 0 #b8e8c9, stop: 1 #91d2ac);
                border: 2px solid #6b5b47;
            }
            QPushButton:pressed {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                                                 stop: 0 #81c29c, stop: 1 #a8d8b9);
            }
        """)
        close_button.clicked.connect(self.accept)
        
        button_layout.addWidget(close_button)
        main_layout.addLayout(button_layout)
        
        # 设置窗口样式
        self.setStyleSheet("""
            TutorialDialog {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                                          stop: 0 #f5f0e6, stop: 1 #e6d4b3);
                border: 3px solid #8b7355;
                border-radius: 12px;
            }
        """)


DELETE_CONFIRMATION = """⚠️ 您确定要删除以下Mod吗？

{}

注意：
• Mod之间可能存在依赖关系
• 删除某些Mod可能导致其他Mod无法正常工作
• 删除后需要重启游戏

请确认是否继续删除？"""

class ModInstallWorker(QThread):
    """后台线程用于安装Mod"""
    progress = Signal(int)
    status = Signal(str)
    finished = Signal(bool, str)

    def __init__(self, zip_path, mods_folder):
        super().__init__()
        self.zip_path = zip_path
        self.mods_folder = mods_folder

    def run(self):
        try:
            self.status.emit(f"正在安装: {os.path.basename(self.zip_path)}")

            # 打开zip文件
            with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
                # 获取所有文件
                file_list = zip_ref.namelist()

                # 分析zip结构，判断是否有顶级文件夹
                has_top_folder = self._has_top_level_folder(file_list)

                if has_top_folder:
                    # 如果有顶级文件夹，直接解压到mods文件夹
                    zip_ref.extractall(self.mods_folder)
                    self.status.emit("✓ Mod已解压到mods文件夹")
                else:
                    # 如果没有顶级文件夹，创建一个以zip文件名为名的文件夹
                    mod_name = os.path.splitext(
                        os.path.basename(self.zip_path))[0]
                    target_folder = os.path.join(self.mods_folder, mod_name)
                    os.makedirs(target_folder, exist_ok=True)

                    # 解压到创建的文件夹
                    zip_ref.extractall(target_folder)
                    self.status.emit(f"✓ Mod已安装到: {mod_name}")

            self.finished.emit(
                True, f"成功安装: {os.path.basename(self.zip_path)}")

        except Exception as e:
            self.finished.emit(False, f"安装失败: {str(e)}")

    def _has_top_level_folder(self, file_list):
        """检查zip是否包含顶级文件夹"""
        if not file_list:
            return False

        # 获取第一个文件的路径结构
        first_file = file_list[0]
        parts = first_file.split('/')

        # 如果所有文件都在同一个顶级文件夹下
        if len(parts) > 1:
            top_folder = parts[0]
            # 检查是否所有文件都以这个文件夹开头
            for file in file_list[1:]:
                if not file.startswith(top_folder + '/'):
                    return False
            return True
        return False


class StardewModInstaller(QMainWindow):
    def __init__(self):
        super().__init__()
        self.mods_folder = None
        self.settings = QSettings("StardewModInstaller", "Config")
        self.init_ui()
        self.load_settings()
        self.load_installed_mods()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("星露谷物语 Mod 安装器")
        icon_path = resource_path("icon.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.setGeometry(100, 100, 900, 700)
        self.setMinimumSize(800, 600)

        # 设置拖放接受
        self.setAcceptDrops(True)

        # 创建中央widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局 - 垂直布局（标题和文件夹在上，下方是左右分栏）
        main_layout = QVBoxLayout(central_widget)

        # 顶部区域 - 标题和Mods文件夹位置（居中）
        top_layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("📦 星露谷物语 Mod 安装器")
        title_label.setStyleSheet(
            "font-size: 26px; font-weight: bold; padding: 15px; color: #5d4037;")
        title_label.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(title_label)

        # Mods文件夹显示区域
        folder_group = QGroupBox("Mods文件夹位置")
        folder_layout = QVBoxLayout()

        self.folder_label = QLabel("未设置Mods文件夹")
        self.folder_label.setStyleSheet(
            "padding: 8px; background-color: rgba(255, 255, 255, 0.6); border: 1px solid #8b7355; border-radius: 6px; font-weight: bold;")
        self.folder_label.setWordWrap(True)
        self.folder_label.setAlignment(Qt.AlignCenter)  # 居中对齐
        folder_layout.addWidget(self.folder_label)

        folder_btn_layout = QHBoxLayout()
        self.change_folder_btn = QPushButton("更改Mods文件夹")
        self.change_folder_btn.clicked.connect(self.change_mods_folder)
        self.open_folder_btn = QPushButton("打开Mods文件夹")
        self.open_folder_btn.clicked.connect(self.open_mods_folder)
        self.open_folder_btn.setEnabled(False)

        folder_btn_layout.addWidget(self.change_folder_btn)
        folder_btn_layout.addWidget(self.open_folder_btn)
        folder_layout.addLayout(folder_btn_layout)

        folder_group.setLayout(folder_layout)
        top_layout.addWidget(folder_group)
        
        main_layout.addLayout(top_layout)

        # 下方区域 - 左右分栏布局
        bottom_layout = QHBoxLayout()

        # 左侧布局 - 已安装Mod区域
        left_layout = QVBoxLayout()

        # 已安装Mod显示区域
        installed_mods_group = QGroupBox("已安装的Mod")
        installed_mods_layout = QVBoxLayout()

        # Mod列表显示
        self.mods_list = QListWidget()
        self.mods_list.setSelectionMode(QListWidget.ExtendedSelection)
        installed_mods_layout.addWidget(self.mods_list)

        # Mod管理按钮
        mod_management_layout = QHBoxLayout()
        
        self.refresh_mods_btn = QPushButton("刷新Mod列表")
        self.refresh_mods_btn.clicked.connect(self.refresh_installed_mods)
        
        self.delete_mods_btn = QPushButton("删除选中Mod")
        self.delete_mods_btn.setObjectName("delete_mods_btn")
        self.delete_mods_btn.clicked.connect(self.delete_selected_mods)
        
        mod_management_layout.addWidget(self.refresh_mods_btn)
        mod_management_layout.addWidget(self.delete_mods_btn)
        
        installed_mods_layout.addLayout(mod_management_layout)
        installed_mods_group.setLayout(installed_mods_layout)
        left_layout.addWidget(installed_mods_group)

        # 右侧布局 - 拖放区域和状态区域
        right_layout = QVBoxLayout()

        # 拖放区域
        drop_frame = QFrame()
        drop_frame.setObjectName("drop_frame")
        drop_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        drop_frame.setAcceptDrops(True)
        drop_frame.setMinimumHeight(150)
        drop_layout = QVBoxLayout(drop_frame)

        # 组合所有文本在一个标签中
        drop_text = QLabel("📦\n拖放Mod压缩包到这里\n支持.zip格式的Mod文件")
        drop_text.setAlignment(Qt.AlignCenter)
        drop_text.setStyleSheet("""
            QLabel {
                font-size: 15px; 
                color: #5d4037; 
                padding: 25px; 
                qproperty-wordWrap: true;
                font-weight: bold;
            }
            QLabel:hover {
                color: #8b7355;
            }
        """)
        drop_layout.addWidget(drop_text)

        # 设置拖放事件
        drop_frame.dragEnterEvent = self.drag_enter_event
        drop_frame.dropEvent = self.drop_event

        right_layout.addWidget(drop_frame)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        right_layout.addWidget(self.progress_bar)

        # 状态显示
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(180)
        self.status_text.setPlaceholderText("安装状态和日志将显示在这里...")
        right_layout.addWidget(self.status_text)

        # 按钮区域
        button_layout = QHBoxLayout()

        self.install_btn = QPushButton("手动选择Mod文件")
        self.install_btn.clicked.connect(self.manual_select_mod)
        self.install_btn.setEnabled(False)

        self.clear_btn = QPushButton("清空日志")
        self.clear_btn.clicked.connect(self.clear_status)

        self.help_btn = QPushButton("使用教程")
        self.help_btn.clicked.connect(self.show_tutorial)

        button_layout.addWidget(self.install_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addWidget(self.help_btn)

        right_layout.addLayout(button_layout)

        # 将左右布局添加到下方布局中
        bottom_layout.addLayout(left_layout)
        bottom_layout.addLayout(right_layout)

        # 将下方布局添加到主布局中
        main_layout.addLayout(bottom_layout)

        # 从外部文件加载样式
        try:
            with open("style.qss", "r", encoding="utf-8") as f:
                style = f.read()
            self.setStyleSheet(style)
        except FileNotFoundError:
            # 如果样式文件不存在，使用默认样式
            pass

    def load_settings(self):
        """加载保存的设置"""
        self.mods_folder = self.settings.value("mods_folder")

        if self.mods_folder and os.path.exists(self.mods_folder):
            self.folder_label.setText(self.mods_folder)
            self.open_folder_btn.setEnabled(True)
            self.install_btn.setEnabled(True)
        else:
            # 尝试自动查找mods文件夹
            self.auto_find_mods_folder()

    def auto_find_mods_folder(self):
        """自动查找星露谷mods文件夹"""
        possible_paths = []

        # Steam默认安装路径
        steam_paths = [
            r"C:\Program Files (x86)\Steam\steamapps\common\Stardew Valley",
            r"C:\Program Files\Steam\steamapps\common\Stardew Valley",
            r"D:\Program Files (x86)\Steam\steamapps\common\Stardew Valley",
            r"D:\Program Files\Steam\steamapps\common\Stardew Valley",
            r"E:\Program Files (x86)\Steam\steamapps\common\Stardew Valley",
            r"E:\Program Files\Steam\steamapps\common\Stardew Valley",
        ]

        for steam_path in steam_paths:
            mods_path = os.path.join(steam_path, "Mods")
            if os.path.exists(mods_path):
                possible_paths.append(mods_path)

        # 检查AppData中的mods文件夹
        appdata_path = os.path.join(
            os.getenv('APPDATA'), "StardewValley", "Mods")
        if os.path.exists(appdata_path):
            possible_paths.append(appdata_path)

        if possible_paths:
            # 使用第一个找到的路径
            self.mods_folder = possible_paths[0]
            self.folder_label.setText(f"自动检测到: {self.mods_folder}")
            self.open_folder_btn.setEnabled(True)
            self.install_btn.setEnabled(True)
            self.settings.setValue("mods_folder", self.mods_folder)
            self.add_status("✓ 自动检测到Mods文件夹")
        else:
            self.show_folder_prompt()

    def show_folder_prompt(self):
        """显示文件夹选择提示"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("未找到Mods文件夹")
        msg.setText("未能自动找到星露谷物语的Mods文件夹")
        msg.setInformativeText(
            "请手动选择您的星露谷物语Mods文件夹位置。\n\n通常位于：\nSteam/steamapps/common/Stardew Valley/Mods")

        # 添加自定义按钮
        select_btn = msg.addButton("选择文件夹", QMessageBox.ActionRole)
        msg.addButton("稍后选择", QMessageBox.RejectRole)

        msg.exec()

        if msg.clickedButton() == select_btn:
            self.change_mods_folder()

    def change_mods_folder(self):
        """更改Mods文件夹"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "选择星露谷物语Mods文件夹",
            os.path.expanduser("~"),
            QFileDialog.ShowDirsOnly
        )

        if folder:
            self.mods_folder = folder
            self.folder_label.setText(folder)
            self.open_folder_btn.setEnabled(True)
            self.install_btn.setEnabled(True)
            self.settings.setValue("mods_folder", folder)
            self.add_status("✓ Mods文件夹已设置")

    def open_mods_folder(self):
        """打开Mods文件夹"""
        if self.mods_folder and os.path.exists(self.mods_folder):
            os.startfile(self.mods_folder)

    def drag_enter_event(self, event: QDragEnterEvent):
        """拖拽进入事件"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            # 检查是否都是zip文件
            if all(url.toLocalFile().lower().endswith('.zip') for url in urls):
                event.acceptProposedAction()

    def drop_event(self, event: QDropEvent):
        """拖拽释放事件"""
        if not self.mods_folder:
            QMessageBox.warning(self, "错误", "请先设置Mods文件夹")
            return

        urls = event.mimeData().urls()
        for url in urls:
            file_path = url.toLocalFile()
            if file_path.lower().endswith('.zip'):
                self.install_mod(file_path)

    def manual_select_mod(self):
        """手动选择Mod文件"""
        if not self.mods_folder:
            QMessageBox.warning(self, "错误", "请先设置Mods文件夹")
            return

        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择Mod压缩包",
            os.path.expanduser("~"),
            "ZIP文件 (*.zip);;所有文件 (*.*)"
        )

        for file_path in files:
            self.install_mod(file_path)

    def install_mod(self, zip_path):
        """安装Mod"""
        try:
            # 检查文件是否存在
            if not os.path.exists(zip_path):
                self.add_status(f"✗ 文件不存在: {zip_path}")
                return

            # 检查是否是zip文件
            if not zipfile.is_zipfile(zip_path):
                self.add_status(f"✗ 不是有效的ZIP文件: {os.path.basename(zip_path)}")
                return

            # 创建工作线程
            self.worker = ModInstallWorker(zip_path, self.mods_folder)
            self.worker.status.connect(self.add_status)
            self.worker.finished.connect(self.on_installation_finished)

            # 显示进度条
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # 不确定进度

            # 启动线程
            self.worker.start()

        except Exception as e:
            self.add_status(f"✗ 安装失败: {str(e)}")

    def on_installation_finished(self, success, message):
        """安装完成回调"""
        self.progress_bar.setVisible(False)
        self.add_status(message)

        if success:
            success_msg = QMessageBox(self)
            success_msg.setWindowTitle("✅ 成功")
            success_msg.setText("Mod安装完成！")
            success_msg.exec()
            self.refresh_installed_mods()
        else:
            error_msg = QMessageBox(self)
            error_msg.setWindowTitle("❌ 错误")
            error_msg.setText("Mod安装失败，请检查控制台输出。")
            error_msg.exec()

    def add_status(self, message):
        """添加状态消息"""
        # 根据消息类型添加不同的颜色
        timestamp = f"[{self.get_current_time()}]"
        if "✓" in message or "成功" in message:
            # 成功消息 - 绿色
            self.status_text.setTextColor("#2e7d32")
            self.status_text.append(f"{timestamp} {message}")
        elif "✗" in message or "失败" in message or "错误" in message:
            # 错误消息 - 红色
            self.status_text.setTextColor("#c62828")
            self.status_text.append(f"{timestamp} {message}")
        elif "警告" in message or "注意" in message:
            # 警告消息 - 橙色
            self.status_text.setTextColor("#ef6c00")
            self.status_text.append(f"{timestamp} {message}")
        else:
            # 普通消息 - 默认颜色
            self.status_text.setTextColor("#333333")
            self.status_text.append(f"{timestamp} {message}")
        
        # 恢复默认颜色
        self.status_text.setTextColor("#333333")
        
        self.status_text.verticalScrollBar().setValue(
            self.status_text.verticalScrollBar().maximum()
        )

    def get_current_time(self):
        """获取当前时间字符串"""
        return datetime.now().strftime("%H:%M:%S")

    def clear_status(self):
        """清空日志"""
        self.status_text.clear()

    def refresh_installed_mods(self):
        """刷新已安装的Mod列表"""
        if not self.mods_folder or not os.path.exists(self.mods_folder):
            self.mods_list.clear()
            self.add_status("未设置Mods文件夹或文件夹不存在")
            return

        self.mods_list.clear()
        
        try:
            # 获取Mods文件夹中的所有项目
            items = os.listdir(self.mods_folder)
            
            # 过滤出文件夹（Mod通常以文件夹形式存在）
            mods = []
            for item in items:
                item_path = os.path.join(self.mods_folder, item)
                if os.path.isdir(item_path):
                    mods.append(item)
            
            # 按名称排序
            mods.sort()
            
            # 添加到列表中，显示从manifest.json中提取的信息
            for mod in mods:
                mod_path = os.path.join(self.mods_folder, mod)
                mod_info = self.get_mod_info(mod_path)
                
                mod_item = QListWidgetItem(mod_info)
                mod_item.setData(Qt.UserRole, mod_path) # 记录实际路径
                self.mods_list.addItem(mod_item)
            
            self.add_status(f"已加载 {len(mods)} 个已安装的Mod")
            
        except Exception as e:
            self.add_status(f"刷新Mod列表失败: {str(e)}")

    def get_mod_info(self, mod_path):
        """从mod文件夹的manifest.json中获取mod信息"""
        manifest_path = os.path.join(mod_path, "manifest.json")
        
        if not os.path.exists(manifest_path):
            # 如果没有manifest.json，返回文件夹名称
            folder_name = os.path.basename(mod_path)
            return f"{folder_name}"
        
        try:
            with open(manifest_path, 'r', encoding='utf-8-sig') as f:
                manifest_data = json5.load(f)
            
            # 提取基本信息
            name = manifest_data.get("Name", "未知名称")
            
            # 查找Nexus更新链接
            nexus_id = ""
            update_keys = manifest_data.get("UpdateKeys", [])
            for item in update_keys:
                if isinstance(item, str) and item.startswith("Nexus:"):
                    nexus_id = item.split(":")[-1]
                    break
            
            # 格式化显示文本
            if nexus_id:
                return f"{name} ({nexus_id})"

            return name
                
        except Exception as e:
            folder_name = os.path.basename(mod_path)
            return f"{folder_name} (解析manifest失败: {str(e)})"

    def load_installed_mods(self):
        """加载已安装的Mod（在初始化时调用）"""
        # 延迟加载，确保UI完全初始化后再加载
        QTimer.singleShot(100, self.refresh_installed_mods)

    def delete_selected_mods(self):
        """删除选中的Mod"""
        selected_items = self.mods_list.selectedItems()
        
        if not selected_items:
            QMessageBox.warning(self, "警告", "请先选择要删除的Mod")
            return

        # 获取选中的Mod显示文本
        display_texts = [item.text() for item in selected_items]
        
        # 提取实际的文件夹路径
        mod_paths = [item.data(Qt.UserRole) for item in selected_items]
        
        # 创建确认对话框
        mods_text = "\n".join([f"  - {display_text}" for display_text in display_texts])
        confirmation_msg = DELETE_CONFIRMATION.format(mods_text)
        
        msg = QMessageBox(self)
        msg.setWindowTitle("确认删除")
        msg.setText(confirmation_msg)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        
        reply = msg.exec()

        if reply == QMessageBox.Yes:
            deleted_count = 0
            failed_count = 0

            for i, mod_path in enumerate(mod_paths):
                try:
                    
                    if os.path.isdir(mod_path):
                        import shutil
                        shutil.rmtree(mod_path)
                        self.add_status(f"✓ 已删除Mod: {display_texts[i]}")
                        deleted_count += 1
                    else:
                        self.add_status(f"✗ Mod不存在: {display_texts[i]}")
                        failed_count += 1
                        
                except Exception as e:
                    self.add_status(f"✗ 删除Mod失败 {display_texts[i]}: {str(e)}")
                    failed_count += 1

            # 更新列表
            self.refresh_installed_mods()
            
            # 显示结果
            result_msg = f"删除完成！\n成功: {deleted_count} 个, 失败: {failed_count} 个"
            if failed_count == 0:
                QMessageBox.information(self, "删除完成", result_msg)
            else:
                QMessageBox.warning(self, "删除完成", result_msg)

    def show_tutorial(self):
        """显示使用教程"""
        tutorial_dialog = TutorialDialog(self)
        tutorial_dialog.exec()

    def closeEvent(self, event):
        """关闭事件"""
        # 保存设置
        if self.mods_folder:
            self.settings.setValue("mods_folder", self.mods_folder)
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("星露谷Mod安装器")
    app.setOrganizationName("StardewModInstaller")

    installer = StardewModInstaller()
    installer.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
