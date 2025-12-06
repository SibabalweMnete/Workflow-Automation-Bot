"""File organization system for processed files"""
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class FileOrganizer:
    """Organizes files into structured folders"""

    def __init__(self, base_processed_dir: str = "processed"):
        """
        Initialize file organizer.

        Args:
            base_processed_dir: Base directory for organized files
        """
        self.base_dir = Path(base_processed_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def organize_file(
        self, source_file: Path, file_type: str, archive_original: bool = True
    ) -> Optional[Path]:
        """
        Organize file into appropriate folder structure.

        Args:
            source_file: Path to file to organize
            file_type: Type of file (csv, json, excel, etc.)
            archive_original: Whether to keep original file

        Returns:
            Path to organized file or None if failed
        """
        try:
            # Create type-specific directory
            type_dir = self.base_dir / file_type.lower()
            type_dir.mkdir(parents=True, exist_ok=True)

            # Create date-based subdirectories
            now = datetime.now()
            date_dir = (
                type_dir / str(now.year) / f"{now.month:02d}" / f"{now.day:02d}"
            )
            date_dir.mkdir(parents=True, exist_ok=True)

            # Create new filename with timestamp
            timestamp = now.strftime("%H%M%S")
            new_name = f"{source_file.stem}_{timestamp}{source_file.suffix}"
            destination_file = date_dir / new_name

            # Copy file to new location
            shutil.copy2(source_file, destination_file)
            logger.info(
                f"File organized: {source_file.name} -> {destination_file.relative_to(self.base_dir)}"
            )

            # Remove original if not archiving
            if not archive_original and source_file.exists():
                source_file.unlink()
                logger.info(f"Original file removed: {source_file.name}")

            return destination_file

        except Exception as e:
            logger.error(f"Error organizing file {source_file.name}: {e}")
            return None

    def move_to_failed(self, source_file: Path, error_message: str) -> Optional[Path]:
        """
        Move file to failed directory.

        Args:
            source_file: Path to file that failed
            error_message: Error description

        Returns:
            Path to failed file or None if failed
        """
        try:
            failed_dir = Path("failed")
            failed_dir.mkdir(parents=True, exist_ok=True)

            # Create error log file
            timestamp = datetime.now().strftime("%H%M%S")
            error_filename = f"{source_file.stem}_{timestamp}.error"
            error_file = failed_dir / error_filename

            # Write error message
            with open(error_file, "w") as f:
                f.write(f"Original file: {source_file.name}\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                f.write(f"Error: {error_message}\n")

            # Move the problematic file
            destination = failed_dir / source_file.name
            shutil.move(str(source_file), str(destination))

            logger.warning(
                f"File moved to failed directory: {source_file.name} (Error: {error_message})"
            )
            return destination

        except Exception as e:
            logger.error(f"Error moving file to failed directory: {e}")
            return None

    def get_organized_path(self, filename: str, file_type: str) -> Path:
        """Get the path where a file would be organized"""
        now = datetime.now()
        return (
            self.base_dir
            / file_type.lower()
            / str(now.year)
            / f"{now.month:02d}"
            / f"{now.day:02d}"
            / filename
        )
