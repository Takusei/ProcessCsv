import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from tkcalendar import Calendar
import pandas as pd

selected_date = None  # グローバル変数として選択した日付を保存
selected_entry_file = None
selected_other_files = None

def center_window(window):
    # ウィンドウサイズを定義
    width = 800
    height = 500
    # 画面の幅と高さを取得
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # ウィンドウを中央に配置する位置を計算
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    # ウィンドウの位置を設定
    window.geometry(f"{width}x{height}+{x}+{y}")

def open_calendar():
    def on_date_select(event):
        global selected_date
        selected_date = calendar.get_date()  # 選択した日付を更新
        date_label.config(text=f"選択した日付: {selected_date}")  # ラベルを更新
        calendar_window.destroy()  # 日付を選択したらポップアップを閉じる

    # カレンダー用のポップアップウィンドウを作成
    calendar_window = tk.Toplevel()
    calendar_window.title("締切日を選択してください")
    center_window(calendar_window)

    # カレンダーのタイトル
    calendar_title = tk.Label(calendar_window, text="締切日を選択してください", font=("Arial", 12))
    calendar_title.pack(pady=10)

    # カレンダーウィジェット
    calendar = Calendar(calendar_window, selectmode="day", date_pattern="yyyy-mm-dd")
    calendar.pack(pady=10)

    # カレンダー選択イベントをバインド
    calendar.bind("<<CalendarSelected>>", on_date_select)

def select_entry_file(): 
    global selected_entry_file
    # CSVファイルを選択するファイルダイアログを開く
    selected_entry_file = filedialog.askopenfilename(
        title="SPS登録者リストを選択してください",
        filetypes=[("All Files", "*.*")]
    )
    if selected_entry_file:
        entry_label.config(text=f"選択したSPS登録者リスト: \n{selected_entry_file}")

def select_other_files(): 
    global selected_other_files
    # CSVファイルを選択するファイルダイアログを開く
    selected_other_files = filedialog.askopenfilenames(
        title="他のファイルをまとめて選択してください",
        filetypes=[("All Files", "*.*")]
    )
    if selected_other_files:
        formatted_files = "/\n".join(selected_other_files)
        other_label.config(text=f"選択した他のファイル: \n{formatted_files}")

def process_operation():
    global selected_date, selected_entry_file, selected_other_files

    if not selected_date:
        messagebox.showwarning("日付が選択されていません", "日付を選択してください。")
        return

    if not selected_entry_file or not selected_other_files:
        messagebox.showwarning("ファイルが選択されていません", "エントリーファイルと他のファイルを選択してください。")
        return

    response = messagebox.askyesno(
        "確認",
        f"選択したSPS登録者リスト:\n{selected_entry_file}\n"
        f"選択した他のファイル:\n{selected_other_files}\n"
        f"選択した日付:\n{selected_date}\n"
        "これで処理を開始しますか？"
    )

    if not response:
        messagebox.showinfo("キャンセル", "処理はキャンセルされました。")
        return

    # 出力フォルダを選択
    output_folder = filedialog.askdirectory(title="出力先フォルダを選択してください")
    if not output_folder:
        messagebox.showwarning("フォルダが選択されていません", "出力先フォルダを選択してください。")
        return

    # ステータスウィンドウを作成
    status_window = tk.Toplevel()
    status_window.title("処理ステータス")
    center_window(status_window)
    tk.Label(status_window, text="ファイルを処理中です。少々お待ちください...", font=("Arial", 12)).pack(pady=10)
    status_label = tk.Label(status_window, text="", font=("Arial", 10), fg="blue")
    status_label.pack(pady=10)
    progress_bar = ttk.Progressbar(status_window, mode="indeterminate")
    progress_bar.pack(pady=10, fill=tk.X, padx=20)
    progress_bar.start()

    def update_status(message):
        status_label.config(text=message)
        status_window.update()

    try:
        # エントリーファイルを処理
        update_status("SPS登録者リストを読み込んでいます...")
        df_entry = pd.read_csv(selected_entry_file, sep="\t", header=0)
        if "easy_id" not in df_entry.columns or "registration_finish_datetime" not in df_entry.columns:
            raise ValueError(f"エントリーファイルには 'easy_id' と 'registration_finish_datetime' 列が必要です。\n{df_entry.columns}")

        update_status("SPS登録者リストをフィルタリングしています...")
        df_entry['registration_finish_datetime'] = pd.to_datetime(df_entry['registration_finish_datetime'], errors='coerce')
        df_entry_filtered = df_entry[df_entry['registration_finish_datetime'] <= pd.to_datetime(selected_date)]

        if df_entry_filtered.empty:
            raise ValueError("選択した日付に一致するデータがありません。")

        # 他のファイルを処理
        easy_id_sets = []
        for idx, file_path in enumerate(selected_other_files, start=1):
            update_status(f"ファイル {idx}/{len(selected_other_files)} を処理しています: {file_path}")
            df_other = pd.read_csv(file_path, usecols=[0], skiprows=1, header=None, encoding="utf-8")
            df_other.columns = ['easy_id']
            easy_id_sets.append(set(df_other['easy_id'].dropna()))

        # 共通のIDを計算
        update_status("共通IDを計算しています...")
        common_easy_ids = set(df_entry_filtered['easy_id']).intersection(*easy_id_sets)

        # フィルタリング
        update_status("共通IDでエントリーファイルをフィルタリングしています...")
        result_df = df_entry_filtered[df_entry_filtered['easy_id'].isin(common_easy_ids)]

        if result_df.empty:
            raise ValueError("一致するデータがありません。")

        # 結果を保存
        update_status("結果を保存しています...")
        output_file1 = f"{output_folder}/結果1.txt"
        output_file2 = f"{output_folder}/結果2.txt"
        result_df[['easy_id', 'registration_finish_datetime']].to_csv(output_file1, sep="\t", index=False, header=True)
        result_df[['easy_id']].to_csv(output_file2, sep="\t", index=False, header=True)
        
        update_status(f"処理が完了しました。結果を保存しました:\n{output_file1}")
        messagebox.showinfo("処理完了", f"結果を保存しました:\n{output_file1}")

    except Exception as e:
        messagebox.showerror("処理エラー", f"エラーが発生しました:\n{e}")
    finally:
        progress_bar.stop()
        status_window.destroy()


def main():
    global date_label, entry_label, other_label

    window = tk.Tk()
    window.title("データ抽出ツール")
    center_window(window)

    calendar_button = tk.Button(window, text="いつまでのデータを抽出しますか？", command=open_calendar, font=("Arial", 12))
    calendar_button.pack(pady=10)

    date_label = tk.Label(window, text="日付がまだ選択されていません。", font=("Arial", 12), fg="blue")
    date_label.pack(pady=10)

    select_file_button = tk.Button(window, text="SPS登録者リストを選択してください", command=select_entry_file, font=("Arial", 12))
    select_file_button.pack(pady=10)

    entry_label = tk.Label(window, text="SPS登録者リストがまだ選択されていません。", font=("Arial", 12), fg="blue")
    entry_label.pack(pady=10)

    select_multiple_files_button = tk.Button(window, text="他のファイルをまとめて選択してください", command=select_other_files, font=("Arial", 12))
    select_multiple_files_button.pack(pady=10)

    other_label = tk.Label(window, text="他のファイルがまだ選択されていません。", font=("Arial", 12), fg="blue")
    other_label.pack(pady=10)

    process_button = tk.Button(window, text="実行", command=process_operation, font=("Arial", 12))
    process_button.pack(pady=10)

    window.mainloop()

if __name__ == "__main__":
    main()
