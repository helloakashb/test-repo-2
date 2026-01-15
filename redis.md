# Redis - How It Works

## What is Redis?

Redis (Remote Dictionary Server) is an in-memory data structure store used as a database, cache, and message broker. It stores data in RAM for ultra-fast access.

**Image Description:** *A diagram showing Redis as a box labeled "In-Memory Storage" sitting between "Application" and "Database", with arrows showing fast data flow.*

---

## Redis Architecture

### Single-Threaded Event Loop

```
[Client Request] → [Event Loop] → [Command Execution] → [Response]
```

**How it works:**
- Single main thread handles all operations
- Uses epoll/kqueue for I/O multiplexing
- No locks needed = no context switching overhead
- Processes commands sequentially

**Image Description:** *A circular diagram showing the event loop with incoming client connections feeding into a single processing thread, then responses going back out.*

### Memory Layout

```
Redis Memory Structure:
┌─────────────────┐
│   Key Space     │ ← Hash table of all keys
├─────────────────┤
│   Expires Dict  │ ← TTL tracking
├─────────────────┤
│   Data Objects  │ ← Actual values
├─────────────────┤
│   Overhead      │ ← Metadata, fragmentation
└─────────────────┘
```

**Image Description:** *A memory stack diagram showing different layers: key space at top, expiration dictionary, data objects, and overhead at bottom.*

---

## Data Structures

### 1. Strings
```redis
SET user:1000 "John Doe"
GET user:1000
INCR counter
```

**Internal:** Simple Dynamic Strings (SDS)
- Length prefixed
- Binary safe
- O(1) length operation

### 2. Hashes
```redis
HSET user:1000 name "John" age 30
HGET user:1000 name
HGETALL user:1000
```

**Internal:** Hash table or ziplist (for small hashes)

**Image Description:** *A hash table visualization with buckets containing key-value pairs, showing collision handling with chaining.*

### 3. Lists
```redis
LPUSH queue "task1"
RPOP queue
LRANGE queue 0 -1
```

**Internal:** Doubly linked list + ziplist optimization

**Image Description:** *A doubly-linked list with nodes containing data and pointers to previous/next nodes.*

### 4. Sets
```redis
SADD tags "redis" "cache" "nosql"
SMEMBERS tags
SINTER set1 set2
```

**Internal:** Hash table or intset (for integers)

### 5. Sorted Sets (ZSets)
```redis
ZADD leaderboard 100 "player1" 200 "player2"
ZRANGE leaderboard 0 -1 WITHSCORES
```

**Internal:** Skip list + hash table

**Image Description:** *A skip list structure with multiple levels of linked lists, showing how higher levels skip over elements for faster traversal.*

---

## Persistence Mechanisms

### 1. RDB (Redis Database Backup)

**How it works:**
```
Fork Process → Child dumps memory → Write .rdb file
```

**Image Description:** *A timeline showing the main Redis process forking, child process creating a snapshot, and writing to disk while main process continues serving requests.*

**Pros:**
- Compact single file
- Fast restart
- Good for backups

**Cons:**
- Data loss between snapshots
- Fork can be expensive

### 2. AOF (Append Only File)

**How it works:**
```
Command → Write to AOF buffer → Sync to disk
```

**Image Description:** *A flow diagram showing commands being logged to a file, with options for sync frequency (always, every second, or OS-controlled).*

**Pros:**
- Better durability
- Human readable
- Auto-rewrite compaction

**Cons:**
- Larger files
- Slower restart

### 3. Hybrid Persistence (RDB + AOF)
- RDB snapshot + AOF incremental changes
- Best of both worlds

---

## Replication

### Master-Slave Architecture

```
Master Redis ←→ Slave Redis 1
            ←→ Slave Redis 2
            ←→ Slave Redis 3
```

**Image Description:** *A star topology with master Redis in center connected to multiple slave instances, showing read/write flow.*

**Process:**
1. Slave connects to master
2. Master creates RDB snapshot
3. Master sends snapshot to slave
4. Master streams new commands to slave
5. Slave applies commands to stay in sync

### Replication Flow

```
[Write Command] → [Master] → [Replicate to Slaves] → [ACK]
```

**Image Description:** *A sequence diagram showing write command flow from client to master, then replication to slaves with acknowledgments.*

---

## Redis Cluster

### Hash Slot Distribution

```
16384 hash slots distributed across nodes:
Node A: slots 0-5460
Node B: slots 5461-10922  
Node C: slots 10923-16383
```

**Image Description:** *A circular hash ring divided into colored segments, each representing a node's responsibility for certain hash slots.*

**Key Features:**
- Automatic sharding
- No single point of failure
- Client-side routing
- Resharding support

### Cluster Topology

```
Master A ←→ Slave A
Master B ←→ Slave B  
Master C ←→ Slave C
```

**Image Description:** *A network diagram showing 3 master nodes each with a slave, all interconnected with gossip protocol lines.*

---

## Memory Management

### Eviction Policies

When memory limit reached:

1. **noeviction**: Return errors
2. **allkeys-lru**: Remove least recently used
3. **volatile-lru**: Remove LRU with TTL
4. **allkeys-random**: Remove random keys
5. **volatile-random**: Remove random keys with TTL
6. **volatile-ttl**: Remove keys with shortest TTL

**Image Description:** *A flowchart showing memory pressure triggering eviction policy selection, with different paths for each policy type.*

### Memory Optimization

```
Memory Usage Breakdown:
- Keys: 20-30%
- Values: 60-70% 
- Overhead: 10-20%
```

**Optimization techniques:**
- Use shorter key names
- Choose appropriate data structures
- Enable compression
- Set appropriate TTLs

---

## Performance Characteristics

### Throughput
```
Single Instance: 100K+ ops/sec
Pipelined: 1M+ ops/sec
Cluster: Scales linearly
```

### Latency
```
Local: < 1ms
Network: 1-5ms
Complex operations: varies
```

**Image Description:** *A performance graph showing operations per second on Y-axis and number of clients on X-axis, with different lines for various operation types.*

---

## Use Cases & Patterns

### 1. Caching
```python
def get_user(user_id):
    # Try cache first
    user = redis.get(f"user:{user_id}")
    if user:
        return json.loads(user)
    
    # Cache miss - get from DB
    user = database.get_user(user_id)
    redis.setex(f"user:{user_id}", 3600, json.dumps(user))
    return user
```

### 2. Session Store
```python
# Store session
redis.hset(f"session:{session_id}", {
    "user_id": 1000,
    "login_time": time.time(),
    "permissions": ["read", "write"]
})
redis.expire(f"session:{session_id}", 1800)  # 30 min TTL
```

### 3. Rate Limiting
```python
def is_rate_limited(user_id):
    key = f"rate_limit:{user_id}"
    current = redis.incr(key)
    if current == 1:
        redis.expire(key, 60)  # 1 minute window
    return current > 100  # Max 100 requests per minute
```

### 4. Pub/Sub Messaging
```python
# Publisher
redis.publish("notifications", json.dumps({
    "user_id": 1000,
    "message": "New message received"
}))

# Subscriber
pubsub = redis.pubsub()
pubsub.subscribe("notifications")
for message in pubsub.listen():
    process_notification(message)
```

**Image Description:** *A pub/sub diagram showing publishers sending messages to Redis channels, and multiple subscribers receiving messages from those channels.*

---

## Redis vs Other Solutions

| Feature | Redis | Memcached | Database |
|---------|-------|-----------|----------|
| Data Types | Rich | Key-Value | Rich |
| Persistence | Yes | No | Yes |
| Replication | Yes | No | Yes |
| Clustering | Yes | No | Yes |
| Memory Usage | Higher | Lower | Varies |
| Performance | Very Fast | Fastest | Slower |

---

## Best Practices

### 1. Key Naming
```
✅ user:1000:profile
✅ session:abc123
✅ cache:product:1000

❌ user_1000_profile_data_cache
❌ really:long:key:names:waste:memory
```

### 2. Memory Management
- Monitor memory usage
- Set appropriate maxmemory
- Choose right eviction policy
- Use TTLs for temporary data

### 3. Connection Pooling
```python
import redis
pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
redis_client = redis.Redis(connection_pool=pool)
```

### 4. Pipeline Operations
```python
pipe = redis.pipeline()
pipe.set("key1", "value1")
pipe.set("key2", "value2")
pipe.incr("counter")
results = pipe.execute()
```

**Image Description:** *A comparison diagram showing individual commands vs pipelined commands, illustrating reduced network round trips.*
