# CipherBreak 验证码爆破专家


CipherBreak 是一款功能强大的验证码爆破工具，专为安全测试人员设计，可以帮助您在进行安全测试时绕过验证码保护机制，自动化测试登录系统的安全性。
![image](https://github.com/user-attachments/assets/0fb59585-1ceb-41de-ae4b-0baaf26f9555)


## 功能特点

- **自动验证码识别**：集成 ddddocr 引擎，自动识别验证码
- **智能重试机制**：当检测到验证码错误时，自动重新获取验证码并重试
- **数据包解析**：自动解析 HTTP/HTTPS 请求数据包，提取参数
- **多协议支持**：支持 HTTP 和 HTTPS 协议
- **自定义字典**：支持自定义密码字典，灵活配置爆破参数
- **可视化界面**：美观直观的用户界面，实时显示爆破进度和结果
- **验证码历史**：记录所有识别过的验证码，方便分析和调试
- **自定义关键词**：可自定义成功和验证码错误的判断关键词

## 安装说明

### 系统要求

- Python 3.6 或更高版本
- macOS, Windows 或 Linux 系统

### 依赖安装

```bash
克隆仓库
git clone https://github.com/wxi3/CipherBreak.git
cd CipherBreak

安装依赖
pip install -r requirements.txt
依赖库
- PyQt5：用于构建图形界面
- requests：处理 HTTP 请求
- ddddocr：验证码识别引擎

快速开始
1. 运行主程序：python main.py
2. 在界面中粘贴登录请求和验证码请求的数据包
3. 点击"解析数据包"按钮，自动提取参数
4. 选择或输入要爆破的参数和验证码参数
5. 选择密码字典文件
6. 设置成功关键词和验证码错误关键词
7. 点击"开始爆破"按钮开始测试
```
### 数据包格式
CipherBreak 支持标准 HTTP 请求格式的数据包，例如：

```plaintext
POST /login.php HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
User-Agent: Mozilla/5.0

username=admin&password=123456&captcha=1234
 ```


### 参数说明
- 协议 ：选择 HTTP 或 HTTPS
- 字典 ：密码字典文件路径
- 爆破参数 ：要测试的参数名（如 password）
- 验证码参数 ：验证码参数名（如 captcha）
- 成功关键词 ：登录成功时响应中包含的关键词
- 验证码错误关键词 ：验证码错误时响应中包含的关键词
- 请求延迟 ：每次请求之间的延迟时间（秒）
## 高级用法
### 自定义字典
您可以创建自己的密码字典文件，每行一个密码：

```plaintext
123456
password
admin
admin123
root
 ```

### 验证码错误处理
当服务器返回验证码错误时，CipherBreak 会自动重新获取验证码并使用相同的密码重试，最多重试 3 次。这确保了即使验证码识别偶尔出错，也不会错过正确的密码。

### 关键词设置
- 成功关键词 ：多个关键词用逗号分隔，如 success,登录成功,登陆成功
- 验证码错误关键词 ：多个关键词用逗号分隔，如 验证码不正确,验证码错误,验证码已失效
## 注意事项
- 本工具仅用于安全测试和教育目的
- 未经授权对系统进行测试可能违反法律法规
- 使用本工具造成的任何后果由使用者自行承担
## 常见问题
Q: 为什么验证码识别率不高？ A: ddddocr 对标准验证码的识别率较高，但对于复杂的验证码可能效果不佳。您可以考虑集成其他验证码识别服务。

Q: 如何提高爆破效率？ A: 可以减小请求延迟，但过快的请求可能触发服务器的防护机制。

Q: 支持哪些类型的请求？ A: 目前支持标准的 GET 和 POST 请求，包括表单数据和 JSON 数据。

## 贡献指南
欢迎提交 Pull Request 或 Issue 来帮助改进 CipherBreak。

## 许可证
本项目采用 MIT 许可证。详见 LICENSE 文件。

## 联系方式
如有问题或建议，请提issue
