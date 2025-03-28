import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
import time
import random
import threading
import unicodedata
import pynput.keyboard as keyboard

class UnicodeSpamGUI:
    def __init__(self, master):
        self.keyboard = keyboard.Controller()
        self.master = master
        master.title("Unicode消息助手 v1.0")
        
        # 输入参数区域
        frame = ttk.LabelFrame(master, text="设置参数")
        frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        ttk.Label(frame, text="消息内容：").grid(row=0, column=0, sticky="w")
        self.message_entry = ttk.Entry(frame, width=40)
        self.message_entry.grid(row=0, column=1, columnspan=2, sticky="ew")
        
        ttk.Label(frame, text="发送次数：").grid(row=1, column=0, sticky="w")
        self.count_entry = ttk.Entry(frame, width=15)
        self.count_entry.grid(row=1, column=1, sticky="w")
        
        ttk.Label(frame, text="间隔时间（秒）：").grid(row=2, column=0, sticky="w")
        self.interval_entry = ttk.Entry(frame, width=15)
        self.interval_entry.grid(row=2, column=1, sticky="w")
        
        # 选项区域
        self.random_interval = tk.BooleanVar()
        ttk.Checkbutton(frame, text="随机间隔 (±20%)", variable=self.random_interval).grid(row=3, column=1, sticky="w")
        
        self.multi_message = tk.BooleanVar()
        ttk.Checkbutton(frame, text="多重消息（分号分隔）", variable=self.multi_message).grid(row=3, column=2, sticky="w")

        # 控制按钮
        btn_frame = ttk.Frame(master)
        btn_frame.grid(row=1, column=0, pady=10)
        
        self.start_btn = ttk.Button(btn_frame, text="开始发送", command=self.start_sending)
        self.start_btn.pack(side="left", padx=5)
        
        self.stop_btn = ttk.Button(btn_frame, text="停止", state="disabled", command=self.stop_sending)
        self.stop_btn.pack(side="left", padx=5)

        # 状态栏
        self.status = ttk.Label(master, text="准备就绪", relief="sunken", anchor="w")
        self.status.grid(row=2, column=0, sticky="ew", padx=10, pady=5)

        # 线程控制
        self.running = False
        self.thread = None

    def validate_input(self):
        try:
            message = self.message_entry.get().strip()
            if not message:
                raise ValueError("消息内容不能为空")
            
            # 检查Unicode字符是否可打印
            for char in message:
                if unicodedata.category(char) in ('Cc', 'Cf', 'Co', 'Cn'):  # 仅限制控制/格式/未分配字符
                    raise ValueError(f"包含不可打印字符: {char}")
                    
            count = int(self.count_entry.get())
            interval = float(self.interval_entry.get())
            if count <=0 or interval <=0:
                raise ValueError
            return True
        except ValueError as e:
            error_msg = str(e) if str(e) else "请输入有效的正整数（发送次数）和正数（间隔时间）"
            messagebox.showerror("输入错误", error_msg)
            return False

    def start_sending(self):
        if not self.validate_input():
            return
            
        self.running = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.status.config(text="运行中...")
        
        self.thread = threading.Thread(target=self.send_messages)
        self.thread.start()

    def stop_sending(self):
        self.running = False
        self.status.config(text="正在停止...")

    def send_messages(self):
        messages = self.message_entry.get().split(";") if self.multi_message.get() else [self.message_entry.get()]
        count = int(self.count_entry.get())
        base_interval = float(self.interval_entry.get())
        
        try:
            time.sleep(3)
            for i in range(count):
                if not self.running:
                    break
                
                for msg in messages:
                    # 确保Unicode字符正确发送
                    normalized_msg = unicodedata.normalize('NFC', msg.strip())
                    try:
                        for char in normalized_msg:
                            self.keyboard.type(char)
                        self.keyboard.press(keyboard.Key.enter)
                        self.keyboard.release(keyboard.Key.enter)
                    except Exception as e:
                        if 'character' in str(e):
                            pyautogui.write(normalized_msg.encode('utf-8').decode('unicode_escape'))
                        else:
                            raise
                
                interval = base_interval * random.uniform(0.8, 1.2) if self.random_interval.get() else base_interval
                time.sleep(interval)
                
                self.master.after(100, lambda: self.status.config(text=f"已发送 {i+1}/{count} 条：{msg.strip()[:10]}..."))
            
            self.master.after(100, self.on_finish)
        except Exception as e:
            self.master.after(100, lambda: messagebox.showerror("错误", str(e)))
            self.on_finish()

    def on_finish(self):
        self.running = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status.config(text=f"完成：{self.message_entry.get()[:20]}...")

if __name__ == "__main__":
    root = tk.Tk()
    app = UnicodeSpamGUI(root)
    
    # 安全提示
    messagebox.showinfo("使用提示", "请确保：\n1. 已切换到目标输入窗口\n2. 间隔时间设置合理\n3. 遵守相关平台使用规定")
    
    root.mainloop()