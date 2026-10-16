"""Jemini Studio MCP Server.

Provides a Model Context Protocol (MCP) stdio server exposing tools to search,
retrieve, and inspect Jemini Studio and project documentation across docs/.
"""

from __future__ import annotations

import json
import logging
import sys
from typing import Any

from jemini.mcp.studio_docs import StudioDocsEngine

logger = logging.getLogger(__name__)

SERVER_INFO = {
    "name": "jemini-studio-docs",
    "version": "1.0.0",
}

TOOLS = [
    {
        "name": "jemini_search_docs",
        "description": "Performs token-based relevance search across all Jermina documentation in docs/ (including studio_knowledge, wiki, and guidelines).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query (e.g. 'WebSocket 1007', 'Stickman kinematics', 'Voice archetypes', 'YouTube categories')",
                },
                "section": {
                    "type": "string",
                    "description": "Optional section to narrow search (e.g. 'DevDocs', 'LiveAPIDocs', 'VideoProductionDocs', 'PublishingDocs', 'wiki', 'guidelines')",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "jemini_get_doc",
        "description": "Retrieves the full markdown content of a specific documentation file by name, stem, or relative path.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "doc_name": {
                    "type": "string",
                    "description": "Document name or path (e.g. 'StickmanKinematics', 'git_flow', 'rate_limits_by_model', 'LiveAPIDocs/WebSocketStreaming')",
                },
            },
            "required": ["doc_name"],
        },
    },
    {
        "name": "jemini_list_docs",
        "description": "Lists metadata (name, section, title, path, size) for all markdown documents in the knowledge base.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "section": {
                    "type": "string",
                    "description": "Optional section filter (e.g. 'DevDocs', 'LiveAPIDocs', 'VideoProductionDocs', 'PublishingDocs', 'wiki', 'guidelines')",
                },
            },
        },
    },
    {
        "name": "jemini_list_sections",
        "description": "Lists all available document sections in the Jemini knowledge base.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
]


class MCPServer:
    """JSON-RPC 2.0 stdio MCP server for Studio documentation."""

    def __init__(self, engine: StudioDocsEngine | None = None):
        self.engine = engine or StudioDocsEngine()

    def handle_request(self, request: dict[str, Any]) -> dict[str, Any] | None:
        """Processes a single JSON-RPC request and returns the response dictionary."""
        req_id = request.get("id")
        method = request.get("method")
        params = request.get("params") or {}

        # Notifications (no id) do not expect a response
        if req_id is None:
            if method == "notifications/initialized":
                logger.info("MCP client initialized notification received.")
            return None

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                    },
                    "serverInfo": SERVER_INFO,
                },
            }

        if method == "ping":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {},
            }

        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": TOOLS,
                },
            }

        if method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments") or {}
            content = self._execute_tool(tool_name, tool_args)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": content,
                        }
                    ],
                },
            }

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {
                "code": -32601,
                "message": f"Method not found: {method}",
            },
        }

    def _execute_tool(self, name: str, args: dict[str, Any]) -> str:
        if name == "jemini_search_docs":
            query = args.get("query", "")
            section = args.get("section")
            hits = self.engine.search_docs(query=query, section=section)
            if not hits:
                return f"No documents matched query: '{query}'" + (f" in section '{section}'" if section else "")
            
            lines = [f"# Search Results for '{query}' ({len(hits)} matches):\n"]
            for h in hits:
                lines.append(f"### [{h.section}] {h.title} (`{h.doc_name}`)")
                lines.append(f"- **File:** `{h.file_path}`")
                lines.append(f"- **Score:** {h.relevance_score:.1f}")
                lines.append(f"- **Snippet:** {h.snippet}\n")
            return "\n".join(lines)

        if name == "jemini_get_doc":
            doc_name = args.get("doc_name", "")
            content = self.engine.get_document(doc_name)
            if content is None:
                return f"Error: Document '{doc_name}' not found in docs/."
            return content

        if name == "jemini_list_docs":
            section = args.get("section")
            docs = self.engine.list_documents(section=section)
            lines = [
                f"# Jemini Studio Documentation Catalog ({len(docs)} documents)" + (f" - Section: {section}" if section else "") + ":\n",
                "| Section | Document | Title | Size (bytes) |",
                "| :--- | :--- | :--- | :---: |",
            ]
            for d in docs:
                lines.append(f"| {d['section']} | `{d['doc_name']}` | {d['title']} | {d['size_bytes']} |")
            return "\n".join(lines)

        if name == "jemini_list_sections":
            sections = self.engine.list_sections()
            lines = ["# Available Documentation Sections:\n"]
            for s in sections:
                lines.append(f"- `{s}`")
            return "\n".join(lines)

        return f"Error: Unknown tool '{name}'."

    def run_stdio(self) -> None:
        """Runs the main stdio loop reading JSON-RPC requests from sys.stdin."""
        logger.info("Jemini Studio MCP Server started on stdio.")
        for line in sys.stdin:
            line_str = line.strip()
            if not line_str:
                continue
            try:
                request = json.loads(line_str)
                response = self.handle_request(request)
                if response is not None:
                    sys.stdout.write(json.dumps(response) + "\n")
                    sys.stdout.flush()
            except Exception as e:
                err_resp = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": f"Parse error / Internal server error: {e}",
                    },
                }
                sys.stdout.write(json.dumps(err_resp) + "\n")
                sys.stdout.flush()


def main() -> None:
    server = MCPServer()
    server.run_stdio()


if __name__ == "__main__":
    main()
