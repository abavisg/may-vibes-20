# CFP Scout Testing Guide

This guide covers comprehensive testing for **CFP Scout** - the AI-powered conference CFP discovery system built with Anthropic's Model Context Protocol (MCP).

---

## 🧪 **Quick Test Commands**

```bash
# 1. Quick system test
python src/main.py --run-once

# 2. Test specific modes
python src/main.py --run-once --mode traditional
python src/main.py --run-once --mode hybrid
python src/main.py --run-once --mode mcp

# 3. Test individual components
python src/cfp_filter_agent.py
python src/email_sender.py
python src/scraper.py

# 4. Run comprehensive test suite
python test_cfp_scout.py
```

---

## 🔧 **Component Testing**

### **Individual Component Tests**

#### **1. Scraper Test**
```bash
python src/scraper.py
```
**Expected**: Events scraped from confs.tech, saved to `logs/scraped_events.json`

#### **2. AI Filter Test**
```bash
python src/cfp_filter_agent.py
```
**Expected**: Events filtered with relevance scores using Ollama

#### **3. Email Sender Test**
```bash
python src/email_sender.py
```
**Expected**: 
- Email formatting test completed
- External terminal launched (if enabled)
- Connection test results displayed

#### **4. Event Orchestrator Test**
```bash
python src/event_orchestrator.py
```
**Expected**: Complete pipeline execution from scraping to email

---

## 🎯 **Full System Testing**

### **Production Test**

```bash
# Complete system test
python test_cfp_scout.py
```

**Test Coverage:**
- ✅ **Environment Setup** - All dependencies and configurations
- ✅ **Ollama Connection** - Local LLM availability and model access
- ✅ **Web Scraping** - Event data extraction from sources
- ✅ **AI Filtering** - Relevance scoring with detailed interests
- ✅ **Email System** - Mailgun/SMTP connectivity and formatting
- ✅ **External Terminal** - macOS terminal launching
- ✅ **All Execution Modes** - Traditional, Hybrid, MCP
- ✅ **Scheduling** - Daily automation setup
- ✅ **Production Readiness** - Deployment validation

---

## 📊 **Performance Testing**

### **Execution Time Benchmarks**

```bash
# Benchmark different modes
time python src/main.py --run-once --mode traditional
time python src/main.py --run-once --mode hybrid  
time python src/main.py --run-once --mode mcp
```

**Expected Performance:**
- **Traditional Mode**: ~15-17 seconds
- **Hybrid Mode**: ~16-18 seconds  
- **MCP Mode**: ~20-25 seconds
- **Memory Usage**: <200MB typical

### **Load Testing**

```bash
# Multiple rapid executions
for i in {1..5}; do
  echo "Run $i"
  python src/main.py --run-once --no-email
  sleep 2
done
```

---

## ⚙️ **Environment Testing**

### **Python Dependencies**
```bash
# Verify all dependencies
pip freeze | grep -E "(selenium|ollama|requests|schedule)"

# Install missing dependencies
pip install -r requirements.txt
```

### **System Requirements**
```bash
# Check Chrome/ChromeDriver
which google-chrome
which chromedriver

# Check Ollama
ollama list
ollama ps
curl http://localhost:11434/api/version
```

### **Configuration Validation**
```bash
# Test environment loading
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('✅ Config loaded')"

# Check critical variables
python src/main.py --status
```

---

## 🚀 **Deployment Testing**

### **Systemd Service Test**
```bash
# Test service file
sudo systemctl daemon-reload
sudo systemctl status cfp-scout
sudo systemctl start cfp-scout
sudo journalctl -u cfp-scout -f
```

### **Background Execution Test**
```bash
# Test background execution
nohup python src/main.py --schedule > logs/test_bg.log 2>&1 &

# Check process
ps aux | grep "python.*main.py"

# Stop background process
pkill -f "python.*main.py"
```

### **Cron Integration Test**
```bash
# Test cron command
cd /path/to/cfp-scout && python src/main.py --run-once >> logs/cron_test.log 2>&1

# Check cron log
cat logs/cron_test.log
```

---

## 🔍 **Debugging & Troubleshooting**

### **Common Issues**

#### **1. Ollama Connection Failed**
```bash
# Check Ollama status
ollama list
ollama ps
curl http://localhost:11434/api/version

# Restart Ollama
ollama serve
```

#### **2. Chrome/Selenium Issues**
```bash
# Check Chrome installation
google-chrome --version
chromedriver --version

# Test Chrome headless
google-chrome --headless --disable-gpu --dump-dom https://google.com
```

#### **3. Email Configuration**
```bash
# Test email settings
python src/email_sender.py

# Check Mailgun configuration
curl -s --user 'api:YOUR_API_KEY' \
    https://api.mailgun.net/v3/YOUR_DOMAIN/stats/total
```

#### **4. External Terminal Issues (macOS)**
```bash
# Check Terminal app
osascript -e 'tell application "Terminal" to do script "echo test"'

# Alternative: use iTerm2
osascript -e 'tell application "iTerm" to create window with default profile'
```

### **Debug Mode**
```bash
# Enable verbose logging
python src/main.py --run-once --debug

# Check all log files
ls -la logs/
tail -f logs/cfp_scout_main.log
```

---

## ✅ **Testing Checklist**

### **Pre-Deployment Checklist**

- [ ] **Python Environment**: Dependencies installed and working
- [ ] **Ollama Setup**: Model downloaded and accessible
- [ ] **Chrome/Selenium**: Web scraping functional
- [ ] **Email Configuration**: Mailgun or SMTP configured and tested
- [ ] **Environment Variables**: All required settings in `.env`
- [ ] **Single Execution**: `python src/main.py --run-once` successful
- [ ] **Scheduled Execution**: `python src/main.py --schedule` functional
- [ ] **External Terminal**: macOS terminal launching works
- [ ] **All Modes**: Traditional, Hybrid, MCP execution successful
- [ ] **Production Service**: Systemd or cron integration tested

### **Post-Deployment Verification**

- [ ] **Daily Execution**: Scheduled runs working automatically
- [ ] **Email Delivery**: Daily CFP emails being received
- [ ] **Log Monitoring**: Execution logs being generated
- [ ] **Error Handling**: System recovering from failures
- [ ] **Performance**: Execution times within expected ranges

---

✅ **System ready for production deployment!**

---

## 📧 **Support**

For issues or questions:
- **Check logs**: `logs/cfp_scout_main.log`
- **Run diagnostics**: `python test_cfp_scout.py`
- **Test components**: Individual script testing
- **Review configuration**: `.env` file settings 