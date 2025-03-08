import sys
import requests
from PyQt5.QtWidgets import QApplication
from ui import LoginCrackerApp
from utils import setup_logging

if __name__ == "__main__":
    # 设置日志
    logger = setup_logging()
    
    # 禁用SSL警告
    requests.packages.urllib3.disable_warnings()
    
    # 创建应用
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # 使用Fusion风格，在所有平台上看起来一致
    
    # 创建主窗口
    window = LoginCrackerApp()
    window.show()
    
    # 运行应用
    sys.exit(app.exec_())