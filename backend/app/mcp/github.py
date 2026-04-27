from __future__ import annotations

import logging
from typing import Any

import httpx

from app.config import Settings
from app.mcp.base import MCPServer
from app.mcp.schema import MCPInvokeOAuth, ToolDefinition

logger = logging.getLogger(__name__)


class GitHubMCPServer(MCPServer):
    id = "github"
    display_name = "GitHub"
    description = "A comprehensive suite of tools for interacting with GitHub repositories."

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._token = (settings.MY_GITHUB_TOKEN or "").strip()

    def _effective_token(self, oauth: MCPInvokeOAuth | None) -> str:
        if oauth and (oauth.github_token or "").strip():
            return oauth.github_token.strip()
        return self._token

    def is_configured(self) -> bool:
        return bool(self._token)

    async def list_tools(self) -> list[ToolDefinition]:
        # Preserving original tools and adding new ones for enhanced functionality
        existing_tools = [
            ToolDefinition(
                name="github_list_prs",
                description="List pull requests for a repository.",
                input_schema={                    "type": "object",
                    "properties": {
                        "owner": {"type": "string", "description": "GitHub org or user"},
                        "repo": {"type": "string", "description": "Repository name"},
                        "state": {"type": "string", "enum": ["open", "closed", "all"], "default": "open"},
                    },
                    "required": ["owner", "repo"],
                },
            ),
            ToolDefinition(
                name="github_get_pr_details",
                description="Get the details of a specific pull request.",
                input_schema={                    "type": "object",
                    "properties": {
                        "owner": {"type": "string", "description": "GitHub org or user"},
                        "repo": {"type": "string", "description": "Repository name"},
                        "pr_number": {"type": "integer", "description": "The number of the pull request"},
                    },
                    "required": ["owner", "repo", "pr_number"],
                },
            ),
            ToolDefinition(
                name="github_list_commits",
                description="List commits on a branch.",
                input_schema={                    "type": "object",
                    "properties": {
                        "owner": {"type": "string", "description": "GitHub org or user"},
                        "repo": {"type": "string", "description": "Repository name"},
                        "branch": {"type": "string", "description": "Branch name", "default": "main"},
                    },
                    "required": ["owner", "repo"],
                },
            ),
            ToolDefinition(
                name="github_create_issue",
                description="Create a new issue in a repository.",
                input_schema={                    "type": "object",
                    "properties": {
                        "owner": {"type": "string", "description": "GitHub org or user"},
                        "repo": {"type": "string", "description": "Repository name"},
                        "title": {"type": "string", "description": "The title of the issue"},
                        "body": {"type": "string", "description": "The content of the issue"},
                    },
                    "required": ["owner", "repo", "title"],
                },
            ),
            ToolDefinition(
                name="github_summarize_pr",
                description="Get the diff of a pull request for summarization.",
                input_schema={                    "type": "object",
                    "properties": {
                        "owner": {"type": "string", "description": "GitHub org or user"},
                        "repo": {"type": "string", "description": "Repository name"},
                        "pr_number": {"type": "integer", "description": "The number of the pull request"},
                    },
                    "required": ["owner", "repo", "pr_number"],
                },
            ),
        ]
        
        new_tools = [
            ToolDefinition(
                name="github_get_repo_details",
                description="Get high-level details about a repository.",
                input_schema={                    "type": "object",
                    "properties": {
                        "owner": {"type": "string", "description": "GitHub org or user"},
                        "repo": {"type": "string", "description": "Repository name"},
                    },
                    "required": ["owner", "repo"],
                },
            ),
            ToolDefinition(
                name="github_list_repo_contents",
                description="List files and directories at a given path in a repository.",
                input_schema={                    "type": "object",
                    "properties": {
                        "owner": {"type": "string", "description": "GitHub org or user"},
                        "repo": {"type": "string", "description": "Repository name"},
                        "path": {"type": "string", "description": "The path to list contents from", "default": ""},
                    },
                    "required": ["owner", "repo"],
                },
            ),
            ToolDefinition(
                name="github_add_pr_comment",
                description="Add a comment to an existing pull request.",
                input_schema={                    "type": "object",
                    "properties": {
                        "owner": {"type": "string", "description": "GitHub org or user"},
                        "repo": {"type": "string", "description": "Repository name"},
                        "pr_number": {"type": "integer", "description": "The pull request number"},
                        "comment": {"type": "string", "description": "The comment to post"},
                    },
                    "required": ["owner", "repo", "pr_number", "comment"],
                },
            ),
            ToolDefinition(
                name="github_create_pr",
                description="Create a new pull request.",
                input_schema={                    "type": "object",
                    "properties": {
                        "owner": {"type": "string", "description": "GitHub org or user"},
                        "repo": {"type": "string", "description": "Repository name"},
                        "head": {"type": "string", "description": "The source branch"},
                        "base": {"type": "string", "description": "The target branch"},
                        "title": {"type": "string", "description": "The title of the pull request"},
                        "body": {"type": "string", "description": "The content of the pull request"},
                    },
                    "required": ["owner", "repo", "head", "base", "title"],
                },
            ),
            ToolDefinition(
                name="github_merge_pr",
                description="Merge a pull request.",
                input_schema={                    "type": "object",
                    "properties": {
                        "owner": {"type": "string", "description": "GitHub org or user"},
                        "repo": {"type": "string", "description": "Repository name"},
                        "pr_number": {"type": "integer", "description": "The number of the pull request to merge"},
                        "merge_method": {"type": "string", "enum": ["merge", "squash", "rebase"], "default": "merge"},
                    },
                    "required": ["owner", "repo", "pr_number"],
                },
            ),
        ]
        
        return existing_tools + new_tools

    async def invoke(
        self, tool_name: str, arguments: dict[str, Any], oauth: MCPInvokeOAuth | None = None
    ) -> dict[str, Any]:
        token = self._effective_token(oauth)
        if not token:
            return {"ok": False, "error": "not_configured", "message": "GitHub token is not set."}

        owner = arguments.get("owner")
        repo = arguments.get("repo")
        if not owner or not repo:
            return {"ok": False, "error": "validation_error", "message": "'owner' and 'repo' are required."}

        headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        base_url = f"https://api.github.com/repos/{owner}/{repo}"

        try:
            async with httpx.AsyncClient(timeout=30.0, headers=headers) as client:
                # --- Existing Tool Implementations ---
                if tool_name == "github_list_prs":
                    r = await client.get(f"{base_url}/pulls", params={"state": arguments.get("state", "open")})
                elif tool_name == "github_get_pr_details":
                    pr_number = arguments["pr_number"]
                    r = await client.get(f"{base_url}/pulls/{pr_number}")
                elif tool_name == "github_list_commits":
                    r = await client.get(f"{base_url}/commits", params={"sha": arguments.get("branch", "main")})
                elif tool_name == "github_create_issue":
                    payload = {"title": arguments["title"], "body": arguments.get("body", "")}
                    r = await client.post(f"{base_url}/issues", json=payload)
                elif tool_name == "github_summarize_pr":
                    pr_number = arguments["pr_number"]
                    diff_headers = headers.copy()
                    diff_headers["Accept"] = "application/vnd.github.v3.diff"
                    r = await client.get(f"{base_url}/pulls/{pr_number}", headers=diff_headers)
                    return {"ok": True, "diff": r.text} if r.is_success else self._http_error(r)
                
                # --- New Tool Implementations ---
                elif tool_name == "github_get_repo_details":
                    r = await client.get(base_url)
                elif tool_name == "github_list_repo_contents":
                    path = arguments.get("path", "")
                    r = await client.get(f"{base_url}/contents/{path}")
                elif tool_name == "github_add_pr_comment":
                    pr_number = arguments["pr_number"]
                    payload = {"body": arguments["comment"]}
                    r = await client.post(f"{base_url}/issues/{pr_number}/comments", json=payload)
                elif tool_name == "github_create_pr":
                    payload = {
                        "head": arguments["head"],
                        "base": arguments["base"],
                        "title": arguments["title"],
                        "body": arguments.get("body", ""),
                    }
                    r = await client.post(f"{base_url}/pulls", json=payload)
                elif tool_name == "github_merge_pr":
                    pr_number = arguments["pr_number"]
                    payload = {"merge_method": arguments.get("merge_method", "merge")}
                    r = await client.put(f"{base_url}/pulls/{pr_number}/merge", json=payload)
                else:
                    return {"ok": False, "error": "unknown_tool", "message": f"Unknown tool: {tool_name}"}
                
                r.raise_for_status()
                return {"ok": True, "data": r.json()}

        except httpx.HTTPStatusError as exc:
            return self._http_error(exc.response)
        except httpx.RequestError as exc:
            logger.exception("GitHub request failed")
            return {"ok": False, "error": "request_error", "message": str(exc)}

    def _http_error(self, response: httpx.Response) -> dict[str, Any]:
        logger.warning(f"GitHub HTTP error: {response.status_code} {response.text[:500]}")
        return {
            "ok": False,
            "error": "upstream_error",
            "status_code": response.status_code,
            "message": response.text[:2000],
        }
