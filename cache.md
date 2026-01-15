# 4 Essential Cache Types

## 1. Application Cache (In-Memory Cache)

**What:** Cache stored within application memory (HashMap, Dictionary)

**Pros:**
- Fastest access (no network calls)
- Simple implementation
- No external dependencies
- Direct memory access

**Cons:**
- Limited to single application instance
- Lost on application restart
- Memory constraints
- Not shared across servers

**Use Cases:** Configuration data, computed results, temporary calculations

```python
# Simple in-memory cache
cache = {}
def get_user(user_id):
    if user_id in cache:
        return cache[user_id]
    user = database.get_user(user_id)
    cache[user_id] = user
    return user
```

---

## 2. Distributed Cache

**What:** Cache shared across multiple application instances (Redis, Memcached)

**Pros:**
- Shared across all app instances
- Survives application restarts
- Scalable and fault-tolerant
- Rich data structures (Redis)

**Cons:**
- Network latency overhead
- Additional infrastructure complexity
- Potential single point of failure
- Memory costs

**Use Cases:** Session data, user profiles, database query results, API responses

```python
import redis
r = redis.Redis(host='cache-server')

def get_user(user_id):
    cached = r.get(f"user:{user_id}")
    if cached:
        return json.loads(cached)
    user = database.get_user(user_id)
    r.setex(f"user:{user_id}", 3600, json.dumps(user))
    return user
```

---

## 3. Global Cache

**What:** Centralized cache serving multiple applications/services

**Pros:**
- Single source of truth
- Consistent data across services
- Centralized management
- Cost-effective for shared data

**Cons:**
- Network bottleneck risk
- Single point of failure
- Complex cache invalidation
- Higher latency than local cache

**Use Cases:** Reference data, configuration, shared lookup tables, cross-service data

```python
# Global cache accessed by multiple services
class GlobalCache:
    def __init__(self):
        self.redis_cluster = RedisCluster(nodes=[...])
    
    def get_config(self, key):
        return self.redis_cluster.get(f"global:config:{key}")
```

---

## 4. CDN Cache

**What:** Geographically distributed edge servers caching content

**Pros:**
- Global distribution, low latency
- Handles massive traffic spikes
- Reduces origin server load
- Built-in DDoS protection

**Cons:**
- Expensive for high traffic
- Complex cache invalidation
- Best for static/semi-static content
- Vendor dependency

**Use Cases:** Static assets, images, videos, API responses, web pages

```javascript
// CDN cache headers
app.get('/api/products', (req, res) => {
    res.set({
        'Cache-Control': 'public, max-age=300', // 5 minutes
        'CDN-Cache-Control': 'max-age=3600'     // 1 hour on CDN
    });
    res.json(products);
});
```

## Quick Comparison

| Cache Type | Speed | Scope | Persistence | Complexity |
|------------|-------|-------|-------------|------------|
| Application (In-Memory) | Fastest | Single Instance | No | Low |
| Distributed | Fast | Multi-Instance | Yes | Medium |
| Global | Medium | Multi-Service | Yes | High |
| CDN | Varies by Location | Global | Yes | High |

## When to Use Each

- **Application Cache**: Small, frequently accessed data within single app
- **Distributed Cache**: Shared data across app instances (sessions, user data)
- **Global Cache**: Reference data shared across multiple services
- **CDN Cache**: Static content served globally with low latency

---

# Distributed Caching with Redis - Architecture Deep Dive

## Architecture Placement

```
Client → ALB → App_Server → Redis → Database
                ↓
Client → ALB → App_Server → Redis → Database
                ↓
Client → ALB → App_Server → Redis → Database
```

**Key Points:**
- Redis sits between application servers and database
- Multiple app servers share the same Redis cluster
- Cache-aside pattern: App checks Redis first, then DB on miss

## Redis Cluster Setup

### Single Redis Instance (Development)
```
Client → ALB → App_Server_1 ↘
                              Redis_Instance → Database
Client → ALB → App_Server_2 ↗
```

### Redis Cluster (Production)
```
Client → ALB → App_Server_1 ↘
                              Redis_Master_1   ↘
Client → ALB → App_Server_2 → Redis_Master_2   → Database
                              Redis_Master_3   ↗
Client → ALB → App_Server_3 ↗
```

## Implementation Example

### 1. Redis Connection Setup
```python
import redis
import json
from redis.sentinel import Sentinel

# Single Redis instance
redis_client = redis.Redis(
    host='redis-cluster.internal',
    port=6379,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5
)

# Redis Cluster
from rediscluster import RedisCluster
redis_cluster = RedisCluster(
    startup_nodes=[
        {"host": "redis-1.internal", "port": "6379"},
        {"host": "redis-2.internal", "port": "6379"},
        {"host": "redis-3.internal", "port": "6379"}
    ],
    decode_responses=True
)
```

### 2. Cache-Aside Pattern Implementation
```python
class UserService:
    def __init__(self, redis_client, database):
        self.redis = redis_client
        self.db = database
        self.cache_ttl = 3600  # 1 hour
    
    def get_user(self, user_id):
        cache_key = f"user:{user_id}"
        
        # 1. Check Redis first
        cached_user = self.redis.get(cache_key)
        if cached_user:
            print("Cache HIT")
            return json.loads(cached_user)
        
        # 2. Cache miss - query database
        print("Cache MISS")
        user = self.db.execute(
            "SELECT * FROM users WHERE id = %s", 
            (user_id,)
        ).fetchone()
        
        if user:
            # 3. Store in Redis for future requests
            self.redis.setex(
                cache_key, 
                self.cache_ttl, 
                json.dumps(user)
            )
        
        return user
    
    def update_user(self, user_id, user_data):
        # 1. Update database
        self.db.execute(
            "UPDATE users SET name=%s, email=%s WHERE id=%s",
            (user_data['name'], user_data['email'], user_id)
        )
        
        # 2. Invalidate cache
        cache_key = f"user:{user_id}"
        self.redis.delete(cache_key)
        
        return user_data
```

### 3. Application Server Integration
```python
from flask import Flask, jsonify
import redis

app = Flask(__name__)

# Redis connection
redis_client = redis.Redis(
    host='redis-cluster.internal',
    port=6379,
    decode_responses=True
)

@app.route('/users/<int:user_id>')
def get_user_endpoint(user_id):
    user_service = UserService(redis_client, database)
    user = user_service.get_user(user_id)
    return jsonify(user)

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user_endpoint(user_id):
    user_data = request.json
    user_service = UserService(redis_client, database)
    updated_user = user_service.update_user(user_id, user_data)
    return jsonify(updated_user)
```

## Redis Configuration for Distributed Caching

### Redis.conf Settings
```conf
# Memory management
maxmemory 2gb
maxmemory-policy allkeys-lru

# Persistence (optional for cache)
save ""  # Disable RDB snapshots for pure cache
appendonly no  # Disable AOF for pure cache

# Network
bind 0.0.0.0
port 6379
timeout 300

# Cluster settings (if using Redis Cluster)
cluster-enabled yes
cluster-config-file nodes.conf
cluster-node-timeout 5000
```

### Connection Pooling
```python
import redis.connection

# Connection pool for better performance
redis_pool = redis.ConnectionPool(
    host='redis-cluster.internal',
    port=6379,
    max_connections=20,
    decode_responses=True
)

redis_client = redis.Redis(connection_pool=redis_pool)
```

## Cache Strategies in Distributed Setup

### 1. Cache-Aside (Lazy Loading)
```python
def get_product(product_id):
    # App manages cache manually
    cached = redis.get(f"product:{product_id}")
    if cached:
        return json.loads(cached)
    
    product = db.get_product(product_id)
    redis.setex(f"product:{product_id}", 3600, json.dumps(product))
    return product
```

### 2. Write-Through
```python
def create_product(product_data):
    # Write to DB and cache simultaneously
    product = db.create_product(product_data)
    redis.setex(f"product:{product.id}", 3600, json.dumps(product))
    return product
```

### 3. Write-Behind (Async)
```python
import asyncio

async def update_product_async(product_id, product_data):
    # Update cache immediately
    redis.setex(f"product:{product_id}", 3600, json.dumps(product_data))
    
    # Update DB asynchronously
    await asyncio.sleep(0.1)  # Simulate async operation
    db.update_product(product_id, product_data)
```

## Benefits of This Architecture

1. **Reduced Database Load**: Cache absorbs read traffic
2. **Improved Response Time**: Redis responds in microseconds
3. **Scalability**: Multiple app servers share cached data
4. **High Availability**: Redis cluster provides redundancy
5. **Session Sharing**: User sessions work across any app server

## Monitoring & Metrics

```python
def get_cache_stats():
    info = redis_client.info()
    return {
        'connected_clients': info['connected_clients'],
        'used_memory': info['used_memory_human'],
        'keyspace_hits': info['keyspace_hits'],
        'keyspace_misses': info['keyspace_misses'],
        'hit_rate': info['keyspace_hits'] / (info['keyspace_hits'] + info['keyspace_misses'])
    }
```

This architecture ensures your application can scale horizontally while maintaining fast data access through distributed caching.
