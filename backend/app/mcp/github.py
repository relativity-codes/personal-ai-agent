from __future__ import annotations

import logging
from typing import Any

import httpx

from app.config import Settings
from app.mcp.base import MCPServer
from app.mcp.schema import ToolDefinition

logger = logging.getLogger(__name__)


class GitHubMCPServer(MCPServer):
    id = "github"
    display_name = "GitHub"
    description = "Pull requests, commits, and repository activity for standup and review flows."

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._token = (settings.GITHUB_TOKEN or "").strip()

    def is_configured(self) -> bool:
        return bool(self._token)

    async def list_tools(self) -> list[ToolDefinition]:
        return [
            ToolDefinition(
                name="list_open_pull_requests",
                description="List open pull requests for a repository.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "owner": {"type": "string", "description": "GitHub org or user"},
                        "repo": {"type": "string", "description": "Repository name"},
                        "state": {"type": "string", "enum": ["open", "closed", "all"], "default": "open"},
                    },
                    "required": ["owner", "repo"],
                },
            ),
            ToolDefinition(
                name="list_commits",
                description="List commits on a branch (default branch if omitted).",
                input_schema={
                    "type": "object",
                    "properties": {
                        "owner": {"type": "string"},
                        "repo": {"type": "string"},
                        "sha": {"type": "string", "description": "Branch or SHA", "default": "HEAD"},
                        "per_page": {"type": "integer", "default": 10},
                    },
                    "required": ["owner", "repo"],
                },
            ),
        ]

    async def invoke(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if not self.is_configured():
            return {
                "ok": False,
                "error": "not_configured",
                "message": "Set GITHUB_TOKEN in the environment to call GitHub tools.",
            }
        owner = arguments.get("owner")
        repo = arguments.get("repo")
        if not owner or not repo:
            return {"ok": False, "error": "validation_error", "message": "owner and repo are required."}

        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self._token.startswith("ghp_") or self._token.startswith("github_pat_"):
            headers["Authorization"] = f"Bearer {self._token}"
        else:
            headers["Authorization"] = f"token {self._token}"

        path = f"https://api.github.com/repos/{owner}/{repo}"
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                if tool_name == "list_open_pull_requests":
                    state = arguments.get("state", "open")
                    r = await client.get(f"{path}/pulls", headers=headers, params={"state": state})
                    r.raise_for_status()
                    return {"ok": True, "pull_requests": r.json()}
                if tool_name == "list_commits":
                    sha = arguments.get("sha", "HEAD")
                    per_page = min(int(arguments.get("per_page", 10)), 100)
                    r = await client.get(
                        f"{path}/commits",
                        headers=headers,
                        params={"sha": sha, "per_page": per_page},
                    )
                    r.raise_for_status()
                    return {"ok": True, "commits": r.json()}
                return {"ok": False, "error": "unknown_tool", "message": f"Unknown tool: {tool_name}"}
        except httpx.HTTPStatusError as exc:
            logger.warning("github http error: %s %s", exc.response.status_code, exc.response.text[:500])
            return {
                "ok": False,
                "error": "upstream_error",
                "status_code": exc.response.status_code,
                "message": exc.response.text[:2000],
            }
        except httpx.RequestError as exc:
            logger.exception("github request failed")
            return {"ok": False, "error": "request_error", "message": str(exc)}
