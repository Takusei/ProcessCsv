import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd

class CampaignProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Campaign Processor")

        self.campaign_data = [
            {"applied_file": None, "priority": None, "points": None, "successful_file": None}
            for _ in range(7)
        ]

        self.shared_successful_file = None  # Shared successful file for the last 4 campaigns
        self.initial_processed_files = [None, None, None]  # To store the initial processed_easy_ids files
        self.create_widgets()

    def create_widgets(self):
        # File inputs for initial processed_easy_ids
        for i in range(3):
            tk.Button(self.root, text=f"Select Initial Processed File {i + 1}", command=lambda i=i: self.select_initial_file(i)).grid(row=i, column=0, padx=10, pady=5)
            self.initial_file_label = tk.Label(self.root, text="No file selected", width=30)
            self.initial_file_label.grid(row=i, column=1, padx=10, pady=5)

        # Frame for campaigns 1-3
        for i in range(3):
            frame = ttk.LabelFrame(self.root, text=f"Campaign {i + 1}", padding=(10, 10))
            frame.grid(row=i + 3, column=0, columnspan=9, padx=10, pady=5, sticky="ew")

            # File input for applied file
            tk.Button(frame, text="Select Applied File", command=lambda i=i: self.select_file(i, "applied_file")).grid(row=0, column=0, padx=10, pady=5)
            tk.Label(frame, text="Applied File: ").grid(row=0, column=1, padx=5, pady=5, sticky="w")
            applied_label = tk.Label(frame, text="No file selected", width=20)
            applied_label.grid(row=0, column=2, padx=10, pady=5)
            self.campaign_data[i]["applied_label"] = applied_label

            # Priority input
            tk.Label(frame, text="Priority").grid(row=0, column=3, padx=10, pady=5)
            priority_entry = tk.Entry(frame, width=5)
            priority_entry.grid(row=0, column=4, padx=10, pady=5)
            self.campaign_data[i]["priority_entry"] = priority_entry

            # Points input
            tk.Label(frame, text="Points").grid(row=0, column=5, padx=10, pady=5)
            points_entry = tk.Entry(frame, width=10)
            points_entry.grid(row=0, column=6, padx=10, pady=5)
            self.campaign_data[i]["points_entry"] = points_entry

            # File input for successful file
            tk.Button(frame, text="Select Successful File", command=lambda i=i: self.select_file(i, "successful_file")).grid(row=0, column=7, padx=10, pady=5)
            tk.Label(frame, text="Successful File: ").grid(row=0, column=8, padx=5, pady=5, sticky="w")
            successful_label = tk.Label(frame, text="No file selected", width=20)
            successful_label.grid(row=0, column=9, padx=10, pady=5)
            self.campaign_data[i]["successful_label"] = successful_label

        # Frame for campaigns 4-7
        frame_shared = ttk.LabelFrame(self.root, text="Campaigns 4-7 (Shared Successful File)", padding=(10, 10))
        frame_shared.grid(row=6, column=0, columnspan=9, padx=10, pady=5, sticky="ew")

        for i in range(3, 7):
            tk.Label(frame_shared, text=f"Campaign {i + 1}").grid(row=i - 3, column=0, padx=10, pady=5, sticky="w")

            # File input for applied file
            tk.Button(frame_shared, text="Select Applied File", command=lambda i=i: self.select_file(i, "applied_file")).grid(row=i - 3, column=1, padx=10, pady=5)
            applied_label = tk.Label(frame_shared, text="No file selected", width=20)
            applied_label.grid(row=i - 3, column=2, padx=10, pady=5)
            self.campaign_data[i]["applied_label"] = applied_label

            # Priority input
            tk.Label(frame_shared, text="Priority").grid(row=i - 3, column=3, padx=10, pady=5)
            priority_entry = tk.Entry(frame_shared, width=5)
            priority_entry.grid(row=i - 3, column=4, padx=10, pady=5)
            self.campaign_data[i]["priority_entry"] = priority_entry

            # Points input
            tk.Label(frame_shared, text="Points").grid(row=i - 3, column=5, padx=10, pady=5)
            points_entry = tk.Entry(frame_shared, width=10)
            points_entry.grid(row=i - 3, column=6, padx=10, pady=5)
            self.campaign_data[i]["points_entry"] = points_entry

        # Shared successful file input for last 4 campaigns
        tk.Button(frame_shared, text="Select Shared Successful File", command=self.select_shared_successful_file).grid(row=4, column=1, padx=10, pady=5)
        tk.Label(frame_shared, text="Shared Successful File: ").grid(row=4, column=2, padx=5, pady=5, sticky="w")
        self.shared_successful_label = tk.Label(frame_shared, text="No file selected", width=20)
        self.shared_successful_label.grid(row=4, column=3, padx=10, pady=5)

        # Execute button
        tk.Button(self.root, text="Process and Save", command=self.process_files).grid(row=7, column=0, columnspan=9, pady=20)

    def select_file(self, campaign_index, file_type):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.campaign_data[campaign_index][file_type] = file_path
            if file_type == "applied_file":
                self.campaign_data[campaign_index]["applied_label"].config(text=file_path.split("/")[-1])
            elif file_type == "successful_file":
                self.campaign_data[campaign_index]["successful_label"].config(text=file_path.split("/")[-1])

    def select_shared_successful_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.shared_successful_file = file_path
            self.shared_successful_label.config(text=file_path.split("/")[-1])

    def select_initial_file(self, index):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.initial_processed_files[index] = file_path
            self.root.grid_slaves(row=index, column=1)[0].config(text=file_path.split("/")[-1])

    def process_files(self):
        try:
            # Initialize processed_easy_ids with data from initial files
            processed_easy_ids = set()
            for file_path in self.initial_processed_files:
                if file_path:
                    initial_df = pd.read_csv(file_path)
                    processed_easy_ids.update(initial_df['easyId'])

            # To collect all easyIds, priorities, and points for the extra file
            all_results = []

            # Sort campaigns by priority (descending order, larger number = higher priority)
            sorted_campaigns = sorted(
                self.campaign_data,
                key=lambda x: int(x["priority_entry"].get()) if x["priority_entry"].get() else 0,
                reverse=True
            )

            for i, campaign in enumerate(sorted_campaigns):
                applied_file = campaign["applied_file"]
                priority = campaign["priority_entry"].get()
                points = campaign["points_entry"].get()

                if not applied_file or not priority or not points:
                    messagebox.showerror("Error", f"Missing input for campaign {i + 1}.")
                    return

                if not campaign["successful_file"] and self.shared_successful_file is None:
                    messagebox.showerror("Error", "Shared successful file is missing for the last 4 campaigns.")
                    return

                # Determine the successful_file based on the original index
                original_index = self.campaign_data.index(campaign)
                successful_file = (
                    self.shared_successful_file if original_index >= 3 else campaign["successful_file"]
                )

                priority = int(priority)
                points = int(points)

                applied_df = pd.read_csv(applied_file)
                successful_df = pd.read_csv(successful_file)

                applied_ids = set(applied_df['easyId'])
                successful_ids = set(successful_df['easyId'])

                # Get intersection and exclude IDs already processed in higher-priority campaigns
                valid_ids = (applied_ids & successful_ids) - processed_easy_ids

                # Update the set of processed IDs
                processed_easy_ids.update(valid_ids)

                # Save the result to a new CSV file
                output_df = pd.DataFrame({'easyId': list(valid_ids)})
                output_file = f"{points}_points.csv"
                output_df.to_csv(output_file, index=False)

                # Append to all_results with their priority and points
                all_results.extend([(easy_id, priority, points) for easy_id in valid_ids])

            # Save the extra file with all results, priorities, and points
            all_results_df = pd.DataFrame(all_results, columns=['easyId', 'priority', 'points'])
            all_results_df.to_csv("all_campaign_results.csv", index=False)

            messagebox.showinfo("Success", "Processing complete! Output files have been saved.")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during processing: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CampaignProcessorApp(root)
    root.mainloop()
