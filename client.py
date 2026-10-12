"""Multi-Agent Conflict Detector & Resource Lock Arbiter.
100% Python Standard Library.
"""

from typing import List, Dict, Any, Optional, Set
import time


class ResourceLockArbiter:
    """Coordinates parallel multi-agent swarms by detecting concurrent resource collisions,
    granting TTL-governed leases, and resolving competing edit proposals."""

    def __init__(self):
        # Maps resource_uri -> {"agent_id": str, "lock_type": "EXCLUSIVE" | "SHARED", "expires_at": float}
        self._locks: Dict[str, Dict[str, Any]] = {}

    def _purge_expired(self):
        now = time.time()
        expired = [r for r, l in self._locks.items() if l["expires_at"] <= now]
        for r in expired:
            del self._locks[r]

    def acquire_lock(
        self,
        resource_uri: str,
        agent_id: str,
        ttl_seconds: int = 60,
        lock_type: str = "EXCLUSIVE",
    ) -> Dict[str, Any]:
        """Attempts to acquire a lock on a designated resource for an agent."""
        self._purge_expired()
        now = time.time()

        if resource_uri in self._locks:
            curr = self._locks[resource_uri]
            if curr["agent_id"] == agent_id:
                # Renew lease
                curr["expires_at"] = now + ttl_seconds
                return {
                    "granted": True,
                    "renewed": True,
                    "resource_uri": resource_uri,
                    "agent_id": agent_id,
                    "expires_in_seconds": ttl_seconds,
                }
            return {
                "granted": False,
                "renewed": False,
                "resource_uri": resource_uri,
                "held_by_agent": curr["agent_id"],
                "expires_in_seconds": round(max(0, curr["expires_at"] - now), 1),
                "error": f"Resource '{resource_uri}' is currently locked by agent '{curr['agent_id']}'.",
            }

        # Grant new lock
        self._locks[resource_uri] = {
            "agent_id": agent_id,
            "lock_type": lock_type.upper(),
            "expires_at": now + ttl_seconds,
        }
        return {
            "granted": True,
            "renewed": False,
            "resource_uri": resource_uri,
            "agent_id": agent_id,
            "expires_in_seconds": ttl_seconds,
        }

    def release_lock(self, resource_uri: str, agent_id: str) -> Dict[str, Any]:
        """Explicitly releases an active lock held by the designated agent."""
        self._purge_expired()
        if resource_uri in self._locks:
            if self._locks[resource_uri]["agent_id"] == agent_id:
                del self._locks[resource_uri]
                return {"released": True, "resource_uri": resource_uri}
            return {
                "released": False,
                "error": f"Cannot release lock held by another agent '{self._locks[resource_uri]['agent_id']}'.",
            }
        return {"released": True, "notice": "Lock did not exist or was already expired."}

    @classmethod
    def detect_proposal_conflicts(
        cls,
        proposals: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Analyzes an array of parallel agent action proposals to detect collisions on shared resources.
        Each proposal should contain:
            - 'agent_id' (str)
            - 'target_resources' (List[str])
            - 'priority' (int, higher is more important)
        """
        resource_to_agents: Dict[str, List[Dict[str, Any]]] = {}
        for p in proposals:
            agent = p.get("agent_id", "unknown")
            priority = p.get("priority", 0)
            for res in p.get("target_resources", []):
                if res not in resource_to_agents:
                    resource_to_agents[res] = []
                resource_to_agents[res].append({"agent_id": agent, "priority": priority})

        conflicts = {}
        for res, claimants in resource_to_agents.items():
            if len(claimants) > 1:
                # Collision detected
                sorted_claimants = sorted(claimants, key=lambda x: x["priority"], reverse=True)
                winner = sorted_claimants[0]["agent_id"]
                losers = [c["agent_id"] for c in sorted_claimants[1:]]
                conflicts[res] = {
                    "competing_agents": [c["agent_id"] for c in claimants],
                    "arbitrated_winner": winner,
                    "blocked_agents": losers,
                    "resolution": f"Agent '{winner}' has highest priority and proceeds. Blocked: {', '.join(losers)}.",
                }

        return {
            "has_conflicts": len(conflicts) > 0,
            "conflict_count": len(conflicts),
            "conflicts": conflicts,
        }
