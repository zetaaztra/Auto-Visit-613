# 🚀 Quick Start Guide - How to Run & Scale Visitors

## 📋 Table of Contents
1. [Initial Setup (5 minutes)](#initial-setup-5-minutes)
2. [Run Locally](#run-locally)
3. [Increase Visitors](#increase-visitors)
4. [GitHub Actions Setup](#github-actions-setup)
5. [Monitoring & Troubleshooting](#monitoring--troubleshooting)

---

## Initial Setup (5 minutes)

### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/Auto-Visit-613.git
cd Auto-Visit-613
```

### Step 2: Install Python Dependencies
```bash
# Windows
pip install -r requirements.txt

# macOS/Linux
pip3 install -r requirements.txt
```

**What gets installed:**
- `selenium` - Browser automation
- `undetected-chromedriver` - Anti-detection browser
- `requests` - HTTP requests for proxies

### Step 3: Install Chrome/Chromium
**Windows:**
```bash
# Already installed on most Windows systems
# Or download from: https://www.google.com/chrome/
```

**macOS:**
```bash
brew install chromium
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install chromium-browser
```

### Step 4: Configure Your Websites
Edit `fraud_detection_tester.py` and find line 38:

```python
WEBSITES = [
    "https://your-site-1.com",
    "https://your-site-2.com",
    "https://your-site-3.com",
]
```

Replace with your actual websites:
```python
WEBSITES = [
    "https://pravinmathew613.netlify.app/",
    "https://tradyxa-alephx.pages.dev/",
]
```

---

## Run Locally

### Basic Run (25 Visitors)
```bash
python fraud_detection_tester.py
```

**What happens:**
- Generates 25 random visitors
- Each visit takes ~30-60 seconds
- Total time: ~12-25 minutes
- Logs to `fraud_detection_test.log`

### Custom Visitor Count
**Windows (PowerShell):**
```bash
$env:DAILY_VISITS=50; python fraud_detection_tester.py
```

**macOS/Linux (Bash):**
```bash
export DAILY_VISITS=50 && python fraud_detection_tester.py
```

### Monitor in Real-Time
**Windows (PowerShell):**
```bash
Get-Content fraud_detection_test.log -Wait
```

**macOS/Linux:**
```bash
tail -f fraud_detection_test.log
```

### View Results When Done
```bash
# Session report
grep "ADSTERRA IMPRESSION REPORT" -A 10 fraud_detection_test.log

# All impressions
grep "REAL IMPRESSIONS GENERATED" fraud_detection_test.log

# Ad interactions
grep "AD HOVER\|AD CLICK\|AD VIEW" fraud_detection_test.log
```

---

## Increase Visitors

### Strategy 1: Single Daily Run (100-150 Visitors)
**Best for:** Testing, small sites

```bash
# Run 100 visitors at once
$env:DAILY_VISITS=100; python fraud_detection_tester.py

# Duration: ~50 minutes
# Impressions: ~400-600 total
```

### Strategy 2: Multiple Runs Per Day (200+ Visitors)
**Best for:** Distributed traffic

**Terminal 1:**
```bash
$env:DAILY_VISITS=50; python fraud_detection_tester.py
```

**Terminal 2 (wait 5 minutes, then run):**
```bash
$env:DAILY_VISITS=50; python fraud_detection_tester.py
```

**Terminal 3 (wait 5 minutes, then run):**
```bash
$env:DAILY_VISITS=50; python fraud_detection_tester.py
```

**Terminal 4 (wait 5 minutes, then run):**
```bash
$env:DAILY_VISITS=50; python fraud_detection_tester.py
```

**Result:** 200 visitors spread throughout the day

### Strategy 3: Continuous Background Runs
**Best for:** Maximum scale

```bash
# Run in background (Windows)
Start-Process -NoNewWindow python -ArgumentList "fraud_detection_tester.py" -EnvironmentVariables @{DAILY_VISITS=100}

# Run in background (macOS/Linux)
nohup bash -c 'export DAILY_VISITS=100 && python fraud_detection_tester.py' > output.log 2>&1 &
```

### Performance Benchmarks

| Visitors | Duration | Avg/Visit | Impressions | System Load |
|----------|----------|-----------|-------------|------------|
| 25 | 12 min | 30s | 100-150 | Low |
| 50 | 25 min | 30s | 200-300 | Low |
| 100 | 50 min | 30s | 400-600 | Medium |
| 150 | 75 min | 30s | 600-900 | Medium |
| 250 | 125 min | 30s | 1000-1500 | Medium |
| 500 | 250 min | 30s | 2000-3000 | High |

---

## GitHub Actions Setup

### Automatic Daily Runs (Recommended)

#### Step 1: Push to GitHub
```bash
git add .
git commit -m "Add fraud detection tester"
git push origin main
```

#### Step 2: Enable GitHub Actions
1. Go to your repository on GitHub
2. Click **"Actions"** tab
3. Click **"I understand my workflows, go ahead and enable them"**

#### Step 3: Configure Visitor Count
Edit `.github/workflows/fraud-testing.yml`:

```yaml
env:
  MIN_VISITS: 50      # Minimum random visitors
  MAX_VISITS: 100     # Maximum random visitors
```

**Examples:**
- `MIN_VISITS: 50, MAX_VISITS: 100` → Random 50-100 each day
- `MIN_VISITS: 100, MAX_VISITS: 150` → Random 100-150 each day
- `MIN_VISITS: 200, MAX_VISITS: 250` → Random 200-250 each day

#### Step 4: Set Schedule
Edit `.github/workflows/fraud-testing.yml`:

```yaml
on:
  schedule:
    - cron: '0 2 * * *'    # 2 AM UTC daily
    - cron: '0 14 * * *'   # 2 PM UTC daily (backup)
```

**Common Timezones:**
- `0 2 * * *` = 2 AM UTC (7:30 AM IST)
- `0 8 * * *` = 8 AM UTC (1:30 PM IST)
- `0 14 * * *` = 2 PM UTC (7:30 PM IST)
- `0 20 * * *` = 8 PM UTC (1:30 AM IST next day)

#### Step 5: Multiple Daily Runs
For 200+ visitors per day, add multiple schedules:

```yaml
schedule:
  - cron: '5 8 * * *'    # 8:05 AM UTC
  - cron: '5 14 * * *'   # 2:05 PM UTC
  - cron: '5 20 * * *'   # 8:05 PM UTC
```

**Result:** 3 runs × 50-100 visitors = 150-300 visitors/day

### Monitor GitHub Actions

1. Go to your repository
2. Click **"Actions"** tab
3. Click the latest workflow run
4. Scroll to **"Generate Summary Report"** step
5. View the impression metrics:

```
🎯 ADSTERRA IMPRESSION REPORT
- Planned visitors: 75
- Successful visits: 75
- Failed visits: 0
- 🔥 Total Impressions Generated: 600
- 📈 Avg Impressions/Visit: 8.0
```

### Download Logs
1. Click the workflow run
2. Scroll to **"Artifacts"** section
3. Download `fraud-test-logs-*` file
4. Extract and view `fraud_detection_test.log`

---

## Monitoring & Troubleshooting

### Check If Script Is Running
**Windows:**
```bash
Get-Process python
```

**macOS/Linux:**
```bash
ps aux | grep python
```

### View Live Logs
```bash
# Real-time (Windows)
Get-Content fraud_detection_test.log -Wait

# Real-time (macOS/Linux)
tail -f fraud_detection_test.log
```

### Common Issues

#### Issue: "Chrome not found"
**Solution:**
```bash
# Install Chrome
# Windows: Download from https://www.google.com/chrome/
# macOS: brew install chromium
# Linux: sudo apt-get install chromium-browser
```

#### Issue: "No impressions generated"
**Solution:**
- Check if your websites have ads
- Verify websites load properly
- Check logs for errors: `grep ERROR fraud_detection_test.log`

#### Issue: "Proxy errors"
**Solution:**
- Use TEST_MODE (direct connection):
  Edit line 36 in `fraud_detection_tester.py`:
  ```python
  TEST_MODE = True  # Use direct connection instead of proxies
  ```

#### Issue: "Timeout errors"
**Solution:**
- Increase timeout in `fraud_detection_tester.py` line 1047:
  ```python
  driver.set_page_load_timeout(30)  # Increase from 20 to 30
  ```

### Success Indicators

✅ **Good signs:**
- Logs show "VISIT COMPLETED"
- Impressions generated: 3-12 per visit
- No repeated errors
- Session report shows success rate > 90%

❌ **Bad signs:**
- Logs show "VISIT FAILED"
- 0 impressions generated
- Same error repeated
- Success rate < 50%

---

## 📊 Scaling Examples

### Example 1: Small Site (50 visitors/day)
```bash
# Local run
$env:DAILY_VISITS=50; python fraud_detection_tester.py
```

### Example 2: Medium Site (150 visitors/day)
```yaml
# GitHub Actions
env:
  MIN_VISITS: 75
  MAX_VISITS: 75

schedule:
  - cron: '0 8 * * *'    # Morning run
  - cron: '0 20 * * *'   # Evening run
```

### Example 3: Large Site (300+ visitors/day)
```yaml
# GitHub Actions
env:
  MIN_VISITS: 100
  MAX_VISITS: 150

schedule:
  - cron: '5 8 * * *'    # 8:05 AM
  - cron: '5 14 * * *'   # 2:05 PM
  - cron: '5 20 * * *'   # 8:05 PM
```

---

## 🎯 Quick Reference

### Run Locally
```bash
python fraud_detection_tester.py              # 25 visitors
$env:DAILY_VISITS=100; python fraud_detection_tester.py  # 100 visitors
```

### View Results
```bash
grep "ADSTERRA IMPRESSION REPORT" -A 10 fraud_detection_test.log
```

### GitHub Actions
1. Edit `.github/workflows/fraud-testing.yml`
2. Set `MIN_VISITS` and `MAX_VISITS`
3. Set schedule (cron times)
4. Push to GitHub
5. Check "Actions" tab for results

### Scale Up
- **Local:** Run multiple terminals in parallel
- **GitHub:** Add more schedule entries (multiple daily runs)
- **Production:** Use multiple GitHub accounts or cloud runners

---

## ✨ Summary

**To run the script:**
1. Install dependencies: `pip install -r requirements.txt`
2. Configure websites in `fraud_detection_tester.py`
3. Run: `python fraud_detection_tester.py`

**To increase visitors:**
- **Local:** Run multiple times or in parallel terminals
- **GitHub Actions:** Increase `MIN_VISITS`/`MAX_VISITS` or add more schedules
- **Scale:** Use multiple runs throughout the day

**To monitor:**
- View logs: `tail -f fraud_detection_test.log`
- Check impressions: `grep "REAL IMPRESSIONS GENERATED"`
- GitHub Actions: Check workflow summary report

**Expected results:**
- 3-12 impressions per visit
- 30-60 seconds per visit
- 90%+ success rate
- Real ad interactions logged
