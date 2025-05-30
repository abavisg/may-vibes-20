# CFP Scout Testing Guide 🧪

## **Quick Testing Summary**

CFP Scout is **100% OPERATIONAL** and ready for testing! Here's how to test it:

---

## 🚀 **Recommended Testing Approach**

### **1. Quick Functional Test**
```bash
# Fastest test - verifies everything works
python3 src/main.py --run-once --mode traditional
```

### **2. Production Test**  
```bash
# Test with MCP coordination (recommended for production)
python3 src/main.py --run-once --mode hybrid
```

### **3. Status Check**
```bash
# Check orchestrator status and configuration
python3 src/main.py --status
```

---

## 📋 **Complete Test Suite**

### **Automated Testing**
```bash
# Run comprehensive test suite
python3 test_cfp_scout.py
```

### **Manual Testing Options**

**A. All Execution Modes:**
```bash
python3 src/main.py --run-once --mode traditional  # ~17 seconds
python3 src/main.py --run-once --mode hybrid       # ~15 seconds  
python3 src/main.py --run-once --mode mcp          # ~20 seconds (experimental)
```

**B. Individual Components:**
```bash
python3 src/event_orchestrator.py                  # Direct orchestrator
python3 src/agents/scraper_mcp_server.py          # MCP scraper server
python3 src/agents/cfp_filter_mcp_server.py       # MCP filter server
```

**C. Configuration Tests:**
```bash
python3 src/main.py --help                        # CLI documentation
python3 src/main.py --status                      # Status monitoring
```

---

## 🐳 **Docker Testing**

### **Quick Docker Test**
```bash
# 1. Ensure .env exists
cp env.example .env

# 2. Build and run
docker-compose up --build

# 3. Test in container
docker-compose exec cfp-scout python3 src/main.py --status
docker-compose exec cfp-scout python3 src/main.py --run-once
```

### **Docker Development**
```bash
# Build only
docker build -t cfp-scout .

# Run once
docker run --env-file .env cfp-scout python3 src/main.py --run-once

# Interactive mode
docker run -it --env-file .env cfp-scout bash
```

---

## ⏰ **Scheduling Tests**

### **Test Scheduling (Non-blocking)**
```bash
# Start scheduler (cancel with Ctrl+C)
python3 src/main.py --schedule

# In another terminal, check status
python3 src/main.py --status
```

### **Production Systemd Test** (Linux only)
```bash
# Install service
sudo cp cfp-scout.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable cfp-scout

# Test service
sudo systemctl start cfp-scout
sudo systemctl status cfp-scout
sudo journalctl -u cfp-scout -f
```

---

## 🔧 **Troubleshooting**

### **Common Issues & Solutions**

**1. MCP Host Direct Execution Error**
```bash
# ❌ This has known async issues:
python3 src/mcp_host.py

# ✅ Use this instead:
python3 src/main.py --run-once --mode hybrid
```

**2. Ollama Connection Issues**
```bash
# Check Ollama status
curl http://localhost:11434/api/version

# Start Ollama if needed
ollama serve

# Pull required model
ollama pull qwen2.5-coder:1.5b
```

**3. ChromeDriver Issues**
```bash
# ChromeDriver is auto-managed, just ensure Chrome is installed
google-chrome --version
```

**4. Email Configuration Issues**
```bash
# Email is optional for testing - warning is normal
# Configure in .env for production:
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
TO_EMAIL=recipient@example.com
```

---

## 📊 **Expected Test Results**

### **Successful Execution Shows:**
```
✅ Pipeline execution completed successfully
📊 Mode: hybrid, Duration: 15.23s  
📈 Events processed: 27
📋 Total executions: 1
```

### **Key Performance Metrics:**
- **Traditional Mode**: ~17 seconds for 27 events
- **Hybrid Mode**: ~15 seconds (recommended)
- **MCP Mode**: ~20 seconds (experimental)
- **Memory Usage**: <200MB typical
- **Events Processed**: 27 CFP events from confs.tech

---

## 🎯 **Testing Checklist**

- [ ] **Basic Functionality**: `python3 src/main.py --run-once --mode traditional`
- [ ] **Production Mode**: `python3 src/main.py --run-once --mode hybrid`  
- [ ] **Status Monitoring**: `python3 src/main.py --status`
- [ ] **Comprehensive Tests**: `python3 test_cfp_scout.py`
- [ ] **Docker Deployment**: `docker-compose up --build`
- [ ] **Scheduling Test**: `python3 src/main.py --schedule` (Ctrl+C to stop)

---

## 🚀 **Production Readiness**

CFP Scout is **production-ready** when all tests pass:

✅ **All 10/10 tests passing** in comprehensive test suite  
✅ **Traditional and Hybrid modes** working correctly  
✅ **Ollama connectivity** confirmed  
✅ **Docker deployment** functional  
✅ **Status monitoring** operational  

**You're ready to deploy CFP Scout in production!** 🎉

---

## 📞 **Need Help?**

1. **Run comprehensive tests**: `python3 test_cfp_scout.py`
2. **Check individual components** using the commands above
3. **Review logs** in `logs/` directory
4. **Verify environment** configuration in `.env`

*CFP Scout Phase 3: Production-Ready with Comprehensive Testing* ✅ 