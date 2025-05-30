# CFP Scout

AI-powered agent system for discovering relevant tech conference CFPs using **Anthropic's Model Context Protocol (MCP)**

**CFP Scout** is a fully Dockerized AI-powered agent system that scrapes tech events with open CFPs, filters them using a local language model via Ollama based on user-defined interests, and sends daily email notifications at 8am UK time with the most relevant results. **Now enhanced with complete MCP integration for standardized agent communication.**

---

## Features

- **🔍 Smart Scraping** – Automatically scrapes CFP events from confs.tech/cfp using Selenium
- **🎼 Event Orchestrator** – Central coordinator that normalizes, deduplicates, and manages event data flow
- **🤖 AI Filtering** – Uses Ollama locally with Llama 3.2 to filter events based on user interests (AI, engineering leadership, fintech, developer experience)
- **📧 Email Notifications** – Sends beautifully formatted HTML email notifications with filtered CFP results
- **⏰ Automated Scheduling** – Docker container runs daily at 8am UK time via cron
- **🌐 Complete MCP Integration** – All agents implement Anthropic's Model Context Protocol
- **🏗️ Modular Architecture** – Four specialized MCP agents communicate via standardized protocol

---

## Tech Stack

- **Language**: Python 3.12
- **Web Scraping**: Selenium with Chrome WebDriver
- **Local LLM**: Ollama (qwen2.5-coder:1.5b)
- **Agent Protocol**: Anthropic's Model Context Protocol (MCP)
- **Email**: SMTP with Gmail integration and HTML formatting
- **Containerization**: Docker with scheduled execution
- **Data Storage**: JSON files for event pipeline stages

---

## Architecture

CFP Scout uses **Complete Event-Driven MCP Architecture** with four specialized agents:

```
┌─────────────────┐    MCP     ┌──────────────────┐
│   CFP Scout    │◄──────────►│ Event Orchestr.  │
│   MCP Host     │            │   MCP Server     │
└─────────────────┘            └──────────────────┘
         │                              │
         │ MCP Tool Calls              │
         ▼                              ▼
┌─────────────────┐            ┌──────────────────┐
│  CFP Filter     │            │    Scraper       │
│  MCP Server     │            │   MCP Server     │
└─────────────────┘            └──────────────────┘
         │                              │
         │                              │
         ▼                              ▼
┌─────────────────┐            ┌──────────────────┐
│  Email Sender   │            │   Future Agent   │
│  MCP Server     │            │   MCP Server     │
└─────────────────┘            └──────────────────┘
```

### **Data Flow**
1. **Collection** → Scraper MCP Server gathers raw CFP events from various sources
2. **Coordination** → Event Orchestrator MCP Server normalizes and deduplicates data
3. **Intelligence** → CFP Filter MCP Server uses Ollama LLM to score event relevance
4. **Communication** → Email Sender MCP Server delivers beautifully formatted results
5. **Orchestration** → MCP Host coordinates all agent interactions using standard protocol

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

**Option A: Complete MCP Pipeline** (Recommended)
```bash
# Run complete MCP agent ecosystem
python src/mcp_host.py
```

**Option B: Individual MCP Servers**
```bash
# Run specific MCP servers
python src/agents/scraper_mcp_server.py          # Web scraping
python src/agents/cfp_filter_mcp_server.py       # AI filtering  
python src/agents/email_sender_mcp_server.py     # Email notifications
python src/agents/event_orchestrator_mcp_server.py # Pipeline coordination
```

**Option C: Traditional Pipeline** (Backward Compatible)
```bash
# Run legacy pipeline
python src/event_orchestrator.py
```

---

## Project Structure

```
cfp-scout/
├── 📁 src/
│   ├── 📄 event_orchestrator.py        # Central pipeline coordinator
│   ├── 📄 cfp_filter_agent.py          # LLM-based event filtering
│   ├── 📄 scraper.py                   # Web scraping engine
│   ├── 📄 email_sender.py              # Email notification system
│   ├── 📄 main.py                      # Main execution script
│   ├── 📄 mcp_host.py                  # Complete MCP ecosystem coordinator
│   └── 📁 agents/                      # All MCP server implementations
│       ├── 📄 scraper_mcp_server.py
│       ├── 📄 cfp_filter_mcp_server.py
│       ├── 📄 email_sender_mcp_server.py
│       └── 📄 event_orchestrator_mcp_server.py
├── 📄 Dockerfile                       # Container configuration
├── 📄 requirements.txt                 # Python dependencies
├── 📄 env.example                      # Environment template
└── 📄 README.md                        # This file
```

---

## Complete MCP Integration

CFP Scout now uses **Anthropic's Model Context Protocol** across all agents:

### **MCP Benefits**
- **Standardization**: All agents communicate via JSON-RPC 2.0
- **Composability**: Agents can be both clients and servers
- **Self-Discovery**: Dynamic capability discovery
- **Security**: Built-in authentication and authorization
- **Ecosystem**: Compatible with Claude Desktop, Cursor, Windsurf

### **Complete MCP Agent Ecosystem**

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

### **MCP Pipeline Usage**

```python
# Complete MCP ecosystem coordination
async with CFPScoutMCPHost() as mcp_host:
    # Execute full pipeline via MCP
    results = await mcp_host.execute_full_mcp_pipeline()
    
    # Get pipeline status
    status = await mcp_host.get_pipeline_status()
    
    # List all available tools across agents
    tools = await mcp_host.list_all_available_tools()
    
    # Access agent resources
    resources = await mcp_host.list_all_available_resources()
```

---

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `OLLAMA_HOST` | Ollama API endpoint | `http://localhost:11434` |
| `OLLAMA_MODEL` | Local LLM model name | `qwen2.5-coder:1.5b` |
| `USER_INTERESTS` | Comma-separated interests | `AI,machine learning,fintech` |
| `EMAIL_ADDRESS` | Sender email address | `your_email@gmail.com` |
| `EMAIL_PASSWORD` | Email app password | `your_app_password_here` |
| `TO_EMAIL` | Recipient email address | `recipient@example.com` |
| `SMTP_SERVER` | SMTP server hostname | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP server port | `587` |
| `SCHEDULE_TIME` | Daily execution time | `08:00` |
| `TIMEZONE` | Execution timezone | `Europe/London` |

---

## Development

### **Test Complete MCP Ecosystem**

```bash
# Test all MCP agents
python src/mcp_host.py

# Test individual agents
python src/agents/scraper_mcp_server.py
python src/agents/cfp_filter_mcp_server.py
python src/agents/email_sender_mcp_server.py
python src/agents/event_orchestrator_mcp_server.py

# Test traditional pipeline (backward compatibility)
python src/event_orchestrator.py
```

### **Add New MCP Agent**

1. Create MCP server: `src/agents/new_agent_mcp_server.py`
2. Expose tools, resources, and prompts using FastMCP decorators
3. Register in MCP Host: `src/mcp_host.py`
4. Update configuration and documentation

---

## Docker Deployment

### **Build and Run**

```bash
# Build container
docker build -t cfp-scout .

# Run once
docker run --env-file .env cfp-scout

# Run with schedule (daily 8am UK time)
docker run -d --env-file .env --restart unless-stopped cfp-scout
```

---

## Progress

### **✅ Phase 1: Core MCP Integration (COMPLETED)**
- [x] **Event Orchestrator MCP Server** - Pipeline coordination via MCP
- [x] **CFP Filter MCP Server** - LLM-based filtering via MCP
- [x] **MCP Host** - Agent coordination and discovery
- [x] **Testing & Validation** - Comprehensive test suite
- [x] **Documentation** - Complete setup and usage guides

### **✅ Phase 2: Complete Agent Ecosystem (COMPLETED)**
- [x] **Email Sender MCP Server** - HTML email notifications via MCP
- [x] **Scraper MCP Server** - Web scraping via MCP
- [x] **Full MCP Pipeline** - End-to-end MCP execution
- [x] **Four-Agent System** - Complete agent ecosystem operational

### **🚧 Phase 3: Advanced Features (IN PROGRESS)**  
- [ ] **Main Orchestration** - Scheduled execution logic
- [ ] **Docker Container** - Production deployment setup
- [ ] **Claude Desktop Integration** - MCP ecosystem connection

### **🔮 Phase 4: Future Enhancements**
- [ ] **Additional Scrapers** - More CFP sources
- [ ] **Advanced Filtering** - ML-based relevance scoring
- [ ] **Web Interface** - Dashboard for management
- [ ] **Analytics** - Success tracking and insights
- [ ] **MCP Registry** - Public agent discovery

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

**🎉 Phase 2 Complete: Four-Agent MCP Ecosystem Operational!**

