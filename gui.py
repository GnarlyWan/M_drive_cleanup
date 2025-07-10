import tkinter as tk
import tkinter.font as tkFont
from tkinter import filedialog, ttk, messagebox
from core import run_scan
from config import EXTENSIONS, MIN_SIZE_MB, OLDER_THAN_DAYS, REVIEW_FOLDER, TEST_MODE, DEFAULT_FILTER

class CreateToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        widget.bind("<Enter>", self.show_tooltip)
        widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            self.tooltip, text=self.text, justify='left',
            background="#ffffe0", relief='solid', borderwidth=1,
            font=("tahoma", "8", "normal")
        )
        label.pack(ipadx=1)

    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

def show_size_help():
    help_text = (
        "Choose the smallest file size to include in the scan.\n"
        "Examples:\n"
        "- 0.02 MB = small Word or PDF document (~20 KB)\n"
        "- 1 MB = average-sized audio file or large Word doc\n"
        "- 2+ MB = high-res image or PowerPoint\n\n"
        "1 MB = 1,000 KB\n"
        "Tip: Leave this at 0 to include all files regardless of size."
    )
    messagebox.showinfo("Help: Minimum Size", help_text)

def build_gui():
    root = tk.Tk()
    root.title("M: Drive Cleanup Tool")

    test_mode_var = tk.BooleanVar(value=True)

    def calculate_days():
        try:
            years = int(years_var.get() or 0)
            months = int(months_var.get() or 0)
            weeks = int(weeks_var.get() or 0)
            return years * 365 + months * 30 + weeks * 7
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for years, months, and weeks.")
            return OLDER_THAN_DAYS

    FILTER_OPTIONS = {"Last Accessed": "accessed", "Last Modified": "modified"}

    animation_running = False

    def start_progress_animation():
        nonlocal animation_running
        animation_running = True
        progress_bar.config(mode="indeterminate")
        progress_bar.start(10)

        def animate(count=0):
            if not animation_running:
                return
            dots = "." * (count % 4)
            progress_label_var.set(f"Scanning{dots}")
            root.after(500, lambda: animate(count + 1))

        animate()

    def stop_progress_animation():
        nonlocal animation_running
        animation_running = False
        progress_bar.stop()
        progress_bar.config(mode="determinate")

    def start_scan():
        days = calculate_days()
        selected_filter = FILTER_OPTIONS.get(filter_var.get(), "accessed")
        start_progress_animation()
        run_scan(
            folder_entry, ext_entry, size_entry,
            tk.StringVar(value=str(days)),  # simulate entry-like object for days
            move_var, test_mode_var, root,
            preview_results, progress_var, progress_label_var,
            filter_by=selected_filter,
            stop_animation=stop_progress_animation
        )

    test_mode_var.trace_add("write", lambda *args: toggle_move_checkbox(move_checkbox, test_mode_var))

    # GUI Widgets
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
    size_entry.insert(0, "0")
    size_entry.grid(row=2, column=1, sticky="we")
    CreateToolTip(size_entry, "Enter minimum file size to include.\n0 = include all files.")
    tk.Button(root, text="?", width=2, command=show_size_help).grid(row=2, column=2, sticky="w")

    # Age Inputs (Accessed Time)
    tk.Label(root, text="Not Accessed In:").grid(row=3, column=0, sticky="e")
    years_var = tk.StringVar(value="2")
    months_var = tk.StringVar(value="0")
    weeks_var = tk.StringVar(value="0")

    years_entry = tk.Entry(root, width=5, textvariable=years_var)
    months_entry = tk.Entry(root, width=5, textvariable=months_var)
    weeks_entry = tk.Entry(root, width=5, textvariable=weeks_var)

    years_entry.grid(row=3, column=1, sticky="w")
    months_entry.grid(row=3, column=1)
    weeks_entry.grid(row=3, column=1, sticky="e")

    tk.Label(root, text="Years").grid(row=4, column=1, sticky="w")
    tk.Label(root, text="Months").grid(row=4, column=1)
    tk.Label(root, text="Weeks").grid(row=4, column=1, sticky="e")

    tk.Label(root, text="Filter By:").grid(row=5, column=0, sticky="e")
    default_label = next((k for k, v in FILTER_OPTIONS.items() if v == DEFAULT_FILTER), "Last Accessed")
    filter_var = tk.StringVar(value=default_label)
    tk.OptionMenu(root, filter_var, *FILTER_OPTIONS.keys()).grid(row=5, column=1, sticky="w")

    move_var = tk.BooleanVar()
    move_checkbox = tk.Checkbutton(root, text="Move files instead of just listing", variable=move_var)
    move_checkbox.grid(row=6, column=0, columnspan=3, pady=(5, 10))

    bold_red_font = tkFont.Font(weight="bold")
    test_checkbox = tk.Checkbutton(root, text="Test mode (simulate moves only)",
                                   variable=test_mode_var, fg="red", font=bold_red_font)
    test_checkbox.grid(row=7, column=0, columnspan=3)

    tk.Label(root, text="(Test mode is safe: no files will actually be moved)", fg="gray").grid(
        row=8, column=0, columnspan=3, pady=(0, 10))

    tk.Button(root, text="Run Scan", bg="purple", command=start_scan).grid(
        row=9, column=0, columnspan=3, pady=10)

    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100, length=300)
    progress_bar.grid(row=10, column=0, columnspan=3, pady=(0, 10))

    progress_label_var = tk.StringVar()
    progress_label = tk.Label(root, textvariable=progress_label_var, fg="gray")
    progress_label.grid(row=11, column=0, columnspan=3, pady=(0, 10))

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
