"""Main application entry point for Workflow Automation Bot"""
import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

from src.config import Config
from src.file_monitor import FileMonitor
from src.file_processor import FileProcessor
from src.notifier import Notifier, ProcessingResult
from src.organizer import FileOrganizer


def setup_logging(verbose: bool = False) -> None:
    """
    Setup logging configuration.

    Args:
        verbose: Enable verbose logging
    """
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    log_level = logging.DEBUG if verbose else logging.INFO
    log_format = "%(asctime)s [%(levelname)s] %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # File handler
    fh = logging.FileHandler(log_dir / "automation.log")
    fh.setLevel(log_level)
    fh.setFormatter(logging.Formatter(log_format, datefmt=date_format))

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    ch.setFormatter(logging.Formatter(log_format, datefmt=date_format))

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(fh)
    root_logger.addHandler(ch)


def setup_directories() -> None:
    """Create required directory structure"""
    directories = [
        "watched/incoming",
        "processed/csv",
        "processed/json",
        "processed/excel",
        "failed",
        "logs",
        "config",
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

    logging.info("✅ Directory structure created/verified")


class WorkflowBot:
    """Main workflow automation bot"""

    def __init__(
        self,
        watch_path: str = "watched/incoming",
        verbose: bool = False,
    ):
        """
        Initialize the workflow bot.

        Args:
            watch_path: Directory to watch for incoming files
            verbose: Enable verbose logging
        """
        setup_logging(verbose)
        setup_directories()

        self.logger = logging.getLogger(__name__)
        self.config = Config("config/rules.json")
        self.monitor = FileMonitor(watch_path)
        self.processor = FileProcessor(self.config.config)
        self.organizer = FileOrganizer()
        self.notifier = Notifier(self.config.get_nested("notifications"))

    def process_file(self, filepath: Path) -> None:
        """
        Process a detected file.

        Args:
            filepath: Path to file to process
        """
        try:
            # Validate file
            is_valid, error = self.processor.validate_file(filepath)
            if not is_valid:
                self.logger.error(f"❌ Validation failed: {error}")
                result = ProcessingResult(
                    filename=filepath.name,
                    success=False,
                    error_message=error,
                )
                self.notifier.notify_failure(result)
                self.organizer.move_to_failed(filepath, error)
                return

            self.logger.info("✅ Validation passed")

            # Process file
            self.logger.info("🔄 Processing started...")
            success, process_result = self.processor.process_file(filepath)

            if not success:
                # Processing failed
                error_msg = process_result.get("error", "Unknown error")
                self.logger.error(f"❌ Processing failed: {error_msg}")
                result = ProcessingResult(
                    filename=filepath.name,
                    success=False,
                    error_message=error_msg,
                    processing_time=process_result.get("processing_time", 0),
                )
                self.notifier.notify_failure(result)
                self.organizer.move_to_failed(filepath, error_msg)
                return

            # Organize file
            self.logger.info("📁 Organizing file...")
            file_type = process_result.get("file_type", "unknown")
            organized_path = self.organizer.organize_file(filepath, file_type)

            # Create result and notify
            result = ProcessingResult(
                filename=filepath.name,
                success=True,
                records_processed=process_result.get("records_processed", 0),
                duplicates_removed=process_result.get("duplicates_removed", 0),
                missing_values_handled=process_result.get("missing_values_handled", 0),
                processing_time=process_result.get("processing_time", 0),
                output_path=str(organized_path),
            )

            self.logger.info("📊 Processing complete")
            self.logger.info(f"   - Records processed: {result.records_processed:,}")
            self.logger.info(f"   - Duplicates removed: {result.duplicates_removed}")
            self.logger.info(f"   - Missing values handled: {result.missing_values_handled}")
            self.logger.info(f"   - Processing time: {result.processing_time:.2f}s")

            self.notifier.notify_success(result)

        except Exception as e:
            self.logger.error(f"Unexpected error: {e}", exc_info=True)

    def start(self) -> None:
        """Start the workflow bot"""
        self.logger.info("=" * 60)
        self.logger.info("🤖 Workflow Automation Bot Started")
        self.logger.info(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("=" * 60)

        try:
            self.monitor.start_monitoring(on_file_created=self.process_file)
            self.monitor.join()
        except KeyboardInterrupt:
            self.logger.info("\n⏹️  Bot interrupted by user")
            self.stop()
        except Exception as e:
            self.logger.error(f"Fatal error: {e}", exc_info=True)
            self.stop()
            sys.exit(1)

    def stop(self) -> None:
        """Stop the workflow bot"""
        self.monitor.stop_monitoring()
        self.logger.info("🛑 Workflow Automation Bot Stopped")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Workflow Automation Bot - Intelligent file monitoring and processing"
    )
    parser.add_argument(
        "--watch",
        type=str,
        default="watched/incoming",
        help="Directory to watch for files (default: watched/incoming)",
    )
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Setup directory structure and exit",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test mode - process existing files once and exit",
    )

    args = parser.parse_args()

    if args.setup:
        setup_logging(args.verbose)
        setup_directories()
        print("✅ Setup complete!")
        return

    bot = WorkflowBot(watch_path=args.watch, verbose=args.verbose)

    if args.test:
        # Test mode: process existing files
        watch_path = Path(args.watch)
        if watch_path.exists():
            files = list(watch_path.glob("*"))
            if files:
                logging.info(f"Test mode: Processing {len(files)} file(s)")
                for file in files:
                    if file.is_file():
                        bot.process_file(file)
            else:
                logging.info("No files found in watch directory")
        else:
            logging.error(f"Watch directory does not exist: {watch_path}")
    else:
        # Normal mode: continuous monitoring
        bot.start()


if __name__ == "__main__":
    main()
