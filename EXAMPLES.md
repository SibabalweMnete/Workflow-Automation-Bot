# 📝 Example Usage & Walkthrough

## Example 1: Basic Setup and First Run

### Step 1: Create Virtual Environment
```bash
cd workflow-automation-bot
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```
Expected output:
```
Collecting watchdog==3.0.0
Collecting pandas==2.1.3
Collecting openpyxl==3.11.0
Collecting python-dateutil==2.8.2
Installing collected packages: ...
Successfully installed watchdog pandas openpyxl python-dateutil
```

### Step 3: Initialize Directories
```bash
python main.py --setup
```
Expected output:
```
2024-12-06 14:23:15 [INFO] ✅ Directory structure created/verified
```

### Step 4: Create Test Data
```bash
cat > watched/incoming/sales_data.csv << 'EOF'
id,date,value
1,2024-01-01,100
2,2024-01-02,200
1,2024-01-01,100
3,2024-01-03,
EOF
```

### Step 5: Run Bot in Test Mode
```bash
python main.py --test
```

Expected output:
```
============================================================
🤖 Workflow Automation Bot Started
⏰ Timestamp: 2024-12-06 14:23:15
============================================================
2024-12-06 14:23:45 [INFO] 👁️  NEW FILE DETECTED: sales_data.csv
2024-12-06 14:23:45 [INFO] ✅ Validation passed
2024-12-06 14:23:46 [INFO] 🔄 Processing started...
2024-12-06 14:23:47 [INFO] 📊 Processing complete
           - Records processed: 3
           - Duplicates removed: 1
           - Missing values handled: 1
           - Processing time: 0.25s

2024-12-06 14:23:47 [INFO] 📁 Organizing file...
2024-12-06 14:23:47 [INFO] File organized: sales_data.csv -> csv/2024/12/06/sales_data_142345.csv
2024-12-06 14:23:47 [INFO] 🔔 NOTIFICATION SENT - SUCCESS
⏰ Timestamp: 2024-12-06 14:23:47
📄 File: sales_data.csv

📊 Processing Details:
   • Records processed: 3
   • Duplicates removed: 1
   • Missing values handled: 1
   • Processing time: 0.25s

📁 Output Location: processed/csv/2024/12/06/sales_data_142345.csv
✅ Workflow completed successfully

2024-12-06 14:23:47 [INFO] 🛑 Workflow Automation Bot Stopped
```

### Step 6: Check Results
```bash
# View processed file
ls -la processed/csv/2024/12/06/

# View logs
tail logs/automation.log

# Verify processing
head processed/csv/2024/12/06/sales_data_142345.csv
```

---

## Example 2: Continuous Monitoring

### Start Continuous Monitoring
```bash
python main.py
```

Expected output:
```
============================================================
🤖 Workflow Automation Bot Started
⏰ Timestamp: 2024-12-06 14:24:00
============================================================
2024-12-06 14:24:00 [INFO] File Monitor Started
2024-12-06 14:24:00 [INFO] 📁 Watching: /path/to/watched/incoming
```

Bot now waits for new files...

### Add Files (in another terminal)
```bash
cp your_data.csv watched/incoming/
```

Bot automatically detects and processes the file.

### Stop Bot
Press `Ctrl+C` to stop gracefully:
```
^C
2024-12-06 14:25:30 [INFO] Bot interrupted by user
2024-12-06 14:25:30 [INFO] 🛑 Workflow Automation Bot Stopped
```

---

## Example 3: Processing Different File Types

### CSV File Example
```bash
cat > watched/incoming/customers.csv << 'EOF'
customer_id,date,amount
C001,2024-01-01,1000
C002,2024-01-02,2000
C001,2024-01-01,1000
EOF

python main.py --test
```

Result: Duplicates removed, organized to `processed/csv/2024/01/01/`

### JSON File Example
```bash
cat > watched/incoming/transactions.json << 'EOF'
[
  {"id": 1, "timestamp": "2024-01-01T10:00:00", "data": {"amount": 100}},
  {"id": 2, "timestamp": "2024-01-01T11:00:00", "data": {"amount": 200}}
]
EOF

python main.py --test
```

Result: Validated and organized to `processed/json/2024/01/01/`

### Excel File Example
```bash
# Create test Excel with pandas
python << 'PYTHON'
import pandas as pd
df = pd.DataFrame({
    'id': [1, 2, 3],
    'date': ['2024-01-01', '2024-01-02', '2024-01-01'],
    'value': [100, 200, 100]
})
df.to_excel('watched/incoming/data.xlsx', index=False)
PYTHON

python main.py --test
```

Result: Deduplicated and organized to `processed/excel/2024/01/01/`

---

## Example 4: Customizing Configuration

### Edit Processing Rules
```bash
cat > config/rules.json << 'EOF'
{
  "csv": {
    "remove_duplicates": true,
    "handle_missing": "fill_zeros",
    "required_columns": ["id", "date", "amount"],
    "date_format": "%Y-%m-%d"
  },
  "json": {
    "validate_schema": true,
    "required_fields": ["id", "timestamp"]
  },
  "excel": {
    "remove_duplicates": true,
    "handle_missing": "fill_zeros",
    "required_columns": ["id", "date", "amount"]
  },
  "notifications": {
    "console": true,
    "log_file": true,
    "slack": false
  }
}
EOF
```

### Test New Configuration
```bash
python main.py --test
```

Bot will validate using new rules.

---

## Example 5: Error Handling

### Missing Required Column
```bash
cat > watched/incoming/invalid.csv << 'EOF'
id,value
1,100
2,200
EOF

python main.py --test
```

Expected: File moves to `failed/` with error log
```
2024-12-06 14:26:00 [ERROR] ❌ Validation failed: Missing required columns: ['date', 'amount']
```

### Corrupted File
```bash
echo "not a valid csv,file" > watched/incoming/corrupted.csv
python main.py --test
```

Expected: File moves to `failed/` with detailed error message

---

## Example 6: Verbose Debugging

### Run with Debug Output
```bash
python main.py --verbose
```

Shows DEBUG level logs:
```
2024-12-06 14:27:00 [DEBUG] File ready: test.csv (size: 1024 bytes)
2024-12-06 14:27:00 [DEBUG] Detecting file type from extension: .csv
2024-12-06 14:27:01 [DEBUG] Loading CSV with pandas...
2024-12-06 14:27:01 [DEBUG] Checking required columns: ['id', 'date', 'value']
2024-12-06 14:27:01 [DEBUG] Removing 2 duplicate records
```

---

## Example 7: Monitoring Large Operations

### Watch Multiple Files
```bash
# Terminal 1: Monitor logs
tail -f logs/automation.log

# Terminal 2: Copy multiple files
for i in {1..5}; do
  cp template.csv watched/incoming/file_$i.csv
done

# Terminal 3: Run bot
python main.py
```

Bot processes all files:
```
[14:28:00] 👁️  NEW FILE DETECTED: file_1.csv
[14:28:02] ✅ Workflow completed successfully
[14:28:02] 👁️  NEW FILE DETECTED: file_2.csv
[14:28:04] ✅ Workflow completed successfully
...
```

---

## Example 8: Checking Processing Results

### View Processed Files
```bash
# List by date
ls -la processed/csv/2024/12/06/

# Count processed files
find processed -type f | wc -l

# Check file organization
tree processed/

# View specific file
head -5 processed/csv/2024/12/06/data_142345.csv
```

### Review Logs
```bash
# Last 20 lines
tail -20 logs/automation.log

# Search for errors
grep ERROR logs/automation.log

# Count successful processes
grep "Workflow completed successfully" logs/automation.log | wc -l
```

---

## Example 9: Testing Edge Cases

### Empty File
```bash
touch watched/incoming/empty.csv
python main.py --test
```

Expected: Processed but noted as 0 records

### Large File (simulate)
```bash
python << 'PYTHON'
import pandas as pd
df = pd.DataFrame({
    'id': range(10000),
    'value': range(10000)
})
df.to_csv('watched/incoming/large.csv', index=False)
PYTHON

python main.py --test --verbose
```

Expected: Processed and timed

### Special Characters in Filename
```bash
cp template.csv "watched/incoming/data with spaces & symbols.csv"
python main.py --test
```

Expected: Handled gracefully

---

## Example 10: Performance Testing

### Benchmark Single File
```bash
python << 'PYTHON'
import time
from pathlib import Path
from src.file_processor import FileProcessor
from src.config import Config

config = Config()
processor = FileProcessor(config.config)

# Create test file
import pandas as pd
df = pd.DataFrame({'id': range(1000), 'value': range(1000)})
df.to_csv('test_large.csv', index=False)

start = time.time()
success, result = processor.process_file(Path('test_large.csv'))
elapsed = time.time() - start

print(f"Time: {elapsed:.2f}s")
print(f"Records: {result['records_processed']}")
print(f"Records/sec: {result['records_processed']/elapsed:.0f}")
PYTHON
```

---

## Example 11: Running Tests

### Run All Tests
```bash
python -m pytest tests/ -v
```

### Run Specific Test
```bash
python -m pytest tests/test_processor.py::TestFileProcessor::test_process_csv_success -v
```

### Generate Coverage Report
```bash
python -m pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html  # View in browser
```

---

## Summary

These examples show how to:
- ✅ Set up and initialize the system
- ✅ Process different file types
- ✅ Customize configuration
- ✅ Handle errors and edge cases
- ✅ Monitor operations
- ✅ Debug issues
- ✅ Test performance
- ✅ Run unit tests

For more detailed documentation, see:
- [README.md](README.md) - Full features and documentation
- [QUICKSTART.md](QUICKSTART.md) - Quick setup guide
- [DEVELOPMENT.md](DEVELOPMENT.md) - Advanced topics
