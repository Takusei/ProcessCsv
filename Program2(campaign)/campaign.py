import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import os

class CampaignProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Campaign Processor")

        self.campaign_data = [
            {"applied_file": None, "priority_entry": None, "points_entry": None, "successful_file": None, "extra_file": None}
            for _ in range(7)
        ]

        self.shared_successful_file = None  # Shared successful file for the last 4 campaigns
        self.shared_extra_file = None  # Shared extra file for the last 4 campaigns
        
        self.initial_processed_files = [None, None]  # Two global initial processed_easy_ids files
        self.create_widgets()

    def create_widgets(self):
        left_frame = tk.Frame(self.root)
        left_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ns")

        right_frame = tk.Frame(self.root)
        right_frame.grid(row=0, column=1, padx=10, pady=5, sticky="ns")

        # File inputs for initial processed_easy_ids
        for i in range(2):
            tk.Button(left_frame, text=f"除外するファイル {i + 1}", command=lambda i=i: self.select_initial_file(i)).grid(row=i, column=0, padx=10, pady=5)
            self.initial_file_label = tk.Label(left_frame, text="No file selected", width=30)
            self.initial_file_label.grid(row=i, column=1, padx=10, pady=5)

        # Frame for campaigns 1-3
        for i in range(3):
            frame = ttk.LabelFrame(left_frame, text=f"Campaign {i + 1}", padding=(10, 10))
            frame.grid(row=i + 2, column=0, columnspan=10, padx=10, pady=5, sticky="ew")

            tk.Button(frame, text="エントリーリスト：", command=lambda i=i: self.select_file(i, "applied_file")).grid(row=0, column=0, padx=10, pady=5)
            applied_label = tk.Label(frame, text="No file selected", width=20)
            applied_label.grid(row=0, column=1, padx=10, pady=5)
            self.campaign_data[i]["applied_label"] = applied_label

            tk.Label(frame, text="Priority").grid(row=0, column=2, padx=10, pady=5)
            priority_entry = tk.Entry(frame, width=5)
            priority_entry.grid(row=0, column=3, padx=10, pady=5)
            self.campaign_data[i]["priority_entry"] = priority_entry

            tk.Label(frame, text="Points").grid(row=0, column=4, padx=10, pady=5)
            points_entry = tk.Entry(frame, width=10)
            points_entry.grid(row=0, column=5, padx=10, pady=5)
            self.campaign_data[i]["points_entry"] = points_entry

            tk.Button(frame, text="条件達成者リスト：", command=lambda i=i: self.select_file(i, "successful_file")).grid(row=1, column=0, padx=10, pady=5)
            successful_label = tk.Label(frame, text="No file selected", width=20)
            successful_label.grid(row=1, column=1, padx=10, pady=5)
            self.campaign_data[i]["successful_label"] = successful_label

            tk.Button(frame, text="追加リスト：", command=lambda i=i: self.select_file(i, "extra_file")).grid(row=1, column=2, padx=10, pady=5)
            extra_label = tk.Label(frame, text="No file selected", width=20)
            extra_label.grid(row=1, column=3, padx=10, pady=5)
            self.campaign_data[i]["extra_label"] = extra_label

        # Frame for campaigns 4-7
        frame_shared = ttk.LabelFrame(right_frame, text="Campaigns 4-7", padding=(10, 10))
        frame_shared.grid(row=0, column=0, columnspan=10, padx=10, pady=5, sticky="ew")

        for i in range(3, 7):
            tk.Label(frame_shared, text=f"Campaign {i + 1}").grid(row=i - 3, column=0, padx=10, pady=5, sticky="w")

            tk.Button(frame_shared, text="エントリーリスト：", command=lambda i=i: self.select_file(i, "applied_file")).grid(row=i - 3, column=1, padx=10, pady=5)
            applied_label = tk.Label(frame_shared, text="No file selected", width=20)
            applied_label.grid(row=i - 3, column=2, padx=10, pady=5)
            self.campaign_data[i]["applied_label"] = applied_label

            tk.Label(frame_shared, text="Priority").grid(row=i - 3, column=3, padx=10, pady=5)
            priority_entry = tk.Entry(frame_shared, width=5)
            priority_entry.grid(row=i - 3, column=4, padx=10, pady=5)
            self.campaign_data[i]["priority_entry"] = priority_entry

            tk.Label(frame_shared, text="Points").grid(row=i - 3, column=5, padx=10, pady=5)
            points_entry = tk.Entry(frame_shared, width=10)
            points_entry.grid(row=i - 3, column=6, padx=10, pady=5)
            self.campaign_data[i]["points_entry"] = points_entry

        tk.Button(frame_shared, text="条件達成者リスト：", command=self.select_shared_successful_file).grid(row=4, column=1, padx=10, pady=5)
        self.shared_successful_label = tk.Label(frame_shared, text="No file selected", width=30)
        self.shared_successful_label.grid(row=4, column=2, padx=10, pady=5)

        tk.Button(frame_shared, text="追加リスト：", command=self.select_shared_extra_file).grid(row=5, column=1, padx=10, pady=5)
        self.shared_extra_label = tk.Label(frame_shared, text="No file selected", width=30)
        self.shared_extra_label.grid(row=5, column=2, padx=10, pady=5)

        tk.Button(right_frame, text="実行", command=self.process_files).grid(row=1, column=0, columnspan=9, pady=20)


    def select_file(self, campaign_index, file_type):
        if file_type == "extra_file":
            file_path = filedialog.askopenfilename(filetypes=[("Text or TSV files", "*.txt;*.tsv")])
        else:
            file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.campaign_data[campaign_index][file_type] = file_path
            if file_type == "applied_file":
                self.campaign_data[campaign_index]["applied_label"].config(text=file_path.split("/")[-1])
            elif file_type == "successful_file":
                self.campaign_data[campaign_index]["successful_label"].config(text=file_path.split("/")[-1])
            elif file_type == "extra_file":
                self.campaign_data[campaign_index]["extra_label"].config(text=file_path.split("/")[-1])

    def select_shared_successful_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.shared_successful_file = file_path
            self.shared_successful_label.config(text=file_path.split("/")[-1])

    def select_shared_extra_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text or TSV files", "*.txt;*.tsv")])
        if file_path:
            self.shared_extra_file = file_path
            self.shared_extra_label.config(text=file_path.split("/")[-1])

    def select_initial_file(self, index):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            self.initial_processed_files[index] = file_path
            self.root.grid_slaves(row=index, column=1)[0].config(text=file_path.split("/")[-1])

    def process_files(self):
        output_folder = filedialog.askdirectory()
        if not output_folder:
            messagebox.showerror("Error", "Please select an output folder.")
            return

        try:
            # Initialize processed_easy_ids with data from initial files
            processed_easy_ids = set()
            for file_path in self.initial_processed_files:
                if file_path:
                    with open(file_path, "r", encoding="utf-8") as f:
                        for line in f:
                            processed_easy_ids.add(line.strip())  # Strip to remove extra whitespace or newline


            # To collect all easyIds, priorities, and points for the extra file
            all_results = []

            # Filter campaigns that have a valid priority
            valid_campaigns = [
                campaign for campaign in self.campaign_data
                if campaign["priority_entry"].get() and campaign["applied_file"]
            ]

            # Sort campaigns by priority (descending order, larger number = higher priority)
            sorted_campaigns = sorted(
                valid_campaigns,
                key=lambda x: int(x["priority_entry"].get()),
                reverse=True
            )

            for i, campaign in enumerate(sorted_campaigns):
                applied_file = campaign["applied_file"]
                priority = campaign["priority_entry"].get()
                points = campaign["points_entry"].get()

                if not applied_file or not points:
                    messagebox.showerror("Error", f"Missing input for campaign {i + 1}.")
                    return

                # Determine the successful_file based on the original index
                original_index = self.campaign_data.index(campaign)
                successful_file = (
                    self.shared_successful_file if original_index >= 3 else campaign["successful_file"]
                )
                extra_file = (
                    self.shared_extra_file if original_index >= 3 else campaign["extra_file"]
                )

                if not successful_file:
                    messagebox.showerror("Error", f"Missing successful file for campaign {i + 1}.")
                    return

                priority = int(priority)
                points = int(points)

                # Read applied_file (CSV with a single column, no header)
                applied_df = pd.read_csv(applied_file, header=None, names=["easy_id"])  
                applied_ids = set(applied_df["easy_id"])

                # Read successful_file (CSV with headers, assuming it has 'easy_id' column)
                successful_df = pd.read_csv(successful_file)
                successful_ids = set(successful_df["easy_id"])

                # Read extra_file (TXT or TSV)
                extra_ids = set()

                if extra_file.lower().endswith(".txt"):
                    with open(extra_file, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                        if lines[0].strip() != "easy_id":
                            raise ValueError(f"Invalid format in {extra_file}. First line must be 'easy_id'")
                        extra_ids = set(line.strip() for line in lines[1:])  # Skip the header

                elif extra_file.lower().endswith(".tsv"):
                    extra_df = pd.read_csv(extra_file, sep="\t")  # Read TSV file
                    if "easy_id" not in extra_df.columns:
                        raise ValueError(f"Invalid format in {extra_file}. Must contain 'easy_id' column")
                    extra_ids = set(extra_df["easy_id"])


                # Get intersection and exclude IDs already processed in higher-priority campaigns
                valid_ids = (applied_ids & successful_ids & extra_ids) - processed_easy_ids

                # Update the set of processed IDs
                processed_easy_ids.update(valid_ids)

                # Save the result to a new CSV file
                output_df = pd.DataFrame({'easyId': list(valid_ids)})
                output_file = os.path.join(output_folder, f"{points}_points.csv")
                output_df.to_csv(output_file, index=False)

                # Append to all_results with their priority and points
                all_results.extend([(easy_id, priority, points) for easy_id in valid_ids])

            # Save the extra file with all results, priorities, and points
            all_results_df = pd.DataFrame(all_results, columns=['easyId', 'priority', 'points'])
            all_results_df.to_csv(os.path.join(output_folder, "all_campaign_results.csv"), index=False)

            messagebox.showinfo("Success", "Processing complete! Output files have been saved.")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during processing: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CampaignProcessorApp(root)
    root.mainloop()
