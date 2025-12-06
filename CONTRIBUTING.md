cd /home/wtc/Desktop/Workflow-Automation-Bot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py --setup
python main.py --test# Contributing to Workflow Automation Bot

## 🤝 How to Contribute

### Setting Up Development Environment

```bash
# Clone the repo
git clone https://github.com/SibabalweMnete/workflow-automation-bot.git
cd workflow-automation-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies + dev tools
pip install -r requirements.txt
pip install pytest pytest-cov black flake8
```

### Code Style

We use:
- **Black** for formatting: `black src/ tests/`
- **Flake8** for linting: `flake8 src/ tests/`
- **Type hints** for better code clarity

### Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src

# Run specific test file
python -m pytest tests/test_processor.py -v
```

### Adding New Features

1. **New File Type Support**
   - Add processor method in `src/file_processor.py`
   - Add validation logic
   - Add tests in `tests/test_processor.py`
   - Update `config/rules.json` with default rules

2. **New Notification Channel**
   - Add method to `Notifier` class in `src/notifier.py`
   - Implement channel-specific formatting
   - Add configuration options in `config/rules.json`
   - Document in README

3. **New Features**
   - Create feature branch: `git checkout -b feature/your-feature`
   - Write tests first (TDD)
   - Implement feature
   - Update documentation
   - Submit pull request

### Project Structure Overview

```
src/
├── __init__.py           # Package initialization
├── config.py             # Configuration loader
├── file_monitor.py       # File system watcher
├── file_processor.py     # Processing logic
├── organizer.py          # File organization
└── notifier.py           # Notification system

tests/
├── __init__.py
└── test_processor.py     # Unit tests

config/
└── rules.json            # Processing rules configuration
```

### Key Classes and Methods

**FileMonitor**
- `start_monitoring(callback)` - Start watching directory
- `stop_monitoring()` - Stop watching

**FileProcessor**
- `process_file(filepath)` - Process a file
- `validate_file(filepath)` - Validate before processing

**FileOrganizer**
- `organize_file(source, file_type)` - Move to organized location
- `move_to_failed(source, error_msg)` - Move failed files

**Notifier**
- `notify_success(result)` - Send success notification
- `notify_failure(result)` - Send failure notification

### Adding Tests

Example test structure:
```python
def test_process_csv_with_duplicates(processor):
    """Test CSV processing with duplicate removal"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("id,value\n1,100\n1,100\n2,200\n")
        filepath = Path(f.name)
    
    try:
        success, result = processor.process_file(filepath)
        assert success is True
        assert result["duplicates_removed"] == 1
    finally:
        filepath.unlink()
```

## 🐛 Bug Reports

Please include:
- OS and Python version
- Steps to reproduce
- Expected vs actual behavior
- Relevant log output from `logs/automation.log`

## 📝 Documentation

- Update README.md for major features
- Add docstrings to all functions
- Include type hints
- Document configuration options

## 🔄 Git Workflow

1. Fork the repository
2. Create feature branch: `git checkout -b feature/your-feature`
3. Make changes with clear commit messages
4. Run tests: `pytest tests/`
5. Push to your fork
6. Create Pull Request with description

## 💡 Ideas for Contributions

- [ ] Slack integration
- [ ] Email notifications
- [ ] Web dashboard
- [ ] Support for PDF/XML files
- [ ] Anomaly detection
- [ ] REST API
- [ ] Cloud storage integration
- [ ] Parallel file processing
- [ ] Advanced scheduling
- [ ] Webhooks

## 📚 Resources

- **watchdog**: https://watchdog.readthedocs.io/
- **pandas**: https://pandas.pydata.org/docs/
- **Python logging**: https://docs.python.org/3/library/logging.html

## ✨ Code Example: Adding Slack Support

```python
# In notifier.py
import requests

def notify_slack(self, result: ProcessingResult, webhook_url: str) -> None:
    """Send Slack notification"""
    message = {
        "text": f"🤖 Workflow Complete: {result.filename}",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*File:* {result.filename}\n"
                            f"*Status:* {'✅ Success' if result.success else '❌ Failed'}\n"
                            f"*Records:* {result.records_processed:,}"
                }
            }
        ]
    }
    try:
        requests.post(webhook_url, json=message)
    except Exception as e:
        self.logger.error(f"Failed to send Slack notification: {e}")
```

---

Thank you for contributing! 🙏
