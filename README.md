# CFP Scout

AI-powered agent system for discovering relevant tech conference CFPs using **Anthropic's Model Context Protocol (MCP)**

**CFP Scout** is a fully Dockerized AI-powered agent system that scrapes tech events with open CFPs, filters them using a local language model via Ollama based on user-defined interests, and sends daily email notifications at 8am UK time with the most relevant results. **Now with complete MCP integration and production-ready scheduling.**

---

## Features

- **🔍 Smart Scraping** – Automatically scrapes CFP events from confs.tech/cfp using Selenium
- **🎼 Event Orchestrator** – Central coordinator that normalizes, deduplicates, and manages event data flow
- **🤖 AI Filtering** – Uses Ollama locally with Llama 3.2 to filter events based on user interests (AI, engineering leadership, fintech, developer experience)
- **📧 Email Notifications** – Sends beautifully formatted HTML email notifications with filtered CFP results
- **⏰ Production Scheduling** – Automated daily execution with systemd, Docker, and cron support
- **🌐 Complete MCP Integration** – All agents implement Anthropic's Model Context Protocol
- **🏗️ Multi-Mode Architecture** – Traditional, MCP, and Hybrid execution modes
- **📊 Monitoring & Logging** – Comprehensive status tracking and health checks

---

## Tech Stack

- **Language**: Python 3.12
- **Web Scraping**: Selenium with Chrome WebDriver
- **Local LLM**: Ollama (qwen2.5-coder:1.5b)
- **Agent Protocol**: Anthropic's Model Context Protocol (MCP)
- **Email**: SMTP with Gmail integration and HTML formatting
- **Scheduling**: Python schedule, systemd, Docker cron
- **Containerization**: Docker with health checks and orchestration
- **Data Storage**: JSON files for event pipeline stages

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

### **Execution Modes**
1. **Traditional** → Direct module imports (fastest, basic)
2. **Hybrid** → MCP coordination + traditional execution (balanced)
3. **Pure MCP** → Complete agent-to-agent communication (future-ready)

---

## Quick Start

### **1. Clone and Setup**

```bash
git clone <repository-url>
cd cfp-scout
cp env.example .env
```

### **2. Configure Environment**

Edit `.env` with your settings:

```bash
# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen2.5-coder:1.5b

# User Interests (comma-separated)
USER_INTERESTS=AI,machine learning,engineering leadership,fintech,developer experience

# Email Configuration
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password_here
TO_EMAIL=recipient@example.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Scheduling
SCHEDULE_TIME=08:00
TIMEZONE=Europe/London
EXECUTION_MODE=hybrid
```

### **3. Install Dependencies**

```bash
pip install -r requirements.txt
```

### **4. Setup Ollama**

```bash
# Install and start Ollama
ollama serve

# Pull the model
ollama pull qwen2.5-coder:1.5b
```

### **5. Run CFP Scout**

**Option A: Production Scheduling** (Recommended)
```bash
# Run with daily scheduling
python src/main.py --schedule

# Run once for testing
python src/main.py --run-once

# Check status
python src/main.py --status
```

**Option B: Docker Deployment**
```bash
# Complete setup with Ollama
docker-compose up -d

# Check status
docker-compose exec cfp-scout python3 src/main.py --status

# View logs
docker-compose logs -f cfp-scout
```

**Option C: Manual Agent Execution**
```bash
# Run complete MCP agent ecosystem
python src/mcp_host.py

# Run individual MCP servers
python src/agents/scraper_mcp_server.py
python src/agents/cfp_filter_mcp_server.py
python src/agents/email_sender_mcp_server.py
python src/agents/event_orchestrator_mcp_server.py
```

**Option D: Traditional Pipeline** (Backward Compatible)
```bash
# Run legacy pipeline
python src/event_orchestrator.py
```

---

## Production Deployment

### **Docker Compose (Recommended)**

```bash
# 1. Configure environment
cp env.example .env
# Edit .env with your settings

# 2. Start services
docker-compose up -d

# 3. Verify deployment
docker-compose ps
docker-compose logs cfp-scout

# 4. Test execution
docker-compose exec cfp-scout python3 src/main.py --run-once
```

### **Systemd Service (Linux)**

```bash
# 1. Install to /opt/cfp-scout
sudo mkdir -p /opt/cfp-scout
sudo cp -r . /opt/cfp-scout/
sudo chown -R cfpscout:cfpscout /opt/cfp-scout

# 2. Install systemd service
sudo cp cfp-scout.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable cfp-scout

# 3. Start service
sudo systemctl start cfp-scout
sudo systemctl status cfp-scout

# 4. Monitor logs
sudo journalctl -u cfp-scout -f
```

### **Manual Cron (Alternative)**

```bash
# Add to crontab
0 8 * * * cd /path/to/cfp-scout && python3 src/main.py --run-once >> logs/cron.log 2>&1
```

---

## Project Structure

```
cfp-scout/
├── 📁 src/
│   ├── 📄 main.py                      # 🆕 Main orchestration script
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
├── 📄 Dockerfile                       # 🆕 Production container
├── 📄 docker-compose.yml               # 🆕 Complete deployment
├── 📄 cfp-scout.service                # 🆕 Systemd service
├── 📄 requirements.txt                 # Python dependencies
├── 📄 env.example                      # Environment template
└── 📄 README.md                        # This file
```

---

## Usage

### **Command Line Interface**

```bash
# Main orchestrator options
python src/main.py --help

# Execution modes
python src/main.py --mode traditional  # Fast, basic
python src/main.py --mode hybrid       # Balanced (default)
python src/main.py --mode mcp          # Full agent mesh

# Operation modes
python src/main.py --run-once          # Single execution
python src/main.py --schedule          # Daily scheduling
python src/main.py --status            # Show status

# Examples
python src/main.py --run-once --mode mcp
python src/main.py --schedule --mode hybrid
```

### **Docker Commands**

```bash
# Start complete system
docker-compose up -d

# Execute different modes
docker-compose exec cfp-scout python3 src/main.py --run-once --mode traditional
docker-compose exec cfp-scout python3 src/main.py --run-once --mode mcp

# Monitor and manage
docker-compose logs -f cfp-scout
docker-compose restart cfp-scout
docker-compose down
```

### **Status Monitoring**

```bash
# Check orchestrator status
python src/main.py --status

# Example output:
# execution_mode: hybrid
# schedule_time: 08:00
# timezone: Europe/London
# last_execution: 2025-05-30T18:18:44.694000
# execution_count: 1
# total_events_processed: 27
```

---

## Complete MCP Integration

CFP Scout implements **Anthropic's Model Context Protocol** across all agents:

### **MCP Agent Ecosystem**

**Main Orchestrator** (`src/main.py`)
- **Multi-Mode Execution**: Traditional, Hybrid, Pure MCP
- **Scheduling**: Daily execution with timezone support  
- **Monitoring**: Health checks and performance tracking
- **Deployment**: Docker, systemd, cron integration

**Scraper MCP Server** (`src/agents/scraper_mcp_server.py`)
- **Tools**: `scrape_cfp_events`, `get_available_sources`, `test_scraper_connectivity`
- **Resources**: `scraper://sources`, `scraper://statistics`, `scraper://status`
- **Prompts**: `create_scraping_strategy_prompt`, `create_event_validation_prompt`

**Event Orchestrator MCP Server** (`src/agents/event_orchestrator_mcp_server.py`)
- **Tools**: `run_cfp_pipeline`, `normalize_events`, `get_pipeline_statistics`, `clean_storage`
- **Resources**: `pipeline://status`, `events://raw`, `events://normalized`, `events://filtered`
- **Prompts**: `create_pipeline_execution_prompt`, `create_event_analysis_prompt`

**CFP Filter MCP Server** (`src/agents/cfp_filter_mcp_server.py`)
- **Tools**: `filter_cfp_events`, `test_ollama_connection`, `get_filter_summary`
- **Resources**: `user://interests`, `ollama://status`, `config://filter`
- **Prompts**: `create_filter_prompt`, `create_batch_filter_prompt`

**Email Sender MCP Server** (`src/agents/email_sender_mcp_server.py`)
- **Tools**: `send_cfp_emails`, `test_email_connection`, `send_test_email`
- **Resources**: `email://config`, `email://status`
- **Prompts**: `create_email_template_prompt`, `create_email_summary_prompt`

---

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `EXECUTION_MODE` | Pipeline execution mode | `hybrid` |
| `SCHEDULE_TIME` | Daily execution time | `08:00` |
| `TIMEZONE` | Execution timezone | `Europe/London` |
| `OLLAMA_HOST` | Ollama API endpoint | `http://localhost:11434` |
| `OLLAMA_MODEL` | Local LLM model name | `qwen2.5-coder:1.5b` |
| `USER_INTERESTS` | Comma-separated interests | `AI,machine learning,fintech` |
| `EMAIL_ADDRESS` | Sender email address | `your_email@gmail.com` |
| `EMAIL_PASSWORD` | Email app password | `your_app_password_here` |
| `TO_EMAIL` | Recipient email address | `recipient@example.com` |
| `SMTP_SERVER` | SMTP server hostname | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP server port | `587` |

---

## Development

### **Testing All Modes**

```bash
# Test traditional mode
python src/main.py --run-once --mode traditional

# Test hybrid mode  
python src/main.py --run-once --mode hybrid

# Test MCP mode
python src/main.py --run-once --mode mcp

# Test individual agents
python src/agents/scraper_mcp_server.py
python src/agents/cfp_filter_mcp_server.py
python src/agents/email_sender_mcp_server.py
python src/agents/event_orchestrator_mcp_server.py

# Test complete MCP ecosystem
python src/mcp_host.py
```

### **Add New Execution Mode**

1. Extend `CFPScoutOrchestrator` class in `src/main.py`
2. Add new execution method: `execute_new_mode_pipeline()`
3. Update mode selection in `execute_pipeline()`
4. Add command line argument to `--mode` choices
5. Update documentation and tests

---

## Progress

### **✅ Phase 1: Core MCP Integration (COMPLETED)**
- [x] **Event Orchestrator MCP Server** - Pipeline coordination via MCP
- [x] **CFP Filter MCP Server** - LLM-based filtering via MCP
- [x] **MCP Host** - Agent coordination and discovery
- [x] **Testing & Validation** - Comprehensive test suite

### **✅ Phase 2: Complete Agent Ecosystem (COMPLETED)**
- [x] **Email Sender MCP Server** - HTML email notifications via MCP
- [x] **Scraper MCP Server** - Web scraping via MCP
- [x] **Full MCP Pipeline** - End-to-end MCP execution
- [x] **Four-Agent System** - Complete agent ecosystem operational

### **✅ Phase 3: Production Orchestration (COMPLETED)**
- [x] **Main Orchestration Script** - Multi-mode execution with scheduling
- [x] **Docker Integration** - Complete containerization with Ollama
- [x] **Production Deployment** - Systemd service and Docker Compose
- [x] **Monitoring & Health Checks** - Status tracking and error handling

### **🚧 Phase 4: Advanced Features (IN PROGRESS)**  
- [ ] **Claude Desktop Integration** - MCP ecosystem connection
- [ ] **Web Dashboard** - Visual monitoring and management
- [ ] **Analytics & Insights** - Success metrics and reporting

### **🔮 Phase 5: Future Enhancements**
- [ ] **Additional Scrapers** - More CFP sources beyond confs.tech
- [ ] **Advanced AI Filtering** - Context-aware relevance scoring
- [ ] **Multi-User Support** - User management and personalization
- [ ] **API Endpoints** - REST API for external integrations
- [ ] **MCP Registry** - Public agent discovery and sharing

---

## Contributing

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Make** your changes and add tests
4. **Update** documentation (README, docstrings)
5. **Commit** your changes: `git commit -m 'Add amazing feature'`
6. **Push** to branch: `git push origin feature/amazing-feature`
7. **Submit** a Pull Request

### **Guidelines**
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

**🎉 Phase 3 Complete: Production-Ready Orchestration with Scheduling!**

