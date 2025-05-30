# CFP Scout
AI-powered agent system for discovering relevant tech conference CFPs

**CFP Scout** is a fully Dockerized AI-powered agent system that scrapes tech events with open CFPs, filters them using a local language model via Ollama based on user-defined interests, and sends daily email notifications at 8am UK time with the most relevant results.

---

## Features

- **🔍 Smart Scraping** – Automatically scrapes CFP events from confs.tech/cfp using Selenium
- **🎯 Event MCP Agent** – Central orchestrator that normalizes, deduplicates, and manages event data flow
- **🤖 AI Filtering** – Uses Ollama locally with Llama 3.2 to filter events based on user interests (AI, engineering leadership, fintech, developer experience)
- **📧 Daily Notifications** – Sends formatted emails with relevant CFPs every day at 8am UK time
- **🐳 Fully Dockerized** – Easy deployment with Docker container
- **🛡️ Error Handling** – Robust error handling and logging throughout the pipeline
- **🔄 Deduplication** – Automatic duplicate event detection and removal
- **🏠 Local AI** – Uses Ollama for private, local LLM processing without API costs

---

## Tech Stack

- **Python 3.11** – Core application language
- **Selenium/Chrome** – Web scraping for JavaScript-rendered content
- **Ollama + Llama 3.2** – Local LLM for event filtering and relevance scoring
- **SMTP/Gmail** – Email delivery
- **Docker** – Containerization
- **JSON** – Data storage and interchange

---

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Scraper(s)    │───▶│   Event MCP     │───▶│   CFP Filter    │───▶│   Email Sender  │
│   (scraper.py)  │    │  (event_mcp.py) │    │   Agent         │    │(email_sender.py)│
│                 │    │                 │    │(cfp_filter_agent│    │                 │
└─────────────────┘    │  • Normalize    │    │     .py)        │    └─────────────────┘
                       │  • Deduplicate  │    │                 │             │
                       │  • Store        │    │  • Ollama LLM   │             ▼
                       │  • Orchestrate  │    │  • Relevance    │      📧 Daily Email
                       │                 │◀───│    Scoring      │         8am UK
                       └─────────────────┘    └─────────────────┘
                                │
                                ▼
                        ┌─────────────────┐
                        │   Main Scheduler│
                        │    (main.py)    │
                        └─────────────────┘
```

**Event MCP Agent** acts as the central orchestrator:
- ✅ Collects raw events from one or more scrapers
- ✅ Normalizes data into consistent structure
- ✅ Deduplicates events based on title + link
- ✅ Stores events at each pipeline stage (raw, normalized, filtered)
- ✅ Coordinates filtering and email processes
- ✅ Provides comprehensive error handling and logging

---

## Project Structure

```
cfp-scout/
├── src/
│   ├── scraper.py              # Event scraper agent (Selenium-based)
│   ├── event_mcp.py            # Event MCP agent (central orchestrator)
│   ├── cfp_filter_agent.py     # AI filtering agent (Ollama-based)
│   ├── email_sender.py         # Email notification agent
│   ├── main.py                 # Main orchestrator
│   └── test_event_mcp.py       # Event MCP tests
├── logs/
│   ├── raw_events.json         # Raw scraped events
│   ├── normalized_events.json  # Normalized & deduplicated events
│   └── filtered_events.json    # LLM-filtered relevant events
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker configuration
├── .env.example               # Environment variables template
├── docker-compose.yml         # Docker compose setup
└── README.md                  # This file
```

---

## Environment Variables

Create a `.env` file with the following variables:

```env
# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b

# Email Configuration  
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
TO_EMAIL=recipient@example.com

# User Interests for CFP Filtering (comma-separated)
USER_INTERESTS=AI,machine learning,artificial intelligence,engineering leadership,fintech,financial technology,developer experience,DevOps,software architecture,data engineering,cloud computing

# Scheduling Configuration
SCHEDULE_TIME=08:00
TIMEZONE=Europe/London

# Logging Configuration
LOG_LEVEL=INFO
```

---

## Setup the Application

### Prerequisites
- Docker and Docker Compose
- **Ollama** installed and running locally
- **Llama 3.2:3b model** downloaded via Ollama
- Gmail account with App Password enabled

### Ollama Setup

1. **Install Ollama**
   ```bash
   # macOS
   brew install ollama
   
   # Or download from https://ollama.ai
   ```

2. **Start Ollama service**
   ```bash
   ollama serve
   ```

3. **Download the Llama 3.2 model**
   ```bash
   ollama pull llama3.2:3b
   ```

4. **Verify setup**
   ```bash
   ollama list
   # Should show llama3.2:3b in the list
   ```

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd cfp-scout
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

3. **Install dependencies (optional for local development)**
   ```bash
   pip install -r requirements.txt
   ```

### Docker Setup

1. **Build the Docker image**
   ```bash
   docker build -t cfp-scout .
   ```

2. **Run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

---

## Run the Application

### Manual Run
```bash
# Test Ollama connection and CFP Filter
python src/cfp_filter_agent.py

# Run the complete pipeline
python src/event_mcp.py

# Run individual components
python src/scraper.py           # Scraper only
python src/test_event_mcp.py    # Run MCP tests
```

### Docker Run
```bash
docker run --env-file .env --network host cfp-scout
```
*Note: `--network host` is needed for Docker to access local Ollama*

### Scheduled Daily Execution
The application is designed to run daily at 8am UK time. Use your preferred scheduling method:

- **Docker Compose with cron**: Already configured in docker-compose.yml
- **Host cron**: Add cron job to run the Docker container
- **Cloud scheduler**: Use AWS EventBridge, Google Cloud Scheduler, etc.

---

## Development Progress

### ✅ Completed
- [x] Project structure and README setup
- [x] Event Scraper Agent (scraper.py) - Selenium-based scraping from confs.tech/cfp
- [x] Event MCP Agent (event_mcp.py) - Central orchestrator with normalization and deduplication
- [x] CFP Filter Agent (cfp_filter_agent.py) - Ollama-based LLM filtering

### 🚧 In Progress  
- [ ] Email Sender Agent (email_sender.py)

### 📋 Upcoming
- [ ] Main Scheduler (main.py)
- [ ] Final Docker integration and testing

---

## Data Flow

1. **Scraping Phase**: Scraper agents collect raw CFP events
2. **MCP Phase**: Event MCP normalizes, deduplicates, and stores events
3. **Filtering Phase**: Ollama LLM filters events based on user interests  
4. **Notification Phase**: Email sender delivers relevant events

**Current Status**: Successfully scraping and processing **27 CFP events** with full deduplication, normalization, and **local AI filtering via Ollama**.

---

## Troubleshooting

### Ollama Issues
- **Connection Error**: Make sure Ollama is running (`ollama serve`)
- **Model Not Found**: Download the model (`ollama pull llama3.2:3b`)
- **Port Issues**: Check if port 11434 is available or change `OLLAMA_HOST` in `.env`

### Docker Network Issues
- Use `--network host` flag when running Docker to access local Ollama
- Or run Ollama in Docker and connect containers via Docker network

---

## Future Improvements

- 🎯 **Feedback Agent** – Learn user preferences over time
- 💬 **Slack/Telegram Integration** – Multiple notification channels
- 📅 **Calendar Sync** – Auto-add deadlines to calendar
- 🎨 **Web UI** – Dashboard with historical logs and preferences
- 📊 **Analytics** – Track CFP success rates and preferences
- 🔌 **Additional Scrapers** – Support for more conference listing sites
- 🤖 **Model Options** – Support for different Ollama models (larger/smaller)

---

## License
MIT

