import os
import threading
import csv
import tkinter as tk
import tkinter.font as tkFont
from tkinter import filedialog, messagebox
from datetime import datetime, timedelta

# === CONFIGURATION ===
# Path to the CSV file
TEST_MODE = True # Set to False for production
SCAN_ROOT = 'M:/Department/'
EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp', '.svg', '.ico', '.jfif', '.pjpeg', '.pjp']
MIN_SIZE_MB = 0.1  # Minimum size in MB
OLDER_THAN_DAYS = 365 * 2  # Older than 2 years
FILTER_CREATED = False # Filter by created date instead of modified date
FILTER_ACCESSED = False # Filter by accessed date instead of modified date
MOVE_FILES = False  # default

# === END CONFIGURATION ===


# === BACKEND FUNCTION ===
def scan_and_export(folder, extensions, min_size_mb, older_than_days, move_files=False, test_mode=True): 
    min_size_bytes = min_size_mb * 1024 * 1024
    cutoff_date = datetime.now() - timedelta(days=older_than_days)
    results = []
    total_bytes = 0

    for root, dirs, files in os.walk(folder):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                if not any(file.lower().endswith(ext) for ext in extensions): 
                    continue 
                
                size = os.path.getsize(file_path)
                modified = datetime.fromtimestamp(os.path.getmtime(file_path))
                created = datetime.fromtimestamp(os.path.getctime(file_path))
                accessed = datetime.fromtimestamp(os.path.getatime(file_path))

                #Apply all filters
                if size >= min_size_bytes and modified < cutoff_date:
                  results.append([
                      file_path, 
                      round(size / (1024 * 1024), 2), 
                      modified.strftime("%Y-%m-%d %H:%M"), 
                      created.strftime("%Y-%m-%d %H:%M"), 
                      accessed.strftime("%Y-%m-%d %H:%M")
                  ])
                  total_bytes += size

                # === MOVE FILES ===
                if move_files:
                    review_root = "M:/MDriveCleanup/flagged_files"
                    dest_path = None
                    try:
                        relative_path = os.path.relpath(file_path, folder)
                        dest_path = os.path.join(review_root, relative_path)
                        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

                        base, ext = os.path.splitext(dest_path)
                        counter = 1
                        while os.path.exists(dest_path):
                            dest_path = f"{base}_{counter}{ext}"
                            counter += 1

                        if test_mode:
                            print(f"[TEST] Would move: {file_path} → {dest_path}")
                        else:
                            os.rename(file_path, dest_path)
                            print(f"Moved: {file_path} → {dest_path}")

                    except Exception as e:
                        print(f"Error moving {file_path} → {dest_path}: {e}")

            except Exception as e:
                print(f"Error processing {file_path}: {e}")


# === EXPORT TO CSV ===
    output_file = os.path.join(folder, "cleanup_results.csv")
    with open(output_file, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["File Path", "Size (MB)", "Last Modified", "Created", "Last Accessed"])
        writer.writerows(results)
        
    return output_file, round(total_bytes / (1024 * 1024), 2), results

# === GUI FUNCTION ===
def browse_folder():
    path = filedialog.askdirectory()
    folder_entry.delete(0, tk.END)
    folder_entry.insert(0, path)

def run_scan():
    # Inner function to run the scan in background
    def threaded_scan():
        folder = folder_entry.get()
        extensions = [e.strip() for e in ext_entry.get().split(",")]
        move_files = move_var.get()
        test_mode = test_mode_var.get()

        try:
            min_size_mb = float(size_entry.get())
            older_than_days = int(days_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter numeric values for size and days.")
            return

        try:
            output_file, total_size, matched_results = scan_and_export(
                folder, extensions, min_size_mb, older_than_days,
                move_files=move_files, test_mode=test_mode
            )

            # Use Tkinter-safe method to show results
            root.after(0, lambda: [
                preview_results(matched_results),
                messagebox.showinfo(
                    "Scan Complete",
                    f"Results saved to: {output_file}\nTotal amount matched: {total_size:.2f} MB")
            ])

        except Exception as e:
            root.after(0, lambda: messagebox.showerror("Scan Error", f"An unexpected error occurred:\n\n{str(e)}"))

    # Run scan in a new thread
    threading.Thread(target=threaded_scan, daemon=True).start()


def toggle_move_checkbox(*args):
    if test_mode_var.get():
        move_checkbox.config(state=tk.DISABLED)
    else:
        move_checkbox.config(state=tk.NORMAL)



# === GUI ===
root = tk.Tk()
root.title("M: Drive Cleanup Tool")

test_mode_var = tk.BooleanVar(value=True)
test_mode_var.trace_add("write", toggle_move_checkbox)

tk.Label(root, text="Target Folder:").grid(row=0, column=0, sticky="e")
folder_entry = tk.Entry(root, width=50)
folder_entry.grid(row=0, column=1)
tk.Button(root, text="Browse", command=browse_folder).grid(row=0, column=2)

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
move_checkbox = tk.Checkbutton(
    root, 
    text="Move files instead of just listing", 
    variable=move_var
)
move_checkbox.grid(row=4, column=0, columnspan=3, pady=(5, 10))

bold_red_font = tkFont.Font(weight="bold")

test_checkbox = tk.Checkbutton(
    root,
    text="Test mode (simulate moves only)",
    variable=test_mode_var,
    fg="red",
    font=bold_red_font
)
test_checkbox.grid(row=5, column=0, columnspan=3)

tk.Label(
    root,
    text="(Test mode is safe: no files will actually be moved)",
    fg="gray"
).grid(row=6, column=0, columnspan=3, pady=(0, 10))



tk.Button(root, text="Run Scan", command=run_scan, bg="purple").grid(row=7, column=0, columnspan=3, pady=10)

def preview_results(results):
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
    

root.mainloop()

