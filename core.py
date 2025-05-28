import os
import shutil
import threading
import csv
from datetime import datetime, timedelta
from tkinter import messagebox
from config import EXTENSIONS, MIN_SIZE_MB, OLDER_THAN_DAYS, REVIEW_FOLDER, TEST_MODE



def run_scan(folder_entry, ext_entry, size_entry, days_entry, move_var, test_mode_var, root, preview_callback):
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

            # Use callback to update results in GUI
            root.after(0, lambda: [
                preview_callback(matched_results, root),
                messagebox.showinfo(
                    "Scan Complete",
                    f"Results saved to: {output_file}\nTotal matched size: {total_size:.2f} MB")
            ])

        except Exception as e:
            root.after(0, lambda: messagebox.showerror("Scan Error", f"An unexpected error occurred:\n\n{str(e)}"))

    threading.Thread(target=threaded_scan, daemon=True).start()



def scan_and_export(folder, extensions, min_size_mb, older_than_days, move_files=False, test_mode=True):
    min_size_bytes = min_size_mb * 1024 * 1024
    cutoff_date = datetime.now() - timedelta(days=older_than_days)
    results = []
    total_bytes = 0

    for root, _, files in os.walk(folder):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                if not any(file.lower().endswith(ext) for ext in extensions):
                    continue

                size = os.path.getsize(file_path)
                modified = datetime.fromtimestamp(os.path.getmtime(file_path))
                created = datetime.fromtimestamp(os.path.getctime(file_path))
                accessed = datetime.fromtimestamp(os.path.getatime(file_path))

                if size >= min_size_bytes and modified < cutoff_date:
                    results.append([
                        file_path,
                        round(size / (1024 * 1024), 2),
                        modified.strftime("%Y-%m-%d %H:%M"),
                        created.strftime("%Y-%m-%d %H:%M"),
                        accessed.strftime("%Y-%m-%d %H:%M")
                    ])
                    total_bytes += size

                    if move_files:
                        move_file(file_path, folder, test_mode)

            except Exception as e:
                print(f"Error processing {file_path}: {e}")

    # Export to CSV
    output_file = os.path.join(folder, "cleanup_results.csv")
    with open(output_file, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["File Path", "Size (MB)", "Last Modified", "Created", "Last Accessed"])
        writer.writerows(results)

    return output_file, round(total_bytes / (1024 * 1024), 2), results


def move_file(file_path, folder, test_mode):
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
            shutil.move(file_path, dest_path)
            print(f"Moved: {file_path} → {dest_path}")

    except Exception as e:
        print(f"Error moving {file_path} → {dest_path}: {e}")
