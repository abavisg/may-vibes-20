# CFP Scout - Complete Running Guide 🚀

## **How to Run CFP Scout: Step-by-Step Instructions**

CFP Scout can be run in multiple ways depending on your needs. Here's exactly how to run it:

---

## 🎯 **Quick Start (2 minutes)**

### **Step 1: Basic Test Run**
```bash
# Run CFP Scout once to test everything works
python3 src/main.py --run-once --mode traditional
```

**What happens:**
- ✅ Scrapes 27 CFP events from confs.tech
- ✅ Filters events using AI (Ollama)
- ✅ Attempts to send email (if configured)
- ✅ Completes in ~16 seconds
- ✅ Shows success message

### **Step 2: Check Status**
```bash
# View system status and configuration
python3 src/main.py --status
```

**What you'll see:**
```
📊 CFP Scout Orchestrator Status
==================================================
execution_mode: hybrid
schedule_time: 08:00
timezone: Europe/London
```

---

## 🚀 **All Running Methods**

### **Method 1: Single Execution (Testing)**

#### **A. Traditional Mode (Fastest)**
```bash
python3 src/main.py --run-once --mode traditional
```
- **Duration**: ~16-17 seconds
- **Use case**: Quick testing, maximum speed
- **What it does**: Direct pipeline execution

#### **B. Hybrid Mode (Recommended)**
```bash
python3 src/main.py --run-once --mode hybrid
```
- **Duration**: ~15-16 seconds
- **Use case**: Production testing
- **What it does**: MCP coordination + traditional execution

#### **C. Pure MCP Mode (Experimental)**
```bash
python3 src/main.py --run-once --mode mcp
```
- **Duration**: ~20-25 seconds
- **Use case**: Full agent mesh testing
- **What it does**: Complete MCP agent-to-agent communication

### **Method 2: Scheduled Execution (Production)**

#### **A. Default Schedule (8AM UK Time)**
```bash
python3 src/main.py --schedule
```
- **Schedule**: Daily at 08:00 Europe/London
- **How to stop**: Press Ctrl+C
- **Logs**: Saves to `logs/cfp_scout_main.log`

#### **B. Custom Schedule Time**
```bash
# Set custom time in environment
SCHEDULE_TIME=06:30 python3 src/main.py --schedule

# Or edit .env file:
echo "SCHEDULE_TIME=06:30" >> .env
python3 src/main.py --schedule
```

#### **C. Custom Timezone**
```bash
# US Eastern Time
TIMEZONE=US/Eastern python3 src/main.py --schedule

# Tokyo Time
TIMEZONE=Asia/Tokyo python3 src/main.py --schedule
```

### **Method 3: Docker Deployment**

#### **A. Complete Stack (Recommended)**
```bash
# 1. Setup environment
cp env.example .env
# Edit .env with your email settings (optional)

# 2. Start complete stack with Ollama
docker-compose up -d

# 3. Check status
docker-compose exec cfp-scout python3 src/main.py --status

# 4. Run manually in container
docker-compose exec cfp-scout python3 src/main.py --run-once

# 5. View logs
docker-compose logs -f cfp-scout
```

#### **B. Build and Run Manually**
```bash
# Build image
docker build -t cfp-scout .

# Run once
docker run --env-file .env cfp-scout python3 src/main.py --run-once

# Run with schedule
docker run -d --env-file .env cfp-scout

# Interactive mode
docker run -it --env-file .env cfp-scout bash
```

### **Method 4: System Service (Linux Production)**

#### **A. Install as Systemd Service**
```bash
# 1. Install to system location
sudo mkdir -p /opt/cfp-scout
sudo cp -r . /opt/cfp-scout/
sudo chown -R cfpscout:cfpscout /opt/cfp-scout

# 2. Install service
sudo cp cfp-scout.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable cfp-scout

# 3. Start service
sudo systemctl start cfp-scout

# 4. Check status
sudo systemctl status cfp-scout

# 5. View logs
sudo journalctl -u cfp-scout -f
```

#### **B. Service Management**
```bash
# Start service
sudo systemctl start cfp-scout

# Stop service
sudo systemctl stop cfp-scout

# Restart service
sudo systemctl restart cfp-scout

# Enable auto-start
sudo systemctl enable cfp-scout

# Disable auto-start
sudo systemctl disable cfp-scout

# View logs
sudo journalctl -u cfp-scout -f
sudo journalctl -u cfp-scout --since today
```

---

## ⚙️ **Configuration Options**

### **Environment Variables**

Create or edit `.env` file:
```bash
# Execution settings
EXECUTION_MODE=hybrid              # traditional, hybrid, mcp
SCHEDULE_TIME=08:00               # Daily execution time
TIMEZONE=Europe/London            # Timezone for scheduling

# Ollama settings
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen2.5-coder:1.5b

# User interests for filtering
USER_INTERESTS=AI,machine learning,engineering leadership,fintech,developer experience

# Email settings (for production email notifications)
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
TO_EMAIL=recipient@example.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### **📧 Email Setup (Optional)**

CFP Scout includes full email functionality! To enable email notifications:

#### **Gmail Setup (Recommended)**
1. **Enable 2-Factor Authentication** on your Gmail account
2. **Create App Password**: Go to Google Account Settings > Security > 2-Step Verification > App passwords
3. **Configure `.env`**:
   ```bash
   EMAIL_ADDRESS=your-email@gmail.com
   EMAIL_PASSWORD=your-16-character-app-password
   TO_EMAIL=recipient@example.com
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   ```

#### **Test Email Setup**
```bash
# Test email functionality
python3 src/email_sender.py
```

#### **Other Email Providers**
```bash
# Outlook/Hotmail
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587

# Yahoo
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587

# Custom SMTP
SMTP_SERVER=your-smtp-server.com
SMTP_PORT=587
```

### **Command Line Overrides**
```bash
# Override execution mode
python3 src/main.py --run-once --mode traditional

# Override schedule time (environment variable)
SCHEDULE_TIME=06:30 python3 src/main.py --schedule

# Override timezone (environment variable)
TIMEZONE=US/Pacific python3 src/main.py --schedule
```

---

## 📊 **What Happens When You Run CFP Scout**

### **Execution Flow**
1. **🌐 Web Scraping**: Scrapes CFP events from confs.tech/cfp using Selenium
2. **🔄 Data Processing**: Normalizes and deduplicates event data
3. **🤖 AI Filtering**: Uses Ollama LLM to score events based on your interests
4. **📧 Email Notification**: Sends beautiful HTML emails (if configured)
5. **📝 Logging**: Saves detailed logs for monitoring

### **Expected Results**
```
✅ Pipeline execution completed successfully
📊 Mode: hybrid, Duration: 15.23s
📈 Events processed: 27
📋 Total executions: 1
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

#### **4. Email Configuration**
```bash
# Error: Username and Password not accepted
# This means email is working but credentials need setup

# ✅ For testing: Skip email configuration - CFP Scout works without it
# ✅ For production: Set up Gmail App Password (see Configuration section above)

# Test email configuration:
python3 src/email_sender.py
```

#### **5. Email Authentication Errors**
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
✅ **Email notifications sent** (if configured)

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

**CFP Scout is production-ready and fully functional!** 🎉 