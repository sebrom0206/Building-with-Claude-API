# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository overview

This is a personal learning repository for an Anthropic course on building with the Claude API. It is organized as a sequence of numbered modules (`01` through `08`), each covering a different capability. Most modules are Jupyter notebooks meant to be run top-to-bottom and edited in place while experimenting; two modules (`07` and `08`) are standalone Python applications.

```
01 Accessing Claude with the API/   basic Messages API usage, system prompts, temperature, streaming, structured output
02 Prompt evaluation/               building prompt eval harnesses (grading functions, LLM-as-judge)
03 prompt engineering/              prompting technique experiments
04 Tool use/                        tool-use / function-calling notebooks + a standalone main.py demo
05 RAG and Agentic Search/          chunking, embeddings, vector DB, BM25, hybrid search
06 Claude features/                 extended thinking, image support, PDF support, prompt caching, code execution / files API
07 Model Context Protocol/          cli_project — a full MCP client+server chat CLI (see below)
08 Anthropic apps/                  app_starter — a minimal MCP tool server template (see below)
```

Notebooks in `01`–`06` install their own dependencies in the first cell (`%pip install ...`) and read `ANTHROPIC_API_KEY` (and `VOYAGE_API_KEY` for the RAG module) from the repo-root `.env`. There is no shared package or build step across modules — each notebook/folder is self-contained. When editing a notebook, only modify the relevant cells; don't restructure unrelated cells.

The two Python projects (`07 Model Context Protocol/cli_project` and `08 Anthropic apps/app_starter`) each have their own `.env`, `pyproject.toml`, and `uv.lock` and must be worked on from within their own directory — they are independent projects, not part of a shared workspace.

## Commands

### `07 Model Context Protocol/cli_project` (MCP chat CLI)

```bash
uv venv
uv pip install -e .
uv run main.py                # run the interactive chat CLI
```

Without uv: `pip install anthropic python-dotenv prompt-toolkit "mcp[cli]==1.8.0"` then `python main.py`. Requires `.env` with `ANTHROPIC_API_KEY` and `CLAUDE_MODEL` set (`main.py` asserts both are non-empty at startup). Set `USE_UV=1` in `.env` if launching the bundled `mcp_server.py` subprocess via `uv run` rather than plain `python`.

No lint or type checks or automated tests are set up for this project (per its README).

### `08 Anthropic apps/app_starter` (MCP tool server template)

```bash
uv venv
uv pip install -e .
uv run main.py                 # start the MCP server
uv run pytest                  # run all tests
uv run pytest tests/test_document.py            # run one test file
uv run pytest tests/test_document.py::TestBinaryDocumentToMarkdown::test_binary_document_to_markdown_with_docx  # run one test
```

## Architecture: `cli_project` (module 07)

A terminal chat app that connects an Anthropic `Messages` conversation loop to one or more MCP servers over stdio.

- **`main.py`** — entry point. Loads env vars, constructs a `Claude` service, spins up an `MCPClient` for the bundled `mcp_server.py` (registered as `doc_client`) plus one additional `MCPClient` per server script passed as a CLI arg, wires them into `CliChat`, and runs the `CliApp` REPL. All client lifecycles are managed together via `AsyncExitStack`.
- **`mcp_client.py`** — `MCPClient` wraps an MCP `ClientSession` over a stdio subprocess (`stdio_client`). Exposes `list_tools`, `call_tool`, `list_prompts`, `get_prompt`, `read_resource`. Used as an async context manager (`connect`/`cleanup` on enter/exit).
- **`mcp_server.py`** — the example MCP server (`FastMCP`) exposing an in-memory `docs` dict via tools (`read_doc_contents`, `edit_document`), resources (`docs://documents`, `docs://documents/{doc_id}`), and a prompt (`format`). This file is intentionally left with unfinished TODOs (e.g. a summarize prompt) as course exercises.
- **`core/claude.py`** — thin wrapper (`Claude`) around the `anthropic.Anthropic` client: builds `messages.create` params (model, temperature, stop_sequences, optional `thinking`, optional `tools`/`system`), and has helpers to append user/assistant messages and extract text blocks from a `Message`.
- **`core/chat.py`** — `Chat` holds the running message list and drives the agent loop: call Claude → if `stop_reason == "tool_use"`, execute the requested tools via `ToolManager` and feed results back as a user message → repeat until Claude returns a non-tool-use response.
- **`core/tools.py`** — `ToolManager` aggregates tool schemas from all connected `MCPClient`s (`get_all_tools`), routes a `tool_use` block to whichever client actually has that tool (`_find_client_with_tool`), invokes it, and formats the result (or error) as an Anthropic `tool_result` content block.
- **`core/cli_chat.py`** — `CliChat(Chat)` adds document/resource awareness on top of the base loop: expands `@doc_id` mentions in the user's query into `<document>` context blocks pulled from the doc MCP server, and treats `/command doc_id` input as an MCP *prompt* invocation (via `get_prompt`) rather than a normal chat turn.
- **`core/cli.py`** — `CliApp` is the `prompt_toolkit` REPL: custom key bindings/completer for `@resource` and `/command` autocomplete (pulled from `list_docs_ids()` / `list_prompts()`), and the main input/response loop.

Key flow to understand when modifying this project: `CliApp.run()` → `CliChat._process_query` (resolve `@mentions` or `/commands`) → `Chat.run()` (Claude ⇄ tool-use loop via `ToolManager`) → tools dispatched to whichever `MCPClient` owns them.

## Architecture: `app_starter` (module 08)

A minimal template for building an MCP tool server from scratch (used as the starting point for course exercises building new tools).

- **`main.py`** — creates a `FastMCP("docs")` instance and registers tools with `mcp.tool()(fn)`; run via `mcp.run()` (stdio transport).
- **`tools/`** — plain Python functions, registered as MCP tools in `main.py`. `tools/math.py::add` is the reference example for tool style (see below); `tools/document.py::binary_document_to_markdown` converts binary doc bytes (docx/pdf/etc.) to markdown via `markitdown`.
- **`tests/`** — pytest tests for the tools (not for the MCP server wiring itself), with binary fixtures under `tests/fixtures/`.

### Defining MCP tools (from the module README)

Register a tool by passing the function to `mcp.tool()`:

```python
mcp.tool()(my_function)
```

Tool function conventions used throughout this repo:

- Take parameters typed with `pydantic.Field(description=...)` so each argument's purpose is visible to the model via the generated schema — do not rely on bare type hints alone.
- Write a docstring that:
  - Begins with a one-line summary.
  - Gives a more detailed explanation of what the tool does.
  - States when to use (and explicitly when *not* to use) the tool.
  - Includes usage examples showing expected input/output (doctest-style `>>>` examples, as in `tools/math.py::add`).

```python
from pydantic import Field

def my_tool(
    param1: str = Field(description="Detailed description of this parameter"),
    param2: int = Field(description="Explain what this parameter does"),
) -> ReturnType:
    """One-line summary.

    Longer explanation of behavior.

    When to use:
    - ...

    Examples:
    >>> my_tool("x", 1)
    ...
    """
    # Implementation
```

This same convention (`Field`-described params + structured docstring) is what `mcp_server.py` in the `cli_project` module follows for its `read_doc_contents` / `edit_document` tools, and what the client-side tool schemas (`core/tools.py::ToolManager.get_all_tools`) surface to Claude as `name` / `description` / `input_schema` — so a poorly described tool here directly degrades Claude's ability to pick and call it correctly at runtime.