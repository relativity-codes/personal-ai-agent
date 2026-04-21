# Frontend Pages Documentation
## Personal AI Agent - UI/UX Specification

---

## Document Control

| Version | Date | Author | Status |
|---------|------|--------|--------|
| 1.0 | 2026-04-21 | UI/UX Designer | Final |

---

## 1. Page Overview

### 1.1 Complete Page Inventory

| # | Page | Route | Purpose | Authentication |
|---|------|-------|---------|----------------|
| 1 | Landing Page | `/` | Product introduction, sign-up CTA | Public |
| 2 | Sign In | `/sign-in` | User authentication | Public |
| 3 | Sign Up | `/sign-up` | New user registration | Public |
| 4 | Dashboard | `/dashboard` | Overview, activity, quick actions | Required |
| 5 | Chat | `/chat` | Main AI interaction interface | Required |
| 6 | Chat History | `/chat/history` | Past conversations | Required |
| 7 | Chat Session | `/chat/session/[id]` | Specific conversation view | Required |
| 8 | Integrations | `/integrations` | Connect MCP servers (GitHub, Notion, etc.) | Required |
| 9 | Settings | `/settings` | User preferences | Required |
| 10 | Settings/Profile | `/settings/profile` | User profile information | Required |
| 11 | Settings/Preferences | `/settings/preferences` | Default repos, timezone, working hours | Required |
| 12 | Settings/Tokens | `/settings/tokens` | API tokens, usage statistics | Required |
| 13 | Plans | `/plans` | View execution plans history | Required |
| 14 | Plan Details | `/plans/[id]` | Detailed plan execution view | Required |
| 15 | Activity | `/activity` | User activity log | Required |
| 16 | Help | `/help` | Documentation, FAQs | Public |
| 17 | About | `/about` | About the project | Public |
| 18 | Privacy | `/privacy` | Privacy policy | Public |
| 19 | Terms | `/terms` | Terms of service | Public |
| 20 | 404 | `/404` | Not found page | Public |

### 1.2 Page Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              PUBLIC PAGES                                    │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐           │
│  │ Landing │  │ Sign In │  │ Sign Up │  │  Help   │  │  About  │           │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘           │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Authenticated
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AUTHENTICATED PAGES                               │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         MAIN NAVIGATION                              │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │    │
│  │  │Dashboard │ │   Chat   │ │Integrations│ │  Plans  │ │Settings  │   │    │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                    ┌───────────────┼───────────────┐                        │
│                    ▼               ▼               ▼                        │
│            ┌────────────┐  ┌────────────┐  ┌────────────┐                   │
│            │Chat History│  │Plan Details│  │  Activity  │                   │
│            └────────────┘  └────────────┘  └────────────┘                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Page Specifications

### 2.1 Landing Page (`/`)

**Purpose:** First impression, product introduction, conversion

#### Layout Structure

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              HEADER                                         │
│  ┌──────────────┐                              ┌─────────┐ ┌─────────┐     │
│  │ Logo/AI Agent│                              │ Sign In │ │Sign Up  │     │
│  └──────────────┘                              └─────────┘ └─────────┘     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                         HERO SECTION                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                                                                      │    │
│  │                     Your Personal AI Assistant                       │    │
│  │          That Actually Does Things Across Your Tools                 │    │
│  │                                                                      │    │
│  │            ┌─────────────────────────────────────┐                  │    │
│  │            │  Get Started - It's Free →          │                  │    │
│  │            └─────────────────────────────────────┘                  │    │
│  │                                                                      │    │
│  │         "Prepare for tomorrow's standup" - and it just works        │    │
│  │                                                                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                        FEATURES SECTION                                      │
│  ┌─────────────────────────┐ ┌─────────────────────────┐ ┌───────────────┐  │
│  │    Natural Language     │ │    Multi-Tool Actions   │ │  Real-Time    │  │
│  │    "Show me my PRs"     │ │    GitHub + Notion +    │ │  Streaming    │  │
│  │                         │ │    Calendar + Gmail     │ │  Responses    │  │
│  └─────────────────────────┘ └─────────────────────────┘ └───────────────┘  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                        DEMO SECTION                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         Animated Demo                                │    │
│  │                  [Interactive command demonstration]                 │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                        INTEGRATIONS SECTION                                  │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐               │
│  │ GitHub  │ │ Notion  │ │Calendar │ │  Gmail  │ │ More... │               │
│  │   Logo  │ │  Logo   │ │  Logo   │ │  Logo   │ │         │               │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘               │
├─────────────────────────────────────────────────────────────────────────────┤
│                              FOOTER                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Product    │  │   Resources  │  │   Company    │  │   Legal      │     │
│  │   Features   │  │   Docs       │  │   About      │  │   Privacy    │     │
│  │   Pricing    │  │   Help       │  │   Contact    │  │   Terms      │     │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Components Required

| Component | Description | State |
|-----------|-------------|-------|
| NavigationBar | Logo, nav links, auth buttons | Static |
| HeroSection | Headline, subheadline, CTA button | Static |
| FeatureCard | Icon, title, description | Static |
| DemoAnimation | Interactive command demo | Animated |
| IntegrationLogoGrid | Logos of supported services | Static |
| Footer | Links and copyright | Static |
| CTASection | Call to action banner | Static |

#### User Interactions

| Action | Expected Behavior |
|--------|-------------------|
| Click "Get Started" | Redirect to `/sign-up` |
| Click "Sign In" | Redirect to `/sign-in` |
| Type in demo input | Show animated response |
| Click feature card | Scroll to relevant section |

---

### 2.2 Dashboard (`/dashboard`)

**Purpose:** Overview of activity, quick actions, system status

#### Layout Structure

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              HEADER                                          │
│  ┌──────────────┐ ┌────────────────────────────────┐ ┌─────────┐           │
│  │ Logo│Dashboard│ │ Search...                      │ │ Avatar │           │
│  └──────────────┘ └────────────────────────────────┘ └─────────┘           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    QUICK ACTIONS                                     │    │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐    │    │
│  │  │  New Chat   │ │  Standup    │ │  PR Review  │ │  My Week    │    │    │
│  │  │   →         │ │   Prep →    │ │    →        │ │    →        │    │    │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────┐ ┌─────────────────────────────────────┐    │
│  │     STATS CARDS             │ │                                      │    │
│  │  ┌─────────┐ ┌─────────┐    │ │         RECENT ACTIVITY             │    │
│  │  │ 45      │ │ 12      │    │ │                                      │    │
│  │  │ Requests│ │ Plans   │    │ │  • Today 9:00 AM - Standup prep     │    │
│  │  └─────────┘ └─────────┘    │ │  • Yesterday - PR summary           │    │
│  │  ┌─────────┐ ┌─────────┐    │ │  • Yesterday - Calendar check       │    │
│  │  │ 3       │ │ 98%     │    │ │  • Apr 20 - Created meeting note    │    │
│  │  │ Tools   │ │ Success │    │ │                                      │    │
│  │  └─────────┘ └─────────┘    │ │  ┌─────────────────────────────┐    │    │
│  └─────────────────────────────┘ │  │  View All Activity →         │    │    │
│                                  │  └─────────────────────────────┘    │    │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    CONNECTED SERVICES                               │    │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐                   │    │
│  │  │ GitHub  │ │ Notion  │ │Calendar │ │ Gmail   │                   │    │
│  │  │  ✓      │ │   ✓     │ │   ✓     │ │   ○     │                   │    │
│  │  │Connected│ │Connected│ │Connected│ │Connect  │                   │    │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘                   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    RECENT PLANS                                      │    │
│  │  ┌─────────────────────────────────────────────────────────────┐    │    │
│  │  │ Plan #abc123 - Standup Preparation - Completed - 2 min ago │    │    │
│  │  ├─────────────────────────────────────────────────────────────┤    │    │
│  │  │ Plan #def456 - PR Summary - Completed - 1 hour ago         │    │    │
│  │  ├─────────────────────────────────────────────────────────────┤    │    │
│  │  │ Plan #ghi789 - Calendar Check - Failed - 3 hours ago       │    │    │
│  │  └─────────────────────────────────────────────────────────────┘    │    │
│  │  ┌─────────────────────────────────────────────────────────────┐    │    │
│  │  │  View All Plans →                                            │    │    │
│  │  └─────────────────────────────────────────────────────────────┘    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Components Required

| Component | Description | Data Source |
|-----------|-------------|-------------|
| QuickActionCard | Pre-built command buttons | Static + dynamic |
| StatsCard | Usage statistics | API: `/api/v1/users/stats` |
| ActivityList | Recent user activity | API: `/api/v1/activity?limit=5` |
| ServiceStatusCard | MCP connection status | API: `/api/v1/mcp/servers` |
| RecentPlansList | Recent execution plans | API: `/api/v1/plans?limit=5` |

#### API Endpoints

```typescript
GET /api/v1/users/stats
Response: {
  total_requests: number;
  total_plans: number;
  connected_tools: number;
  success_rate: number;
}

GET /api/v1/activity?limit=5
Response: {
  activities: Array<{
    id: string;
    action: string;
    timestamp: string;
    status: 'success' | 'failed';
  }>
}

GET /api/v1/mcp/servers
Response: {
  servers: Array<{
    name: string;
    connected: boolean;
    last_sync?: string;
  }>
}
```

---

### 2.3 Chat Page (`/chat`)

**Purpose:** Main AI interaction interface

#### Layout Structure

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              HEADER                                          │
│  ┌──────────────┐ ┌────────────────────────────────┐ ┌─────────┐           │
│  │ Logo│Chat    │ │ Session: Today's Standup Prep  │ │ Avatar │           │
│  └──────────────┘ └────────────────────────────────┘ └─────────┘           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         MESSAGE LIST                                 │    │
│  │                                                                      │    │
│  │  ┌─────────────────────────────────────────────────────────────┐    │    │
│  │  │  User [10:00 AM]                                             │    │    │
│  │  │  ┌─────────────────────────────────────────────────────────┐│    │    │
│  │  │  │ "Prepare for tomorrow's standup"                        ││    │    │
│  │  │  └─────────────────────────────────────────────────────────┘│    │    │
│  │  └─────────────────────────────────────────────────────────────┘    │    │
│  │                                                                      │    │
│  │  ┌─────────────────────────────────────────────────────────────┐    │    │
│  │  │  Assistant [10:00 AM]                                        │    │    │
│  │  │  ┌─────────────────────────────────────────────────────────┐│    │    │
│  │  │  │ ## 📅 Tomorrow's Calendar (April 22, 2026)              ││    │    │
│  │  │  │                                                         ││    │    │
│  │  │  │ - **10:00 AM** - Sprint Planning (1 hour)              ││    │    │
│  │  │  │ - **2:00 PM** - Code Review (30 min)                   ││    │    │
│  │  │  │                                                         ││    │    │
│  │  │  │ ## 🔀 Pull Requests Needing Review                      ││    │    │
│  │  │  │                                                         ││    │    │
│  │  │  │ - **#245**: Auth middleware (by @alice)                ││    │    │
│  │  │  │ - **#247**: Fix timeout bug (by @bob)                  ││    │    │
│  │  │  │                                                         ││    │    │
│  │  │  │ ## 📝 Agenda Created in Notion                         ││    │    │
│  │  │  │                                                         ││    │    │
│  │  │  │ [ ] Review PR #245                                     ││    │    │
│  │  │  │ [ ] Discuss sprint outcomes                            ││    │    │
│  │  │  │                                                         ││    │    │
│  │  │  │ [View Agenda →](https://notion.so/...)                ││    │    │
│  │  │  └─────────────────────────────────────────────────────────┘│    │    │
│  │  └─────────────────────────────────────────────────────────────┘    │    │
│  │                                                                      │    │
│  │  ┌─────────────────────────────────────────────────────────────┐    │    │
│  │  │  User [10:05 AM]                                             │    │    │
│  │  │  ┌─────────────────────────────────────────────────────────┐│    │    │
│  │  │  │ "What about the PR from yesterday?"                     ││    │    │
│  │  │  └─────────────────────────────────────────────────────────┘│    │    │
│  │  └─────────────────────────────────────────────────────────────┘    │    │
│  │                                                                      │    │
│  │  ┌─────────────────────────────────────────────────────────────┐    │    │
│  │  │  Assistant [10:05 AM]                                        │    │    │
│  │  │  ┌─────────────────────────────────────────────────────────┐│    │    │
│  │  │  │ Here's the PR from yesterday:                           ││    │    │
│  │  │  │                                                         ││    │    │
│  │  │  │ **#240**: Update documentation (merged)                 ││    │    │
│  │  │  │ - 5 files changed, +120/-45 lines                      ││    │    │
│  │  │  │ - Approved by @alice and @charlie                      ││    │    │
│  │  │  └─────────────────────────────────────────────────────────┘│    │    │
│  │  └─────────────────────────────────────────────────────────────┘    │    │
│  │                                                                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         INPUT AREA                                   │    │
│  │  ┌─────────────────────────────────────────────────────────────┐    │    │
│  │  │  Type your message...                              ┌──────┐ │    │    │
│  │  │                                                      │ Send │ │    │    │
│  │  │                                                      │  →   │ │    │    │
│  │  └──────────────────────────────────────────────────────┴──────┘ │    │    │
│  │                                                                      │    │
│  │  Press Enter to send, Shift+Enter for new line                       │    │
│  │  ┌─────────────────────────────────────────────────────────────┐    │    │
│  │  │  Suggested: "Summarize my week" | "What's on my calendar"   │    │    │
│  │  └─────────────────────────────────────────────────────────────┘    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Components Required

| Component | Description | State |
|-----------|-------------|-------|
| MessageList | Scrollable list of messages | Dynamic |
| UserMessage | User's message bubble | Dynamic |
| AssistantMessage | AI response with markdown | Dynamic |
| TypingIndicator | Shows AI is thinking | Animated |
| ChatInput | Textarea with send button | Controlled |
| SuggestionsBar | Suggested commands | Static/Dynamic |
| SessionHeader | Current session info | Dynamic |
| Sidebar (optional) | Session list | Dynamic |

#### Streaming Implementation

```typescript
// Streaming response handling
const handleStreamingResponse = async (message: string) => {
  // Add user message to UI
  addUserMessage(message);
  
  // Add placeholder assistant message
  const assistantMessageId = addAssistantMessagePlaceholder();
  
  // Stream response
  const eventSource = new EventSource('/api/chat/stream');
  
  eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.event === 'chunk') {
      updateAssistantMessage(assistantMessageId, data.content);
    } else if (data.event === 'complete') {
      updateAssistantMetadata(assistantMessageId, data.metadata);
      eventSource.close();
    }
  };
};
```

---

### 2.4 Integrations Page (`/integrations`)

**Purpose:** Connect and manage MCP server connections

#### Layout Structure

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              HEADER                                          │
│  ┌──────────────┐ ┌────────────────────────────────┐ ┌─────────┐           │
│  │Logo│Integrations│                              │ │ Avatar │           │
│  └──────────────┘ └────────────────────────────────┘ └─────────┘           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    INTEGRATIONS HEADER                               │    │
│  │                                                                      │    │
│  │  Connect your tools to enable AI-powered automation                 │    │
│  │                                                                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         GITHUB                                       │    │
│  │  ┌─────────────────────────────────────────────────────────────┐    │    │
│  │  │  ┌─────────┐                                                │    │    │
│  │  │  │ GitHub  │  Connect to GitHub for PR management,          │    │    │
│  │  │  │  Logo   │  commit summaries, and issue creation          │    │    │
│  │  │  └─────────┘                                                │    │    │
│  │  │                                                              │    │    │
│  │  │  Status: ● Connected as @username                           │    │    │
│  │  │  Permissions: Read repos, Read PRs, Write issues            │    │    │
│  │  │                                                              │    │    │
│  │  │  ┌──────────┐ ┌──────────┐                                  │    │    │
│  │  │  │ Configure│ │Disconnect│                                  │    │    │
│  │  │  └──────────┘ └──────────┘                                  │    │    │
│  │  └─────────────────────────────────────────────────────────────┘    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         NOTION                                       │    │
│  │  ┌─────────────────────────────────────────────────────────────┐    │    │
│  │  │  ┌─────────┐                                                │    │    │
│  │  │  │ Notion  │  Connect to Notion for page creation,          │    │    │
│  │  │  │  Logo   │  database queries, and agenda extraction       │    │    │
│  │  │  └─────────┘                                                │    │    │
│  │  │                                                              │    │    │
│  │  │  Status: ● Connected to "Personal Workspace"                │    │    │
│  │  │                                                              │    │    │
│  │  │  ┌──────────┐ ┌──────────┐                                  │    │    │
│  │  │  │ Configure│ │Disconnect│                                  │    │    │
│  │  │  └──────────┘ └──────────┘                                  │    │    │
│  │  └─────────────────────────────────────────────────────────────┘    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                      GOOGLE CALENDAR                                 │    │
│  │  ┌─────────────────────────────────────────────────────────────┐    │    │
│  │  │  ┌─────────┐                                                │    │    │
│  │  │  │Calendar │  Connect to Google Calendar for event          │    │    │
│  │  │  │  Logo   │  fetching, scheduling, and availability        │    │    │
│  │  │  └─────────┘                                                │    │    │
│  │  │                                                              │    │    │
│  │  │  Status: ○ Not connected                                    │    │    │
│  │  │                                                              │    │    │
│  │  │  ┌──────────┐                                               │    │    │
│  │  │  │ Connect →│                                               │    │    │
│  │  │  └──────────┘                                               │    │    │
│  │  └─────────────────────────────────────────────────────────────┘    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         GMAIL                                        │    │
│  │  ┌─────────────────────────────────────────────────────────────┐    │    │
│  │  │  ┌─────────┐                                                │    │    │
│  │  │  │  Gmail  │  Connect to Gmail for email summarization,     │    │    │
│  │  │  │  Logo   │  thread analysis, and action extraction        │    │    │
│  │  │  └─────────┘                                                │    │    │
│  │  │                                                              │    │    │
│  │  │  Status: ○ Not connected                                    │    │    │
│  │  │                                                              │    │    │
│  │  │  ┌──────────┐                                               │    │    │
│  │  │  │ Connect →│                                               │    │    │
│  │  │  └──────────┘                                               │    │    │
│  │  └─────────────────────────────────────────────────────────────┘    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### OAuth Flow

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│  User   │     │  Frontend│     │ Backend │     │  GitHub │
└────┬────┘     └────┬────┘     └────┬────┘     └────┬────┘
     │               │               │               │
     │ Click "Connect"               │               │
     │──────────────>│               │               │
     │               │               │               │
     │               │ GET /api/v1/mcp/github/auth   │
     │               │──────────────>│               │
     │               │               │               │
     │               │ OAuth URL      │               │
     │               │<──────────────│               │
     │               │               │               │
     │ Redirect to GitHub OAuth       │               │
     │<──────────────│               │               │
     │               │               │               │
     │ Authorize on GitHub            │               │
     │──────────────────────────────────────────────>│
     │               │               │               │
     │ Redirect back with code        │               │
     │<──────────────────────────────────────────────│
     │               │               │               │
     │               │ POST /api/v1/mcp/github/callback│
     │               │──────────────>│               │
     │               │               │               │
     │               │               │ Exchange code │
     │               │               │──────────────>│
     │               │               │               │
     │               │               │ Access token  │
     │               │               │<──────────────│
     │               │               │               │
     │               │ Success       │               │
     │               │<──────────────│               │
     │               │               │               │
     │ Update UI - Connected          │               │
     │<──────────────│               │               │
     │               │               │               │
```

#### Components Required

| Component | Description |
|-----------|-------------|
| IntegrationCard | Card for each MCP server |
| ConnectionStatusBadge | Connected/Disconnected status |
| OAuthButton | Initiates OAuth flow |
| ConfigureModal | Settings for connected service |
| DisconnectButton | Removes connection |

---

### 2.5 Settings Pages

#### 2.5.1 Profile Settings (`/settings/profile`)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              HEADER                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         PROFILE                                      │    │
│  │                                                                      │    │
│  │  ┌─────────────────────────────────────────────────────────────┐    │    │
│  │  │                      AVATAR                                   │    │    │
│  │  │  ┌─────────────────────────────────────────────────────────┐│    │    │
│  │  │  │                                                         ││    │    │
│  │  │  │                      [Avatar]                           ││    │    │
│  │  │  │                                                         ││    │    │
│  │  │  │              ┌──────────────────────┐                   ││    │    │
│  │  │  │              │   Change Avatar      │                   ││    │    │
│  │  │  │              └──────────────────────┘                   ││    │    │
│  │  │  └─────────────────────────────────────────────────────────┘│    │    │
│  │  └─────────────────────────────────────────────────────────────┘    │    │
│  │                                                                      │    │
│  │  ┌─────────────────────────────────────────────────────────────┐    │    │
│  │  │                    PERSONAL INFO                             │    │    │
│  │  │                                                              │    │    │
│  │  │  Name:        [John Doe                    ]                │    │    │
│  │  │  Email:       john@example.com (verified)                   │    │    │
│  │  │  User ID:     user_abc123                                   │    │    │
│  │  │  Member since: January 15, 2026                             │    │    │
│  │  │                                                              │    │    │
│  │  │  ┌──────────┐                                               │    │    │
│  │  │  │  Save    │                                               │    │    │
│  │  │  └──────────┘                                               │    │    │
│  │  └─────────────────────────────────────────────────────────────┘    │    │
│  │                                                                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 2.5.2 Preferences (`/settings/preferences`)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PREFERENCES                                         │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    DEFAULT REPOSITORY                                │    │
│  │                                                                      │    │
│  │  Default GitHub Repo:  [personal-ai-agent/backend        ]          │    │
│  │  Default Notion DB:     [Daily Standups Database         ]          │    │
│  │                                                                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    WORKING HOURS                                     │    │
│  │                                                                      │    │
│  │  Timezone:           [America/Los_Angeles (GMT-8)       ]           │    │
│  │  Working Hours:      [09:00] to [17:00]                             │    │
│  │  Working Days:       ☑ Mon ☑ Tue ☑ Wed ☑ Thu ☑ Fri ☐ Sat ☐ Sun     │    │
│  │                                                                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    NOTIFICATION PREFERENCES                          │    │
│  │                                                                      │    │
│  │  ☑ Email me weekly summaries                                        │    │
│  │  ☑ Notify when long-running tasks complete                          │    │
│  │  ☐ Daily digest of activity                                         │    │
│  │                                                                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    AI PREFERENCES                                    │    │
│  │                                                                      │    │
│  │  Default Model:      [Claude 3.5 Sonnet (Balanced)     ]            │    │
│  │  Response Style:     [Concise   ] [Detailed   ] [Auto]              │    │
│  │                                                                      │    │
│  │  ☑ Enable streaming responses                                       │    │
│  │  ☐ Save conversation history                                        │    │
│  │                                                                      │    │
│  │  ┌──────────┐ ┌──────────┐                                          │    │
│  │  │  Save    │ │  Reset   │                                          │    │
│  │  └──────────┘ └──────────┘                                          │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 2.5.3 API Tokens (`/settings/tokens`)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         API TOKENS                                          │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    USAGE STATISTICS                                  │    │
│  │                                                                      │    │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                    │    │
│  │  │   45        │ │   12        │ │   98%       │                    │    │
│  │  │ Requests    │ │  This Week  │ │ Success Rate│                    │    │
│  │  │ This Month  │ │             │ │             │                    │    │
│  │  └─────────────┘ └─────────────┘ └─────────────┘                    │    │
│  │                                                                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    API TOKENS                                        │    │
│  │                                                                      │    │
│  │  ┌─────────────────────────────────────────────────────────────┐    │    │
│  │  │ Token Name          │ Created    │ Last Used  │ Actions      │    │    │
│  │  ├─────────────────────────────────────────────────────────────┤    │    │
│  │  │ CLI Token           │ 2026-04-01 │ 2026-04-20 │ Revoke Copy  │    │    │
│  │  │ GitHub Action       │ 2026-04-10 │ 2026-04-21 │ Revoke Copy  │    │    │
│  │  │ VSCode Extension    │ 2026-04-15 │ Never      │ Revoke Copy  │    │    │
│  │  └─────────────────────────────────────────────────────────────┘    │    │
│  │                                                                      │    │
│  │  ┌─────────────────────────────────────────────────────────────┐    │    │
│  │  │  ┌──────────────┐                                            │    │    │
│  │  │  │ Generate New │                                            │    │    │
│  │  │  │    Token     │                                            │    │    │
│  │  │  └──────────────┘                                            │    │    │
│  │  └─────────────────────────────────────────────────────────────┘    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    DANGER ZONE                                       │    │
│  │                                                                      │    │
│  │  ┌─────────────────────────────────────────────────────────────┐    │    │
│  │  │  Delete all data                                             │    │    │
│  │  │  Permanently delete your account and all associated data    │    │    │
│  │  │                                                              │    │    │
│  │  │  ┌──────────────┐                                           │    │    │
│  │  │  │ Delete Account│                                          │    │    │
│  │  │  └──────────────┘                                           │    │    │
│  │  └─────────────────────────────────────────────────────────────┘    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2.6 Plans Page (`/plans`)

**Purpose:** View execution plan history and details

#### Layout Structure

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              HEADER                                          │
│  ┌──────────────┐ ┌────────────────────────────────┐ ┌─────────┐           │
│  │ Logo│ Plans  │ │ Filter: [All Plans ▼] [Search] │ │ Avatar │           │
│  └──────────────┘ └────────────────────────────────┘ └─────────┘           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    PLANS SUMMARY                                     │    │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐    │    │
│  │  │    156      │ │     12      │ │     3       │ │    98%      │    │    │
│  │  │ Total Plans │ │ This Week   │ │ Failed      │ │ Success     │    │    │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    PLANS LIST                                        │    │
│  │                                                                      │    │
│  │  ┌─────────────────────────────────────────────────────────────┐    │    │
│  │  │  ┌─────────────────────────────────────────────────────────┐│    │    │
│  │  │  │  📋 Plan #abc123                          ✅ Completed   ││    │    │
│  │  │  │  Intent: agenda_preparation                             ││    │    │
│  │  │  │  Created: Apr 21, 2026 10:00 AM • Duration: 2.4s       ││    │    │
│  │  │  │  Tasks: 3/3 completed                                   ││    │    │
│  │  │  │  ┌────────────────────────────────────────────────────┐ ││    │    │
│  │  │  │  │  ✅ Fetch calendar events (0.8s)                   │ ││    │    │
│  │  │  │  │  ✅ List open PRs (1.2s)                           │ ││    │    │
│  │  │  │  │  ✅ Create Notion agenda (0.4s)                    │ ││    │    │
│  │  │  │  └────────────────────────────────────────────────────┘ ││    │    │
│  │  │  └─────────────────────────────────────────────────────────┘│    │    │
│  │  └─────────────────────────────────────────────────────────────┘    │    │
│  │                                                                      │    │
│  │  ┌─────────────────────────────────────────────────────────────┐    │    │
│  │  │  ┌─────────────────────────────────────────────────────────┐│    │    │
│  │  │  │  📋 Plan #def456                          ❌ Failed      ││    │    │
│  │  │  │  Intent: email_summary                                  ││    │    │
│  │  │  │  Created: Apr 20, 2026 3:30 PM • Duration: 5.2s        ││    │    │
│  │  │  │  Tasks: 1/2 completed                                   ││    │    │
│  │  │  │  ┌────────────────────────────────────────────────────┐ ││    │    │
│  │  │  │  │  ✅ Fetch emails (0.5s)                            │ ││    │    │
│  │  │  │  │  ❌ Summarize threads - Rate limit exceeded        │ ││    │    │
│  │  │  │  └────────────────────────────────────────────────────┘ ││    │    │
│  │  │  └─────────────────────────────────────────────────────────┘│    │    │
│  │  └─────────────────────────────────────────────────────────────┘    │    │
│  │                                                                      │    │
│  │  ┌─────────────────────────────────────────────────────────────┐    │    │
│  │  │  ┌─────────────────────────────────────────────────────────┐│    │    │
│  │  │  │  📋 Plan #ghi789                          ⏳ In Progress ││    │    │
│  │  │  │  Intent: pr_management                                  ││    │    │
│  │  │  │  Created: Apr 21, 2026 11:15 AM • Elapsed: 1.2s        ││    │    │
│  │  │  │  Tasks: 1/2 completed                                   ││    │    │
│  │  │  │  ┌────────────────────────────────────────────────────┐ ││    │    │
│  │  │  │  │  ✅ List PRs (0.8s)                                │ ││    │    │
│  │  │  │  │  ⏳ Get PR details - Running...                    │ ││    │    │
│  │  │  │  └────────────────────────────────────────────────────┘ ││    │    │
│  │  │  └─────────────────────────────────────────────────────────┘│    │    │
│  │  └─────────────────────────────────────────────────────────────┘    │    │
│  │                                                                      │    │
│  │  ┌─────────────────────────────────────────────────────────────┐    │    │
│  │  │  Load More...                                               │    │    │
│  │  └─────────────────────────────────────────────────────────────┘    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Components Required

| Component | Description |
|-----------|-------------|
| StatsCards | Summary statistics |
| PlanCard | Individual plan with status |
| StatusBadge | Completed/Failed/In Progress |
| TaskProgressBar | Visual task completion |
| FilterBar | Filter by status, date, intent |
| SearchInput | Search plans |

---

### 2.7 Plan Details Page (`/plans/[id]`)

**Purpose:** Detailed view of a specific execution plan

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              HEADER                                          │
│  ┌──────────────┐ ┌────────────────────────────────┐ ┌─────────┐           │
│  │ Logo│Plan    │ │ Plan #abc123                    │ │ Avatar │           │
│  └──────────────┘ └────────────────────────────────┘ └─────────┘           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    PLAN HEADER                                       │    │
│  │                                                                      │    │
│  │  Plan ID: abc123-4567-8900                    Status: ✅ Completed  │    │
│  │  Intent: agenda_preparation                   Success Rate: 100%    │    │
│  │  Created: Apr 21, 2026 10:00:23 AM                                    │    │
│  │  Completed: Apr 21, 2026 10:00:25 AM                                 │    │
│  │  Duration: 2.4 seconds                                               │    │
│  │                                                                      │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐                             │    │
│  │  │  Retry   │ │  Export  │ │  Share   │                             │    │
│  │  └──────────┘ └──────────┘ └──────────┘                             │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    TASK DEPENDENCY GRAPH                             │    │
│  │                                                                      │    │
│  │  ┌─────────┐                                                         │    │
│  │  │ Task 1  │◄────┐                                                  │    │
│  │  │Calendar │     │                                                  │    │
│  │  │ 0.8s   │     │                                                  │    │
│  │  └────┬────┘     │                                                  │    │
│  │       │          │                                                  │    │
│  │       ▼          │                                                  │    │
│  │  ┌─────────┐     │                                                  │    │
│  │  │ Task 3  │     │                                                  │    │
│  │  │ Notion  │     │                                                  │    │
│  │  │ 0.4s   │     │                                                  │    │
│  │  └─────────┘     │                                                  │    │
│  │                  │                                                  │    │
│  │  ┌─────────┐     │                                                  │    │
│  │  │ Task 2  │─────┘                                                  │    │
│  │  │ GitHub  │                                                        │    │
│  │  │ 1.2s   │                                                        │    │
│  │  └─────────┘                                                        │    │
│  │                                                                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    TASK DETAILS                                      │    │
│  │                                                                      │    │
│  │  ┌─────────────────────────────────────────────────────────────┐    │    │
│  │  │  ✅ Task 1: Fetch calendar events                            │    │    │
│  │  │  ┌─────────────────────────────────────────────────────────┐│    │    │
│  │  │  │ MCP Server: calendar                                    ││    │    │
│  │  │  │ Tool: fetch_events                                       ││    │    │
│  │  │  │ Parameters: {"date": "2026-04-22", "timezone": "UTC"}   ││    │    │
│  │  │  │ Duration: 0.8s                                          ││    │    │
│  │  │  │                                                          ││    │    │
│  │  │  │ Result:                                                 ││    │    │
│  │  │  │ [                                                       ││    │    │
│  │  │  │   {                                                     ││    │    │
│  │  │  │     "title": "Sprint Planning",                         ││    │    │
│  │  │  │     "start": "10:00 AM",                                ││    │    │
│  │  │  │     "duration": "1 hour"                                ││    │    │
│  │  │  │   }                                                     ││    │    │
│  │  │  │ ]                                                       ││    │    │
│  │  │  └─────────────────────────────────────────────────────────┘│    │    │
│  │  └─────────────────────────────────────────────────────────────┘    │    │
│  │                                                                      │    │
│  │  ┌─────────────────────────────────────────────────────────────┐    │    │
│  │  │  ✅ Task 2: List open PRs                                    │    │    │
│  │  │  ┌─────────────────────────────────────────────────────────┐│    │    │
│  │  │  │ MCP Server: github                                      ││    │    │
│  │  │  │ Tool: list_prs                                          ││    │    │
│  │  │  │ Parameters: {"state": "open", "limit": 10}              ││    │    │
│  │  │  │ Duration: 1.2s                                          ││    │    │
│  │  │  │                                                          ││    │    │
│  │  │  │ Result: [3 PRs found]                                   ││    │    │
│  │  │  │ - #245: Auth middleware (by @alice)                     ││    │    │
│  │  │  │ - #247: Fix timeout bug (by @bob)                       ││    │    │
│  │  │  │ - #248: Update docs (by @charlie)                       ││    │    │
│  │  │  └─────────────────────────────────────────────────────────┘│    │    │
│  │  └─────────────────────────────────────────────────────────────┘    │    │
│  │                                                                      │    │
│  │  ┌─────────────────────────────────────────────────────────────┐    │    │
│  │  │  ✅ Task 3: Create Notion agenda                             │    │    │
│  │  │  ┌─────────────────────────────────────────────────────────┐│    │    │
│  │  │  │ MCP Server: notion                                      ││    │    │
│  │  │  │ Tool: create_page                                       ││    │    │
│  │  │  │ Duration: 0.4s                                          ││    │    │
│  │  │  │                                                          ││    │    │
│  │  │  │ Result:                                                 ││    │    │
│  │  │  │ {                                                       ││    │    │
│  │  │  │   "page_id": "abc123",                                  ││    │    │
│  │  │  │   "url": "https://notion.so/..."                        ││    │    │
│  │  │  │ }                                                       ││    │    │
│  │  │  └─────────────────────────────────────────────────────────┘│    │    │
│  │  └─────────────────────────────────────────────────────────────┘    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    RAW RESPONSE                                      │    │
│  │  ┌─────────────────────────────────────────────────────────────┐    │    │
│  │  │  [View Full JSON Response]                                   │    │    │
│  │  └─────────────────────────────────────────────────────────────┘    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Shared Components

### 3.1 Navigation Sidebar

```
┌─────────────────┐
│  ┌───────────┐  │
│  │    Logo   │  │
│  └───────────┘  │
│                 │
│  ┌───────────┐  │
│  │ Dashboard │  │
│  └───────────┘  │
│  ┌───────────┐  │
│  │   Chat    │  │
│  └───────────┘  │
│  ┌───────────┐  │
│  │Integrations│ │
│  └───────────┘  │
│  ┌───────────┐  │
│  │   Plans   │  │
│  └───────────┘  │
│  ┌───────────┐  │
│  │ Activity  │  │
│  └───────────┘  │
│                 │
│  ┌───────────┐  │
│  │ Settings  │  │
│  └───────────┘  │
│                 │
│  ┌───────────┐  │
│  │   Help    │  │
│  └───────────┘  │
└─────────────────┘
```

### 3.2 User Avatar Dropdown

```
┌─────────────────────────────┐
│  ┌─────────┐  John Doe      │
│  │ Avatar  │  john@email.com│
│  └─────────┘                │
├─────────────────────────────┤
│  👤 Profile                 │
│  ⚙️ Settings                │
│  🔌 Integrations            │
│  📊 Usage Stats             │
├─────────────────────────────┤
│  💬 Support                 │
│  📖 Documentation           │
├─────────────────────────────┤
│  🚪 Sign Out                │
└─────────────────────────────┘
```

### 3.3 Loading States

| Component | Loading State |
|-----------|---------------|
| MessageList | Skeleton messages |
| PlanCard | Shimmer effect |
| StatsCard | Placeholder numbers |
| IntegrationCard | Spinner on connect |

### 3.4 Error States

| Component | Error Display |
|-----------|---------------|
| API Error | Toast notification + retry button |
| Rate Limit | Banner with wait time |
| Auth Error | Redirect to sign in |
| Connection Error | Offline indicator |

---

## 4. Responsive Design Breakpoints

| Breakpoint | Width | Layout Changes |
|------------|-------|----------------|
| Mobile | < 640px | Sidebar hidden, bottom navigation |
| Tablet | 640px - 1024px | Collapsible sidebar |
| Desktop | > 1024px | Full sidebar, multi-column layouts |
| Wide | > 1536px | Expanded content width |

---

## 5. Route Protection

```typescript
// Middleware for route protection
export const protectedRoutes = [
  '/dashboard',
  '/chat',
  '/chat/*',
  '/integrations',
  '/plans',
  '/plans/*',
  '/activity',
  '/settings',
  '/settings/*',
];

export const publicRoutes = [
  '/',
  '/sign-in',
  '/sign-up',
  '/help',
  '/about',
  '/privacy',
  '/terms',
];

export const redirectIfAuthenticated = [
  '/sign-in',
  '/sign-up',
];
```

---

## 6. Page Load Performance Targets

| Page | First Paint | Interactive | API Calls |
|------|-------------|-------------|-----------|
| Landing | < 1s | < 2s | 0 |
| Dashboard | < 1.5s | < 2.5s | 3 |
| Chat | < 1s | < 2s | 1 |
| Integrations | < 1.5s | < 2.5s | 1 |
| Plans | < 1.5s | < 2.5s | 2 |
| Settings | < 1s | < 2s | 1 |

---

## 7. Accessibility (A11Y) Requirements

| Requirement | Standard |
|-------------|----------|
| Keyboard navigation | WCAG 2.1 AA |
| Screen reader support | ARIA labels |
| Color contrast | 4.5:1 minimum |
| Focus indicators | Visible outline |
| Alt text | All images |
| Heading hierarchy | Proper H1-H6 |

---

## 8. Browser Support

| Browser | Minimum Version |
|---------|-----------------|
| Chrome | 90+ |
| Firefox | 88+ |
| Safari | 14+ |
| Edge | 90+ |

---

This document provides a complete specification for all frontend pages in the Personal AI Agent application. Each page includes layout structure, component requirements, data dependencies, and user interaction flows.