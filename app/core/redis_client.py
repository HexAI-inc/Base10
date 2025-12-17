"""
Redis client for caching and session management.

Use cases:
1. Leaderboard caching (weekly rankings - fast API response)
2. Rate limiting (prevent abuse)
3. Session storage (SMS OTP codes)
4. Temporary data (search suggestions, autocomplete)
"""
import redis
from typing import Optional, Any
import json
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    """
    Singleton Redis client for Base10.
    
    Handles connection pooling and automatic serialization.
    """
    
    _instance = None
    _client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisClient, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            try:
                self._client = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,  # Auto-decode bytes to strings
                    socket_connect_timeout=5,
                    socket_keepalive=True,
                    health_check_interval=30
                )
                # Test connection
                self._client.ping()
                logger.info(f"✅ Redis connected: {settings.REDIS_URL}")
            except redis.ConnectionError as e:
                logger.warning(f"⚠️  Redis unavailable: {e}")
                logger.info("ℹ️  App will use in-memory fallback (caching disabled, slower leaderboards)")
                self._client = None
            except Exception as e:
                logger.warning(f"⚠️  Redis connection issue: {e}")
                logger.info("ℹ️  App will continue without Redis")
                self._client = None
    
    @property
    def client(self) -> Optional[redis.Redis]:
        """Get Redis client instance."""
        return self._client
    
    def set_json(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Store JSON-serializable data in Redis.
        
        Args:
            key: Redis key
            value: JSON-serializable object
            ttl: Time-to-live in seconds (None = no expiration)
        
        Returns:
            True if successful
        """
        if not self._client:
            logger.warning("Redis not available, skipping cache")
            return False
        
        try:
            serialized = json.dumps(value)
            if ttl:
                self._client.setex(key, ttl, serialized)
            else:
                self._client.set(key, serialized)
            return True
        except Exception as e:
            logger.error(f"❌ Redis SET failed: {e}")
            return False
    
    def get_json(self, key: str) -> Optional[Any]:
        """
        Retrieve JSON data from Redis.
        
        Args:
            key: Redis key
        
        Returns:
            Deserialized object or None if not found
        """
        if not self._client:
            return None
        
        try:
            data = self._client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"❌ Redis GET failed: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete key from Redis."""
        if not self._client:
            return False
        
        try:
            self._client.delete(key)
            return True
        except Exception as e:
            logger.error(f"❌ Redis DELETE failed: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        if not self._client:
            return False
        
        try:
            return bool(self._client.exists(key))
        except Exception as e:
            logger.error(f"❌ Redis EXISTS check failed: {e}")
            return False
    
    def set_with_ttl(self, key: str, value: str, ttl: int) -> bool:
        """Set string value with expiration."""
        if not self._client:
            return False
        
        try:
            self._client.setex(key, ttl, value)
            return True
        except Exception as e:
            logger.error(f"❌ Redis SETEX failed: {e}")
            return False
    
    def increment(self, key: str) -> Optional[int]:
        """Increment counter (useful for rate limiting)."""
        if not self._client:
            return None
        
        try:
            return self._client.incr(key)
        except Exception as e:
            logger.error(f"❌ Redis INCR failed: {e}")
            return None
    
    def get_leaderboard(self, period: str = "weekly") -> Optional[list]:
        """
        Get cached leaderboard.
        
        Args:
            period: 'weekly' or 'monthly'
        
        Returns:
            List of leaderboard entries or None
        """
        key = f"leaderboard:{period}"
        return self.get_json(key)
    
    def set_leaderboard(
        self,
        leaderboard: list,
        period: str = "weekly",
        ttl: int = 3600  # 1 hour cache
    ) -> bool:
        """
        Cache leaderboard data.
        
        Args:
            leaderboard: List of user rankings
            period: 'weekly' or 'monthly'
            ttl: Cache duration in seconds
        
        Returns:
            True if successful
        """
        key = f"leaderboard:{period}"
        return self.set_json(key, leaderboard, ttl)
    
    def clear_leaderboard_cache(self):
        """Clear all leaderboard caches."""
        if not self._client:
            return
        
        try:
            keys = self._client.keys("leaderboard:*")
            if keys:
                self._client.delete(*keys)
                logger.info(f"🗑️  Cleared {len(keys)} leaderboard caches")
        except Exception as e:
            logger.error(f"❌ Failed to clear leaderboard cache: {e}")


# Singleton instance
redis_client = RedisClient()


# Example usage:
if __name__ == "__main__":
    # Test connection
    client = RedisClient()
    
    if client.client:
        # Example 1: Cache leaderboard
        leaderboard_data = [
            {"user_id": 123, "name": "Alice", "score": 950, "rank": 1},
            {"user_id": 456, "name": "Bob", "score": 920, "rank": 2},
            {"user_id": 789, "name": "Charlie", "score": 880, "rank": 3}
        ]
        
        success = client.set_leaderboard(leaderboard_data, period="weekly", ttl=3600)
        print(f"Leaderboard cached: {success}")
        
        # Example 2: Retrieve cached leaderboard
        cached = client.get_leaderboard("weekly")
        print(f"Cached leaderboard: {cached}")
        
        # Example 3: Rate limiting
        user_id = 123
        rate_key = f"rate_limit:api:{user_id}"
        count = client.increment(rate_key)
        if count == 1:
            # First request, set TTL
            client.client.expire(rate_key, 60)  # 60 seconds window
        
        if count > 100:
            print(f"Rate limit exceeded for user {user_id}")
        else:
            print(f"Request {count}/100 in current window")
        
        print("✅ Redis tests passed!")
    else:
        print("❌ Redis not available")
