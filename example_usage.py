"""Example usage for Multi-Agent Conflict Detector & Resource Lock Arbiter."""
from client import ResourceLockArbiter

if __name__ == "__main__":
    arbiter = ResourceLockArbiter()

    # 1. Acquire resource lock
    l1 = arbiter.acquire_lock("file:///workspace/src/auth.py", "worker-agent-1", ttl_seconds=30)
    print("Agent 1 Lock Granted:", l1["granted"])

    # 2. Competing agent attempts to acquire the same lock
    l2 = arbiter.acquire_lock("file:///workspace/src/auth.py", "worker-agent-2")
    print("Agent 2 Lock Granted:", l2["granted"])
    print("Conflict Notice:", l2.get("error"))

    # 3. Detect action proposal conflicts across a swarm
    proposals = [
        {"agent_id": "agent-frontend", "target_resources": ["api/types.ts", "ui/app.tsx"], "priority": 10},
        {"agent_id": "agent-backend", "target_resources": ["api/types.ts", "db/models.py"], "priority": 20},
    ]
    conflicts = ResourceLockArbiter.detect_proposal_conflicts(proposals)
    print("\nHas Swarm Conflicts:", conflicts["has_conflicts"])
    print("Arbitrated Resolution:", conflicts["conflicts"]["api/types.ts"]["resolution"])
