"""
Sistema de Cache Avançado para o Log Analyzer
Implementa cache em memória e Redis para otimização de performance
"""

import hashlib
import json
import time
from collections import OrderedDict
from functools import wraps
from typing import Any, Callable, Dict, Optional


class MemoryCache:
    """Cache em memória com LRU eviction."""

    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: OrderedDict = OrderedDict()
        self._timestamps: Dict[str, float] = {}

    def get(self, key: str) -> Optional[Any]:
        """Obtém valor do cache."""
        if key not in self._cache:
            return None

        # Verificar TTL
        if self._is_expired(key):
            self.delete(key)
            return None

        # Mover para o final (LRU)
        self._cache.move_to_end(key)
        return self._cache[key]

    def set(self, key: str, value: Any) -> None:
        """Define valor no cache."""
        # Remover item existente se existir
        if key in self._cache:
            del self._cache[key]

        # Adicionar novo item
        self._cache[key] = value
        self._timestamps[key] = time.time()

        # Verificar limite de tamanho
        while len(self._cache) > self.max_size:
            oldest_key = next(iter(self._cache))
            self.delete(oldest_key)

    def delete(self, key: str) -> None:
        """Remove item do cache."""
        self._cache.pop(key, None)
        self._timestamps.pop(key, None)

    def clear(self) -> None:
        """Limpa todo o cache."""
        self._cache.clear()
        self._timestamps.clear()

    def _is_expired(self, key: str) -> bool:
        """Verifica se item expirou."""
        timestamp = self._timestamps.get(key, 0)
        return time.time() - timestamp > self.ttl_seconds

    def stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache."""
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "ttl_seconds": self.ttl_seconds,
            "hit_ratio": getattr(self, "_hit_count", 0)
            / max(getattr(self, "_access_count", 1), 1),
        }


class RedisCache:
    """Cache usando Redis."""

    def __init__(self, redis_client=None, ttl_seconds: int = 3600):
        self.redis_client = redis_client
        self.ttl_seconds = ttl_seconds
        self.available = redis_client is not None

    def get(self, key: str) -> Optional[Any]:
        """Obtém valor do Redis."""
        if not self.available:
            return None

        try:
            value = self.redis_client.get(key)
            if value is not None:
                return json.loads(value)
        except Exception:
            pass
        return None

    def set(self, key: str, value: Any) -> None:
        """Define valor no Redis."""
        if not self.available:
            return

        try:
            serialized = json.dumps(value, default=str)
            self.redis_client.setex(key, self.ttl_seconds, serialized)
        except Exception:
            pass

    def delete(self, key: str) -> None:
        """Remove item do Redis."""
        if not self.available:
            return

        try:
            self.redis_client.delete(key)
        except Exception:
            pass

    def clear(self) -> None:
        """Limpa cache (flush database)."""
        if not self.available:
            return

        try:
            self.redis_client.flushdb()
        except Exception:
            pass


class HybridCache:
    """Cache híbrido com memória local e Redis."""

    def __init__(self, memory_cache: MemoryCache, redis_cache: RedisCache):
        self.memory_cache = memory_cache
        self.redis_cache = redis_cache
        self._hit_count = 0
        self._miss_count = 0

    def get(self, key: str) -> Optional[Any]:
        """Obtém valor do cache (L1: memória, L2: Redis)."""
        # Tentar cache de memória primeiro
        value = self.memory_cache.get(key)
        if value is not None:
            self._hit_count += 1
            return value

        # Tentar Redis
        value = self.redis_cache.get(key)
        if value is not None:
            # Armazenar em memória para próximas consultas
            self.memory_cache.set(key, value)
            self._hit_count += 1
            return value

        self._miss_count += 1
        return None

    def set(self, key: str, value: Any) -> None:
        """Define valor em ambos os caches."""
        self.memory_cache.set(key, value)
        self.redis_cache.set(key, value)

    def delete(self, key: str) -> None:
        """Remove item de ambos os caches."""
        self.memory_cache.delete(key)
        self.redis_cache.delete(key)

    def clear(self) -> None:
        """Limpa ambos os caches."""
        self.memory_cache.clear()
        self.redis_cache.clear()

    def stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache."""
        total_requests = self._hit_count + self._miss_count
        hit_ratio = self._hit_count / max(total_requests, 1)

        return {
            "hit_count": self._hit_count,
            "miss_count": self._miss_count,
            "hit_ratio": hit_ratio,
            "memory_cache": self.memory_cache.stats(),
        }


def cache_key(*args, **kwargs) -> str:
    """Gera chave de cache baseada nos argumentos."""
    key_data = {"args": args, "kwargs": sorted(kwargs.items())}
    key_string = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.md5(key_string.encode()).hexdigest()


def cached(cache_instance: HybridCache):
    """Decorator para cache de funções."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Gerar chave de cache
            key = f"{func.__name__}:{cache_key(*args, **kwargs)}"

            # Tentar obter do cache
            result = cache_instance.get(key)
            if result is not None:
                return result

            # Executar função e cachear resultado
            result = func(*args, **kwargs)
            cache_instance.set(key, result)

            return result

        # Adicionar métodos para gerenciar cache
        wrapper.cache_clear = lambda: cache_instance.clear()
        wrapper.cache_stats = lambda: cache_instance.stats()

        return wrapper

    return decorator


# Instâncias globais de cache
memory_cache = MemoryCache(max_size=1000, ttl_seconds=3600)

# Redis será inicializado quando necessário
redis_cache = RedisCache(redis_client=None, ttl_seconds=3600)

# Cache híbrido
hybrid_cache = HybridCache(memory_cache, redis_cache)


def init_redis_cache(redis_client):
    """Inicializa cache Redis."""
    global redis_cache, hybrid_cache
    redis_cache = RedisCache(redis_client, ttl_seconds=3600)
    hybrid_cache = HybridCache(memory_cache, redis_cache)


def get_cache() -> HybridCache:
    """Retorna instância do cache."""
    return hybrid_cache
