# Integrations and MCP

## Summary

The project integrates external productivity services through an MCP-style tool layer. The current runtime path uses [`../../backend/app/mcp_alt`](../../backend/app/mcp_alt), which wraps tools as FastMCP servers and exposes them to both API routes and the agent workflow.

## MCP Folder Structure

```text
backend/app/
├── mcp_alt/
│   ├── registry.py                 # Runtime MCP registry
│   ├── github.py                   # GitHub tools
│   ├── notion.py                   # Notion tools
│   ├── mcp_calendar.py             # Calendar tools
│   └── gmail.py                    # Gmail tools
├── api/
│   └── routers/v1/
│       ├── mcp.py                  # MCP discovery/invoke API
│       ├── mcp_oauth.py            # OAuth authorize/callback routes
│       └── mcp_credential_router.py# Credential CRUD routes
└── db/
    ├── models/mcp_credential.py
    └── repositories/mcp_credential_repository.py
```

## Runtime Registry

`MCPAltRegistry` registers four server IDs:

- `github`
- `notion`
- `calendar`
- `gmail`

It also maps `google_calendar` to `calendar` for compatibility. During application startup, `initialize()` lists all server tools and caches their input schemas. The planner and action agents rely on this catalog so generated tool arguments can be checked before execution.

Core registry responsibilities:

- List configured integration servers.
- List all tools and schemas.
- Return a specific tool schema for validation.
- Invoke a tool by server ID and tool name.
- Inject `user_id` into tool arguments so tools can load user-scoped credentials.

## Tool Contract Enforcement

The action agent uses the registry cache as a contract between planning and execution.

The current behavior includes:

- Dynamic schema discovery on startup.
- Planner access to tool catalog information.
- JSON schema validation before invoking a tool.
- Recursive placeholder substitution for user context and prior task outputs.
- Safe serialization and parser prompts for complex raw tool results.

This is important because it reduces tool-call failures caused by mismatched parameter names, missing required fields, or unstructured tool output.

## OAuth and Credentials

The backend stores per-user integration credentials in the `MCPCredential` model and repository:

- Model: [`../../backend/app/db/models/mcp_credential.py`](../../backend/app/db/models/mcp_credential.py)
- Repository: [`../../backend/app/db/repositories/mcp_credential_repository.py`](../../backend/app/db/repositories/mcp_credential_repository.py)
- API routes: [`../../backend/app/api/routers/v1/mcp_credential_router.py`](../../backend/app/api/routers/v1/mcp_credential_router.py)
- OAuth routes: [`../../backend/app/api/routers/v1/mcp_oauth.py`](../../backend/app/api/routers/v1/mcp_oauth.py)

The registry's `list_servers()` method checks stored credentials and marks servers as configured for the current user. Google credentials are mapped to both Calendar and Gmail configuration flags.

## API Access

The MCP API routes are mounted under `/api/v1/mcp`:

- Server discovery.
- Tool catalog access.
- Tool invocation.
- OAuth authorization/callback helpers.

The frontend integrations area uses these endpoints to show available integrations and connection state.

## Runtime vs Legacy MCP Code

There are two MCP-related implementations in the repository:

- Current runtime path: [`../../backend/app/mcp_alt`](../../backend/app/mcp_alt), used by `app.main`, the agent workflow, and the current API behavior.
- Legacy/class-based path: [`../../backend/app/mcp`](../../backend/app/mcp), still present and referenced by some tests and older code paths.

For reviewers, `mcp_alt` is the implementation to evaluate as the active runtime integration layer. The older `app/mcp` package is useful context for earlier iterations but is not the production registry initialized by the FastAPI lifespan.

## External Service Notes

GitHub, Notion, Google Calendar, and Gmail require provider credentials and/or user OAuth credentials. Production values are injected through GitHub Actions into Cloud Run and must use placeholders in documentation. No real tokens should be committed to the repository.

