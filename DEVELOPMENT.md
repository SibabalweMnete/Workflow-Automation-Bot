# 🚀 Development Tips & Best Practices

## Running the Application

### Normal Operation
```bash
python main.py
```
- Runs continuously, monitoring watched/incoming/
- Press Ctrl+C to stop gracefully

### Test Mode
```bash
python main.py --test
```
- Process all files in watched/incoming/ once
- Useful for quick testing
- Exits after completion

### Verbose Mode
```bash
python main.py --verbose
```
- Enables DEBUG level logging
- More detailed output
- Useful for troubleshooting

### Custom Watch Directory
```bash
python main.py --watch /path/to/folder
```
- Monitors a specific directory
- Useful for testing different locations

### Setup Mode
```bash
python main.py --setup
```
- Creates all required directories
- Safe to run multiple times
- No files are modified

## Testing Workflow

### Run All Tests
```bash
python -m pytest tests/ -v
```

### Run Specific Test
```bash
python -m pytest tests/test_processor.py::TestFileProcessor::test_process_csv_success -v
```

### Run with Coverage
```bash
python -m pytest tests/ --cov=src --cov-report=html
```

### Quick Sanity Check
```bash
python -m pytest tests/test_processor.py -x -v
# -x: Stop on first failure
# -v: Verbose output
```

## Debugging Tips

### Enable Maximum Logging
```python
# In your test or main script
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Configuration
```python
from src.config import Config
config = Config()
print(config.config)  # Print entire configuration
```

### Test File Processing Directly
```python
from pathlib import Path
from src.file_processor import FileProcessor
from src.config import Config

config = Config()
processor = FileProcessor(config.config)
success, result = processor.process_file(Path("test.csv"))
print(f"Success: {success}")
print(f"Result: {result}")
```

### Monitor Logs in Real-Time
```bash
tail -f logs/automation.log
# In another terminal:
python main.py
```

### Check File Organization
```bash
tree processed/  # If you have tree installed
find processed/ -type f  # Alternative
```

## Common Issues & Solutions

### Issue: "No module named 'watchdog'"
**Solution:**
```bash
pip install --upgrade watchdog
```

### Issue: "No module named 'pandas'"
**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: Files not being detected
**Checklist:**
1. Is bot running? (check terminal)
2. File extension supported? (.csv, .json, .xlsx, .xls)
3. File in watched/incoming/? 
4. Check logs/automation.log for errors
5. Ensure file is fully written before being moved

### Issue: Import errors in IDE
**Solution:**
1. Select correct Python interpreter (from venv)
2. Restart IDE
3. Run `pip install -r requirements.txt` again

### Issue: "Permission denied" errors
**Solution:**
```bash
chmod 755 watched/incoming/  # Linux/Mac
# Windows: Right-click folder → Properties → Security
```

## Code Navigation

### Understanding the Flow
1. **main.py** → Entry point and CLI handling
2. **FileMonitor** (file_monitor.py) → Detects files
3. **FileProcessor** (file_processor.py) → Processes data
4. **FileOrganizer** (organizer.py) → Moves files
5. **Notifier** (notifier.py) → Sends notifications

### Key Classes and Methods

**FileMonitor**
```python
from src.file_monitor import FileMonitor
monitor = FileMonitor("watched/incoming")
monitor.start_monitoring(callback_function)
monitor.stop_monitoring()
```

**FileProcessor**
```python
from src.file_processor import FileProcessor
processor = FileProcessor(config_dict)
success, result = processor.process_file(filepath)
is_valid, error = processor.validate_file(filepath)
```

**FileOrganizer**
```python
from src.organizer import FileOrganizer
organizer = FileOrganizer("processed")
output_path = organizer.organize_file(filepath, "csv")
organizer.move_to_failed(filepath, "error message")
```

## Extending the System

### Add a New File Type

1. **Add processor method:**
```python
# In src/file_processor.py
def _process_parquet(self, filepath: Path) -> Dict:
    """Process Parquet file"""
    config = self.parquet_config
    # ... implementation
    return {"records_processed": count, ...}
```

2. **Add to file type detection:**
```python
def _detect_file_type(self, filepath: Path) -> str:
    extension = filepath.suffix.lower()
    # ... existing code ...
    elif extension == ".parquet":
        return "parquet"
```

3. **Add configuration:**
```json
{
  "parquet": {
    "remove_duplicates": true,
    "handle_missing": "fill_zeros"
  }
}
```

4. **Add tests:**
```python
def test_process_parquet_success(processor):
    # Implementation
```

5. **Update supported extensions:**
```python
# In file_monitor.py
self.supported_extensions = (".csv", ".json", ".xlsx", ".xls", ".parquet")
```

### Add a Notification Channel

1. **Implement method in Notifier:**
```python
def notify_slack(self, result: ProcessingResult) -> None:
    if not self.config.get("slack", {}).get("enabled"):
        return
    
    webhook_url = self.config.get("slack", {}).get("webhook_url")
    # ... implementation
```

2. **Add configuration:**
```json
{
  "notifications": {
    "slack": {
      "enabled": true,
      "webhook_url": "https://hooks.slack.com/..."
    }
  }
}
```

3. **Call from main:**
```python
self.notifier.notify_slack(result)
```

## Performance Optimization

### For Large Files
```python
# Process in chunks
def process_large_csv(filepath):
    for chunk in pd.read_csv(filepath, chunksize=10000):
        # Process chunk
        pass
```

### For Multiple Files
```python
# Use thread pool (future enhancement)
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(process_file, f) for f in files]
```

### Memory Efficiency
```python
# Use streaming where possible
# Delete processed files to free space
# Archive old logs
```

## Best Practices

### Code Organization
- ✅ Keep functions focused and small
- ✅ Use meaningful variable names
- ✅ Add docstrings to all functions
- ✅ Use type hints for clarity

### Error Handling
- ✅ Catch specific exceptions
- ✅ Log detailed error information
- ✅ Provide meaningful error messages
- ✅ Clean up resources in finally blocks

### Testing
- ✅ Test happy path
- ✅ Test error cases
- ✅ Use fixtures for setup
- ✅ Mock external dependencies

### Configuration
- ✅ Keep defaults in code
- ✅ Allow file-based overrides
- ✅ Validate configuration on load
- ✅ Document all options

## Git Workflow

### Before Committing
```bash
# Check tests pass
python -m pytest tests/ -v

# Format code
black src/ tests/

# Check for lint issues
flake8 src/ tests/
```

### Good Commit Messages
```
✨ Add Slack notification support
🐛 Fix duplicate detection in CSV processing
📝 Update documentation for configuration
🔄 Refactor file organization logic
```

## Useful Commands

```bash
# Find all TODO comments
grep -r "TODO" src/

# Count lines of code
find src -name "*.py" | xargs wc -l

# Check file sizes in processed/
du -sh processed/

# Clean up old processed files
find processed/ -mtime +30 -delete  # Files older than 30 days

# Monitor real-time logs
watch -n 1 tail logs/automation.log

# Generate test coverage report
python -m pytest tests/ --cov=src --cov-report=term-missing
```

## IDE Setup

### VS Code
1. Install Python extension
2. Select venv interpreter: Ctrl+Shift+P → Python: Select Interpreter
3. Install pylance for better intellisense

### PyCharm
1. File → Settings → Project → Python Interpreter
2. Select venv
3. Mark src/ as Sources Root

### Recommended Extensions
- Python (pylance)
- Pylint or Flake8
- Black Formatter
- Pytest

---

**Happy coding!** 🚀
