import tkinter as tk
from tkinter import filedialog, messagebox
import json
from pathlib import Path
import shutil
import concurrent.futures

CONFIG_FILE = "search_config.json"

def search_key_value(data, key, value) -> bool:
    if isinstance(data, dict):
        if key in data and str(data[key]) == value:
            return True
        return any(search_key_value(v, key, value) for v in data.values())
    elif isinstance(data, list):
        return any(search_key_value(item, key, value) for item in data)
    return False

def search_in_json(json_path: Path, key: str, value: str) -> bool:
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return search_key_value(data, key, value)
    except Exception:
        return False

def is_matching_dir(subdir: Path, key: str, value: str, filename: str) -> str | None:
    json_file = subdir / filename
    if json_file.is_file():
        if search_in_json(json_file, key, value):
            return str(subdir.resolve())
    return None

def find_matching_dirs(root_dir: Path, key: str, value: str, filename: str):
    matched_dirs = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for subdir in root_dir.iterdir():
            if subdir.is_dir():
                futures.append(executor.submit(is_matching_dir, subdir, key, value, filename))

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
    root_dir = Path(root_dir_var.get())
    key = key_entry.get()
    value = value_entry.get()
    filename = filename_entry.get()

    if not root_dir.is_dir():
        messagebox.showerror("エラー", "有効なディレクトリを選んでください。")
        return
    if not filename:
        messagebox.showerror("エラー", "JSONファイル名を入力してください。")
        return

    matched = find_matching_dirs(root_dir, key, value, filename)

    result_list.delete(0, tk.END)
    for d in matched:
        result_list.insert(tk.END, d)

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

def save_state():
    state = {
        "root_dir": root_dir_var.get(),
        "key": key_entry.get(),
        "value": value_entry.get(),
        "filename": filename_entry.get()
    }
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("状態の保存に失敗:", e)

def load_state():
    if Path(CONFIG_FILE).exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                state = json.load(f)
                root_dir_var.set(state.get("root_dir", ""))
                key_entry.insert(0, state.get("key", ""))
                value_entry.insert(0, state.get("value", ""))
                filename_entry.insert(0, state.get("filename", "config.json"))
        except Exception as e:
            print("状態の読み込みに失敗:", e)

# GUI構築
root = tk.Tk()
root.title("JSONディレクトリ検索ツール")

root.protocol("WM_DELETE_WINDOW", lambda: (save_state(), root.destroy()))

root_dir_var = tk.StringVar()

# 入力フィールド
frame_input = tk.Frame(root)
frame_input.pack(padx=10, pady=5, fill="x")

tk.Label(frame_input, text="ディレクトリ:").pack(side="left")
tk.Entry(frame_input, textvariable=root_dir_var, width=40).pack(side="left", padx=5)
tk.Button(frame_input, text="参照", command=choose_directory).pack(side="left")

frame_search = tk.Frame(root)
frame_search.pack(padx=10, pady=5, fill="x")

tk.Label(frame_search, text="ファイル名:").pack(side="left")
filename_entry = tk.Entry(frame_search, width=20)
filename_entry.pack(side="left", padx=5)

tk.Label(frame_search, text="キー:").pack(side="left")
key_entry = tk.Entry(frame_search, width=15)
key_entry.pack(side="left", padx=5)

tk.Label(frame_search, text="値:").pack(side="left")
value_entry = tk.Entry(frame_search, width=15)
value_entry.pack(side="left", padx=5)

tk.Button(frame_search, text="検索", command=run_search).pack(side="left", padx=10)

# 結果表示
frame_result = tk.Frame(root)
frame_result.pack(padx=10, pady=10, fill="both", expand=True)

tk.Label(frame_result, text="一致したディレクトリ:").pack(anchor="w")
result_list = tk.Listbox(frame_result, height=10, selectmode="extended")
result_list.pack(fill="both", expand=True)

# 削除ボタン
frame_delete = tk.Frame(root)
frame_delete.pack(padx=10, pady=5, fill="x")

tk.Button(frame_delete, text="選択したディレクトリを削除", command=delete_selected_dirs).pack(side="right")

# 初期化
load_state()
root.mainloop()
