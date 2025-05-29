import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json
from pathlib import Path
import shutil
import glob
import concurrent.futures
import re
from typing import Optional, Tuple
import os

CONFIG_FILE = "search_config.json"
HISTORY_FILE = "input_history.json"

# --- キャッシュと履歴 ---
json_cache: dict[str, Tuple[float, dict, str]] = {}  # { path: (mtime, json_dict, json_text) }
history_data = {"root_dir": [], "filename": [], "key": [], "value": []}

# --- ユーティリティ ---
def match_with_wildcard(target: str, pattern: str) -> bool:
    if not pattern:
        return True
    regex = re.escape(pattern).replace(r"\*", ".*")
    return re.search(regex, str(target)) is not None

def search_key_value(data, key_pattern: str, value_pattern: str) -> bool:
    if isinstance(data, dict):
        for k, v in data.items():
            if match_with_wildcard(k, key_pattern) and match_with_wildcard(v, value_pattern):
                return True
            if search_key_value(v, key_pattern, value_pattern):
                return True
    elif isinstance(data, list):
        return any(search_key_value(item, key_pattern, value_pattern) for item in data)
    return False

def load_json_with_cache(json_path: Path) -> Optional[Tuple[dict, str]]:
    if not json_path.exists():
        return None
    try:
        stat = json_path.stat()
        mtime = stat.st_mtime
        path_str = str(json_path)

        if path_str in json_cache:
            cached_mtime, cached_data, cached_text = json_cache[path_str]
            if cached_mtime == mtime:
                return cached_data, cached_text

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        json_text = json.dumps(data, ensure_ascii=False)
        json_cache[path_str] = (mtime, data, json_text)
        return data, json_text
    except Exception:
        return None

def search_in_json(json_path: Path, key_pattern: str, value_pattern: str) -> bool:
    if not key_pattern and not value_pattern:
        return False  # 空条件なら検索不要

    result = load_json_with_cache(json_path)
    if not result:
        return False

    data, json_text = result

    if not key_pattern and value_pattern:
        return match_with_wildcard(json_text, value_pattern)

    return search_key_value(data, key_pattern, value_pattern)

def is_matching_dir(subdir: Path, key: str, value: str, filename: str) -> Optional[str]:
    json_file = subdir / filename
    if json_file.is_file():
        if search_in_json(json_file, key, value):
            return str(subdir.resolve())
    return None

def find_matching_dirs(root_pattern: str, key: str, value: str, filename: str):
    matched_dirs = []
    candidate_dirs = [Path(p) for p in glob.glob(root_pattern) if Path(p).is_dir()]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(is_matching_dir, subdir, key, value, filename) for subdir in candidate_dirs]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                matched_dirs.append(result)

    return matched_dirs

def choose_directory():
    dir_path = filedialog.askdirectory()
    if dir_path:
        root_dir_var.set(dir_path)

def run_search():
    root_pattern = root_dir_var.get().strip()
    key = key_entry.get().strip()
    value = value_entry.get().strip()
    filename = filename_entry.get().strip()

    if not root_pattern:
        messagebox.showerror("エラー", "ディレクトリパターンを入力してください。")
        return
    if not filename:
        messagebox.showerror("エラー", "JSONファイル名を入力してください。")
        return

    update_history("root_dir", root_pattern, root_dir_entry)
    update_history("filename", filename, filename_entry)
    update_history("key", key, key_entry)
    update_history("value", value, value_entry)

    result_label_var.set("検索中...")
    root.update_idletasks()

    matched = find_matching_dirs(root_pattern, key, value, filename)
    result_list.delete(0, tk.END)
    for d in matched:
        result_list.insert(tk.END, d)

    result_label_var.set(f"一致したディレクトリ: {len(matched)} 件")

def delete_selected_dirs():
    selected = result_list.curselection()
    if not selected:
        messagebox.showinfo("情報", "削除するディレクトリを選択してください。")
        return

    selected_dirs = [result_list.get(i) for i in selected]
    confirm_text = "以下のディレクトリを削除します。よろしいですか？\n\n" + "\n".join(selected_dirs)
    if messagebox.askokcancel("削除確認", confirm_text):
        for d in selected_dirs:
            try:
                shutil.rmtree(d)
            except Exception as e:
                messagebox.showerror("削除エラー", f"{d} の削除に失敗しました: {e}")
        run_search()

def load_state():
    if Path(CONFIG_FILE).exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                state = json.load(f)
                root_dir_var.set(state.get("root_dir", ""))
                filename_entry.set(state.get("filename", "config.json"))
                key_entry.set(state.get("key", ""))
                value_entry.set(state.get("value", ""))
        except Exception:
            pass

def save_state():
    state = {
        "root_dir": root_dir_var.get(),
        "filename": filename_entry.get(),
        "key": key_entry.get(),
        "value": value_entry.get()
    }
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def load_history():
    global history_data
    if Path(HISTORY_FILE).exists():
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
        except Exception:
            pass

def save_history():
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def update_history(key: str, value: str, combobox: ttk.Combobox):
    if value and value not in history_data[key]:
        history_data[key].insert(0, value)
        history_data[key] = history_data[key][:10]
        combobox["values"] = history_data[key]
        save_history()

# --- GUI構築 ---
root = tk.Tk()
root.title("JSONディレクトリ検索ツール")
root.geometry("800x500")

root_dir_var = tk.StringVar()
result_label_var = tk.StringVar(value="一致したディレクトリ:")

load_history()

frame_input = tk.Frame(root)
frame_input.pack(padx=10, pady=5, fill="x")

frame_search = tk.Frame(root)
frame_search.pack(padx=10, pady=5, fill="x")

frame_result = tk.Frame(root)
frame_result.pack(padx=10, pady=10, fill="both", expand=True)

frame_delete = tk.Frame(root)
frame_delete.pack(padx=10, pady=5, fill="x")

tk.Label(frame_input, text="ディレクトリ（ワイルドカード可）:").pack(side="left")
root_dir_entry = ttk.Combobox(frame_input, textvariable=root_dir_var, values=history_data["root_dir"])
root_dir_entry.pack(side="left", fill="x", expand=True, padx=5)
tk.Button(frame_input, text="参照", command=choose_directory).pack(side="left")

tk.Label(frame_search, text="ファイル名:").pack(side="left")
filename_entry = ttk.Combobox(frame_search, values=history_data["filename"])
filename_entry.pack(side="left", fill="x", expand=True, padx=5)

tk.Label(frame_search, text="キー:").pack(side="left")
key_entry = ttk.Combobox(frame_search, values=history_data["key"])
key_entry.pack(side="left", fill="x", expand=True, padx=5)

tk.Label(frame_search, text="値:").pack(side="left")
value_entry = ttk.Combobox(frame_search, values=history_data["value"])
value_entry.pack(side="left", fill="x", expand=True, padx=5)

tk.Button(frame_search, text="検索", command=run_search).pack(side="left", padx=10)

tk.Label(frame_result, textvariable=result_label_var).pack(anchor="w")

result_frame = tk.Frame(frame_result)
result_frame.pack(fill="both", expand=True)

result_scrollbar = tk.Scrollbar(result_frame, orient="vertical")
result_list = tk.Listbox(result_frame, height=15, selectmode="extended", yscrollcommand=result_scrollbar.set)
result_scrollbar.config(command=result_list.yview)

result_list.pack(side="left", fill="both", expand=True)
result_scrollbar.pack(side="right", fill="y")

tk.Button(frame_delete, text="選択したディレクトリを削除", command=delete_selected_dirs).pack(side="right")

def on_close():
    save_state()
    save_history()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)
load_state()
root.mainloop()
