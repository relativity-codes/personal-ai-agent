# Personal AI Agent - Project Overview Document

---

## Document Control

| Version | Date | Author | Status |
|---------|------|--------|--------|
| 1.0 | 2026-04-21 | Project Lead | Final |

---

## 1. Executive Summary

### 1.1 What is Personal AI Agent?

**Personal AI Agent** is a multi-agent AI system that understands natural language commands and automatically executes complex workflows across your productivity tools. Instead of manually switching between GitHub, Notion, Calendar, and Gmail, you simply type what you want, and the AI agent orchestrates everything.

### 1.2 The Problem We Solve

**The Current Reality:**
- You spend 30-60 minutes daily switching between tools
- Context is scattered across GitHub (code), Notion (docs), Calendar (meetings), and Gmail (communication)
- Manual workflows are repetitive and error-prone
- Existing AI tools are chatbots that can't actually DO anything

**Our Solution:**
- One natural language interface for all your tools
- AI agents that actually execute tasks, not just chat
- Automatic context gathering and summarization
- Structured outputs ready for action

### 1.3 Key Capabilities

| Command | What It Does |
|---------|---------------|
| "Prepare for tomorrow's standup" | Fetches calendar events, summarizes PRs, creates agenda in Notion |
| "What PRs need my review?" | Lists open PRs with summaries and review status |
| "Summarize my week" | Aggregates commits, PRs, meetings, and emails |
| "Create a meeting note for the sprint planning" | Creates Notion page with calendar event details |

---

## 2. How It Works

### 2.1 The Four-Agent Architecture

The system uses four specialized AI agents working together:

```
                    ┌─────────────────┐
                    │     USER        │
                    │  "Prepare for   │
                    │  standup"       │
                    └────────┬────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────────┐
│                    1. INTENT AGENT                                 │
│                    Understands what you want                       │
│                    "agenda_preparation" confidence: 0.95           │
└────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────────┐
│                    2. MANAGERIAL AGENT                             │
│                    Creates the plan                                │
│                    Step 1: Get calendar events                     │
│                    Step 2: List open PRs                           │
│                    Step 3: Create Notion agenda                    │
└────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────────┐
│                    3. TASK PLANNER AGENT                           │
│                    Tracks what's done                              │
│                    ✅ Calendar fetched                             │
│                    ⏳ PRs in progress                              │
│                    ⏸ Notion agenda waiting                        │
└────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────────┐
│                    4. ACTION AGENT                                 │
│                    Executes the tasks                              │
│                    → Calls GitHub API                              │
│                    → Calls Calendar API                            │
│                    → Calls Notion API                              │
└────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │     USER        │
                    │  "Here's your   │
                    │  standup prep"  │
                    └─────────────────┘
```

### 2.2 Simple Example Flow

**You type:** "Prepare for tomorrow's standup"

**What happens behind the scenes:**

1. **Intent Agent** recognizes this as an "agenda preparation" request with 95% confidence

2. **Managerial Agent** creates a 3-step plan:
   - Step 1: Fetch tomorrow's calendar events
   - Step 2: List open pull requests needing review
   - Step 3: Create a standup agenda in Notion

3. **Task Planner Agent** tracks progress:
   - Task 1 and 2 can run simultaneously (no dependencies)
   - Task 3 waits for both to complete

4. **Action Agent** executes:
   - Calls Google Calendar API → gets 2 meetings
   - Calls GitHub API → finds 3 open PRs
   - Calls Notion API → creates agenda page

5. **You receive:** A formatted response with calendar events, PR summaries, and a link to your Notion agenda

### 2.3 Supported Integrations

| Integration | What We Can Do |
|-------------|----------------|
| **GitHub** | List PRs, summarize commits, create issues, get review status |
| **Notion** | Create pages, update documents, extract agenda items, search databases |
| **Google Calendar** | Fetch events, find free time, create meetings, get daily agenda |
| **Gmail** | Summarize threads, search emails, extract action items |

---

## 3. Technology Stack

### 3.1 At a Glance

| Layer | Technology | Why |
|-------|------------|-----|
| **Frontend** | Next.js 14 + React | Fast, modern UI with real-time streaming |
| **Backend** | FastAPI (Python) | High-performance async API |
| **AI Orchestration** | LangGraph | Stateful multi-agent workflows |
| **LLM Gateway** | OpenRouter | Access to Claude, GPT-4o, Llama via one API |
| **Database** | PostgreSQL | Reliable, ACID-compliant storage |
| **Cache** | Redis | Lightning-fast state management |
| **Auth** | Clerk | Simple, secure user management |

### 3.2 Why These Choices?

| Decision | Alternatives | Why We Chose This |
|----------|--------------|-------------------|
| **FastAPI over Django** | Django, Flask | Async native, automatic API docs, better performance |
| **LangGraph over custom** | Custom orchestration | Built-in state management, cycle detection, streaming |
| **OpenRouter over direct** | Direct API calls | One key for all models, automatic fallback, cost optimization |
| **PostgreSQL over MongoDB** | MongoDB, SQLite | ACID compliance, JSON support, reliability |
| **Next.js over Vite** | Vite, CRA | Server components, API routes, built-in streaming |

---

## 4. Key Features

### 4.1 Natural Language Interface

Simply type what you want in plain English:

```
✓ "What's on my calendar today?"
✓ "Show me PRs that need review"
✓ "Summarize emails from yesterday"
✓ "Create a project update for the team"
✓ "What did I work on last week?"
```

### 4.2 Smart Task Decomposition

The system automatically breaks complex requests into steps:

**Request:** "Prepare for tomorrow's standup"

**Decomposed into:**
1. Fetch calendar events (runs immediately)
2. List open PRs (runs immediately)
3. Create Notion agenda (waits for 1 & 2)

### 4.3 Real-Time Streaming

Watch the AI work in real-time:

```
→ Understanding your request...
→ Fetching calendar events... (2 events found)
→ Checking GitHub PRs... (3 PRs need review)
→ Creating Notion agenda... (done)
→ Finalizing response...
```

### 4.4 Structured Output

Responses are formatted for action:

```markdown
## 📅 Tomorrow's Calendar (April 22, 2026)

- **10:00 AM** - Sprint Planning (1 hour)
- **2:00 PM** - Code Review (30 min)

## 🔀 Pull Requests Needing Review

- **#245**: Auth middleware (by @alice) - Ready for review
- **#247**: Fix timeout bug (by @bob) - Changes requested

## 📝 Agenda Created in Notion

[ ] Review PR #245
[ ] Discuss sprint outcomes
[ ] Update team on blockers

[View Agenda →](https://notion.so/...)
```

### 4.5 MCP Server Connections

Connect your tools with one click OAuth:

```
┌────────────────────────────────────────────┐
│         Connected Services                 │
├────────────────────────────────────────────┤
│ ✓ GitHub     • Connected as @username     │
│ ✓ Notion     • Connected to Workspace     │
│ ✓ Calendar   • Connected (Gmail account)  │
│ ○ Gmail      • Connect to enable emails   │
└────────────────────────────────────────────┘
```

---

## 5. User Journey

### 5.1 First-Time User

1. **Sign up** with Google/GitHub (powered by Clerk)
2. **Connect your tools** with one-click OAuth
3. **Type your first command** - "Prepare for tomorrow's standup"
4. **Watch the magic happen** - See real-time progress
5. **Get results** - Formatted response with action items

### 5.2 Daily Usage

**Morning (5 minutes):**
```
"Prepare for standup" → Get agenda, PRs, calendar
```

**During work (as needed):**
```
"What PRs are blocking me?" → List of PRs needing attention
"Summarize my afternoon" → Calendar + action items
```

**End of day (2 minutes):**
```
"What did I accomplish today?" → Summary of commits, PRs, meetings
```

---

## 6. Success Metrics

### 6.1 Target KPIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| Time saved per day | 30-45 minutes | User surveys |
| Intent classification accuracy | >90% | Manual review |
| Task completion rate | >95% | System logs |
| User retention (weekly) | >80% | Analytics |
| Average response time | <3 seconds | System metrics |

### 6.2 Success Stories (Expected)

**Software Engineer:**
> "I save 45 minutes every morning. Instead of checking 4 different tools, I just ask the AI to prepare my standup."

**Team Lead:**
> "I can quickly see what my team accomplished without digging through GitHub and Notion separately."

**Remote Worker:**
> "Starting my day with a single prompt gives me everything I need - calendar, pending reviews, and action items."

---

## 7. Roadmap

### Phase 1: Foundation (Weeks 1-2) ✅
- [ ] Project setup and architecture
- [ ] Basic FastAPI backend
- [ ] Next.js frontend skeleton
- [ ] PostgreSQL + Redis setup

### Phase 2: Core Agents (Weeks 3-5) 🚧
- [ ] Intent Agent with LLM classification
- [ ] Task Planner Agent with dependency tracking
- [ ] Action Agent with MCP execution
- [ ] Managerial Agent orchestration

### Phase 3: Integrations (Weeks 6-7)
- [ ] GitHub MCP Server (PRs, commits, issues)
- [ ] Notion MCP Server (pages, databases)
- [ ] Calendar MCP Server (events, scheduling)
- [ ] Gmail MCP Server (emails, threads)

### Phase 4: Production (Week 8)
- [ ] OAuth for all services
- [ ] Rate limiting and error handling
- [ ] Monitoring and logging
- [ ] Deployment to production

### Future Enhancements

| Feature | Timeline | Description |
|---------|----------|-------------|
| Slack integration | Q2 2026 | Run commands from Slack |
| Custom workflows | Q3 2026 | Save and reuse command sequences |
| Mobile app | Q4 2026 | iOS/Android native apps |
| Team collaboration | Q1 2027 | Shared workflows and reporting |

---

## 8. Getting Started

### 8.1 For End Users

1. **Visit** `https://app.personal-ai-agent.com`
2. **Sign up** with Google or GitHub
3. **Connect** your tools (GitHub, Notion, Google Calendar)
4. **Start typing** your commands

### 8.2 For Developers

```bash
# Clone the repository
git clone https://github.com/your-org/personal-ai-agent.git

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add your API keys

# Frontend setup
cd ../frontend
npm install
cp .env.example .env.local

# Run the stack
# Terminal 1: PostgreSQL & Redis
brew services start postgresql redis

# Terminal 2: Backend
cd backend && uvicorn app.main:app --reload

# Terminal 3: Frontend
cd frontend && npm run dev

# Open http://localhost:3000
```

### 8.3 Requirements

| For Users | For Developers |
|-----------|----------------|
| Modern web browser | Python 3.11+ |
| GitHub account | Node.js 18+ |
| Notion account | PostgreSQL 15+ |
| Google account | Redis 7+ |
| (Optional) Gmail access | API keys (OpenRouter, Clerk) |

---

## 9. Cost Structure

### 9.1 For End Users (Estimated)

| Plan | Price | Features |
|------|-------|----------|
| **Free** | $0 | 50 requests/month, basic integrations |
| **Pro** | $15/month | Unlimited requests, all integrations, priority support |
| **Team** | $50/month | 5 users, shared workflows, admin controls |

### 9.2 Operational Costs (Monthly)

| Service | Development | Production (1000 users) |
|---------|-------------|-------------------------|
| OpenRouter (LLM) | $20 | $500 |
| PostgreSQL (RDS) | $0 (local) | $50 |
| Redis (ElastiCache) | $0 (local) | $30 |
| Vercel (Frontend) | $0 | $20 |
| Clerk (Auth) | $0 | $25 |
| **Total** | ~$20/month | ~$625/month |

---

## 10. Comparison with Alternatives

| Feature | Personal AI Agent | ChatGPT | Custom Scripts | Manual Work |
|---------|-------------------|---------|----------------|-------------|
| **Executes actions** | ✅ | ❌ (read-only) | ✅ | ❌ |
| **Multi-tool workflows** | ✅ | ❌ | ✅ (complex) | ❌ |
| **Natural language** | ✅ | ✅ | ❌ | ❌ |
| **Real-time status** | ✅ | ❌ | ❌ | N/A |
| **No coding required** | ✅ | ✅ | ❌ | N/A |
| **Structured output** | ✅ | ❌ | ✅ | ❌ |
| **Learning curve** | Low | Low | High | None |

**Why Personal AI Agent is better:**
- ChatGPT can't actually DO things (can't create Notion pages or review PRs)
- Custom scripts require programming knowledge
- Manual work is slow and error-prone

---

## 11. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| **API rate limits** | Medium | Implement caching, queuing, and user notifications |
| **LLM hallucinations** | High | Validation layer, confidence scoring, clarification prompts |
| **OAuth token expiry** | Medium | Automatic refresh, clear user prompts |
| **Complex dependency cycles** | Low | Task Planner validates before execution |
| **Cost overruns** | Medium | Rate limiting, cost alerts, user quotas |

---

## 12. Support & Resources

### 12.1 Documentation

| Resource | Location |
|----------|----------|
| User Guide | `docs/user-guide.md` |
| API Reference | `http://localhost:8000/docs` |
| Developer Setup | `README.md` |
| Architecture | `docs/architecture.md` |

### 12.2 Contact

| Purpose | Contact |
|---------|---------|
| Bug reports | `bugs@personal-ai-agent.com` |
| Feature requests | `feedback@personal-ai-agent.com` |
| Security issues | `security@personal-ai-agent.com` |
| General questions | `support@personal-ai-agent.com` |

---

## 13. Glossary

| Term | Definition |
|------|------------|
| **Agent** | An AI component with a specific role (Intent, Managerial, etc.) |
| **MCP** | Model Context Protocol - standard for tool-calling AI |
| **MCP Server** | A service that provides tools for a specific platform (GitHub, Notion) |
| **LangGraph** | Framework for building stateful multi-agent applications |
| **OpenRouter** | Unified API for multiple LLM providers |
| **Task Decomposition** | Breaking a complex request into smaller steps |
| **Dependency Graph** | Map of which tasks depend on others |
| **Streaming** | Real-time response delivery as the AI thinks |

---

## 14. Conclusion

**Personal AI Agent** transforms how you work with your tools. Instead of context switching between 4+ applications, you get a single natural language interface that understands intent, plans execution, tracks progress, and delivers structured results.

**Key Takeaways:**
- ✅ **Save 30-45 minutes daily** on repetitive tasks
- ✅ **One interface** for GitHub, Notion, Calendar, Gmail
- ✅ **No coding required** - just type what you want
- ✅ **Real-time feedback** as tasks execute
- ✅ **Structured outputs** ready for action

**Ready to get started?**
- **Users:** Visit `https://app.personal-ai-agent.com`
- **Developers:** Clone the repository and follow the setup guide

---

*This overview document is living documentation. For the latest information, please refer to the project repository or contact the project team.*