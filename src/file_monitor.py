"""File system monitoring for new file detection"""
import logging
import time
from pathlib import Path
from typing import Callable, Optional

from watchdog.events import FileSystemEventHandler, FileModifiedEvent
from watchdog.observers import Observer

logger = logging.getLogger(__name__)


class FileHandler(FileSystemEventHandler):
    """Handles file system events"""

    def __init__(self, on_file_created: Callable, supported_extensions: tuple = None):
        """
        Initialize file handler.

        Args:
            on_file_created: Callback function when file is created
            supported_extensions: Tuple of supported file extensions (e.g., ('.csv', '.json'))
        """
        super().__init__()
        self.on_file_created = on_file_created
        self.supported_extensions = (
            supported_extensions or (".csv", ".json", ".xlsx", ".xls")
        )
        self.processing_files = set()  # Track files being processed

    def on_created(self, event: FileModifiedEvent) -> None:
        """Handle file creation event"""
        if event.is_directory:
            return

        filepath = Path(event.src_path)

        # Check if file has supported extension
        if not filepath.suffix.lower() in self.supported_extensions:
            logger.debug(f"Ignoring unsupported file type: {filepath.name}")
            return

        # Avoid duplicate processing
        if filepath in self.processing_files:
            logger.debug(f"File already being processed: {filepath.name}")
            return

        logger.info(f"👁️  NEW FILE DETECTED: {filepath.name}")
        self.processing_files.add(filepath)

        try:
            # Wait a moment for file to be fully written
            time.sleep(0.5)

            # Check if file is still accessible and not being written
            if self._is_file_ready(filepath):
                self.on_file_created(filepath)
            else:
                logger.warning(f"File not ready for processing: {filepath.name}")
                self.processing_files.discard(filepath)
        except Exception as e:
            logger.error(f"Error processing file {filepath.name}: {e}")
            self.processing_files.discard(filepath)

    @staticmethod
    def _is_file_ready(filepath: Path, timeout: float = 2.0) -> bool:
        """
        Check if file is ready for processing (not being written).

        Args:
            filepath: Path to file
            timeout: Time to wait for file to stabilize

        Returns:
            True if file is ready, False otherwise
        """
        try:
            start_time = time.time()
            last_size = filepath.stat().st_size

            while time.time() - start_time < timeout:
                time.sleep(0.1)
                current_size = filepath.stat().st_size
                if current_size == last_size:
                    return True
                last_size = current_size

            return True  # Assume ready after timeout
        except Exception:
            return False


class FileMonitor:
    """Monitors directories for new files"""

    def __init__(self, watch_path: str = "watched/incoming"):
        """
        Initialize file monitor.

        Args:
            watch_path: Directory to watch for new files
        """
        self.watch_path = Path(watch_path)
        self.observer: Optional[Observer] = None
        self.is_running = False

    def start_monitoring(self, on_file_created: Callable) -> None:
        """
        Start monitoring for file changes.

        Args:
            on_file_created: Callback function to call when file is created
        """
        # Create watch directory if it doesn't exist
        self.watch_path.mkdir(parents=True, exist_ok=True)

        # Create and configure observer
        self.observer = Observer()
        event_handler = FileHandler(on_file_created=on_file_created)
        self.observer.schedule(event_handler, str(self.watch_path), recursive=False)

        # Start observer
        self.observer.start()
        self.is_running = True
        logger.info(f"🤖 File Monitor Started")
        logger.info(f"⏰ Timestamp: {Path('logs').name}")
        logger.info(f"📁 Watching: {self.watch_path.resolve()}")

    def stop_monitoring(self) -> None:
        """Stop monitoring for file changes"""
        if self.observer and self.is_running:
            self.observer.stop()
            self.observer.join()
            self.is_running = False
            logger.info("File Monitor Stopped")

    def join(self) -> None:
        """Wait for monitoring to complete (blocking)"""
        if self.observer:
            self.observer.join()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop_monitoring()
