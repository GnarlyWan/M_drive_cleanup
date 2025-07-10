import os
from datetime import timedelta

# === File Filter Settings ===
EXTENSIONS = [
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp',
    '.svg', '.ico', '.jfif', '.pjpeg', '.pjp'
]

MIN_SIZE_MB = 0.1  # Only include files larger than this size (MB)
OLDER_THAN_DAYS = 365 * 2  # Only include files not accessed in the last 2 years

# === Date Filter Settings ===
# Options: "accessed" or "modified"
DEFAULT_FILTER = "accessed"

# === Paths ===
SCAN_ROOT = "M:/Department/"
REVIEW_FOLDER = "M:/MDriveCleanup/flagged_files"

# === Mode Flags ===
TEST_MODE = True   # Simulate moves instead of performing them
MOVE_FILES = False  # Default action: just list results

# === Logging (future use) ===
LOG_TO_FILE = True
LOG_PATH = os.path.join(os.getcwd(), "cleanup_log.txt")