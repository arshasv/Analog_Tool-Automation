"""
Design Cache for Memoization
Stores and retrieves circuit evaluation results to avoid redundant simulations.
Analog designs cluster — similar parameters usually yield similar performance.
"""
import json
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class DesignCache:
    """Simple file-based cache for circuit evaluations"""
    
    def __init__(self, cache_dir: str = "data/cache/designs"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.hits = 0
        self.misses = 0
        logger.info(f"DesignCache initialized at {self.cache_dir}")
    
    @staticmethod
    def _round_params(params: Dict[str, float], decimals: int = 3) -> Dict[str, float]:
        """Round parameters for similarity matching"""
        return {
            k: round(v, decimals) if isinstance(v, float) else v
            for k, v in params.items()
        }
    
    @staticmethod
    def _make_key(circuit_type: str, params: Dict[str, float]) -> str:
        """Create cache key from circuit type and parameters"""
        rounded = DesignCache._round_params(params)
        key_str = f"{circuit_type}_{json.dumps(rounded, sort_keys=True)}"
        # Use hash to keep filenames short
        key_hash = hashlib.md5(key_str.encode()).hexdigest()[:12]
        return f"{circuit_type}_{key_hash}"
    
    def get(self, circuit_type: str, params: Dict[str, float]) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached result if available.
        
        Args:
            circuit_type: Type of circuit (e.g., "current_mirror")
            params: Parameter dictionary
        
        Returns:
            Cached result dict or None if not found
        """
        key = self._make_key(circuit_type, params)
        file_path = self.cache_dir / f"{key}.json"
        
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    result = json.load(f)
                self.hits += 1
                logger.debug(f"Cache HIT: {key}")
                return result
            except Exception as e:
                logger.warning(f"Error reading cache file {file_path}: {e}")
                return None
        
        self.misses += 1
        return None
    
    def put(self, circuit_type: str, params: Dict[str, float], result: Dict[str, Any]):
        """
        Store evaluation result in cache.
        
        Args:
            circuit_type: Type of circuit
            params: Parameter dictionary
            result: Simulation result to cache
        """
        key = self._make_key(circuit_type, params)
        file_path = self.cache_dir / f"{key}.json"
        
        try:
            with open(file_path, 'w') as f:
                json.dump(result, f, indent=2)
            logger.debug(f"Cache PUT: {key}")
        except Exception as e:
            logger.warning(f"Error writing to cache {file_path}: {e}")
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        
        return {
            "hits": self.hits,
            "misses": self.misses,
            "total": total,
            "hit_rate": f"{hit_rate:.1f}%",
            "cache_dir": str(self.cache_dir),
            "cached_files": len(list(self.cache_dir.glob("*.json")))
        }
    
    def clear(self):
        """Clear all cached files"""
        for f in self.cache_dir.glob("*.json"):
            f.unlink()
        self.hits = 0
        self.misses = 0
        logger.info("Cache cleared")


# Global cache instance
_cache_instance: Optional[DesignCache] = None


def get_cache() -> DesignCache:
    """Get or create global cache instance (singleton pattern)"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = DesignCache()
    return _cache_instance


def cache_enabled(cache_instance: Optional[DesignCache] = None) -> bool:
    """Check if caching is enabled"""
    cache = cache_instance or get_cache()
    return cache.cache_dir.exists()
