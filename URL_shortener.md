# URL Shortener System Design

## 1. Requirements

### Functional
- Shorten long URLs → short URLs
- Redirect short URLs → original URLs
- Basic analytics (click count)

### Non-Functional
- **Scale**: 100M URLs/day, 10B redirects/day
- **Latency**: < 100ms redirects
- **Availability**: 99.9%

## 2. Capacity Estimation

- **Write**: 1,200 URLs/second
- **Read**: 115,000 redirects/second (100:1 ratio)
- **Storage**: 50GB/day → 91TB (5 years)

## 3. High-Level Architecture

```
Client → API Gateway → Load Balancers → Services → Cache/DB

                    API Gateway
                         |
        ┌────────────────┼────────────────┐
        |                |                |
   /shorten         /{shortCode}     /analytics
        |                |                |
        ▼                ▼                ▼
   ┌─────────┐      ┌─────────┐      ┌─────────┐
   │   LB    │      │   LB    │      │   LB    │
   └─────────┘      └─────────┘      └─────────┘
        |                |                |
        ▼                ▼                ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ Shortening  │  │  Redirect   │  │ Analytics   │
│  Service    │  │  Service    │  │  Service    │
└─────────────┘  └─────────────┘  └─────────────┘
        |                |                |
        └────────────────┼────────────────┘
                         |
                    ┌────┴────┐
                    |         |
                    ▼         ▼
               ┌─────────┐ ┌─────────┐
               │  Cache  │ │Database │
               │ (Redis) │ │(Postgres)│
               └─────────┘ └─────────┘
```

## 4. Core Components

### URL Encoding
```java
@Service
public class URLEncoder {
    private static final String BASE62 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";
    private AtomicLong counter = new AtomicLong(0);
    
    public String encode(String longUrl) {
        long id = System.currentTimeMillis() + counter.incrementAndGet();
        return base62Encode(id);
    }
    
    private String base62Encode(long num) {
        StringBuilder result = new StringBuilder();
        while (num > 0) {
            result.append(BASE62.charAt((int)(num % 62)));
            num /= 62;
        }
        return result.reverse().toString();
    }
}
```

### Database Schema
```sql
CREATE TABLE urls (
    short_code VARCHAR(10) PRIMARY KEY,
    long_url TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    click_count BIGINT DEFAULT 0
);
```

## 5. Services

### Shortening Service
```java
@RestController
public class ShorteningController {
    
    @PostMapping("/shorten")
    public ShortenResponse shorten(@RequestBody ShortenRequest request) {
        String shortCode = urlEncoder.encode(request.getLongUrl());
        urlRepository.save(new URL(shortCode, request.getLongUrl()));
        return new ShortenResponse("https://short.ly/" + shortCode);
    }
}
```

### Redirect Service
```java
@RestController
public class RedirectController {
    
    @GetMapping("/{shortCode}")
    public ResponseEntity<Void> redirect(@PathVariable String shortCode) {
        // Check cache first
        String longUrl = redisTemplate.opsForValue().get(shortCode);
        
        if (longUrl == null) {
            // Fallback to database
            URL url = urlRepository.findByShortCode(shortCode);
            longUrl = url.getLongUrl();
            
            // Cache for 1 hour
            redisTemplate.opsForValue().set(shortCode, longUrl, Duration.ofHours(1));
        }
        
        return ResponseEntity.status(302).location(URI.create(longUrl)).build();
    }
}
```

## 6. Scaling Strategy

### Horizontal Scaling
- **Shortening Service**: 3-5 instances (low write traffic)
- **Redirect Service**: 10-20 instances (high read traffic)
- **Database**: Shard by shortCode hash
- **Cache**: Redis cluster

### Caching
```java
// Multi-level caching
1. Redis (distributed) - 1 hour TTL
2. Database query optimization
3. CDN for popular URLs
```

### Database Sharding
```java
public int getShard(String shortCode) {
    return Math.abs(shortCode.hashCode()) % 4; // 4 shards
}
```

## 7. Key Design Decisions

### Why Separate Services?
- **Different scaling needs**: Redirect service needs more instances
- **Different optimization**: Shortening (write) vs Redirect (read)
- **Independent deployment**: Can update services separately

### Why Redis Cache?
- **Speed**: Sub-millisecond lookups
- **Reduces DB load**: 80% cache hit rate
- **Horizontal scaling**: Redis cluster

### Why Base62 Encoding?
- **URL-safe**: No special characters
- **Compact**: 7 characters for billions of URLs
- **Human-readable**: Easy to share

## 8. Monitoring

- **Metrics**: Response time, error rate, cache hit rate
- **Alerts**: Service health, database connections
- **Logs**: Request tracing, error tracking

This design handles 100M+ URLs daily with sub-100ms redirects while keeping the architecture simple and scalable.
