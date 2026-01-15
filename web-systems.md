# State Management in Web Applications - System Design

## What is State?
State is data that changes over time and affects application behavior:
- User login status
- Shopping cart contents
- Form data
- Application configuration

## Types of State

### 1. Client-Side State
**Stored in browser/frontend**

```javascript
// Browser Local Storage
localStorage.setItem('user', JSON.stringify({id: 123, name: 'John'}));

// React Component State
const [cartItems, setCartItems] = useState([]);

// Session Storage
sessionStorage.setItem('tempData', 'value');
```

**Pros**: Fast access, reduces server load
**Cons**: Limited storage, security risks, lost on device change

### 2. Server-Side State
**Stored on backend servers**

```java
// HTTP Session
@Controller
public class UserController {
    @PostMapping("/login")
    public String login(HttpSession session) {
        session.setAttribute("userId", 123);
        return "dashboard";
    }
}

// In-Memory Cache
@Service
public class UserService {
    private Map<String, User> userCache = new HashMap<>();
    
    public User getUser(String id) {
        return userCache.get(id);
    }
}
```

**Pros**: Secure, persistent, centralized
**Cons**: Server load, network latency

### 3. Database State
**Persistent storage**

```sql
-- User session table
CREATE TABLE user_sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    user_id INT,
    data TEXT,
    expires_at TIMESTAMP
);

-- Shopping cart table
CREATE TABLE cart_items (
    user_id INT,
    product_id INT,
    quantity INT,
    created_at TIMESTAMP
);
```

**Pros**: Persistent, scalable, reliable
**Cons**: Slower access, database load

## State Management Patterns

### 1. Stateless Architecture
**No server-side state, everything in client/database**

```java
@RestController
public class OrderController {
    
    @PostMapping("/orders")
    public Order createOrder(@RequestBody OrderRequest request, 
                           @RequestHeader("Authorization") String token) {
        // Extract user from JWT token (stateless)
        User user = jwtService.getUserFromToken(token);
        
        // Create order (save to database)
        return orderService.create(user.getId(), request);
    }
}
```

**Benefits**: Scalable, no session stickiness needed
**Use case**: REST APIs, microservices

### 2. Session-Based State
**Server maintains user sessions**

```java
@Controller
public class ShoppingController {
    
    @PostMapping("/cart/add")
    public String addToCart(@RequestParam String productId, 
                          HttpSession session) {
        // Get cart from session
        List<String> cart = (List<String>) session.getAttribute("cart");
        if (cart == null) {
            cart = new ArrayList<>();
        }
        
        cart.add(productId);
        session.setAttribute("cart", cart);
        
        return "redirect:/cart";
    }
}
```

**Benefits**: Simple, secure
**Drawbacks**: Server memory usage, sticky sessions

### 3. Token-Based State (JWT)
**State encoded in tokens**

```java
// JWT Token contains user info
{
  "userId": 123,
  "role": "admin",
  "exp": 1640995200,
  "cart": ["item1", "item2"]
}

@RestController
public class ApiController {
    
    @GetMapping("/profile")
    public User getProfile(@RequestHeader("Authorization") String token) {
        // Decode JWT to get user info (stateless)
        Claims claims = jwtService.parseToken(token);
        return userService.getUser(claims.get("userId"));
    }
}
```

**Benefits**: Stateless, scalable, cross-domain
**Drawbacks**: Token size, security concerns

## Distributed State Management

### 1. Sticky Sessions
**Route user to same server**

```
Load Balancer Configuration:
User A → Always routes to Server 1
User B → Always routes to Server 2
User C → Always routes to Server 3
```

**Pros**: Simple session management
**Cons**: Uneven load, server failure issues

### 2. Shared Session Store
**External session storage**

```java
@Configuration
public class RedisConfig {
    
    @Bean
    public RedisTemplate<String, Object> redisTemplate() {
        // Configure Redis for session storage
        return template;
    }
}

// Session stored in Redis
@Controller
public class UserController {
    
    @Autowired
    private RedisTemplate<String, Object> redis;
    
    @PostMapping("/login")
    public String login(@RequestParam String username) {
        String sessionId = UUID.randomUUID().toString();
        
        // Store session in Redis (shared across servers)
        redis.opsForValue().set("session:" + sessionId, 
                               new UserSession(username), 
                               Duration.ofHours(2));
        
        return "redirect:/dashboard";
    }
}
```

**Benefits**: Scalable, fault-tolerant
**Use case**: Multi-server applications

### 3. Database Sessions
**Store sessions in database**

```java
@Entity
public class UserSession {
    @Id
    private String sessionId;
    private Long userId;
    private String data;
    private LocalDateTime expiresAt;
}

@Service
public class SessionService {
    
    public void saveSession(String sessionId, UserSession session) {
        sessionRepository.save(session);
    }
    
    public UserSession getSession(String sessionId) {
        return sessionRepository.findById(sessionId).orElse(null);
    }
}
```

## State Management Strategies by Scale

### Small Applications
- **Client-side state**: localStorage, sessionStorage
- **Simple sessions**: HTTP sessions
- **Database**: Direct database queries

### Medium Applications  
- **JWT tokens**: For API authentication
- **Redis cache**: For frequently accessed data
- **Database sessions**: For persistent state

### Large Applications
- **Microservices**: Each service manages own state
- **Event sourcing**: State from event history
- **CQRS**: Separate read/write state models
- **Distributed cache**: Redis Cluster, Hazelcast

## Best Practices

1. **Keep state minimal**: Only store what's necessary
2. **Use appropriate storage**: Match storage to data lifecycle
3. **Handle expiration**: Set TTL for temporary state
4. **Security**: Encrypt sensitive state data
5. **Consistency**: Choose consistency model based on requirements

## Common Interview Questions

**Q: How do you handle user sessions in a load-balanced environment?**
A: Use shared session store (Redis) or stateless tokens (JWT)

**Q: What's the difference between stateful and stateless architecture?**
A: Stateful stores state on server, stateless stores state in client/database

**Q: How do you scale state management?**
A: External session stores, caching, database partitioning, microservices
