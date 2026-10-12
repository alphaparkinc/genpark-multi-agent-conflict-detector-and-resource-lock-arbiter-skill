"""MCP server for Multi-Agent Conflict Detector & Resource Lock Arbiter."""
import sys
import json
from client import ResourceLockArbiter

_arbiter = ResourceLockArbiter()


def handle_request(req):
    method = req.get("method")
    if method == "tools/list":
        return {
            "tools": [
                {
                    "name": "acquire_resource_lock",
                    "description": "Acquires or renews a TTL-backed lease on a resource (file path, DB key, state object)",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "resource_uri": {"type": "string", "description": "Unique identifier of resource"},
                            "agent_id": {"type": "string", "description": "Identifier of the requesting agent"},
                            "ttl_seconds": {"type": "integer", "default": 60},
                        },
                        "required": ["resource_uri", "agent_id"],
                    },
                },
                {
                    "name": "release_resource_lock",
                    "description": "Releases an active lock held by an agent",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "resource_uri": {"type": "string"},
                            "agent_id": {"type": "string"},
                        },
                        "required": ["resource_uri", "agent_id"],
                    },
                },
                {
                    "name": "detect_proposal_conflicts",
                    "description": "Evaluates concurrent agent action proposals for resource collisions and arbitrates winners based on priority",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "proposals": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "agent_id": {"type": "string"},
                                        "target_resources": {"type": "array", "items": {"type": "string"}},
                                        "priority": {"type": "integer"},
                                    },
                                    "required": ["agent_id", "target_resources"],
                                },
                            }
                        },
                        "required": ["proposals"],
                    },
                },
            ]
        }
    elif method == "tools/call":
        params = req.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})
        if tool_name == "acquire_resource_lock":
            res = _arbiter.acquire_lock(
                args.get("resource_uri", ""),
                args.get("agent_id", ""),
                ttl_seconds=args.get("ttl_seconds", 60),
            )
            return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
        elif tool_name == "release_resource_lock":
            res = _arbiter.release_lock(
                args.get("resource_uri", ""),
                args.get("agent_id", ""),
            )
            return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
        elif tool_name == "detect_proposal_conflicts":
            res = ResourceLockArbiter.detect_proposal_conflicts(args.get("proposals", []))
            return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
    return {"error": "Method not found"}


if __name__ == "__main__":
    for line in sys.stdin:
        if line.strip():
            print(json.dumps(handle_request(json.loads(line))))
            sys.stdout.flush()
