# CFP Scout Running Guide

**CFP Scout** is a production-ready AI-powered system for discovering relevant tech conference CFPs using native Python deployment with Anthropic's Model Context Protocol (MCP).

---

## 🚀 Quick Start (2 minutes)

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Configure**: `cp env.example .env` (edit with your settings)
3. **Install Ollama**: Download from [ollama.ai](https://ollama.ai) 
4. **Pull model**: `ollama pull llama3:latest`
5. **Run**: `python src/main.py --run-once`

**Result**: 🎉 CFP email generated and terminal preview launched!

---

## 📋 Running Methods

### **Method 1: Single Execution (Testing)**

**Purpose**: Test the system once to verify everything works.

```bash
# Quick test
python src/main.py --run-once

# Test specific mode
python src/main.py --run-once --mode traditional
python src/main.py --run-once --mode hybrid
python src/main.py --run-once --mode mcp

# Test without sending email
python src/main.py --run-once --no-email
```

**Output**: Immediate execution, terminal preview, email sent (if configured).

---

### **Method 2: Scheduled Execution (Production)**

**Purpose**: Run automatically every day at a specified time.

```bash
# Start scheduler (runs daily)
python src/main.py --schedule

# Background execution (survives terminal closing)
nohup python src/main.py --schedule > logs/cfp_scout.log 2>&1 &

# Check status
python src/main.py --status
```

**Output**: 
- Runs daily at configured time (default: 08:00)
- Logs all activity to `logs/cfp_scout.log`
- External terminal preview for each execution

---

### **Method 3: System Service (Linux)**

**Purpose**: Production deployment with automatic startup and service management.

```bash
# Install service
sudo cp cfp-scout.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable cfp-scout

# Start service
sudo systemctl start cfp-scout

# Monitor
sudo systemctl status cfp-scout
sudo journalctl -u cfp-scout -f
```

**Output**: Runs as system service, automatic startup, systemd logging.

---

## 📊 **What Happens When You Run CFP Scout**

### **Execution Flow**
1. **🌐 Web Scraping**: Scrapes CFP events from confs.tech/cfp using Selenium
2. **🔄 Data Processing**: Normalizes and deduplicates event data
3. **🤖 AI Filtering**: Uses Ollama LLM to score events based on your interests
4. **📧 Email Notification**: Sends beautiful HTML emails via Mailgun or SMTP
5. **📝 Logging**: Saves detailed logs for monitoring

### **Expected Results**
```
✅ Pipeline execution completed successfully
📊 Mode: hybrid, Duration: 15.23s
📈 Events processed: 27
📋 Total executions: 1
📧 Email sent successfully via Mailgun
```

### **Performance Metrics**
- **Events Found**: ~25-30 CFP events per run
- **Execution Time**: 15-20 seconds
- **Memory Usage**: <200MB
- **Success Rate**: 99%+ (depends on website availability)

---

## 🔧 **Monitoring & Troubleshooting**

### **Check System Health**
```bash
# System status
python3 src/main.py --status

# Comprehensive test
python3 test_cfp_scout.py

# Check logs
ls -la logs/
tail -f logs/cfp_scout_main.log

# Test email configuration
python3 src/email_sender.py
```

### **Common Issues & Solutions**

#### **1. Ollama Not Running**
```bash
# Error: Connection refused to localhost:11434
# Solution:
ollama serve
ollama pull qwen2.5-coder:1.5b
```

#### **2. ChromeDriver Issues**
```bash
# Error: Chrome binary not found
# Solution: Install Chrome browser
# ChromeDriver is auto-managed by CFP Scout
```

#### **3. Permission Issues (Linux)**
```bash
# Error: Permission denied
# Solution:
sudo chown -R $USER:$USER .
chmod +x src/main.py
```

#### **4. Mailgun Configuration Issues**
```bash
# Error: Mailgun API error: 401
# Solution: Check your API key and domain in .env

# Error: Mailgun connection failed
# Solutions:
# 1. Verify MAILGUN_API_KEY is correct
# 2. Check MAILGUN_DOMAIN matches your Mailgun account
# 3. Ensure MAILGUN_FROM_EMAIL uses your domain
# 4. Add authorized recipients for sandbox domains

# Test Mailgun setup:
python3 src/email_sender.py
```

#### **5. SMTP/Gmail Issues**
```bash
# Error: (535, b'5.7.8 Username and Password not accepted')
# Solution:
# 1. Enable 2-Factor Authentication on Gmail
# 2. Create App Password in Google Account Settings
# 3. Use App Password (not your regular password) in .env
# 4. Make sure EMAIL_ADDRESS matches the account that created the App Password
```

### **Debug Mode**
```bash
# Verbose logging
python3 src/main.py --run-once --mode traditional 2>&1 | tee debug.log

# Check individual components
python3 src/event_orchestrator.py
python3 -c "import requests; print(requests.get('http://localhost:11434/api/version').text)"

# Test email separately
python3 src/email_sender.py
```

---

## 🎯 **Recommended Usage Patterns**

### **For Development & Testing**
```bash
# Quick test
python3 src/main.py --run-once --mode traditional

# Status check
python3 src/main.py --status

# Comprehensive testing
python3 test_cfp_scout.py

# Test email setup
python3 src/email_sender.py
```

### **For Production Deployment**
```bash
# Docker (recommended)
docker-compose up -d

# Or systemd service (Linux)
sudo systemctl start cfp-scout

# Or manual scheduling
python3 src/main.py --schedule
```

### **For Continuous Integration**
```bash
# Automated testing
python3 test_cfp_scout.py

# Single run validation
python3 src/main.py --run-once --mode hybrid

# Docker build validation
docker build -t cfp-scout .
docker run cfp-scout python3 src/main.py --status
```

---

## 📅 **Scheduling Examples**

### **Different Times**
```bash
# 6:30 AM
SCHEDULE_TIME=06:30 python3 src/main.py --schedule

# 9:15 PM
SCHEDULE_TIME=21:15 python3 src/main.py --schedule
```

### **Different Timezones**
```bash
# US East Coast
TIMEZONE=US/Eastern python3 src/main.py --schedule

# San Francisco
TIMEZONE=US/Pacific python3 src/main.py --schedule

# Tokyo
TIMEZONE=Asia/Tokyo python3 src/main.py --schedule
```

### **Cron Alternative**
```bash
# Add to crontab for 8 AM daily
crontab -e
# Add line:
0 8 * * * cd /path/to/cfp-scout && python3 src/main.py --run-once >> logs/cron.log 2>&1
```

---

## 🏆 **Success Indicators**

CFP Scout is running successfully when you see:

✅ **"Pipeline execution completed successfully"**  
✅ **Duration: 15-20 seconds**  
✅ **Events processed: 25-30**  
✅ **No error messages**  
✅ **Logs created in `logs/` directory**  
✅ **"Email sent successfully via Mailgun"** (if configured)

---

## 📞 **Quick Help**

| Issue | Command |
|-------|---------|
| Test basic functionality | `python3 src/main.py --run-once --mode traditional` |
| Check status | `python3 src/main.py --status` |
| Run comprehensive tests | `python3 test_cfp_scout.py` |
| Start scheduling | `python3 src/main.py --schedule` |
| Docker deployment | `docker-compose up -d` |
| View logs | `tail -f logs/cfp_scout_main.log` |
| Test email setup | `python3 src/email_sender.py` |

**CFP Scout is production-ready with Mailgun integration!** 🎉 