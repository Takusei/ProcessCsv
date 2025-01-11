import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from tkcalendar import Calendar
import pandas as pd

selected_date = None  # Global variable to store the selected date
selected_entry_file = None
selected_other_files = None

def center_window(window):
    # Define the window size
    width = 800
    height = 500
    # Get screen width and height
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Calculate the position for the window to be centered
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    # Set the geometry of the window
    window.geometry(f"{width}x{height}+{x}+{y}")

def open_calendar():
    def on_date_select(event):
        global selected_date
        selected_date = calendar.get_date()  # Update the global selected date
        date_label.config(text=f"Selected Date: {selected_date}")  # Update the label
        calendar_window.destroy()  # Close the popup after date selection

    # Create a new popup window for the calendar
    calendar_window = tk.Toplevel()
    calendar_window.title("Select Deadline")
    center_window(calendar_window)

    # Inline title for the calendar
    calendar_title = tk.Label(calendar_window, text="Please select the deadline", font=("Arial", 12))
    calendar_title.pack(pady=10)

    # Calendar widget
    calendar = Calendar(calendar_window, selectmode="day", date_pattern="yyyy-mm-dd")
    calendar.pack(pady=10)

    # Bind the calendar selection event
    calendar.bind("<<CalendarSelected>>", on_date_select)

def select_entry_file(): 
    global selected_entry_file
    # Open file dialog to select a CSV file
    selected_entry_file = filedialog.askopenfilename(
        title="Select a CSV File",
        filetypes=[("All Files", "*.*")]
    )
    if selected_entry_file:
        entry_label.config(text=f"Selected Entry File: \n{selected_entry_file}")

def select_other_files(): 
    global selected_other_files
    # Open file dialog to select a CSV file
    selected_other_files = filedialog.askopenfilenames(
        title="Select a CSV File",
        filetypes=[("All Files", "*.*")]
    )
    if selected_other_files:
        formatted_files = "/\n".join(selected_other_files)
        other_label.config(text=f"Selected Other File: \n{formatted_files}")

def process_operation():
    global selected_date, selected_entry_file, selected_other_files

    if not selected_date:
        messagebox.showwarning("No Date Selected", "Please select a date.")
        return

    if not selected_entry_file or not selected_other_files:
        messagebox.showwarning("No File Selected", "Please select at least 2 CSV files.")
        return

    response = messagebox.askyesno(
        "もう一度確認",
        f"選択したエントリーファイルは:\n{selected_entry_file}\n"
        f"選択した他のファイルは:\n{selected_other_files}\n"
        f"選択した日付は: \n{selected_date}\n"
        "これらでよろしいでしょうか?"
    )

    if not response:
        messagebox.showinfo("Cancelled", "File processing was cancelled.")
        return

    # Step 1: Ask user to select the output folder
    output_folder = filedialog.askdirectory(title="Select Output Folder")
    if not output_folder:
        messagebox.showwarning("No Folder Selected", "Please select an output folder.")
        return

    # Create a status window
    status_window = tk.Toplevel()
    status_window.title("Processing Status")
    center_window(status_window)
    # status_window.geometry("400x200")
    tk.Label(status_window, text="Processing files, please wait...", font=("Arial", 12)).pack(pady=10)
    status_label = tk.Label(status_window, text="", font=("Arial", 10), fg="blue")
    status_label.pack(pady=10)
    progress_bar = ttk.Progressbar(status_window, mode="indeterminate")
    progress_bar.pack(pady=10, fill=tk.X, padx=20)
    progress_bar.start()

    # Update the status window with messages
    def update_status(message):
        status_label.config(text=message)
        status_window.update()

    try:
        # Step 2: Process the entry CSV file
        update_status("Reading the entry file...")
        df_entry = pd.read_csv(selected_entry_file, sep="\t", header=0)
        if "easy_id" not in df_entry.columns or "registration_finish_datetime" not in df_entry.columns:
            raise ValueError(f"The entry file must contain 'easy_id' and 'registration_finish_datetime' columns.\n{df_entry.columns}")

        update_status("Filtering the entry file by date...")
        df_entry['registration_finish_datetime'] = pd.to_datetime(df_entry['registration_finish_datetime'], errors='coerce')
        df_entry_filtered = df_entry[df_entry['registration_finish_datetime'] <= pd.to_datetime(selected_date)]

        if df_entry_filtered.empty:
            raise ValueError("No rows found in the entry file matching the selected date.")

        # Step 3: Read and process "other" files
        easy_id_sets = []
        for idx, file_path in enumerate(selected_other_files, start=1):
            update_status(f"Processing file {idx}/{len(selected_other_files)}: {file_path}")
            df_other = pd.read_csv(file_path, sep="\t", header=0)
            if "easy_id" not in df_other.columns:
                raise ValueError(f"The file must contain 'easy_id' column.\n{file_path}")
            easy_id_sets.append(set(df_other['easy_id'].dropna()))

        # Step 4: Find the intersection of all easy_ids
        update_status("Calculating common IDs...")
        if easy_id_sets:
            common_easy_ids = set(df_entry_filtered['easy_id']).intersection(*easy_id_sets)
        else:
            common_easy_ids = set()

        # Step 5: Filter df_entry_filtered to keep only rows with common easy_ids
        update_status("Filtering the entry file with common IDs...")
        result_df = df_entry_filtered[df_entry_filtered['easy_id'].isin(common_easy_ids)]

        if result_df.empty:
            raise ValueError("No matching rows found across all files.")

        # Step 6: Save the result
        update_status("Saving the result...")
        output_file = f"{output_folder}/filtered_result.txt"  # Change the extension to .txt
        result_df[['easy_id', 'registration_finish_datetime']].to_csv(output_file, sep="\t", index=False, header=True)

        update_status(f"Processing complete. Result saved to:\n{output_file}")
        messagebox.showinfo("Processing Complete", f"Filtered file saved to:\n{output_file}")

    except Exception as e:
        messagebox.showerror("Processing Error", f"An error occurred:\n{e}")
    finally:
        progress_bar.stop()
        status_window.destroy()



def main():
    global date_label, entry_label, other_label

    window = tk.Tk()
    window.title("Date Picker Example")
    
    # Center the window
    center_window(window)

    # Button 1: Open calendar
    calendar_button = tk.Button(window, text="いつまでのデータを抽出しますか？", command=open_calendar, font=("Arial", 12))
    calendar_button.pack(pady=10)

    # Label to display the selected date
    date_label = tk.Label(window, text="No date selected yet.", font=("Arial", 12), fg="blue")
    date_label.pack(pady=10)

    # Button 2: Open file dialog to select a CSV file
    select_file_button = tk.Button(window, text="エントリーファイルを選択してください", command=select_entry_file, font=("Arial", 12))
    select_file_button.pack(pady=10)

    # Label to display the selected entry file
    entry_label = tk.Label(window, text="No entry file selected yet.", font=("Arial", 12), fg="blue")
    entry_label.pack(pady=10)

    # Button 3: Open file dialog to select multiple CSV files
    select_multiple_files_button = tk.Button(window, text="他のファイルまとめて選択してください", command=select_other_files, font=("Arial", 12))
    select_multiple_files_button.pack(pady=10)

    # Label to display the selected entry file
    other_label = tk.Label(window, text="No other files selected yet.", font=("Arial", 12), fg="blue")
    other_label.pack(pady=10)

    # Button 4: Processing
    process_button = tk.Button(window, text="実行", command=process_operation, font=("Arial", 12))
    process_button.pack(pady=10)

    window.mainloop()

if __name__ == "__main__":
    main()
