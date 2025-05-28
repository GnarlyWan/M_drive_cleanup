import tkinter as tk
import tkinter.font as tkFont
from tkinter import filedialog, ttk
from core import run_scan  # You'll define this wrapper in core.py
from config import EXTENSIONS, MIN_SIZE_MB, OLDER_THAN_DAYS, REVIEW_FOLDER, TEST_MODE


def build_gui():
    root = tk.Tk()
    root.title("M: Drive Cleanup Tool")

    test_mode_var = tk.BooleanVar(value=True)
    test_mode_var.trace_add("write", lambda *args: toggle_move_checkbox(move_checkbox, test_mode_var))

    # === GUI Widgets ===
    tk.Label(root, text="Target Folder:").grid(row=0, column=0, sticky="e")
    folder_entry = tk.Entry(root, width=50)
    folder_entry.grid(row=0, column=1)
    tk.Button(root, text="Browse", command=lambda: browse_folder(folder_entry)).grid(row=0, column=2)

    tk.Label(root, text="File Extensions (comma separated):").grid(row=1, column=0, sticky="e")
    ext_entry = tk.Entry(root, width=50)
    ext_entry.insert(0, ", ".join(EXTENSIONS))
    ext_entry.grid(row=1, column=1, columnspan=2, sticky="we")

    tk.Label(root, text="Minimum Size (MB):").grid(row=2, column=0, sticky="e")
    size_entry = tk.Entry(root)
    size_entry.insert(0, str(MIN_SIZE_MB))
    size_entry.grid(row=2, column=1, columnspan=2, sticky="we")

    tk.Label(root, text="Older Than (Days):").grid(row=3, column=0, sticky="e")
    days_entry = tk.Entry(root)
    days_entry.insert(0, str(OLDER_THAN_DAYS))
    days_entry.grid(row=3, column=1, columnspan=2, sticky="we")

    move_var = tk.BooleanVar()
    move_checkbox = tk.Checkbutton(root, text="Move files instead of just listing", variable=move_var)
    move_checkbox.grid(row=4, column=0, columnspan=3, pady=(5, 10))

    bold_red_font = tkFont.Font(weight="bold")
    test_checkbox = tk.Checkbutton(root, text="Test mode (simulate moves only)",
                                   variable=test_mode_var, fg="red", font=bold_red_font)
    test_checkbox.grid(row=5, column=0, columnspan=3)

    tk.Label(root, text="(Test mode is safe: no files will actually be moved)", fg="gray").grid(
        row=6, column=0, columnspan=3, pady=(0, 10))

    tk.Button(root, text="Run Scan", bg="purple", command=lambda: run_scan(
        folder_entry, ext_entry, size_entry, days_entry,
        move_var, test_mode_var, root, preview_results, progress_var, progress_label_var)).grid(
        row=7, column=0, columnspan=3, pady=10)

    # Progress Bar
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100, length=300)
    progress_bar.grid(row=8, column=0, columnspan=3, pady=(0, 10))

    progress_label_var = tk.StringVar()
    progress_label = tk.Label(root, textvariable=progress_label_var, fg="gray")
    progress_label.grid(row=9, column=0, columnspan=3, pady=(0, 10))

    root.mainloop()

def toggle_move_checkbox(checkbox, test_mode_var):
    state = tk.DISABLED if test_mode_var.get() else tk.NORMAL
    checkbox.config(state=state)

def browse_folder(entry):
    path = filedialog.askdirectory()
    entry.delete(0, tk.END)
    entry.insert(0, path)

def preview_results(results, root):
    preview_window = tk.Toplevel(root)
    preview_window.title("Preview Results")

    text_area = tk.Text(preview_window, wrap=tk.NONE, width=100, height=30)
    text_area.pack(fill=tk.BOTH, expand=True)

    scrollbar_y = tk.Scrollbar(preview_window, command=text_area.yview)
    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
    text_area.config(yscrollcommand=scrollbar_y.set)

    if not results:
        text_area.insert(tk.END, "No matching files found.")
    else:
        for row in results:
            path = row[0]
            size = f"{row[1]} MB"
            text_area.insert(tk.END, f"{path} - {size}\n")
