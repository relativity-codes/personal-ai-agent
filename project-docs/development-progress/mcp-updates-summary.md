# MCP Server Tool Inventory (Canonical)

This document provides the canonical list of tools available across all MCP servers, as defined in the core `task_decomposer.md` prompt. This serves as the single source of truth for the system's capabilities.

---

### GitHub MCP Server (`github`)

| Tool | Description | Parameters |
|---|---|---|
| `github_list_prs` | List pull requests for a repository. | `repo`, `state`, `limit` |
| `github_get_pr_details` | Get the detailed information for a single pull request. | `repo`, `pr_number` |
| `github_list_commits` | List the commits for a pull request or branch. | `repo`, `pr_number`, `branch`, `limit` |
| `github_create_issue` | Create a new issue in a repository. | `repo`, `title`, `body`, `labels` |
| `github_summarize_pr` | Generate a summary of the changes in a pull request. | `repo`, `pr_number` |

---

### Notion MCP Server (`notion`)

| Tool | Description | Parameters |
|---|---|---|
| `notion_query_pages` | Search for pages within a database or globally. | `database_id`, `query`, `filter` |
| `notion_create_page` | Create a new page in Notion. | `parent_id`, `title`, `content` |
| `notion_update_page` | Update the content or properties of an existing page. | `page_id`, `title`, `content` |
| `notion_get_agenda` | Extract a structured agenda from a Notion page. | `page_id` |

---

### Google Calendar MCP Server (`calendar`)

| Tool | Description | Parameters |
|---|---|---|
| `calendar_fetch_events` | Get a list of calendar events within a specified time range. | `start_date`, `end_date`, `max_results` |
| `calendar_find_free_slots` | Find available time slots on a given date. | `date`, `duration_minutes`, `working_hours` |
| `calendar_create_event` | Schedule a new event on the calendar. | `title`, `start_time`, `end_time`, `attendees` |

---

### Gmail MCP Server (`gmail`)

| Tool | Description | Parameters |
|---|---|---|
| `gmail_summarize_threads` | Summarize recent email threads. | `max_threads`, `days_back` |
| `gmail_search` | Search for emails using a specific query. | `query`, `max_results` |
