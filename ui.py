import os
import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QTextEdit, QLabel, QPushButton, QComboBox, 
                            QFileDialog, QMessageBox, QProgressBar, 
                            QListWidget, QListWidgetItem, QSplitter, QFrame,
                            QGroupBox, QTabWidget, QApplication, QStyleFactory)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, pyqtSlot, QObject, QMetaObject, Q_ARG
from PyQt5.QtGui import QPixmap, QFont, QColor, QPalette, QIcon

from utils import extract_params
from cracker import Cracker

class LoginCrackerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.cracker = None
        
        # 禁用SSL警告
        import requests
        requests.packages.urllib3.disable_warnings()
        
        # 添加右键菜单功能
        self.setup_context_menus()
        
    def initUI(self):
        self.setWindowTitle('CipherBreak')
        self.setGeometry(100, 100, 1200, 800)  # 增大窗口尺寸
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2D2D30;
                color: #FFFFFF;
            }
            QWidget {
                background-color: #2D2D30;
                color: #FFFFFF;
            }
            QLabel {
                color: #FFFFFF;
                font-size: 13px;
            }
            QPushButton {
                background-color: #0078D7;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1C97EA;
            }
            QPushButton:pressed {
                background-color: #00559B;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
            QTextEdit, QListWidget {
                background-color: #1E1E1E;
                color: #DCDCDC;
                border: 1px solid #3F3F46;
                border-radius: 3px;
                font-family: Consolas, Monaco, monospace;
            }
            QComboBox {
                background-color: #333337;
                color: white;
                border: 1px solid #3F3F46;
                border-radius: 3px;
                padding: 3px 5px;
            }
            QComboBox:editable {
                background-color: #252526;
            }
            QComboBox QAbstractItemView {
                background-color: #252526;
                color: white;
                selection-background-color: #3F3F46;
            }
            QProgressBar {
                border: 1px solid #3F3F46;
                border-radius: 3px;
                background-color: #1E1E1E;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #0078D7;
                width: 10px;
            }
            QGroupBox {
                border: 1px solid #3F3F46;
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
                color: #FFFFFF;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                padding: 0 5px;
            }
            QTabWidget::pane {
                border: 1px solid #3F3F46;
                border-radius: 3px;
            }
            QTabBar::tab {
                background-color: #2D2D30;
                color: #FFFFFF;
                padding: 8px 15px;
                border-top-left-radius: 3px;
                border-top-right-radius: 3px;
            }
            QTabBar::tab:selected {
                background-color: #0078D7;
            }
            QTabBar::tab:hover:!selected {
                background-color: #3F3F46;
            }
            QSplitter::handle {
                background-color: #3F3F46;
            }
        """)
        
        # 主布局
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)  # 适当增加边距
        main_layout.setSpacing(10)
        
        # 添加标题 - 移除Logo相关代码，只保留标题
        header_layout = QHBoxLayout()
        
        # 标题标签
        title_label = QLabel("CipherBreak")
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #0078D7;
            padding: 5px 0;
        """)
        
        # 添加到头部布局
        header_layout.addWidget(title_label)
        header_layout.addStretch(1)  # 右侧留白
        
        # 添加头部到主布局
        main_layout.addLayout(header_layout)
        
        # 创建控制面板组
        control_group = QGroupBox("控制面板")
        control_layout = QVBoxLayout()
        
        # 上部控制区域 - 分为两行
        top_control_layout = QHBoxLayout()
        bottom_control_layout = QHBoxLayout()
        
        # 第一行控制区域
        # 协议选择
        protocol_layout = QHBoxLayout()
        self.protocol_label = QLabel('协议:')
        self.protocol_label.setFixedWidth(60)  # 固定标签宽度
        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems(['HTTP', 'HTTPS'])
        self.protocol_combo.setCurrentText('HTTP')
        self.protocol_combo.setFixedWidth(80)  # 设置协议下拉框更短
        protocol_layout.addWidget(self.protocol_label)
        protocol_layout.addWidget(self.protocol_combo)
        
        # 字典选择
        dict_layout = QHBoxLayout()
        self.dict_label = QLabel('字典:')
        self.dict_label.setFixedWidth(60)  # 固定标签宽度
        self.dict_combo = QComboBox()
        self.dict_combo.setEditable(True)
        self.dict_combo.setMinimumWidth(300)  # 增加字典下拉框的最小宽度
        self.browse_btn = QPushButton('浏览...')
        self.browse_btn.clicked.connect(self.browse_dictionary)
        dict_layout.addWidget(self.dict_label)
        dict_layout.addWidget(self.dict_combo)
        dict_layout.addWidget(self.browse_btn)
        
        # 参数设置
        param_layout = QHBoxLayout()
        self.target_label = QLabel('爆破参数:')
        self.target_label.setFixedWidth(80)  # 固定标签宽度
        self.target_param = QComboBox()
        self.target_param.setEditable(True)
        self.captcha_label = QLabel('验证码参数:')
        self.captcha_label.setFixedWidth(90)  # 固定标签宽度
        self.captcha_param = QComboBox()
        self.captcha_param.setEditable(True)
        param_layout.addWidget(self.target_label)
        param_layout.addWidget(self.target_param)
        param_layout.addWidget(self.captcha_label)
        param_layout.addWidget(self.captcha_param)
        
        # 添加到第一行
        top_control_layout.addLayout(protocol_layout)
        top_control_layout.addLayout(dict_layout)
        top_control_layout.addLayout(param_layout)
        
        # 第二行控制区域
        # 成功关键词设置
        success_layout = QHBoxLayout()
        self.success_label = QLabel('成功关键词:')
        self.success_label.setFixedWidth(90)  # 固定标签宽度
        self.success_keywords = QComboBox()
        self.success_keywords.setEditable(True)
        self.success_keywords.addItems(["success", "登录成功", "登陆成功"])
        success_layout.addWidget(self.success_label)
        success_layout.addWidget(self.success_keywords)
        
        # 验证码错误关键词设置
        captcha_error_layout = QHBoxLayout()
        self.captcha_error_label = QLabel('验证码错误关键词:')
        self.captcha_error_label.setFixedWidth(120)  # 固定标签宽度
        self.captcha_error_keywords = QComboBox()
        self.captcha_error_keywords.setEditable(True)
        self.captcha_error_keywords.addItems(["验证码不正确", "验证码错误", "验证码已失效"])
        captcha_error_layout.addWidget(self.captcha_error_label)
        captcha_error_layout.addWidget(self.captcha_error_keywords)
        
        # 延迟设置
        delay_layout = QHBoxLayout()
        self.delay_label = QLabel('请求延迟(秒):')
        self.delay_label.setFixedWidth(90)  # 固定标签宽度
        self.delay_combo = QComboBox()
        self.delay_combo.setEditable(True)
        self.delay_combo.addItems(["0", "0.5", "1", "2", "3", "5"])
        self.delay_combo.setCurrentText("1")
        delay_layout.addWidget(self.delay_label)
        delay_layout.addWidget(self.delay_combo)
        
        # 控制按钮
        button_layout = QHBoxLayout()
        self.parse_btn = QPushButton('解析数据包')
        self.parse_btn.setIcon(QIcon.fromTheme("document-properties"))
        self.parse_btn.clicked.connect(self.parse_packets)
        self.parse_btn.setFixedWidth(120)  # 固定按钮宽度
        
        self.start_btn = QPushButton('开始爆破')
        self.start_btn.setIcon(QIcon.fromTheme("media-playback-start"))
        self.start_btn.clicked.connect(self.start_cracking)
        self.start_btn.setFixedWidth(120)  # 固定按钮宽度
        
        self.stop_btn = QPushButton('停止')
        self.stop_btn.setIcon(QIcon.fromTheme("media-playback-stop"))
        self.stop_btn.clicked.connect(self.stop_cracking)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setFixedWidth(120)  # 固定按钮宽度
        
        # 修改按钮布局，添加弹性空间使按钮靠右对齐
        button_layout.addStretch(1)  # 添加弹性空间使按钮靠右对齐
        button_layout.addWidget(self.parse_btn)
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        
        # 添加到第二行
        bottom_control_layout.addLayout(success_layout)
        bottom_control_layout.addLayout(captcha_error_layout)
        bottom_control_layout.addLayout(delay_layout)
        bottom_control_layout.addLayout(button_layout)
        
        # 添加两行到控制布局
        control_layout.addLayout(top_control_layout)
        control_layout.addLayout(bottom_control_layout)
        control_group.setLayout(control_layout)
        
        # 添加控制组到主布局
        main_layout.addWidget(control_group)
        
        # 创建数据包区域
        data_group = QGroupBox("请求数据包")
        data_tab = QTabWidget()
        
        # 登录数据包
        login_widget = QWidget()
        login_layout = QVBoxLayout()
        self.login_text = QTextEdit()
        self.login_text.setPlaceholderText('在此粘贴登录请求的完整数据包...')
        login_layout.addWidget(self.login_text)
        login_widget.setLayout(login_layout)
        
        # 验证码数据包
        captcha_widget = QWidget()
        captcha_layout = QVBoxLayout()
        self.captcha_text = QTextEdit()
        self.captcha_text.setPlaceholderText('在此粘贴获取验证码的请求数据包...')
        captcha_layout.addWidget(self.captcha_text)
        captcha_widget.setLayout(captcha_layout)
        
        # 添加到选项卡
        data_tab.addTab(login_widget, "登录数据包")
        data_tab.addTab(captcha_widget, "验证码数据包")
        
        data_layout = QVBoxLayout()
        data_layout.addWidget(data_tab)
        data_group.setLayout(data_layout)
        
        # 添加数据包组到主布局
        main_layout.addWidget(data_group)
        
        # 创建底部区域 - 使用分割器
        bottom_splitter = QSplitter(Qt.Horizontal)
        
        # 日志区域
        log_group = QGroupBox("爆破日志")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        # 进度条
        self.progress_bar = QProgressBar()
        log_layout.addWidget(self.progress_bar)
        log_group.setLayout(log_layout)
        
        # 验证码显示区域
        captcha_group = QGroupBox("验证码历史")
        captcha_display_layout = QVBoxLayout()
        
        # 验证码历史列表
        self.captcha_list = QListWidget()
        self.captcha_list.setSpacing(2)
        captcha_display_layout.addWidget(self.captcha_list)
        captcha_group.setLayout(captcha_display_layout)
        
        # 添加到分割器
        bottom_splitter.addWidget(log_group)
        bottom_splitter.addWidget(captcha_group)
        bottom_splitter.setStretchFactor(0, 7)  # 日志区域占70%
        bottom_splitter.setStretchFactor(1, 3)  # 验证码区域占30%
        
        # 添加分割器到主布局
        main_layout.addWidget(bottom_splitter, 1)  # 底部区域可伸展
        
        # 设置主布局
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # 添加一些默认字典
        default_dicts = [
            "./dicts/passwords.txt",
            "./dicts/common_passwords.txt"
        ]
        self.dict_combo.addItems(default_dicts)
        
        # 添加一些常见参数名
        common_params = ["username", "password", "user", "pass", "pwd", "login", "captcha", "code", "verifyCode"]
        self.target_param.addItems(common_params)
        self.captcha_param.addItems(["captcha", "code", "verifyCode", "validateCode"])
        
        # 显示欢迎信息
        self.log("欢迎使用 CipherBreak 验证码爆破专家 v1.0")
        self.log("请粘贴登录和验证码数据包，然后点击'解析数据包'按钮")

    def browse_dictionary(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择字典文件", "", "文本文件 (*.txt);;所有文件 (*)")
        if file_path:
            self.dict_combo.setCurrentText(file_path)
    
    def log(self, message):
        self.log_text.append(message)
        # 滚动到底部
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())
    
    def parse_packets(self):
        """解析数据包并自动填充参数下拉框"""
        login_data = self.login_text.toPlainText().strip()
        captcha_data = self.captcha_text.toPlainText().strip()
        
        if login_data:
            login_params = extract_params(login_data)
            self.target_param.clear()
            self.target_param.addItems(login_params)
            self.log("已解析登录数据包参数")
        
        if captcha_data:
            captcha_params = extract_params(login_data)
            self.captcha_param.clear()
            self.captcha_param.addItems(captcha_params)
            self.log("已解析验证码数据包参数")
    
    def start_cracking(self):
        login_data = self.login_text.toPlainText().strip()
        captcha_data = self.captcha_text.toPlainText().strip()
        dictionary_path = self.dict_combo.currentText()
        target_param = self.target_param.currentText()
        captcha_param = self.captcha_param.currentText()
        success_keywords = self.success_keywords.currentText()
        captcha_error_keywords = self.captcha_error_keywords.currentText()  # 获取验证码错误关键词
        
        # 获取延迟设置
        try:
            delay = float(self.delay_combo.currentText())
        except ValueError:
            delay = 1.0  # 默认1秒
        
        # 验证输入
        if not login_data:
            QMessageBox.warning(self, "警告", "请输入登录数据包")
            return
        
        if not captcha_data:
            QMessageBox.warning(self, "警告", "请输入验证码数据包")
            return
        
        if not os.path.exists(dictionary_path):
            # 尝试创建默认字典文件
            try:
                os.makedirs(os.path.dirname(dictionary_path), exist_ok=True)
                with open(dictionary_path, 'w', encoding='utf-8') as f:
                    f.write("123456\npassword\nadmin\nadmin123\n12345678")
                self.log(f"已创建默认字典文件: {dictionary_path}")
            except Exception as e:
                QMessageBox.warning(self, "警告", f"字典文件不存在且无法创建: {e}")
                return
        
        if not target_param:
            QMessageBox.warning(self, "警告", "请指定要爆破的参数名")
            return
        
        if not captcha_param:
            QMessageBox.warning(self, "警告", "请指定验证码参数名")
            return
        
        # 更新UI状态
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        self.log(f"开始爆破... 延迟: {delay}秒")
        
        # 修改验证码回调，使用信号槽机制在主线程中更新UI
        from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QMetaObject, Qt
        
        class CaptchaSignalHandler(QObject):
            captcha_signal = pyqtSignal(object, str)
            
        self.captcha_handler = CaptchaSignalHandler()
        self.captcha_handler.captcha_signal.connect(self.add_captcha_to_history)
        
        def handle_captcha(img, text):
            # 通过信号发送数据到主线程
            self.captcha_handler.captcha_signal.emit(img, text)
        
        # 获取选择的协议
        protocol = self.protocol_combo.currentText().lower()
        
        # 创建并启动爆破
        import threading
        self.cracker = Cracker(
            login_data, captcha_data, target_param, captcha_param, dictionary_path, success_keywords,
            protocol=protocol,  # 传递协议参数
            delay=delay,  # 传递延迟参数
            captcha_error_keywords=captcha_error_keywords,  # 传递验证码错误关键词
            update_callback=lambda msg: QMetaObject.invokeMethod(self, "log", Qt.QueuedConnection, 
                                                               Q_ARG(str, msg)),
            progress_callback=lambda val: QMetaObject.invokeMethod(self.progress_bar, "setValue", 
                                                                 Qt.QueuedConnection, Q_ARG(int, val)),
            finished_callback=lambda msg: QMetaObject.invokeMethod(self, "cracking_finished", 
                                                                 Qt.QueuedConnection, Q_ARG(str, msg)),
            captcha_callback=handle_captcha
        )
        
        # 使用线程运行爆破过程，避免UI卡死
        self.cracker_thread = threading.Thread(target=self.cracker.start)
        self.cracker_thread.daemon = True
        self.cracker_thread.start()
    
    def stop_cracking(self):
        """停止爆破过程"""
        if self.cracker:
            self.cracker.stop()
            self.log("正在停止爆破...")
            # 更新UI状态
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
    
    # 将log方法标记为槽，以便可以从其他线程调用
    @pyqtSlot(str)
    def log(self, message):
        self.log_text.append(message)
        # 滚动到底部
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())
    
    # 将cracking_finished方法标记为槽
    @pyqtSlot(str)
    def cracking_finished(self, message):
        self.log(message)
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setValue(100)

    # 将add_captcha_to_history方法标记为槽
    @pyqtSlot(object, str)
    def add_captcha_to_history(self, image_data, text):
        """添加验证码到历史记录"""
        # 创建新的列表项
        item = QListWidgetItem()
        item.setSizeHint(QSize(280, 50))  # 调整项目大小
        
        # 创建容器widget
        widget = QWidget()
        layout = QHBoxLayout()  # 使用水平布局
        layout.setContentsMargins(5, 5, 5, 5)  # 设置边距
        
        # 创建图片标签
        image_label = QLabel()
        image_label.setFixedSize(120, 40)  # 调整图片大小
        image_label.setAlignment(Qt.AlignCenter)
        image_label.setStyleSheet("border: 1px solid #444; background-color: #222;")
        
        # 将图片数据转换为QPixmap并显示
        pixmap = QPixmap()
        pixmap.loadFromData(image_data)
        image_label.setPixmap(pixmap.scaled(120, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        # 创建文本标签
        text_label = QLabel(text)  # 只显示识别结果
        text_label.setAlignment(Qt.AlignCenter)  # 居中对齐
        text_label.setStyleSheet("color: white; font-size: 14px;")
        text_label.setContentsMargins(10, 0, 0, 0)  # 添加左边距
        
        # 添加到布局
        layout.addWidget(image_label)
        layout.addWidget(text_label, 1)  # 文本标签占用剩余空间
        
        # 设置widget的布局
        widget.setLayout(layout)
        widget.setStyleSheet("background-color: #333333;")
        
        # 将widget添加到列表项
        self.captcha_list.insertItem(0, item)  # 在开头插入
        self.captcha_list.setItemWidget(item, widget)
        
    def closeEvent(self, event):
        """程序关闭时的处理"""
        if self.cracker and self.cracker.is_running:
            self.cracker.stop()
        event.accept()


    def setup_context_menus(self):
        """设置右键菜单"""
        from PyQt5.QtWidgets import QMenu, QAction
        
        # 为日志文本框添加右键菜单
        self.log_text.setContextMenuPolicy(Qt.CustomContextMenu)
        self.log_text.customContextMenuRequested.connect(self.show_log_context_menu)
        
        # 为验证码历史列表添加右键菜单
        self.captcha_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.captcha_list.customContextMenuRequested.connect(self.show_captcha_context_menu)
    
    def show_log_context_menu(self, position):
        """显示日志的右键菜单"""
        from PyQt5.QtWidgets import QMenu, QAction
        
        menu = QMenu()
        clear_action = QAction("清空日志", self)
        clear_action.triggered.connect(self.clear_log)
        menu.addAction(clear_action)
        
        # 在鼠标位置显示菜单
        menu.exec_(self.log_text.mapToGlobal(position))
    
    def show_captcha_context_menu(self, position):
        """显示验证码历史的右键菜单"""
        from PyQt5.QtWidgets import QMenu, QAction
        
        menu = QMenu()
        clear_action = QAction("清空验证码历史", self)
        clear_action.triggered.connect(self.clear_captcha_history)
        menu.addAction(clear_action)
        
        # 在鼠标位置显示菜单
        menu.exec_(self.captcha_list.mapToGlobal(position))
    
    def clear_log(self):
        """清空日志"""
        self.log_text.clear()
        self.log("日志已清空")
    
    def clear_captcha_history(self):
        """清空验证码历史"""
        self.captcha_list.clear()
        self.log("验证码历史已清空")
