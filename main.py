import subprocess
import tkinter as tk
import json
import os

# 初次运行检测并创建连接
def check():
    user_pbk = os.path.join(os.environ.get('APPDATA', ''), r"Microsoft\Network\Connections\Pbk\rasphone.pbk")
    all_user_pbk = os.path.join(os.environ.get('PROGRAMDATA', ''), r"Microsoft\Network\Connections\Pbk\rasphone.pbk")
    
    connection_exists = False
    
    name_gbk = "校园网".encode('gbk')
    name_utf8 = "校园网".encode('utf-8')
    
    for pbk_path in [user_pbk, all_user_pbk]:
        if os.path.exists(pbk_path):
            with open(pbk_path, "rb") as f:
                content = f.read()
                if name_gbk in content or name_utf8 in content:
                    connection_exists = True
                    break
                    
    if not connection_exists:
        print("未检测到配置文件，正在创建连接...")
        create_cmd = [
            "powershell", 
            "-Command", 
            'Add-VpnConnection -Name "校园网" -ServerAddress "1.1.1.1" -TunnelType Pppoe -AuthenticationMethod Pap,Chap,MSChapv2'
        ]
        subprocess.run(create_cmd, capture_output=True)
    else:
        print("环境自检通过：已发现连接配置。")

# 连接函数
def connect(username, password):
    print("正在拨号...")
    command = ["rasdial", "校园网", username, password]
    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("拨号成功！")
        return True
    else:
        print("拨号失败，错误信息:", result.stdout)
        return False

# 创建主窗口
root = tk.Tk()
root.title("GDUT Wifi Connector")
root.geometry("300x250")

# 账号密码输入区
tk.Label(root, text="账号:").pack(pady=(20, 5))
user = tk.Entry(root)
user.pack()

tk.Label(root, text="密码:").pack(pady=5)
pwd = tk.Entry(root, show="*")
pwd.pack()

# 按钮点击事件
def click():
    info.config(text="正在连接...", fg="blue")
    root.update()
    
    username = user.get()
    password = pwd.get()
    success = connect(username, password)

    if success:
        info.config(text="连接成功！本软件将在3秒后关闭...", fg="green")
        save(username, password)
        root.after(3000, root.destroy)
    else: 
        info.config(text="连接失败，请检查账号密码或网络状态。", fg="red")

button = tk.Button(root, text="开始拨号", command=click)
button.pack(pady=20)

info = tk.Label(root, text="等待输入...", fg="gray")
info.pack()

# 保存配置文件
def save(username, password):
    data = {"username": username, "password": password}
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(data, f)

# 加载配置文件
def load():
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None

# 启动时自动填充与环境检测   
config = load()
if config:
    user.delete(0, tk.END)
    user.insert(0, config.get("username", ""))
    pwd.delete(0, tk.END)
    pwd.insert(0, config.get("password", ""))

    info.config(text="已读取账号，正在准备自动拨号...", fg="green")

    root.after(1000, click) 

try:
    check()
except Exception as e:
    print(f"自动创建连接失败，可能需要管理员权限: {e}")

root.mainloop()