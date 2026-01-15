# Large-Scale Session Management - Facebook, Amazon, Google

## The Scale Challenge
- **Facebook**: 3 billion users, 1.5 billion daily active users
- **Google**: 4 billion users across all services  
- **Amazon**: 300 million active customers
- **Challenge**: Handle millions of requests per second with sub-second response times

## How Facebook Handles Sessions

### 1. TAO (The Associations and Objects) System
Facebook doesn't use traditional sessions. Instead, they use **TAO** - a distributed data store.

**How it works:**
- User login creates an **access token** (not a session)
- Token contains user ID and permissions
- Every API call includes this token
- **No server-side session storage** - completely stateless

**Architecture:**
```
User Login → Generate Access Token → Store in Client
API Request → Include Token → Validate Token → Process Request
```

**Why this works at scale:**
- **No session storage** means no memory/database overhead
- **Stateless servers** can handle any request
- **Horizontal scaling** is easy - just add more servers

### 2. Geographic Distribution
Facebook has data centers worldwide. Here's how they handle global users:

**Data Center Strategy:**
- **Primary region** based on user's location (US users → US data center)
- **Cross-region replication** for backup
- **Edge caches** in every region for fast access

**Example Flow:**
```
User in India → Logs in → Token created in Asia data center
User travels to US → Uses same token → Works in US data center
```

### 3. Caching Strategy
Facebook uses **multiple layers of caching**:

**L1 Cache (Local):** Each server has in-memory cache
**L2 Cache (Regional):** Memcached clusters in each data center  
**L3 Cache (Global):** Cross-region replicated cache

**Cache Hit Ratio:** ~95% of requests served from cache, only 5% hit database

## How Google Handles Sessions

### 1. Service-to-Service Authentication
Google doesn't have "sessions" in traditional sense. They use **service tokens**.

**How it works:**
- User logs into Google Account → Gets **ID token**
- When accessing Gmail → Gets **Gmail-specific token**
- When accessing YouTube → Gets **YouTube-specific token**
- Each service validates its own tokens independently

**Token Structure:**
```java
// Simplified Google token
{
  "user_id": "123456789",
  "email": "user@gmail.com", 
  "service": "gmail",
  "permissions": ["read_email", "send_email"],
  "expires": 1640995200
}
```

### 2. Global Infrastructure
Google has **200+ data centers** worldwide.

**Session Replication Strategy:**
- User data replicated to **3 different regions** minimum
- **Nearest data center** serves the request
- **Automatic failover** if data center goes down

**Example:**
```
User in Japan → Request goes to Tokyo data center
Tokyo down → Automatically routes to Singapore data center
Data still available → No user impact
```

### 3. Bigtable for User Data
Google stores user information in **Bigtable** (their NoSQL database).

**Why Bigtable:**
- **Petabyte scale** - can store data for billions of users
- **Automatic sharding** - data distributed across thousands of servers
- **Strong consistency** - user sees same data everywhere

## How Amazon Handles Sessions

### 1. ElastiCache (Redis) Clusters
Amazon uses **Redis clusters** for session storage.

**Architecture:**
- **Multiple Redis clusters** in each region
- **Cross-region replication** for disaster recovery
- **Automatic failover** between clusters

**Session Storage:**
```java
// Simplified session structure
{
  "session_id": "abc123",
  "user_id": "456789",
  "cart_items": ["item1", "item2"],
  "preferences": {"theme": "dark"},
  "expires": 1640995200
}
```

### 2. Session Sharding
Amazon **shards sessions** based on user ID.

**How sharding works:**
- User ID 123 → Goes to Shard A
- User ID 456 → Goes to Shard B  
- User ID 789 → Goes to Shard C

**Benefits:**
- **Load distribution** - no single server overloaded
- **Fault isolation** - if one shard fails, others continue
- **Easy scaling** - add more shards as users grow

### 3. Multi-Region Setup
Amazon replicates sessions across regions for reliability.

**Replication Strategy:**
- **Primary region** where user is located
- **Secondary region** for backup
- **Async replication** - primary writes immediately, secondary updates later

## Common Patterns Across All Three

### 1. Stateless Architecture
**Key Principle:** Servers don't store user state

**How it works:**
- All user information in **tokens** or **external storage**
- Any server can handle any request
- Easy to **scale horizontally**

### 2. Caching Everywhere
**Multi-level caching** to reduce database load:

```
Request → L1 Cache (memory) → L2 Cache (Redis) → L3 Cache (database)
          ↓ 50ms              ↓ 1-5ms            ↓ 10-100ms
```

### 3. Geographic Distribution
**Global presence** for low latency:
- Data centers in every major region
- User data replicated across regions
- Requests routed to nearest data center

### 4. Fault Tolerance
**Multiple backups** and **automatic failover**:
- If primary data center fails → Route to backup
- If cache fails → Fall back to database
- If token service fails → Use cached tokens

## Interview-Style Architecture Diagram

```
                    Load Balancer
                         |
        ┌────────────────┼────────────────┐
        │                │                │
   Server A         Server B         Server C
        │                │                │
        └────────────────┼────────────────┘
                         │
                   Redis Cluster
                    (Session Store)
                         │
                    Database
                  (User Data)
```

## Key Metrics These Companies Track

### Performance Metrics:
- **Response time:** < 100ms for 95% of requests
- **Cache hit ratio:** > 95%
- **Availability:** 99.99% uptime

### Scale Metrics:
- **Requests per second:** Millions
- **Concurrent users:** Hundreds of millions
- **Data size:** Petabytes

## System Design Interview Questions

**Q: How would you design session management for 1 billion users?**

**Answer Framework:**
1. **Use stateless architecture** - no server-side sessions
2. **Implement token-based auth** - JWT or similar
3. **Add multi-level caching** - memory, Redis, database
4. **Shard data by user ID** - distribute load
5. **Replicate across regions** - for global users
6. **Monitor and alert** - track performance metrics

**Q: What happens when Redis goes down?**

**Answer:**
1. **Circuit breaker** detects failure
2. **Fallback to database** for session data
3. **Auto-failover** to backup Redis cluster
4. **Graceful degradation** - core features still work

**Q: How do you handle user sessions across different services?**

**Answer:**
1. **Single Sign-On (SSO)** - one login for all services
2. **Service-specific tokens** - each service gets its own token
3. **Token exchange** - convert general token to service token
4. **Centralized auth service** - validates all tokens

## Key Takeaways for Interviews

1. **Scale requires stateless design** - no server-side sessions
2. **Caching is critical** - multiple layers reduce database load  
3. **Geographic distribution** - data centers worldwide
4. **Fault tolerance** - multiple backups and failover
5. **Monitoring** - track performance and scale metrics
6. **Sharding** - distribute data across multiple servers

**Remember:** These companies prioritize **availability** and **performance** over perfect consistency. They use **eventual consistency** and **graceful degradation** to handle failures.
