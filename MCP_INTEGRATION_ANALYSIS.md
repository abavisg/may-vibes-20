# MCP Integration Analysis for CFP Scout

## Summary

After renaming our **Event MCP** → **Event Orchestrator** to avoid confusion, I've researched integrating **Anthropic's Model Context Protocol (MCP)** to standardize communications between CFP Scout agents. Here's what needs to be done:

---

## 📋 **Current Status**

✅ **Renamed Components**:
- `src/event_mcp.py` → `src/event_orchestrator.py`
- `EventMCP` class → `EventOrchestrator` class
- Updated all tests and references
- All existing functionality preserved

✅ **Existing Agent Architecture**:
- Event Orchestrator (central coordinator)
- CFP Filter Agent (LLM-based filtering with Ollama)
- Scraper Agent (data collection)
- Email Sender Agent (notifications)

---

## 🎯 **MCP Integration Goals**

1. **Standardize Agent Communications** using Anthropic's MCP protocol
2. **Enable Agent Composability** - agents can act as both clients and servers
3. **Implement Self-Discovery** - agents can dynamically find and use new capabilities
4. **Maintain Security** with proper authentication and authorization

---

## 📚 **Understanding Anthropic's MCP**

### **Core Architecture**
- **Hosts**: AI applications that initiate connections (our main CFP Scout app)
- **Clients**: Connectors within hosts that manage server connections
- **Servers**: Services that provide capabilities via standardized interfaces

### **Three Primary Interfaces**
1. **Tools**: Executable functions (database queries, API calls)
2. **Resources**: Read-only data streams (file contents, configurations)
3. **Prompts**: Templated interactions for LLMs

### **Communication Protocol**
- JSON-RPC 2.0 messaging over STDIO or Server-Sent Events (SSE)
- Capability negotiation during initialization
- Stateful sessions with lifecycle management

---

## 🛠 **Implementation Requirements**

### **1. Install MCP Dependencies**

```bash
# Add to requirements.txt
mcp>=1.9.2  # Official Anthropic MCP Python SDK
```

### **2. Convert Agents to MCP Servers**

Each agent needs to expose its capabilities as an MCP server:

#### **CFP Filter Agent → MCP Server**
```python
# src/agents/cfp_filter_mcp_server.py
from mcp.server.fastmcp import FastMCP
from mcp.server.models import Resource

mcp_server = FastMCP("CFP Filter Agent")

@mcp_server.tool()
async def filter_events(events: list[dict]) -> list[dict]:
    """Filter events based on user interests using Ollama LLM"""
    # Existing filtering logic
    pass

@mcp_server.resource("user://interests")
async def get_user_interests() -> str:
    """Get current user interests configuration"""
    return os.getenv('USER_INTERESTS', '')

@mcp_server.prompt()
async def create_filter_prompt(events_sample: str) -> str:
    """Generate filtering prompt for LLM"""
    return f"Filter these CFP events based on relevance: {events_sample}"
```

#### **Event Orchestrator → MCP Server**
```python
# src/agents/event_orchestrator_mcp_server.py
from mcp.server.fastmcp import FastMCP

orchestrator_server = FastMCP("Event Orchestrator")

@orchestrator_server.tool()
async def run_pipeline(scraper_modules: list[str] = None) -> dict:
    """Execute the complete CFP Scout pipeline"""
    # Existing pipeline logic
    pass

@orchestrator_server.resource("pipeline://status")
async def get_pipeline_status() -> str:
    """Get current pipeline execution status"""
    pass

@orchestrator_server.resource("events://normalized/{event_id}")
async def get_normalized_event(event_id: str) -> str:
    """Get specific normalized event by ID"""
    pass
```

### **3. Create MCP Client Host Application**

```python
# src/mcp_host.py
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class CFPScoutMCPHost:
    """Main MCP host for CFP Scout system"""
    
    def __init__(self):
        self.sessions = {}
        self.server_configs = {
            'event_orchestrator': StdioServerParameters(
                command='python',
                args=['src/agents/event_orchestrator_mcp_server.py']
            ),
            'cfp_filter': StdioServerParameters(
                command='python', 
                args=['src/agents/cfp_filter_mcp_server.py']
            ),
            'scraper': StdioServerParameters(
                command='python',
                args=['src/agents/scraper_mcp_server.py']  
            ),
            'email_sender': StdioServerParameters(
                command='python',
                args=['src/agents/email_sender_mcp_server.py']
            )
        }
    
    async def start_agent_servers(self):
        """Initialize all MCP agent servers"""
        for name, config in self.server_configs.items():
            async with stdio_client(config) as (read, write):
                session = ClientSession(read, write)
                await session.initialize()
                self.sessions[name] = session
    
    async def execute_pipeline(self) -> dict:
        """Execute pipeline using MCP tool calls"""
        # 1. Start scraper
        scrape_result = await self.sessions['scraper'].call_tool(
            'scrape_cfp_events', {}
        )
        
        # 2. Normalize events
        normalize_result = await self.sessions['event_orchestrator'].call_tool(
            'normalize_events', {'raw_events': scrape_result}
        )
        
        # 3. Filter events  
        filter_result = await self.sessions['cfp_filter'].call_tool(
            'filter_events', {'events': normalize_result}
        )
        
        # 4. Send emails
        email_result = await self.sessions['email_sender'].call_tool(
            'send_cfp_emails', {'filtered_events': filter_result}
        )
        
        return {
            'scraped': len(scrape_result),
            'normalized': len(normalize_result), 
            'filtered': len(filter_result),
            'emails_sent': email_result['success']
        }
```

### **4. Update Main Pipeline**

```python
# src/main.py
import asyncio
from mcp_host import CFPScoutMCPHost

async def main():
    """Main CFP Scout application using MCP"""
    host = CFPScoutMCPHost()
    
    async with host:
        await host.start_agent_servers()
        
        # Execute pipeline via MCP
        results = await host.execute_pipeline()
        
        print(f"Pipeline Results: {results}")

if __name__ == "__main__":
    asyncio.run(main())
```

### **5. Configuration Management**

```yaml
# mcp_agent.config.yaml
execution_engine: asyncio
logger:
  transports: [console, file]
  level: info
  path: "logs/cfp-scout-mcp.jsonl"

mcp:
  servers:
    event_orchestrator:
      command: "python"
      args: ["src/agents/event_orchestrator_mcp_server.py"]
      description: "Central pipeline coordinator"
    
    cfp_filter:
      command: "python" 
      args: ["src/agents/cfp_filter_mcp_server.py"]
      description: "LLM-based event filtering"
      
    scraper:
      command: "python"
      args: ["src/agents/scraper_mcp_server.py"] 
      description: "CFP event data collection"
      
    email_sender:
      command: "python"
      args: ["src/agents/email_sender_mcp_server.py"]
      description: "Email notification system"

ollama:
  host: "http://localhost:11434"
  model: "qwen2.5-coder:1.5b"

email:
  smtp_server: "smtp.gmail.com"
  smtp_port: 587
```

---

## 🔄 **Agent Communication Flow with MCP**

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

---

## 🚀 **Implementation Benefits**

### **1. Standardization**
- All agents communicate via JSON-RPC 2.0
- Consistent tool, resource, and prompt interfaces
- Simplified integration of new agents

### **2. Composability**  
- Agents can be both clients and servers
- Easy to chain workflows and create hierarchies
- Reusable across different AI applications

### **3. Self-Discovery**
- Agents can dynamically discover new capabilities
- Support for MCP registry (when available)
- Runtime adaptation to new tools and data sources

### **4. Security**
- Built-in authentication and authorization
- Capability-based access control
- Secure communication channels

### **5. Ecosystem Integration**
- Compatible with Claude Desktop, Cursor, Windsurf
- Works with existing MCP servers
- Future-proof against protocol evolution

---

## 📅 **Implementation Timeline**

### **Phase 1: Foundation (1-2 days)**
1. Add MCP dependencies
2. Create basic MCP server wrappers for existing agents
3. Implement simple MCP host

### **Phase 2: Core Integration (2-3 days)**  
1. Convert all agents to proper MCP servers
2. Implement full MCP client host
3. Update pipeline to use MCP tool calls
4. Test end-to-end functionality

### **Phase 3: Advanced Features (1-2 days)**
1. Add resource and prompt interfaces
2. Implement agent discovery mechanisms
3. Add security and authentication
4. Performance optimization

### **Phase 4: Documentation & Testing (1 day)**
1. Update README with MCP information
2. Create configuration examples
3. Comprehensive testing
4. Docker integration

---

## 🔧 **Migration Strategy**

### **Backward Compatibility**
- Keep existing `EventOrchestrator` class functional
- Add MCP layer as an optional enhancement
- Gradual migration without breaking changes

### **Testing Approach**
- Unit tests for each MCP server
- Integration tests for MCP communication
- End-to-end pipeline tests
- Performance benchmarking

### **Deployment Options**
1. **Standalone**: Continue using current approach
2. **MCP Enhanced**: Use MCP for agent communication
3. **MCP Native**: Full MCP integration with external clients

---

## 🎯 **Next Steps**

1. **Approve Integration Plan**: Confirm this approach aligns with project goals
2. **Install Dependencies**: Add MCP SDK to requirements
3. **Start with CFP Filter**: Convert one agent as proof of concept
4. **Build MCP Host**: Create basic client host application
5. **Test Integration**: Verify MCP communication works
6. **Scale to All Agents**: Convert remaining agents
7. **Documentation**: Update README and configuration

This integration will position CFP Scout as a cutting-edge, standards-compliant AI agent system that can easily integrate with the growing MCP ecosystem! 