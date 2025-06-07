import os
import time
import shutil
import ebookmeta
import fitz  # PyMuPDF for PDF metadata
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BOOKS_SOURCE = "/app/books_source"
DESTINATION_FOLDER = "/app/kavita_destination"


def extract_title(file_path):
    """Extract book title from metadata."""
    ext = os.path.splitext(file_path)[-1].lower()

    if ext == ".epub":
        meta = ebookmeta.get_metadata(file_path)
        return meta.title if meta and meta.title else None
    elif ext == ".pdf":
        doc = fitz.open(file_path)
        return doc.metadata.get("title") if doc.metadata else None
    else:
        return None  # MOBI/ZIP metadata extraction can be extended here


def process_book(file_path):
    """Processes a single book file."""
    logging.info(f"Processing file: {file_path}")
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
    def on_created(self, event):
        if event.is_directory:
            return
        file_path = event.src_path
        if os.path.isfile(file_path):
            process_book(file_path)


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