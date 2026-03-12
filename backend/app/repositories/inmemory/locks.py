"""Lock manager for in-memory repositories"""
import asyncio
from contextlib import asynccontextmanager
from typing import Dict


class LockManager:
    """Manager for per-entity asyncio locks"""
    
    def __init__(self):
        self._locks: Dict[str, asyncio.Lock] = {}
    
    def _get_lock_key(self, entity_type: str, entity_id: str) -> str:
        """Generate lock key for entity"""
        return f"{entity_type}:{entity_id}"
    
    def get_lock(self, entity_type: str, entity_id: str) -> asyncio.Lock:
        """Get or create lock for entity"""
        key = self._get_lock_key(entity_type, str(entity_id))
        if key not in self._locks:
            self._locks[key] = asyncio.Lock()
        return self._locks[key]
    
    @asynccontextmanager
    async def lock_for(self, entity_type: str, entity_id: str):
        """Context manager to lock entity for update"""
        lock = self.get_lock(entity_type, entity_id)
        async with lock:
            yield
    
    def clear_locks(self):
        """Clear all locks (for testing)"""
        self._locks.clear()


# Global lock manager instance
_lock_manager = LockManager()


def get_lock_manager() -> LockManager:
    """Get global lock manager instance"""
    return _lock_manager


# Convenience function for locking trip
async def lock_trip_for_update(trip_id: str):
    """Lock trip for atomic updates"""
    return get_lock_manager().lock_for("trip", trip_id)