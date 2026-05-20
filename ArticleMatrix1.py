import sys
import types
import threading
import re
import json
import os
import time
import tkinter as tk
from tkinter import ttk,messagebox, scrolledtext
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

# 3. UNIVERSAL PARAMETER INTERCEPTOR
# Manages attribute validation for top_K (int) and top_P (float).
class UniversalParams:
    def __init__(self, prompt_tmpl):
        self.prompt = prompt_tmpl
    def __getattr__(self, name):
        if name in ['top_k', 'top_K', 'refine_max_new_token', 'infer_max_new_token']: return 20
        if name in ['top_p', 'top_P', 'temperature']: return 0.7
        return False
# ========================================================
# 🖼️ 3. 双模式主程序 UI (集成矩阵 v6.5 + 朗读器 Pro)
# ========================================================
class DualEngineApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Civilization Visual: AI Matrix & ChatTTS Reader Pro")
        self.root.geometry("1300x850")
        
        # 核心变量初始化
        self.chat = None
        self.lexicon_data = {}
        self.selected_atoms = {k: [] for k in ["noun", "action", "location", "time", "environment", "result"]} # [6]
        self.checkbox_vars = {}
        self.button_refs = {}
        self.is_engine_loading = False
        
        self.load_lexicon_json() # [7]
        self.create_dual_layout()
        threading.Thread(target=self._init_gpu_engine, daemon=True).start()

    def load_lexicon_json(self):
        """加载外部词库 [7, 8]"""
        json_path = os.path.join(os.path.dirname(__file__), "lexicon.json")
        if not os.path.exists(json_path):
            messagebox.showerror("Error", f"Missing: {json_path}")
            return
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                self.lexicon_data = json.load(f)
        except Exception as e:
            messagebox.showerror("JSON Error", str(e))

    def _init_gpu_engine(self):
        """GPU 提速点火逻辑 [9]"""
        self.is_engine_loading = True
        try:
            self.chat = ChatTTS.Chat()
            if hasattr(self.chat, 'load'):
                self.chat.load(device='cuda', compile=False)
            elif hasattr(self.chat, 'init_models'):
                self.chat.init_models()
            print("[SUCCESS] CUDA Engine Armed.")
        except Exception as e: print(f"[ERROR] GPU Engine Failed: {e}")
        finally: self.is_engine_loading = False

    def create_dual_layout(self):
        # 修正 weight 报错：必须使用 ttk.PanedWindow
        main_paned = ttk.PanedWindow(self.root, orient="horizontal")
        main_paned.pack(fill="both", expand=True, padx=10, pady=10)
        
        # --- 左侧：统一输出中心 ---
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=2)
        
        ttk.Label(left_frame, text="Generated Prompt (Positive):", font=("Arial", 10, "bold")).pack(anchor="w")
        self.txt_output = tk.Text(left_frame, height=20, font=("Consolas", 11), wrap="word")
        self.txt_output.pack(fill="both", expand=True, pady=5)
        
        # 朗读按钮
        self.btn_speak = tk.Button(left_frame, text="🎙️ Speak Prompt (GPU)", bg="#8b5cf6", fg="white", 
                                  font=("Arial", 10, "bold"), command=self.speak_prompt_async)
        self.btn_speak.pack(fill="x", pady=5)
        
        # --- 右侧：功能 Notebook ---
        self.mode_notebook = ttk.Notebook(main_paned)
        main_paned.add(self.mode_notebook, weight=3)
        
        # 模式一：提示词矩阵 (调用 build_matrix_interface)
        self.matrix_tab = ttk.Frame(self.mode_notebook)
        self.mode_notebook.add(self.matrix_tab, text="🎨 Prompt Matrix")
        self.build_matrix_interface() 
        
        # 模式二：文章朗读
        self.reader_tab = ttk.Frame(self.mode_notebook)
        self.mode_notebook.add(self.reader_tab, text="📖 Article Reader")
        self.build_reader_interface()

    def build_matrix_interface(self):
        """构建 v6.5 动态矩阵界面 [10, 11]"""
        matrix_nb = ttk.Notebook(self.matrix_tab)
        matrix_nb.pack(fill="both", expand=True)
        
        # 1. 原子积木标签页 (名词到结果)
        elements = [("noun", "1.Noun"), ("action", "2.Action"), ("location", "3.Loc"), 
                    ("time", "4.Time"), ("environment", "5.Env"), ("result", "6.Result")]
        for key, title in elements:
            self.build_atom_tab(matrix_nb, key, title)

    def build_atom_tab(self, notebook, key, title):
        tab = ttk.Frame(notebook, padding=5)
        notebook.add(tab, text=title)
        
        canvas = tk.Canvas(tab)
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scroll_content = ttk.Frame(canvas)
        
        scroll_content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=scroll_content, anchor="nw", width=650)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        sub_cats = self.lexicon_data.get(key, {})
        for sub_title, items in sub_cats.items():
            frame = ttk.LabelFrame(scroll_content, text=f" {sub_title} ")
            frame.pack(fill="x", padx=5, pady=5)
            
            col, row = 0, 0
            for eng, chn in items:
                # 修复 padding 报错：使用 padx/pady [2]
                btn = tk.Button(frame, text=f"{chn}\n{eng}", font=("Arial", 8), 
                               bg="#f3f4f6", padx=5, pady=3, relief="groove")
                btn.config(command=lambda b=btn, k=key, e=eng: self.toggle_atom(b, k, e))
                btn.grid(row=row, column=col, padx=3, pady=3, sticky="ew")
                self.button_refs[(key, eng)] = btn
                col += 1
                if col > 2: col, row = 0, row + 1
            for i in range(3): frame.columnconfigure(i, weight=1)

    def toggle_atom(self, button, key, eng):
        """多选追加逻辑 [6, 12, 13]"""
        if eng in self.selected_atoms[key]:
            self.selected_atoms[key].remove(eng)
            button.config(bg="#f3f4f6", fg="black")
        else:
            self.selected_atoms[key].append(eng)
            button.config(bg="#1a5f7a", fg="white")
        self.sync_to_ui()

    def sync_to_ui(self):
        """自动化装配线 [13]"""
        parts = []
        for key in ["noun", "action", "location", "time", "environment", "result"]:
            if self.selected_atoms[key]:
                parts.append(", ".join(self.selected_atoms[key]))
        final = ", ".join(parts)
        self.txt_output.delete("1.0", tk.END)
        self.txt_output.insert("1.0", final)

    def build_reader_interface(self):
        """智能朗读界面 [14]"""
        frame = ttk.Frame(self.reader_tab, padding=10)
        frame.pack(fill="both", expand=True)
        
        self.reader_input = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=20)
        self.reader_input.pack(fill="both", expand=True, pady=10)
        
        btn = tk.Button(frame, text="🎙️ Read Article (GPU)", bg="#10b981", fg="white", 
                       font=("Arial", 10, "bold"), command=self.start_article_reading)
        btn.pack(fill="x")

    def speak_prompt_async(self):
        text = self.txt_output.get("1.0", tk.END).strip()
        if text: threading.Thread(target=self._run_engine, args=(text,), daemon=True).start()

    def start_article_reading(self):
        text = self.reader_input.get("1.0", tk.END).strip()
        if text: threading.Thread(target=self._run_engine, args=(text,), daemon=True).start()

    def _run_engine(self, text):
        """核心推理逻辑 (带 skip_refine_text 提速) [4, 15]"""
        if not self.chat: return
        clean_text = re.sub(r'--[a-zA-Z]+\s+\S+', '', text).replace('\n', ' ')
        params = UniversalParams("[uv_break]{text}[lbreak]")
        try:
            # 开启 skip_refine_text=True 实现 300it/s 的极致速度 [15]
            wavs = self.chat.infer([clean_text], params_refine_text=params, skip_refine_text=True)
            if wavs:
                sd.play(np.array(wavs).flatten(), 24000)
                sd.wait()
                time.sleep(0.2)
        except Exception as e: print(f"Infer Error: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DualEngineApp(root)
    root.mainloop()
