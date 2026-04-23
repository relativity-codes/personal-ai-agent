
# Backend API Documentation

This document provides a comprehensive overview of the backend API endpoints. It is intended for frontend developers who need to interact with the API.

## Authentication

All API endpoints require authentication. The current user is identified via a JWT token passed in the `Authorization` header.

## Base URL

The base URL for all API endpoints is `/api/v1/`.

---

## Agents API

**File:** `backend/app/api/routers/v1/agents.py`

This API manages the execution plans for the AI agents.

### `GET /{plan_id}/status`

Retrieves the status of a specific execution plan.

*   **Path Parameters:**
    *   `plan_id` (UUID): The ID of the execution plan.
*   **Responses:**
    *   `200 OK`: Returns a `PlanStatusResponse` object with the plan details.
    *   `404 Not Found`: If the plan is not found or the user does not have access.

---

## Audit Log API

**File:** `backend/app/api/routers/v1/audit_log_router.py`

This API provides access to the audit log, which records all significant events in the system.

### `GET /`

Retrieves a list of all audit logs.

*   **Query Parameters:**
    *   `skip` (int): Number of records to skip (for pagination). Default: `0`.
    *   `limit` (int): Maximum number of records to return. Default: `100`.
*   **Responses:**
    *   `200 OK`: Returns a list of `AuditLog` objects.

### `GET /{log_id}`

Retrieves a specific audit log by its ID.

*   **Path Parameters:**
    *   `log_id` (UUID): The ID of the audit log.
*   **Responses:**
    *   `200 OK`: Returns an `AuditLog` object.
    *   `404 Not Found`: If the audit log is not found.

### `GET /user/{user_id}`

Retrieves all audit logs for a specific user.

*   **Path Parameters:**
    *   `user_id` (str): The ID of the user.
*   **Query Parameters:**
    *   `limit` (int): Maximum number of records to return. Default: `20`.
*   **Responses:**
    *   `200 OK`: Returns a list of `AuditLog` objects.

---

## Chat API

**File:** `backend/app/api/routers/v1/chat.py`

This API handles the chat functionality, allowing users to interact with the AI.

### `POST /`

Initiates a chat session or continues an existing one.

*   **Request Body:** `ChatRequest`
    *   `message` (str): The user's message.
    *   `session_id` (UUID, optional): The ID of the chat session. If not provided, a new session is created.
*   **Responses:**
    *   `200 OK`: Returns a `ChatResponse` object with the AI's response and the session ID.
    *   `403 Forbidden`: If the session ID is invalid or does not belong to the user.
    *   `500 Internal Server Error`: If an error occurs during the chat process.

---

## Chat History API

**File:** `backend/app/api/routers/v1/chat_history_router.py`

This API manages the chat history for each session.

### `GET /`

Retrieves a list of all chat histories.

*   **Query Parameters:**
    *   `skip` (int): Number of records to skip. Default: `0`.
    *   `limit` (int): Maximum number of records to return. Default: `100`.
*   **Responses:**
    *   `200 OK`: Returns a list of `ChatHistory` objects.

### `GET /{history_id}`

Retrieves a specific chat history by its ID.

*   **Path Parameters:**
    *   `history_id` (UUID): The ID of the chat history.
*   **Responses:**
    *   `200 OK`: Returns a `ChatHistory` object.
    *   `404 Not Found`: If the chat history is not found.

### `GET /session/{session_id}`

Retrieves the chat history for a specific session.

*   **Path Parameters:**
    *   `session_id` (str): The ID of the session.
*   **Responses:**
    *   `200 OK`: Returns a list of chat messages.

### `DELETE /{history_id}`

Deletes a specific chat history by its ID.

*   **Path Parameters:**
    *   `history_id` (UUID): The ID of the chat history.
*   **Responses:**
    *   `200 OK`: Returns `true` if the deletion was successful.
    *   `404 Not Found`: If the chat history is not found.

---

## MCP (Multi-Capability Plugin) API

**File:** `backend/app/api/routers/v1/mcp.py`

This API allows the AI to invoke various tools and integrations.

### `GET /servers`

Lists all available MCP servers (integrations).

*   **Responses:**
    *   `200 OK`: Returns a list of available servers.

### `GET /tools`

Lists all available tools across all MCP servers.

*   **Responses:**
    *   `200 OK`: Returns a list of available tools.

### `POST /invoke`

Invokes a specific tool on an MCP server.

*   **Request Body:** `InvokeRequest`
    *   `server_id` (str): The ID of the server (e.g., "github", "notion").
    *   `tool` (str): The name of the tool to invoke.
    *   `arguments` (dict): A dictionary of arguments for the tool.
    *   `oauth` (dict, optional): OAuth tokens if required by the tool.
*   **Responses:**
    *   `200 OK`: Returns an `InvokeResponse` object with the result of the tool invocation.
    *   `400 Bad Request`: If the tool is unknown.
    *   `404 Not Found`: If the server is unknown.
    *   `500 Internal Server Error`: If the tool invocation fails.

---

## MCP OAuth API

**File:** `backend/app/api/routers/v1/mcp_oauth.py`

This API handles the OAuth2 flow for MCP integrations, particularly for Google services.

### `GET /oauth/status`

Provides a status of the MCP OAuth configuration.

*   **Responses:**
    *   `200 OK`: Returns a JSON object with the OAuth status for each service.

### `GET /oauth/google/authorize-url`

Generates a Google OAuth authorization URL.

*   **Query Parameters:**
    *   `redirect_uri` (str): The URI to redirect to after authorization.
*   **Responses:**
    *   `200 OK`: Returns the authorization URL.
    *   `503 Service Unavailable`: If `GOOGLE_CLIENT_ID` is not configured.

### `POST /oauth/google/token`

Exchanges a Google OAuth authorization code for an access token and refresh token.

*   **Request Body:** `GoogleOAuthTokenRequest`
    *   `code` (str): The authorization code.
    *   `redirect_uri` (str): The redirect URI used in the authorization request.
*   **Responses:**
    *   `200 OK`: Returns the access token, refresh token, and other token details.
    *   `400 Bad Request`: If the token exchange fails.
    *   `503 Service Unavailable`: If `GOOGLE_CLIENT_ID` or `GOOGLE_CLIENT_SECRET` are not configured.

---

## Plan API

**File:** `backend/app/api/routers/v1/plan_router.py`

This API manages the execution plans.

### `POST /`

Creates a new execution plan.

*   **Request Body:** A dictionary representing the plan data.
*   **Responses:**
    *   `200 OK`: Returns the created `ExecutionPlan` object.

### `GET /`

Retrieves a list of all execution plans.

*   **Query Parameters:**
    *   `skip` (int): Number of records to skip. Default: `0`.
    *   `limit` (int): Maximum number of records to return. Default: `100`.
*   **Responses:**
    *   `200 OK`: Returns a list of `ExecutionPlan` objects.

### `GET /{plan_id}`

Retrieves a specific execution plan by its ID.

*   **Path Parameters:**
    *   `plan_id` (UUID): The ID of the plan.
*   **Responses:**
    *   `200 OK`: Returns an `ExecutionPlan` object.
    *   `404 Not Found`: If the plan is not found.

### `PUT /{plan_id}`

Updates an existing execution plan.

*   **Path Parameters:**
    *   `plan_id` (UUID): The ID of the plan.
*   **Request Body:** A dictionary with the updated plan data.
*   **Responses:**
    *   `200 OK`: Returns the updated `ExecutionPlan` object.
    *   `404 Not Found`: If the plan is not found.

### `DELETE /{plan_id}`

Deletes an execution plan by its ID.

*   **Path Parameters:**
    *   `plan_id` (UUID): The ID of the plan.
*   **Responses:**
    *   `200 OK`: Returns `true` if the deletion was successful.
    *   `404 Not Found`: If the plan is not found.

---

## Session API

**File:** `backend/app/api/routers/v1/session_router.py`

This API manages user chat sessions.

### `POST /`

Creates a new chat session.

*   **Request Body:**
    *   `user_id` (UUID): The ID of the user creating the session.
*   **Responses:**
    *   `200 OK`: Returns the created `Session` object.

### `GET /{session_id}`

Retrieves a specific session by its ID.

*   **Path Parameters:**
    *   `session_id` (UUID): The ID of the session.
*   **Responses:**
    *   `200 OK`: Returns a `Session` object.
    *   `404 Not Found`: If the session is not found.

### `GET /user/{user_id}`

Retrieves all sessions for a specific user.

*   **Path Parameters:**
    *   `user_id` (UUID): The ID of the user.
*   **Query Parameters:**
    *   `skip` (int): Number of records to skip. Default: `0`.
    *   `limit` (int): Maximum number of records to return. Default: `100`.
*   **Responses:**
    *   `200 OK`: Returns a list of `Session` objects.

### `DELETE /{session_id}`

Deletes a session by its ID.

*   **Path Parameters:**
    *   `session_id` (UUID): The ID of the session.
*   **Responses:**
    *   `200 OK`: Returns `true` if the deletion was successful.
    *   `404 Not Found`: If the session is not found.

---

## Task API

**File:** `backend/app/api/routers/v1/task_router.py`

This API manages the individual tasks within an execution plan.

### `POST /`

Creates a new task.

*   **Request Body:** A dictionary representing the task data.
*   **Responses:**
    *   `200 OK`: Returns the created `Task` object.

### `GET /`

Retrieves a list of all tasks.

*   **Query Parameters:**
    *   `skip` (int): Number of records to skip. Default: `0`.
    *   `limit` (int): Maximum number of records to return. Default: `100`.
*   **Responses:**
    *   `200 OK`: Returns a list of `Task` objects.

### `GET /{task_id}`

Retrieves a specific task by its ID.

*   **Path Parameters:**
    *   `task_id` (UUID): The ID of the task.
*   **Responses:**
    *   `200 OK`: Returns a `Task` object.
    *   `404 Not Found`: If the task is not found.

### `PUT /{task_id}`

Updates an existing task.

*   **Path Parameters:**
    *   `task_id` (UUID): The ID of the task.
*   **Request Body:** A dictionary with the updated task data.
*   **Responses:**
    *   `200 OK`: Returns the updated `Task` object.
    *   `404 Not Found`: If the task is not found.

### `DELETE /{task_id}`

Deletes a task by its ID.

*   **Path Parameters:**
    *   `task_id` (UUID): The ID of the task.
*   **Responses:**
    *   `200 OK`: Returns `true` if the deletion was successful.
    *   `404 Not Found`: If the task is not found.

---

## User API

**File:** `backend/app/api/routers/v1/user_router.py`

This API manages user accounts.

### `POST /`

Creates a new user.

*   **Request Body:** `UserCreate`
    *   `email` (EmailStr): The user's email address.
    *   `first_name` (str, optional): The user's first name.
    *   `last_name` (str, optional): The user's last name.
    *   `clerk_id` (str): The user's ID from Clerk.
*   **Responses:**
    *   `200 OK`: Returns the created `User` object.

### `GET /`

Retrieves a list of all users.

*   **Query Parameters:**
    *   `skip` (int): Number of records to skip. Default: `0`.
    *   `limit` (int): Maximum number of records to return. Default: `100`.
*   **Responses:**
    *   `200 OK`: Returns a list of `User` objects.

### `GET /{user_id}`

Retrieves a specific user by their ID.

*   **Path Parameters:**
    *   `user_id` (UUID): The ID of the user.
*   **Responses:**
    *   `200 OK`: Returns a `User` object.
    *   `404 Not Found`: If the user is not found.

### `PUT /{user_id}`

Updates an existing user.

*   **Path Parameters:**
    *   `user_id` (UUID): The ID of the user.
*   **Request Body:** `UserUpdate`
    *   `email` (EmailStr, optional): The user's email address.
    *   `first_name` (str, optional): The user's first name.
    *   `last_name` (str, optional): The user's last name.
*   **Responses:**
    *   `200 OK`: Returns the updated `User` object.
    *   `404 Not Found`: If the user is not found.

### `DELETE /{user_id}`

Deletes a user by their ID.

*   **Path Parameters:**
    *   `user_id` (UUID): The ID of the user.
*   **Responses:**
    *   `200 OK`: Returns `true` if the deletion was successful.
    *   `404 Not Found`: If the user is not found.

