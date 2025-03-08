import os
import re
import json
import logging
import urllib.parse
from datetime import datetime

# 设置日志记录
def setup_logging():
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"cracker_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger("LoginCracker")
    return logger

# 从数据包中提取参数名
def extract_params(text):
    params = []
    # 尝试查找JSON格式的参数
    json_match = re.search(r'{.*}', text, re.DOTALL)
    if json_match:
        try:
            json_data = json.loads(json_match.group(0))
            params.extend(json_data.keys())
        except:
            pass
    
    # 尝试查找表单格式的参数
    form_matches = re.findall(r'([^&=\s]+)=([^&\s]*)', text)
    for key, _ in form_matches:
        if key not in params:
            params.append(key)
    
    return params