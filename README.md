# genpark-multi-agent-conflict-detector-and-resource-lock-arbiter-skill

Detects concurrent multi-agent resource collisions, enforces TTL-backed resource locks, and arbitrates competing agent proposals.

100% Python Standard Library implementation with zero external dependencies.

## Key Capabilities
- **TTL-Backed Leases**: Protects files, database keys, or shared workspace directories from overlapping agent writes with auto-expiring leases.
- **Swarm Proposal Conflict Detection**: Analyzes concurrent agent action plans in parallel and flags resource overlaps before execution.
- **Priority-Driven Arbitration**: Grants execution authority to higher-priority agents while producing structured hold notices for competing subagents.
- **Zero Overhead**: Pure standard library execution with in-memory lock coordination.

## Architecture

```
[Parallel Swarm Action Proposals]
                 │
                 ▼
┌──────────────────────────────────────────────┐
│  ResourceLockArbiter                         │
│  ├─ TTL Lease Expiration Purger              │
│  ├─ Exclusive vs Shared Lock Manager         │
│  └─ Priority Arbitration Matrix              │
└──────────────────────────────────────────────┘
                 │
    ┌────────────┴─────────────┐
    ▼                          ▼
[Winner: Lease Granted]    [Loser: Hold / Backoff Notice]
```

## MCP Server Integration

Run standard MCP stdio server:
```bash
python mcp_server.py
```

Exposed Tools:
- `acquire_resource_lock`: Requests a lease on a designated resource for an agent.
- `release_resource_lock`: Explicitly releases an active lease.
- `detect_proposal_conflicts`: Evaluates concurrent proposals and determines arbitration winners.

## Quickstart

```python
from client import ResourceLockArbiter

arbiter = ResourceLockArbiter()
res = arbiter.acquire_lock("file:///workspace/api.py", "subagent-1", ttl_seconds=60)
print(res["granted"])  # True

# Competing agent tries to lock same file
res_comp = arbiter.acquire_lock("file:///workspace/api.py", "subagent-2")
print(res_comp["granted"])  # False
print(res_comp["error"])
```
