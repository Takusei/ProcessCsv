import tkinter as tk
from tkinter import messagebox, filedialog
from tkcalendar import Calendar
import pandas as pd

selected_date = None  # Global variable to store the selected date

def center_window(window):
    # Define the window size
    width = 400
    height = 250
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


def select_csv_file():
    # Open file dialog to select a CSV file
    file_path = filedialog.askopenfilename(
        title="Select a CSV File",
        filetypes=[("All Files", "*.*")]
    )
    if file_path:
        global selected_date
        response = messagebox.askyesno(
            "Confirmation",
            f"We will now process the selected CSV file:\n{file_path}\n"
            f"with the selected date: \n{selected_date if selected_date else '(No date selected yet.)'}\n"
            "Do you want to continue?"
        )
        if response:
            if not selected_date:
                messagebox.showwarning("No Date Selected", "Please select a deadline date first.")
                return

            # Step 1: Ask user to select the output folder
            output_folder = filedialog.askdirectory(title="Select Output Folder")
            if not output_folder:
                messagebox.showwarning("No Folder Selected", "Please select an output folder.")
                return

            # Step 2: Process the CSV file
            try:
                df = pd.read_csv(file_path, sep="\t", header=0)  # Use detected encoding
                if "easy_id" not in df.columns or "registration_finish_datetime" not in df.columns:
                    messagebox.showerror("Invalid CSV", f"The CSV file must contain 'easy_id' and 'registration_finish_datetime' columns.\n{df.columns}")
                    return

                # Convert date column to datetime and filter rows
                df['registration_finish_datetime'] = pd.to_datetime(df['registration_finish_datetime'], errors='coerce')
                filtered_df = df[df['registration_finish_datetime'] <= pd.to_datetime(selected_date)]

                # Step 3: Save the filtered result as TSV
                output_file = f"{output_folder}/filtered_result.tsv"
                filtered_df.to_csv(output_file, sep="\t", index=False)
                messagebox.showinfo("Processing Complete", f"Filtered file saved to:\n{output_file}")
            except Exception as e:
                messagebox.showerror("Processing Error", f"An error occurred:\n{e}")
        else:
            messagebox.showinfo("Cancelled", "File processing was cancelled.")
    else:
        messagebox.showwarning("No File Selected", "Please select a CSV file.")


def main():
    global date_label

    window = tk.Tk()
    window.title("Date Picker Example")
    
    # Center the window
    center_window(window)

    # Button 1: Open calendar
    calendar_button = tk.Button(window, text="Select Deadline", command=open_calendar, font=("Arial", 12))
    calendar_button.pack(pady=10)

    # Label to display the selected date
    date_label = tk.Label(window, text="No date selected yet.", font=("Arial", 12), fg="blue")
    date_label.pack(pady=10)

    # Button 2: Open file dialog to select a CSV file
    select_file_button = tk.Button(window, text="Select CSV File", command=select_csv_file, font=("Arial", 12))
    select_file_button.pack(pady=10)

    window.mainloop()

if __name__ == "__main__":
    main()
