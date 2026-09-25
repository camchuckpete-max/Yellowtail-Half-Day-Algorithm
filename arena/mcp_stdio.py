"""Minimal MCP (Model Context Protocol) stdio server: JSON-RPC 2.0 over newline-delimited stdin/stdout.

Only the surface Claude Code needs to expose tools: initialize, notifications/initialized, ping,
tools/list, tools/call. No third-party dependency (the `mcp` package cannot be imported in the
run environment). Tools are plain functions registered with a JSON schema.
"""
from __future__ import annotations

import json
import sys
import traceback
from typing import Callable

PROTOCOL = "2024-11-05"


class Tool:
    def __init__(self, name: str, description: str, schema: dict, fn: Callable[..., str]):
        self.name, self.description, self.schema, self.fn = name, description, schema, fn


class Server:
    def __init__(self, name: str, version: str = "0.1", instructions: str = ""):
        self.name, self.version, self.instructions = name, version, instructions
        self.tools: dict[str, Tool] = {}
        self.log = None   # optional callable(record: dict)

    def tool(self, name: str, description: str, schema: dict):
        def deco(fn):
            self.tools[name] = Tool(name, description, schema, fn)
            return fn
        return deco

    # ------------------------------------------------------------ protocol
    def handle(self, msg: dict) -> dict | None:
        method, mid, params = msg.get("method"), msg.get("id"), msg.get("params") or {}
        if method == "initialize":
            return self._ok(mid, {"protocolVersion": params.get("protocolVersion", PROTOCOL),
                                  "capabilities": {"tools": {"listChanged": False}},
                                  "serverInfo": {"name": self.name, "version": self.version},
                                  "instructions": self.instructions})
        if method == "notifications/initialized" or method.startswith("notifications/"):
            return None
        if method == "ping":
            return self._ok(mid, {})
        if method == "tools/list":
            return self._ok(mid, {"tools": [{"name": t.name, "description": t.description, "inputSchema": t.schema}
                                            for t in self.tools.values()]})
        if method == "tools/call":
            name, args = params.get("name"), params.get("arguments") or {}
            t = self.tools.get(name)
            if t is None:
                return self._ok(mid, {"content": [{"type": "text", "text": f"unknown tool {name}"}], "isError": True})
            try:
                text = t.fn(**args)
                err = False
            except ToolError as e:
                text, err = str(e), True
            except Exception:  # noqa: BLE001
                text, err = "tool failed:\n" + traceback.format_exc(limit=2), True
            if self.log:
                self.log({"tool": name, "args": args, "error": err, "result_chars": len(text or "")})
            return self._ok(mid, {"content": [{"type": "text", "text": text if text is not None else ""}], "isError": err})
        if mid is None:
            return None
        return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"method not found: {method}"}}

    @staticmethod
    def _ok(mid, result):
        return {"jsonrpc": "2.0", "id": mid, "result": result}

    def serve(self) -> None:
        out = sys.stdout
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue
            resp = self.handle(msg)
            if resp is not None:
                out.write(json.dumps(resp) + "\n")
                out.flush()


class ToolError(Exception):
    """Raised by a tool to return an error message to the model (not a crash)."""
