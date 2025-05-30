# CFP Scout

**CFP Scout** is an AI-powered agent system that scrapes tech events with open CFPs, filters them using a local language model via Ollama based on user-defined interests, and sends daily email notifications with beautiful formatting. Built with Anthropic's Model Context Protocol (MCP) for modular agent architecture.

🎯 **Perfect for**: Developers, conference speakers, and tech professionals who want automated CFP discovery without manual searching.

## ✨ Key Features

- **🤖 AI-Powered Filtering** – Ollama local LLM analyzes CFP relevance to your interests
- **📧 Beautiful Email Reports** – HTML-formatted emails with relevance scores and CFP details
- **🖥️ External Terminal Display** – Launches separate terminal windows for email previews
- **⚙️ Multi-Mode Execution** – Traditional, Hybrid, and full MCP agent modes
- **⏰ Production Scheduling** – Automated daily execution with systemd and cron support
- **🔗 MCP Integration** – Full Anthropic Model Context Protocol implementation
- **📮 Mailgun Support** – Professional email delivery without personal passwords

---

## 🚀 Quick Start (2 minutes)

```bash
# 1. Clone and setup
git clone <repository-url>
cd cfp-scout
cp env.example .env

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup Ollama
ollama serve
ollama pull llama3:latest

# 4. Configure environment (edit .env with your settings)
# 5. Run CFP Scout
python src/main.py --run-once
```

**Result**: 🎉 CFP email generated and terminal preview launched!

---

## Tech Stack

- **Language**: Python 3.12
- **Web Scraping**: Selenium with Chrome WebDriver
- **Local LLM**: Ollama (llama3:latest)
- **Agent Protocol**: Anthropic's Model Context Protocol (MCP)
- **Email**: Mailgun API and SMTP with HTML formatting
- **Scheduling**: Python schedule, systemd, cron
- **Data Storage**: JSON files for event pipeline stages

---

## Configuration

### Environment Variables

Edit `.env` with your settings:

```bash
# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3:latest

# User Interests & Filtering Criteria
EVENT_THEMES=AI,machine learning,artificial intelligence,engineering leadership,fintech,developer experience,software architecture,cloud computing,DevOps,data science
EVENT_LOCATIONS=Europe,UK
EVENT_TYPE=Online,Physical

# Email Configuration (choose ONE method)

# Method 1: Mailgun (Recommended - no personal passwords)
MAILGUN_API_KEY=your-mailgun-api-key-here
MAILGUN_DOMAIN=your-domain.mailgun.org
MAILGUN_FROM_EMAIL=CFP Scout <noreply@your-domain.mailgun.org>
TO_EMAIL=recipient@example.com

# Method 2: SMTP (Gmail, Outlook, etc.)
# EMAIL_ADDRESS=your_email@gmail.com
# EMAIL_PASSWORD=your_app_password_here
# SMTP_SERVER=smtp.gmail.com
# SMTP_PORT=587
# TO_EMAIL=recipient@example.com

# Schedule Configuration
SCHEDULE_TIME=08:00
TIMEZONE=Europe/London
EXECUTION_MODE=hybrid

# Display Configuration
SHOW_EXTERNAL_TERMINAL=true
```

### Email Setup

#### Mailgun (Recommended)
1. Sign up at [mailgun.com](https://www.mailgun.com/) (free tier: 1,000 emails/month)
2. Get your API key and domain from Mailgun dashboard
3. Configure in `.env` file
4. Test: `python src/email_sender.py`

#### Gmail/SMTP
1. Enable 2-Factor Authentication on Gmail
2. Create App Password in Google Account Settings
3. Use App Password (not regular password) in `.env`
4. Test: `python src/email_sender.py`

---

## Usage

### Command Line Interface

```bash
# Execution modes
python src/main.py --mode traditional  # Fast, basic
python src/main.py --mode hybrid       # Balanced (default)
python src/main.py --mode mcp          # Full agent mesh

# Operation modes
python src/main.py --run-once          # Single execution
python src/main.py --schedule          # Daily scheduling
python src/main.py --status            # Show status

# Examples
python src/main.py --run-once --mode hybrid
python src/main.py --schedule --mode traditional

# Background execution (survives terminal closing)
nohup python src/main.py --schedule > logs/cfp_scout.log 2>&1 &
```

### Expected Results

```
✅ Pipeline execution completed successfully
📊 Mode: hybrid, Duration: 15.23s
📈 Events processed: 27
📋 Total executions: 1
📧 Email sent successfully via Mailgun
```

**Performance Metrics:**
- **Events Found**: ~25-30 CFP events per run
- **Execution Time**: 15-20 seconds
- **Memory Usage**: <200MB
- **Success Rate**: 99%+ (depends on website availability)

---

## Production Deployment

### Native Python Scheduling (Recommended)

```bash
# Test the system
python src/main.py --run-once

# Start scheduled execution
python src/main.py --schedule

# Run in background
nohup python src/main.py --schedule > logs/cfp_scout.log 2>&1 &

# Check status
python src/main.py --status
tail -f logs/cfp_scout.log
```

### Systemd Service (Linux Servers)

```bash
# Install service
sudo cp cfp-scout.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable cfp-scout

# Start service
sudo systemctl start cfp-scout
sudo systemctl status cfp-scout

# Monitor logs
sudo journalctl -u cfp-scout -f
```

### Manual Cron (Alternative)

```bash
# Add to crontab for daily execution at 8 AM
0 8 * * * cd /path/to/cfp-scout && python3 src/main.py --run-once >> logs/cron.log 2>&1
```

---

## Testing & Debugging

### Quick Test Commands

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

### Performance Benchmarks

```bash
# Benchmark different modes
time python src/main.py --run-once --mode traditional  # ~15-17 seconds
time python src/main.py --run-once --mode hybrid       # ~16-18 seconds  
time python src/main.py --run-once --mode mcp          # ~20-25 seconds
```

### Common Issues & Solutions

#### 1. Ollama Not Running
```bash
# Error: Connection refused to localhost:11434
# Solution:
ollama serve
ollama pull llama3:latest
curl http://localhost:11434/api/version  # Test connection
```

#### 2. Chrome/Selenium Issues
```bash
# Error: Chrome binary not found
# Solution: Install Chrome browser (ChromeDriver auto-managed)
google-chrome --version
```

#### 3. Email Configuration Issues
```bash
# Test email setup
python src/email_sender.py

# Mailgun: Check API key and domain in .env
# Gmail: Use App Password, not regular password
```

#### 4. External Terminal Issues (macOS)
```bash
# Test terminal launching
osascript -e 'tell application "Terminal" to do script "echo test"'
```

### System Health Checks

```bash
# Check system status
python src/main.py --status

# Verify dependencies
pip freeze | grep -E "(selenium|ollama|requests|schedule)"

# Check Ollama
ollama list
ollama ps

# Test environment loading
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('✅ Config loaded')"
```

---

## Architecture

CFP Scout uses **Production-Ready MCP Architecture** with scheduling and monitoring:

```
┌─────────────────────────────────────────────────────┐
│              Main Orchestrator                      │
│     (Scheduling, Monitoring, Multi-Mode)           │
└─────────────────────┬───────────────────────────────┘
                      │ Execution Control
          ┌───────────┼───────────────────┐
          │           │                   │
          ▼           ▼                   ▼
   Traditional    Hybrid Mode        Pure MCP Mode
     Pipeline    (MCP + Legacy)     (Full Agent Mesh)
          │           │                   │
          └───────────┼───────────────────┘
                      │
         ┌────────────┴────────────┐
         │    CFP Scout MCP Host   │
         │  (Agent Coordination)   │
         └─────────────┬───────────┘
                       │ MCP JSON-RPC 2.0
           ┌───────────┼───────────┐
           │           │           │
           ▼           ▼           ▼
   ┌─────────────┐ ┌───────────┐ ┌─────────────┐ ┌─────────────┐
   │   Scraper   │ │Event Orch.│ │ CFP Filter  │ │Email Sender │
   │ MCP Server  │ │MCP Server │ │ MCP Server  │ │ MCP Server  │
   └─────────────┘ └───────────┘ └─────────────┘ └─────────────┘
```

### Execution Modes
1. **Traditional** → Direct module imports (fastest, basic)
2. **Hybrid** → MCP coordination + traditional execution (balanced, recommended)
3. **Pure MCP** → Complete agent-to-agent communication (future-ready)

---

## Project Structure

```
cfp-scout/
├── 📁 src/
│   ├── 📄 main.py                      # Main orchestration script
│   ├── 📄 event_orchestrator.py        # Central pipeline coordinator
│   ├── 📄 cfp_filter_agent.py          # LLM-based event filtering
│   ├── 📄 scraper.py                   # Web scraping engine
│   ├── 📄 email_sender.py              # Email notification system
│   ├── 📄 mcp_host.py                  # Complete MCP ecosystem coordinator
│   └── 📁 agents/                      # All MCP server implementations
│       ├── 📄 scraper_mcp_server.py
│       ├── 📄 cfp_filter_mcp_server.py
│       ├── 📄 email_sender_mcp_server.py
│       └── 📄 event_orchestrator_mcp_server.py
├── 📁 logs/                            # Execution logs and data
├── 📄 cfp-scout.service                # Systemd service configuration
├── 📄 requirements.txt                 # Python dependencies
├── 📄 env.example                      # Environment template
├── 📄 test_cfp_scout.py               # Comprehensive test suite
├── 📄 test_mcp_integration.py         # MCP integration tests
└── 📄 README.md                        # This file
```

---

## MCP Integration

CFP Scout implements **Anthropic's Model Context Protocol** across all agents:

### MCP Agent Ecosystem

**Main Orchestrator** (`src/main.py`)
- Multi-Mode Execution: Traditional, Hybrid, Pure MCP
- Scheduling: Daily execution with timezone support  
- Monitoring: Health checks and performance tracking
- Deployment: Native Python, systemd, cron integration

**MCP Servers**: Each agent implements full MCP protocol with tools, resources, and prompts:
- **Scraper MCP Server**: Web scraping with connectivity testing
- **Event Orchestrator MCP Server**: Pipeline management and statistics
- **CFP Filter MCP Server**: AI filtering with Ollama integration
- **Email Sender MCP Server**: Email delivery with connection testing

---

## Monitoring & Status

### Status Monitoring

```bash
# Check orchestrator status
python src/main.py --status

# View logs
tail -f logs/cfp_scout.log

# Check background process
ps aux | grep "python3 src/main.py"

# Example status output:
# execution_mode: hybrid
# schedule_time: 08:00
# timezone: Europe/London
# last_execution: 2025-05-30T18:18:44.694000
# execution_count: 1
# total_events_processed: 27
```

### What Happens During Execution

1. **🌐 Web Scraping**: Scrapes CFP events from confs.tech/cfp using Selenium
2. **🔄 Data Processing**: Normalizes and deduplicates event data
3. **🤖 AI Filtering**: Uses Ollama LLM to score events based on your interests
4. **📧 Email Notification**: Sends beautiful HTML emails via Mailgun or SMTP
5. **🖥️ Terminal Preview**: Launches external terminal with email content
6. **📝 Logging**: Saves detailed logs for monitoring

---

## Contributing

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Make** your changes and add tests
4. **Update** documentation (README, docstrings)
5. **Commit** your changes: `git commit -m 'Add amazing feature'`
6. **Push** to branch: `git push origin feature/amazing-feature`
7. **Submit** a Pull Request

### Guidelines
- Follow modular architecture principles
- Add tests for new functionality
- Update documentation for any changes
- Remove deprecated/unused code
- Ensure MCP compatibility for new agents
- Maintain backward compatibility when possible
- Test all execution modes (traditional, hybrid, mcp)

---

## License

This project is licensed under the MIT License. See LICENSE for details.

---

## Support

- **Issues**: Report bugs via GitHub Issues
- **Documentation**: Check README and code comments
- **MCP Resources**: [Anthropic MCP Documentation](https://modelcontextprotocol.io)
- **Ollama Setup**: [Ollama Installation Guide](https://ollama.ai)

---

*Built with ❤️ using Anthropic's Model Context Protocol and Ollama for local AI processing*

**🎉 Production-Ready Native Python Deployment!**