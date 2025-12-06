# Quick Start Guide - Workflow Automation Bot

## 🚀 5-Minute Setup

### Step 1: Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Initialize Directories
```bash
python main.py --setup
```

### Step 4: Test the Bot
```bash
# Drop a CSV file in watched/incoming/ to test
python main.py --test
```

### Step 5: Run Continuously
```bash
python main.py
```

## 📁 Directory Structure Created

After setup, you'll have:
```
workflow-automation-bot/
├── watched/incoming/          ← Drop files here
├── processed/
│   ├── csv/
│   ├── json/
│   └── excel/
├── failed/                     ← Failed files go here
└── logs/
    └── automation.log         ← Activity log
```

## ⚙️ Configuration

Edit `config/rules.json` to customize:
- Which columns are required
- How to handle missing values
- Date format standards
- Notification preferences

## 🧪 Testing

```bash
# Run unit tests
python -m pytest tests/test_processor.py -v

# Run in test mode (process once and exit)
python main.py --test

# Run with verbose logging
python main.py --verbose
```

## 🎯 Common Tasks

### Process a Specific Directory
```bash
python main.py --watch /path/to/your/folder
```

### Enable Verbose Output
```bash
python main.py --verbose
```

### Stop the Bot
Press `Ctrl+C` to gracefully stop monitoring

## 📊 Example: Process Sample Data

1. Create a test CSV file:
```bash
cat > watched/incoming/test_data.csv << 'EOF'
id,date,value
1,2024-01-01,100
2,2024-01-02,200
3,2024-01-01,100
EOF
```

2. Run the bot:
```bash
python main.py --test
```

3. Check the results:
```bash
ls -la processed/csv/2024/01/01/
cat logs/automation.log
```

## 🔧 File Processor Features

### Automatic Features:
- ✅ Duplicate removal
- ✅ Missing value handling
- ✅ Date format standardization
- ✅ File organization by type and date
- ✅ Comprehensive error logging
- ✅ Validation before processing

### Supported Formats:
- CSV
- JSON
- Excel (.xlsx, .xls)

## 🐛 Troubleshooting

### Bot not detecting files?
- Check that files are being dropped in `watched/incoming/`
- Ensure file has supported extension (.csv, .json, .xlsx, .xls)
- Check `logs/automation.log` for errors

### Import errors?
```bash
pip install -r requirements.txt
python -m pip install --upgrade watchdog pandas openpyxl
```

### Files moving to failed folder?
- Review `logs/automation.log` for error messages
- Check `config/rules.json` for required columns
- Verify CSV format matches requirements

## 📈 Monitoring

Watch logs in real-time:
```bash
tail -f logs/automation.log
```

Check file organization:
```bash
tree processed/
```

## 🔄 Development

Extend functionality:
- Add new file types in `src/file_processor.py`
- Implement Slack notifications in `src/notifier.py`
- Add webhook support for integrations
- Implement retry logic with backoff

## 📝 Author Notes

This bot demonstrates:
- Event-driven architecture patterns
- Robust error handling strategies
- ETL pipeline design
- Production-ready logging
- Clean, modular code structure

---

**Happy automating!** 🤖
