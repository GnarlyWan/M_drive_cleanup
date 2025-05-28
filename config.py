import os
from datetime import timedelta

# === File Filter Settings ===
EXTENSIONS = [
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp',
    '.svg', '.ico', '.jfif', '.pjpeg', '.pjp'
]

MIN_SIZE_MB = 0.1  # Only include files larger than this size (MB)
OLDER_THAN_DAYS = 365 * 2  # Only include files older than 2 years

# === Time Filter Flags ===
FILTER_CREATED = False
FILTER_ACCESSED = False  # Not used yet, but ready for future use

# === Paths ===
SCAN_ROOT = "M:/Department/"
REVIEW_FOLDER = "M:/MDriveCleanup/flagged_files"

# === Mode Flags ===
TEST_MODE = True   # Simulate moves instead of performing them
MOVE_FILES = False  # Default action: just list results

# === Logging (future use) ===
LOG_TO_FILE = True
LOG_PATH = os.path.join(os.getcwd(), "cleanup_log.txt")
