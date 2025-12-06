"""Unit tests for the Workflow Automation Bot"""
import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.config import Config
from src.file_processor import DataValidationError, FileProcessor
from src.notifier import Notifier, ProcessingResult
from src.organizer import FileOrganizer


class TestConfig:
    """Tests for configuration management"""

    def test_config_loading(self):
        """Test configuration file loading"""
        config = Config()
        assert config.config is not None
        assert "csv" in config.config
        assert "json" in config.config
        assert "excel" in config.config

    def test_config_get_nested(self):
        """Test nested configuration retrieval"""
        config = Config()
        csv_config = config.get_nested("csv")
        assert csv_config is not None
        assert "remove_duplicates" in csv_config

    def test_config_default_values(self):
        """Test default configuration values"""
        config = Config()
        csv_remove_dupes = config.get_nested("csv", "remove_duplicates")
        assert csv_remove_dupes is True


class TestFileProcessor:
    """Tests for file processing"""

    @pytest.fixture
    def processor(self):
        """Create processor with default config"""
        config_dict = {
            "csv": {
                "remove_duplicates": True,
                "handle_missing": "fill_zeros",
                "required_columns": ["id", "value"],
                "date_format": "%Y-%m-%d",
            },
            "json": {
                "validate_schema": True,
                "required_fields": ["data"],
            },
            "excel": {
                "remove_duplicates": True,
                "handle_missing": "fill_zeros",
                "required_columns": ["id", "value"],
            },
        }
        return FileProcessor(config_dict)

    def test_detect_csv_file(self, processor):
        """Test CSV file type detection"""
        filepath = Path("test.csv")
        file_type = processor._detect_file_type(filepath)
        assert file_type == "csv"

    def test_detect_json_file(self, processor):
        """Test JSON file type detection"""
        filepath = Path("test.json")
        file_type = processor._detect_file_type(filepath)
        assert file_type == "json"

    def test_detect_excel_file(self, processor):
        """Test Excel file type detection"""
        filepath = Path("test.xlsx")
        file_type = processor._detect_file_type(filepath)
        assert file_type == "excel"

    def test_detect_unknown_file(self, processor):
        """Test unknown file type detection raises error"""
        filepath = Path("test.txt")
        with pytest.raises(ValueError):
            processor._detect_file_type(filepath)

    def test_validate_nonexistent_file(self, processor):
        """Test validation of non-existent file"""
        filepath = Path("nonexistent.csv")
        is_valid, error = processor.validate_file(filepath)
        assert is_valid is False
        assert error is not None

    def test_process_csv_success(self, processor):
        """Test successful CSV processing"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("id,value\n1,100\n2,200\n")
            filepath = Path(f.name)

        try:
            success, result = processor.process_file(filepath)
            assert success is True
            assert result["records_processed"] == 2
            assert "file_type" in result
        finally:
            filepath.unlink()
            Path(f"{filepath.stem}_processed.csv").unlink(missing_ok=True)

    def test_process_json_success(self, processor):
        """Test successful JSON processing"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"data": [{"id": 1}, {"id": 2}]}, f)
            filepath = Path(f.name)

        try:
            success, result = processor.process_file(filepath)
            assert success is True
            assert result["records_processed"] >= 1
        finally:
            filepath.unlink()
            Path(f"{filepath.stem}_processed.json").unlink(missing_ok=True)


class TestFileOrganizer:
    """Tests for file organization"""

    @pytest.fixture
    def organizer(self):
        """Create organizer with temp directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield FileOrganizer(tmpdir)

    def test_organize_creates_directories(self, organizer):
        """Test that organize creates proper directories"""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            filepath = Path(f.name)

        try:
            result = organizer.organize_file(filepath, "csv")
            assert result is not None
            assert result.exists()
            assert "csv" in str(result)
        finally:
            filepath.unlink(missing_ok=True)

    def test_move_to_failed(self, organizer):
        """Test moving file to failed directory"""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            f.write(b"test data")
            filepath = Path(f.name)

        try:
            result = organizer.move_to_failed(filepath, "Test error message")
            assert result is not None
        finally:
            filepath.unlink(missing_ok=True)


class TestNotifier:
    """Tests for notification system"""

    @pytest.fixture
    def notifier(self):
        """Create notifier with test config"""
        config = {"console": True, "log_file": True}
        return Notifier(config)

    def test_processing_result_to_dict(self):
        """Test conversion of ProcessingResult to dictionary"""
        result = ProcessingResult(
            filename="test.csv",
            success=True,
            records_processed=100,
            duplicates_removed=5,
            missing_values_handled=2,
            processing_time=1.5,
            output_path="/path/to/output.csv",
        )

        result_dict = result.to_dict()
        assert result_dict["filename"] == "test.csv"
        assert result_dict["success"] is True
        assert result_dict["records_processed"] == 100

    def test_format_success_message(self, notifier):
        """Test success message formatting"""
        result = ProcessingResult(
            filename="test.csv",
            success=True,
            records_processed=100,
            duplicates_removed=5,
            missing_values_handled=2,
            processing_time=1.5,
            output_path="/path/to/output.csv",
        )

        message = notifier._format_success_message(result)
        assert "SUCCESS" in message
        assert "test.csv" in message
        assert "100" in message

    def test_format_failure_message(self, notifier):
        """Test failure message formatting"""
        result = ProcessingResult(
            filename="test.csv",
            success=False,
            error_message="CSV parsing error",
        )

        message = notifier._format_failure_message(result)
        assert "FAILURE" in message
        assert "test.csv" in message
        assert "CSV parsing error" in message


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
