"""File processing system for different file types"""
import json
import logging
import time
from pathlib import Path
from typing import Dict, Optional, Tuple

import pandas as pd

logger = logging.getLogger(__name__)


class DataValidationError(Exception):
    """Raised when data validation fails"""

    pass


class FileProcessor:
    """Processes different file types (CSV, JSON, Excel)"""

    def __init__(self, config: dict):
        """
        Initialize file processor.

        Args:
            config: Configuration dictionary from config object
        """
        self.csv_config = config.get("csv", {})
        self.json_config = config.get("json", {})
        self.excel_config = config.get("excel", {})

    def process_file(self, filepath: Path) -> Tuple[bool, Dict]:
        """
        Process a file based on its type.

        Args:
            filepath: Path to file to process

        Returns:
            Tuple of (success, result_dict) where result_dict contains processing stats
        """
        start_time = time.time()

        try:
            file_type = self._detect_file_type(filepath)
            logger.info(f"Processing {file_type.upper()} file: {filepath.name}")

            if file_type == "csv":
                result = self._process_csv(filepath)
            elif file_type == "json":
                result = self._process_json(filepath)
            elif file_type == "excel":
                result = self._process_excel(filepath)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")

            processing_time = time.time() - start_time
            result["processing_time"] = processing_time
            result["file_type"] = file_type

            logger.info(f"✅ File processing successful: {filepath.name}")
            return True, result

        except DataValidationError as e:
            logger.error(f"Validation error in {filepath.name}: {e}")
            return False, {
                "error": str(e),
                "processing_time": time.time() - start_time,
            }
        except Exception as e:
            logger.error(f"Unexpected error processing {filepath.name}: {e}")
            return False, {
                "error": str(e),
                "processing_time": time.time() - start_time,
            }

    def _detect_file_type(self, filepath: Path) -> str:
        """Detect file type from extension"""
        extension = filepath.suffix.lower()
        if extension == ".csv":
            return "csv"
        elif extension == ".json":
            return "json"
        elif extension in [".xlsx", ".xls"]:
            return "excel"
        else:
            raise ValueError(f"Unknown file extension: {extension}")

    def _process_csv(self, filepath: Path) -> Dict:
        """
        Process CSV file.

        Args:
            filepath: Path to CSV file

        Returns:
            Dictionary with processing statistics
        """
        config = self.csv_config
        result = {
            "records_processed": 0,
            "duplicates_removed": 0,
            "missing_values_handled": 0,
        }

        try:
            # Read CSV
            df = pd.read_csv(filepath)
            result["records_processed"] = len(df)
            logger.info(f"Loaded {len(df)} records from CSV")

            # Validate required columns
            required_cols = config.get("required_columns", [])
            if required_cols:
                missing_cols = [col for col in required_cols if col not in df.columns]
                if missing_cols:
                    raise DataValidationError(
                        f"Missing required columns: {missing_cols}"
                    )

            # Remove duplicates
            if config.get("remove_duplicates", False):
                before_dedup = len(df)
                df = df.drop_duplicates()
                result["duplicates_removed"] = before_dedup - len(df)
                logger.info(f"Removed {result['duplicates_removed']} duplicate records")

            # Handle missing values
            handle_missing = config.get("handle_missing", None)
            if handle_missing == "fill_zeros":
                numeric_cols = df.select_dtypes(include=["number"]).columns
                before_na = df.isna().sum().sum()
                df[numeric_cols] = df[numeric_cols].fillna(0)
                result["missing_values_handled"] = before_na
                logger.info(f"Filled {before_na} missing values with zeros")

            # Standardize date formats
            date_format = config.get("date_format", "%Y-%m-%d")
            for col in df.columns:
                if "date" in col.lower():
                    try:
                        df[col] = pd.to_datetime(df[col]).dt.strftime(date_format)
                    except Exception as e:
                        logger.warning(f"Could not standardize date column {col}: {e}")

            # Save processed data
            output_path = filepath.parent / f"{filepath.stem}_processed.csv"
            df.to_csv(output_path, index=False)
            result["output_file"] = str(output_path)
            logger.info(f"Processed CSV saved to {output_path}")

            return result

        except DataValidationError:
            raise
        except Exception as e:
            raise DataValidationError(f"CSV processing error: {str(e)}")

    def _process_json(self, filepath: Path) -> Dict:
        """
        Process JSON file.

        Args:
            filepath: Path to JSON file

        Returns:
            Dictionary with processing statistics
        """
        config = self.json_config
        result = {
            "records_processed": 0,
            "duplicates_removed": 0,
            "missing_values_handled": 0,
        }

        try:
            # Read JSON
            with open(filepath, "r") as f:
                data = json.load(f)

            # Validate schema
            if config.get("validate_schema", False):
                required_fields = config.get("required_fields", [])
                if isinstance(data, dict):
                    missing = [f for f in required_fields if f not in data]
                    if missing:
                        raise DataValidationError(
                            f"Missing required fields: {missing}"
                        )
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict):
                            missing = [f for f in required_fields if f not in item]
                            if missing:
                                raise DataValidationError(
                                    f"Missing required fields in item: {missing}"
                                )

            # Count records
            if isinstance(data, list):
                result["records_processed"] = len(data)
            else:
                result["records_processed"] = 1

            # Save processed JSON
            output_path = filepath.parent / f"{filepath.stem}_processed.json"
            with open(output_path, "w") as f:
                json.dump(data, f, indent=2)
            result["output_file"] = str(output_path)

            logger.info(f"Processed JSON file with {result['records_processed']} records")
            return result

        except DataValidationError:
            raise
        except Exception as e:
            raise DataValidationError(f"JSON processing error: {str(e)}")

    def _process_excel(self, filepath: Path) -> Dict:
        """
        Process Excel file.

        Args:
            filepath: Path to Excel file

        Returns:
            Dictionary with processing statistics
        """
        config = self.excel_config
        result = {
            "records_processed": 0,
            "duplicates_removed": 0,
            "missing_values_handled": 0,
        }

        try:
            # Read Excel
            df = pd.read_excel(filepath)
            result["records_processed"] = len(df)
            logger.info(f"Loaded {len(df)} records from Excel")

            # Validate required columns
            required_cols = config.get("required_columns", [])
            if required_cols:
                missing_cols = [col for col in required_cols if col not in df.columns]
                if missing_cols:
                    raise DataValidationError(
                        f"Missing required columns: {missing_cols}"
                    )

            # Remove duplicates
            if config.get("remove_duplicates", False):
                before_dedup = len(df)
                df = df.drop_duplicates()
                result["duplicates_removed"] = before_dedup - len(df)
                logger.info(f"Removed {result['duplicates_removed']} duplicate records")

            # Handle missing values
            handle_missing = config.get("handle_missing", None)
            if handle_missing == "fill_zeros":
                numeric_cols = df.select_dtypes(include=["number"]).columns
                before_na = df.isna().sum().sum()
                df[numeric_cols] = df[numeric_cols].fillna(0)
                result["missing_values_handled"] = before_na
                logger.info(f"Filled {before_na} missing values with zeros")

            # Save processed Excel
            output_path = filepath.parent / f"{filepath.stem}_processed.xlsx"
            df.to_excel(output_path, index=False)
            result["output_file"] = str(output_path)
            logger.info(f"Processed Excel file saved to {output_path}")

            return result

        except DataValidationError:
            raise
        except Exception as e:
            raise DataValidationError(f"Excel processing error: {str(e)}")

    def validate_file(self, filepath: Path) -> Tuple[bool, Optional[str]]:
        """
        Validate file before processing.

        Args:
            filepath: Path to file to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check file exists
            if not filepath.exists():
                return False, "File does not exist"

            # Check file is readable
            if not filepath.is_file():
                return False, "Path is not a file"

            # Check file size (basic check)
            size_mb = filepath.stat().st_size / (1024 * 1024)
            if size_mb > 1000:  # 1GB limit
                return False, f"File too large: {size_mb:.2f}MB"

            # Try to read based on type
            file_type = self._detect_file_type(filepath)
            if file_type == "csv":
                pd.read_csv(filepath, nrows=1)
            elif file_type == "json":
                with open(filepath, "r") as f:
                    json.load(f)
            elif file_type == "excel":
                pd.read_excel(filepath, nrows=1)

            return True, None

        except Exception as e:
            return False, f"Validation error: {str(e)}"
