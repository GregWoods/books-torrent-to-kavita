import os
import time
import shutil
import ebookmeta
import fitz  # PyMuPDF for PDF metadata
import logging
import re
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BOOKS_SOURCE = "/books_source"
DESTINATION_FOLDER = "/books_destination"


def sanitize_filename(filename):
    """Sanitizes a filename to be compatible with most filesystems."""
    # Replace invalid characters with an underscore
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove control characters
    filename = "".join(c for c in filename if ord(c) > 31)
    # Remove leading and trailing spaces
    filename = filename.strip()
    # Shorten filename to a reasonable length (optional)
    filename = filename[:200]  # Limit to 200 characters
    return filename


def extract_title(file_path):
    """Extract book title from metadata."""
    logging.info(f"Extract Title from: {file_path}")
    ext = os.path.splitext(file_path)[-1].lower()

    if ext == ".epub":
        meta = ebookmeta.get_metadata(file_path)
        title = meta.title if meta and meta.title else None
    elif ext == ".pdf":
        doc = fitz.open(file_path)
        title = doc.metadata.get("title") if doc.metadata else None
    else:
        title = None  # MOBI/ZIP metadata extraction can be extended here
    
    if title:
        return sanitize_filename(title)
    else:
        return None


def is_file_ready(file_path, timeout=10, check_interval=1):
    """Checks if a file is ready by monitoring its size."""
    initial_size = -1
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            current_size = os.path.getsize(file_path)
            if current_size == initial_size:
                return True  # Size hasn't changed, assume file is ready
            else:
                initial_size = current_size
                time.sleep(check_interval)
        except OSError as e:
            logging.warning(f"OSError while checking file size: {e}")
            time.sleep(check_interval)  # Wait and retry

    logging.warning(f"File {file_path} not ready after {timeout} seconds.")
    return False  # Timeout reached, file not ready



def process_book(file_path):
    """Processes a single book file."""
    logging.info(f"Processing file: {file_path}")

    if not is_file_ready(file_path):
        logging.warning(f"Skipping {file_path} as it's not ready.")
        return

    filename = os.path.basename(file_path)
    title = extract_title(file_path)
    base_name = os.path.splitext(filename)[0]
    logging.info(f"Title: {title}")

    # Ensure books with same base filename are grouped
    book_folder = base_name if not title else title
    dest_folder = os.path.join(DESTINATION_FOLDER, book_folder)
    os.makedirs(dest_folder, exist_ok=True)

    dest_file_path = os.path.join(dest_folder, filename)
    try:
        shutil.move(file_path, dest_file_path)
        logging.info(f"Moved {filename} to {dest_file_path}")
    except Exception as e:
        logging.error(f"Error moving file: {e}")


class BookEventHandler(FileSystemEventHandler):
    def on_moved(self, event):
        if event.is_directory:
            return
        file_path = event.dest_path
        if os.path.isfile(file_path):
            process_book(file_path)

    def on_created(self, event):
        if event.is_directory:
            return
        file_path = event.src_path
        if os.path.isfile(file_path):
            process_book(file_path)


fitz.TOOLS.mupdf_display_warnings(True)
if __name__ == "__main__":
    path = BOOKS_SOURCE
    event_handler = BookEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    logging.info(f"Watching for new files in: {path}")

    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
