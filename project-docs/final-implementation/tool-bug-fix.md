# Walkthrough - Tool Contract Implementation

I have implemented the "Tool Contract First Design" to improve the reliability and robustness of tool execution.

## 1. Dynamic Tool Discovery
The `MCPAltRegistry` now automatically discovers and caches JSON schemas for all registered tools during initialization. This ensures that the system always has up-to-date information about tool signatures.

## 2. Schema-Injected Planning
The `TaskPlannerAgent` has been upgraded to fetch these schemas and inject them as a structured "Tool Catalog" into the LLM prompt. This forces the LLM to generate task parameters that conform exactly to the required schemas.

## 3. Validation Gate
I added a `jsonschema` validation layer in the `ActionAgent`. Before any tool is invoked, its arguments are checked against the tool's official schema. 

![Validation Logic](file:///Users/macbookpro2015/Documents/andela-ai-bootcamp/production-course/personal-ai-agent/backend/app/agents/action_agent.py#L222-L235)

## 4. Parameter Substitution
The `ActionAgent` now handles recursive placeholder substitution for `user_context` and `task_output` references, ensuring late-bound values are resolved correctly before validation.

## 5. Result Parsing
Improved JSON serialization in the `ActionAgent` ensures that complex tool outputs (like MCP `TextContent`) can be safely passed to the LLM for summarization without causing serialization errors.
