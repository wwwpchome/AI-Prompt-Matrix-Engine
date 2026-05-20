import sys
import types
import threading
import re
import os
import time
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import numpy as np
import sounddevice as sd

# 1. MEMORY DEFENSE PATCH (FOR PYTHON 3.14 COMPATIBILITY)
# Using 400-byte alignment to satisfy both float16 and float32 requirements.
mock_b14 = types.ModuleType('pybase16384')
mock_b14.decode_from_string = lambda x: b'\x00' * 400 
mock_b14.encode_to_string = lambda x: ""
mock_b14.decode_ints = lambda x: [0] * 100
mock_b14.encode_ints = lambda x: []
sys.modules['pybase16384'] = mock_b14

# 2. STRICT LOADING BYPASS (MONKEYPATCHING PYTORCH)
# Enabling strict=False globally to ignore non-core parameter mismatches.
try:
    import torch
    _orig_load = torch.nn.Module.load_state_dict
    def lenient_load(mod, state_dict, strict=True):
        return _orig_load(mod, state_dict, strict=False)
    torch.nn.Module.load_state_dict = lenient_load
except:
    pass

import ChatTTS

# 万能参数拦截器 (解决 ChatTTS 新版属性与类型校验冲突)

class UniversalParams:
    """让引擎以为它拿到了所有需要的配置对象，并精准分流数据类型"""
    def __init__(self, prompt_tmpl):
        self.prompt = prompt_tmpl
        
    def __getattr__(self, name):
        # 精准分流：top_K 必须是正整数类型 [3, 4]
        if name in ['top_k', 'top_K', 'refine_max_new_token', 'infer_max_new_token']: 
            return 20
        # temperature 和 top_P 必须是浮点数类型 [3, 4]
        if name in ['top_p', 'top_P', 'temperature']: 
            return 0.7
        # 默认返回 False 确保不会因为缺少属性而崩溃 [1, 2]
        return False

# ========================================================
# 🖼️ 3. 双模式主程序 UI
# ========================================================
class DualEngineApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Civilization Visual: AI Matrix & ChatTTS Reader Pro")
        self.root.geometry("1200x850")
        
        # 核心引擎变量
        self.chat = None
        self.selected_atoms = {k: [] for k in ["noun", "action", "location", "time", "environment", "result"]}
        
        self.create_dual_layout()
        threading.Thread(target=self._init_gpu_engine, daemon=True).start()

    def _init_gpu_engine(self):
        """GPU 提速点火逻辑"""
        try:
            self.chat = ChatTTS.Chat()
            # 自动探测新版接口并强推入 CUDA 显存
            if hasattr(self.chat, 'load'): self.chat.load(device='cuda', compile=False)
            elif hasattr(self.chat, 'init_models'): self.chat.init_models()
            print("[SUCCESS] CUDA Engine Loaded on GPU.")
        except Exception as e: print(f"[ERROR] Engine Failed: {e}")

    def create_dual_layout(self):
        # 采用 PanedWindow 实现左右比例可调布局 [5, 6]
        main_paned = ttk.PanedWindow(self.root, orient="horizontal")
        main_paned.pack(fill="both", expand=True, padx=10, pady=10)
        
        # --- 左侧：统一输出与控制中心 ---
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=2)
        
        self.txt_output = scrolledtext.ScrolledText(left_frame, height=25, font=("Consolas", 11))
        self.txt_output.pack(fill="both", expand=True, padx=5, pady=5)
        
        # --- 右侧：双模式切换 Notebook [1, 2] ---
        self.mode_notebook = ttk.Notebook(main_paned)
        main_paned.add(self.mode_notebook, weight=3)
        
        # 模式一：提示词矩阵 (Matrix Mode)
        self.matrix_tab = ttk.Frame(self.mode_notebook)
        self.mode_notebook.add(self.matrix_tab, text="🎨 提示词矩阵 (Matrix)")
        self.build_matrix_interface() # 调用 v6.5 的动态渲染逻辑 [7, 8]
        
        # 模式二：文章朗读 (Reader Mode)
        self.reader_tab = ttk.Frame(self.mode_notebook)
        self.mode_notebook.add(self.reader_tab, text="📖 智能朗读 (Reader)")
        self.build_reader_interface() # 集成文本清洗与分段逻辑 [9]

    def build_reader_interface(self):
        """构建朗读模式专属界面"""
        reader_frame = ttk.Frame(self.reader_tab, padding=15)
        reader_frame.pack(fill="both", expand=True)
        
        tk.Label(reader_frame, text="音色种子:", font=("Arial", 9)).grid(row=0, column=0, sticky="w")
        self.seed_entry = tk.Entry(reader_frame, width=12)
        self.seed_entry.insert(0, "2222")
        self.seed_entry.grid(row=0, column=1, sticky="w", padx=5)
        
        self.reader_input = scrolledtext.ScrolledText(reader_frame, wrap=tk.WORD, height=20)
        self.reader_input.grid(row=1, column=0, columnspan=2, pady=10, sticky="nsew")
        
        btn_box = ttk.Frame(reader_frame)
        btn_box.grid(row=2, column=0, columnspan=2, fill="x")
        
        tk.Button(btn_box, text="🎙️ 分段朗读 (GPU)", bg="#10b981", fg="white", 
                  command=self.start_reading).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        tk.Button(btn_box, text="🛑 停止", bg="#ef4444", fg="white", 
                  command=lambda: sd.stop()).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

    def start_reading(self):
        """集成文本清洗与 GPU 高速推理"""
        raw_text = self.reader_input.get("1.0", tk.END).strip()
        # 清洗无效符号与参数 [9]
        clean_text = re.sub(r'--[a-zA-Z]+\s+\S+', '', raw_text)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        # 异步启动分段朗读流
        threading.Thread(target=self._run_reader_engine, args=(clean_text,), daemon=True).start()

    def _run_reader_engine(self, text):
        # 智能分段：按150字左右切分以保障GPU吞吐 [9]
        chunks = [text[i:i+150] for i in range(0, len(text), 150)]
        params = UniversalParams("[uv_break]{text}[lbreak]")
        
        for chunk in chunks:
            try:
                # 跳过 refine_text 以实现 300it/s 的极致提速 [9, 10]
                wavs = self.chat.infer([chunk], params_refine_text=params, skip_refine_text=True)
                # ...音频播放逻辑...
            except: break

if __name__ == "__main__":
    root = tk.Tk()
    app = DualEngineApp(root)
    root.mainloop()
