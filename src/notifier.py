"""Notification system for workflow completion alerts"""
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """Result of a file processing operation"""

    filename: str
    success: bool
    records_processed: int = 0
    duplicates_removed: int = 0
    missing_values_handled: int = 0
    processing_time: float = 0.0
    error_message: Optional[str] = None
    output_path: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert result to dictionary"""
        return {
            "filename": self.filename,
            "success": self.success,
            "records_processed": self.records_processed,
            "duplicates_removed": self.duplicates_removed,
            "missing_values_handled": self.missing_values_handled,
            "processing_time": self.processing_time,
            "error_message": self.error_message,
            "output_path": self.output_path,
        }


class Notifier:
    """Handles notifications for workflow completion"""

    def __init__(self, config: dict):
        """
        Initialize notifier.

        Args:
            config: Configuration dictionary from config.get('notifications')
        """
        self.config = config
        self.console_enabled = config.get("console", True)
        self.log_file_enabled = config.get("log_file", True)

    def notify_success(self, result: ProcessingResult) -> None:
        """Notify about successful file processing"""
        message = self._format_success_message(result)
        self._send_notification(message, "SUCCESS")

    def notify_failure(self, result: ProcessingResult) -> None:
        """Notify about failed file processing"""
        message = self._format_failure_message(result)
        self._send_notification(message, "ERROR")

    def _format_success_message(self, result: ProcessingResult) -> str:
        """Format success notification message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"""
🔔 NOTIFICATION SENT - SUCCESS
⏰ Timestamp: {timestamp}
📄 File: {result.filename}

📊 Processing Details:
   • Records processed: {result.records_processed:,}
   • Duplicates removed: {result.duplicates_removed}
   • Missing values handled: {result.missing_values_handled}
   • Processing time: {result.processing_time:.2f}s

📁 Output Location: {result.output_path}
✅ Workflow completed successfully
"""
        return message

    def _format_failure_message(self, result: ProcessingResult) -> str:
        """Format failure notification message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"""
🔔 NOTIFICATION SENT - FAILURE
⏰ Timestamp: {timestamp}
📄 File: {result.filename}

❌ Error: {result.error_message}
⚠️ Workflow failed - check logs for details
"""
        return message

    def _send_notification(self, message: str, level: str) -> None:
        """
        Send notification through enabled channels.

        Args:
            message: Notification message
            level: Log level (SUCCESS, ERROR, WARNING)
        """
        if self.console_enabled:
            self._notify_console(message, level)
        if self.log_file_enabled:
            self._notify_log(message, level)

    @staticmethod
    def _notify_console(message: str, level: str) -> None:
        """Send notification to console"""
        if level == "SUCCESS":
            logger.info(message)
        elif level == "ERROR":
            logger.error(message)
        else:
            logger.warning(message)

    @staticmethod
    def _notify_log(message: str, level: str) -> None:
        """Log notification to file"""
        logger.info(f"[NOTIFICATION] {message}")

    # Future extensions for Slack, Email, Teams, etc.
    def notify_slack(self, result: ProcessingResult) -> None:
        """Send Slack notification (future implementation)"""
        logger.warning("Slack notifications not yet implemented")

    def notify_email(self, result: ProcessingResult) -> None:
        """Send Email notification (future implementation)"""
        logger.warning("Email notifications not yet implemented")

    def notify_webhook(self, result: ProcessingResult, webhook_url: str) -> None:
        """Send webhook notification (future implementation)"""
        logger.warning("Webhook notifications not yet implemented")
