# CFP Scout

AI-powered agent system for discovering relevant tech conference CFPs using **Anthropic's Model Context Protocol (MCP)**

**CFP Scout** is a fully Dockerized AI-powered agent system that scrapes tech events with open CFPs, filters them using a local language model via Ollama based on user-defined interests, and sends daily email notifications at 8am UK time with the most relevant results. **Now enhanced with MCP for standardized agent communication.**

---

## Features

- **🔍 Smart Scraping** – Automatically scrapes CFP events from confs.tech/cfp using Selenium
- **🎼 Event Orchestrator** – Central coordinator that normalizes, deduplicates, and manages event data flow
- **🤖 AI Filtering** – Uses Ollama locally with Llama 3.2 to filter events based on user interests (AI, engineering leadership, fintech, developer experience)
- **📧 Daily Notifications** – Sends formatted email notifications with filtered CFP results
- **⏰ Automated Scheduling** – Docker container runs daily at 8am UK time via cron
- **🌐 MCP Integration** – Uses Anthropic's Model Context Protocol for standardized agent communication
- **🏗️ Modular Architecture** – Agents communicate via MCP, enabling composability and future extensibility

---

## Tech Stack

- **Language**: Python 3.12
- **Web Scraping**: Selenium with Chrome WebDriver
- **Local LLM**: Ollama (qwen2.5-coder:1.5b)
- **Agent Protocol**: Anthropic's Model Context Protocol (MCP)
- **Email**: SMTP with Gmail integration
- **Containerization**: Docker with scheduled execution
- **Data Storage**: JSON files for event pipeline stages

---

## Architecture

CFP Scout uses **Event-Driven MCP Architecture** with agents communicating via Anthropic's Model Context Protocol:

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
1. **Collection** → Scrapers gather raw CFP events from various sources
2. **Coordination** → Event Orchestrator normalizes and deduplicates data via MCP
3. **Intelligence** → CFP Filter Agent uses Ollama LLM to score event relevance via MCP
4. **Communication** → Email Sender delivers filtered results to users via MCP
5. **Orchestration** → MCP Host coordinates all agent interactions using standard protocol

---

## Quick Start

### **1. Clone and Setup**

```bash
git clone <repository-url>
cd cfp-scout
cp .env.example .env
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

**Option A: Traditional Pipeline**
```bash
# Run complete pipeline
python src/event_orchestrator.py

# Or run individual components
python src/cfp_filter_agent.py  # Test filter
python src/scraper.py           # Test scraper
```

**Option B: MCP-Enhanced Pipeline**
```bash
# Run MCP Host (coordinates all agents)
python src/mcp_host.py

# Or run individual MCP servers
python src/agents/cfp_filter_mcp_server.py
python src/agents/event_orchestrator_mcp_server.py
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
│   ├── 📄 mcp_host.py                  # MCP client host coordinator
│   └── 📁 agents/                      # MCP server implementations
│       ├── 📄 cfp_filter_mcp_server.py
│       └── 📄 event_orchestrator_mcp_server.py
├── 📄 Dockerfile                       # Container configuration
├── 📄 requirements.txt                 # Python dependencies
├── 📄 .env.example                     # Environment template
└── 📄 README.md                        # This file
```

---

## MCP Integration

CFP Scout now uses **Anthropic's Model Context Protocol** for agent communication:

### **MCP Benefits**
- **Standardization**: All agents communicate via JSON-RPC 2.0
- **Composability**: Agents can be both clients and servers
- **Self-Discovery**: Dynamic capability discovery
- **Security**: Built-in authentication and authorization
- **Ecosystem**: Compatible with Claude Desktop, Cursor, Windsurf

### **Available MCP Servers**

**CFP Filter MCP Server** (`src/agents/cfp_filter_mcp_server.py`)
- **Tools**: `filter_cfp_events`, `test_ollama_connection`, `get_filter_summary`
- **Resources**: `user://interests`, `ollama://status`, `config://filter`
- **Prompts**: `create_filter_prompt`, `create_batch_filter_prompt`

**Event Orchestrator MCP Server** (`src/agents/event_orchestrator_mcp_server.py`)
- **Tools**: `run_cfp_pipeline`, `normalize_events`, `get_pipeline_statistics`, `clean_storage`
- **Resources**: `pipeline://status`, `events://raw`, `events://normalized`, `events://filtered`
- **Prompts**: `create_pipeline_execution_prompt`, `create_event_analysis_prompt`

### **MCP Usage Examples**

```python
# Connect to MCP servers
async with CFPScoutMCPHost() as mcp_host:
    # Execute pipeline via MCP
    results = await mcp_host.execute_pipeline_via_mcp()
    
    # Get pipeline status
    status = await mcp_host.get_pipeline_status()
    
    # List available tools
    tools = await mcp_host.list_all_available_tools()
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
| `SCHEDULE_TIME` | Daily execution time | `08:00` |
| `TIMEZONE` | Execution timezone | `Europe/London` |

---

## Development

### **Run Tests**

```bash
# Test Event Orchestrator
python src/test_event_mcp.py

# Test CFP Filter with Ollama
python src/cfp_filter_agent.py

# Test complete pipeline
python src/event_orchestrator.py
```

### **Development with MCP**

```bash
# Start MCP servers individually for debugging
python src/agents/cfp_filter_mcp_server.py
python src/agents/event_orchestrator_mcp_server.py

# Test MCP communication
python src/mcp_host.py
```

### **Add New MCP Agent**

1. Create MCP server: `src/agents/new_agent_mcp_server.py`
2. Expose tools, resources, and prompts using `@mcp_server.tool()`, `@mcp_server.resource()`, `@mcp_server.prompt()`
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

### **Environment in Docker**

```bash
# Use Docker environment file
docker run --env-file .env cfp-scout

# Or pass individual variables
docker run -e OLLAMA_HOST=http://host.docker.internal:11434 \
           -e USER_INTERESTS="AI,engineering" \
           cfp-scout
```

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

---

## Progress

### **✅ Completed**
- [x] **Event Orchestrator** - Central pipeline coordination
- [x] **CFP Filter Agent** - LLM-based event filtering with Ollama
- [x] **Web Scraper** - Selenium-based CFP data collection
- [x] **Data Pipeline** - Normalization, deduplication, storage
- [x] **MCP Integration** - Anthropic's Model Context Protocol implementation
- [x] **Testing & Validation** - Comprehensive test suite
- [x] **Documentation** - Complete setup and usage guides

### **🚧 In Progress**  
- [ ] **Email Sender Agent** - Notification system
- [ ] **Main Orchestration** - Scheduled execution logic
- [ ] **Docker Container** - Production deployment setup

### **🔮 Future Enhancements**
- [ ] **Additional Scrapers** - More CFP sources
- [ ] **Advanced Filtering** - ML-based relevance scoring
- [ ] **Web Interface** - Dashboard for management
- [ ] **Analytics** - Success tracking and insights
- [ ] **MCP Registry** - Public agent discovery

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

