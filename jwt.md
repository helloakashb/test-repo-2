# JWT-Based Authentication & State Management

## What is JWT?
**JSON Web Token** - A compact, URL-safe token that contains user information and claims.

## How JWT Works - Step by Step

### 1. User Login Process in more details 
```
User → Server: POST /login {username, password}
Server: Validates credentials
Server: Creates JWT token
Server → User: Returns JWT token
User: Stores JWT (localStorage/cookie)
```

### 2. JWT Creation Process
```java
// Server creates JWT when user logs in
public String createJWT(User user) {
    // Step 1: Create Header
    Map<String, Object> header = new HashMap<>();
    header.put("alg", "HS256");  // Algorithm
    header.put("typ", "JWT");    // Type
    
    // Step 2: Create Payload (Claims)
    Map<String, Object> payload = new HashMap<>();
    payload.put("sub", user.getId());           // Subject
    payload.put("name", user.getName());        // User name
    payload.put("role", user.getRole());        // User role
    payload.put("iat", System.currentTimeMillis() / 1000);  // Issued at
    payload.put("exp", (System.currentTimeMillis() / 1000) + 3600); // Expires in 1 hour
    
    // Step 3: Create Signature
    String headerEncoded = base64UrlEncode(header);
    String payloadEncoded = base64UrlEncode(payload);
    String signature = HMACSHA256(headerEncoded + "." + payloadEncoded, SECRET_KEY);
    
    // Step 4: Combine all parts
    return headerEncoded + "." + payloadEncoded + "." + signature;
}
```

### 3. JWT Structure Breakdown
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c

Part 1: Header (Base64 encoded)
Part 2: Payload (Base64 encoded)  
Part 3: Signature (HMAC SHA256)
```

#### Header (Decoded):
```json
{
  "alg": "HS256",    // Algorithm used for signing
  "typ": "JWT"       // Token type
}
```

#### Payload/Claims (Decoded):
```json
{
  "sub": "1234567890",    // Subject (user ID)
  "name": "John Doe",     // User name
  "role": "admin",        // User role
  "iat": 1516239022,      // Issued at (timestamp)
  "exp": 1516242622       // Expires at (timestamp)
}
```

#### Signature:
```
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  SECRET_KEY
)
```

### 4. API Request with JWT
```
User → Server: GET /api/profile
Headers: Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Server receives request:
1. Extracts JWT from Authorization header
2. Splits JWT into header.payload.signature
3. Validates signature using SECRET_KEY
4. Checks expiration time
5. Extracts user info from payload
6. Processes request with user context
```

### 5. JWT Validation Process
```java
public boolean validateJWT(String token) {
    try {
        // Step 1: Split token into parts
        String[] parts = token.split("\\.");
        if (parts.length != 3) return false;
        
        String headerEncoded = parts[0];
        String payloadEncoded = parts[1];
        String signatureReceived = parts[2];
        
        // Step 2: Recreate signature with server's secret
        String expectedSignature = HMACSHA256(
            headerEncoded + "." + payloadEncoded, 
            SECRET_KEY
        );
        
        // Step 3: Compare signatures
        if (!expectedSignature.equals(signatureReceived)) {
            return false; // Token tampered with
        }
        
        // Step 4: Check expiration
        Map<String, Object> payload = decodePayload(payloadEncoded);
        long exp = (Long) payload.get("exp");
        long now = System.currentTimeMillis() / 1000;
        
        if (now > exp) {
            return false; // Token expired
        }
        
        return true; // Valid token
        
    } catch (Exception e) {
        return false; // Invalid token format
    }
}
```

## Why JWT is Stateless

### Traditional Session-Based Authentication:
```
1. User logs in → Server creates session → Stores session in memory/database
2. Server returns session ID to client
3. Client sends session ID with each request
4. Server looks up session in storage to get user info
```

### JWT-Based Authentication:
```
1. User logs in → Server creates JWT with user info inside
2. Server returns JWT to client (no server storage needed)
3. Client sends JWT with each request
4. Server validates JWT signature and extracts user info directly
```

**Key Difference**: JWT contains all user information, so server doesn't need to store or lookup anything!

### Complete Flow Example

#### Login Flow:
```java
@PostMapping("/login")
public ResponseEntity<?> login(@RequestBody LoginRequest request) {
    // 1. Validate credentials
    User user = userService.authenticate(request.getUsername(), request.getPassword());
    
    if (user == null) {
        return ResponseEntity.status(401).body("Invalid credentials");
    }
    
    // 2. Create JWT with user information
    String jwt = jwtService.generateToken(user);
    
    // 3. Return JWT to client (no server-side storage)
    return ResponseEntity.ok(new JwtResponse(jwt));
}
```

#### API Request Flow:
```java
@GetMapping("/profile")
public ResponseEntity<User> getProfile(HttpServletRequest request) {
    // 1. Extract JWT from Authorization header
    String authHeader = request.getHeader("Authorization");
    String jwt = authHeader.substring(7); // Remove "Bearer "
    
    // 2. Validate JWT signature and expiration
    if (!jwtService.isTokenValid(jwt)) {
        return ResponseEntity.status(401).build();
    }
    
    // 3. Extract user info directly from JWT (no database lookup needed!)
    Claims claims = jwtService.extractClaims(jwt);
    Long userId = claims.get("userId", Long.class);
    String username = claims.getSubject();
    String role = claims.get("role", String.class);
    
    // 4. Use extracted info to process request
    User user = new User(userId, username, role);
    return ResponseEntity.ok(user);
}
```

## How JWT Ensures Security

### 1. Signature Verification
```java
// When JWT is created:
String signature = HMACSHA256(header + "." + payload, SERVER_SECRET);

// When JWT is validated:
String receivedSignature = jwt.split("\\.")[2];
String expectedSignature = HMACSHA256(header + "." + payload, SERVER_SECRET);

if (!receivedSignature.equals(expectedSignature)) {
    throw new SecurityException("JWT signature invalid - token was tampered with");
}
```

**Why this works:**
- Only server knows the SECRET_KEY
- If someone changes the payload, signature won't match
- Attacker can't create valid signature without the secret

### 2. Expiration Check
```java
public boolean isTokenExpired(String jwt) {
    Claims claims = extractClaims(jwt);
    Date expiration = claims.getExpiration();
    return expiration.before(new Date()); // Check if expired
}
```

### 3. Complete Validation Process
```java
public boolean validateToken(String jwt) {
    try {
        // Parse and validate in one step
        Claims claims = Jwts.parser()
            .setSigningKey(SECRET_KEY)      // Validates signature
            .parseClaimsJws(jwt)            // Validates format
            .getBody();                     // Extracts claims
        
        // JWT library automatically checks:
        // 1. Signature validity
        // 2. Token format
        // 3. Expiration time
        
        return true;
    } catch (ExpiredJwtException e) {
        System.out.println("Token expired");
        return false;
    } catch (SignatureException e) {
        System.out.println("Invalid signature");
        return false;
    } catch (Exception e) {
        System.out.println("Invalid token");
        return false;
    }
}
```

## Implementation Example

### 1. Login & JWT Creation
```java
@RestController
public class AuthController {
    
    @Autowired
    private JwtService jwtService;
    
    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody LoginRequest request) {
        // Validate user credentials
        User user = userService.authenticate(request.getUsername(), request.getPassword());
        
        if (user != null) {
            // Create JWT token
            String token = jwtService.generateToken(user);
            
            return ResponseEntity.ok(new JwtResponse(token));
        }
        
        return ResponseEntity.status(401).body("Invalid credentials");
    }
}

class JwtResponse {
    private String token;
    private String type = "Bearer";
    
    public JwtResponse(String token) {
        this.token = token;
    }
    // getters
}
```

### 2. JWT Service
```java
@Service
public class JwtService {
    
    private String secret = "mySecretKey";
    private int expiration = 86400; // 24 hours
    
    public String generateToken(User user) {
        Map<String, Object> claims = new HashMap<>();
        claims.put("userId", user.getId());
        claims.put("username", user.getUsername());
        claims.put("role", user.getRole());
        
        return Jwts.builder()
                .setClaims(claims)
                .setSubject(user.getUsername())
                .setIssuedAt(new Date())
                .setExpiration(new Date(System.currentTimeMillis() + expiration * 1000))
                .signWith(SignatureAlgorithm.HS256, secret)
                .compact();
    }
    
    public Claims extractClaims(String token) {
        return Jwts.parser()
                .setSigningKey(secret)
                .parseClaimsJws(token)
                .getBody();
    }
    
    public boolean isTokenValid(String token) {
        try {
            Claims claims = extractClaims(token);
            return !claims.getExpiration().before(new Date());
        } catch (Exception e) {
            return false;
        }
    }
}
```

### 3. JWT Filter/Interceptor
```java
@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {
    
    @Autowired
    private JwtService jwtService;
    
    @Override
    protected void doFilterInternal(HttpServletRequest request, 
                                  HttpServletResponse response, 
                                  FilterChain filterChain) throws ServletException, IOException {
        
        String authHeader = request.getHeader("Authorization");
        
        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            String token = authHeader.substring(7); // Remove "Bearer "
            
            if (jwtService.isTokenValid(token)) {
                // Extract user info from token
                Claims claims = jwtService.extractClaims(token);
                String username = claims.getSubject();
                String role = (String) claims.get("role");
                
                // Set user context (no database call needed!)
                UserContext.setCurrentUser(username, role);
            }
        }
        
        filterChain.doFilter(request, response);
    }
}
```

### 4. Protected API Endpoint
```java
@RestController
public class UserController {
    
    @GetMapping("/profile")
    public ResponseEntity<User> getProfile(HttpServletRequest request) {
        // Extract user info from JWT (stateless!)
        String authHeader = request.getHeader("Authorization");
        String token = authHeader.substring(7);
        
        Claims claims = jwtService.extractClaims(token);
        Long userId = claims.get("userId", Long.class);
        
        User user = userService.findById(userId);
        return ResponseEntity.ok(user);
    }
    
    @GetMapping("/admin/users")
    public ResponseEntity<List<User>> getAllUsers(HttpServletRequest request) {
        // Check role from JWT
        String token = extractToken(request);
        Claims claims = jwtService.extractClaims(token);
        String role = (String) claims.get("role");
        
        if (!"admin".equals(role)) {
            return ResponseEntity.status(403).build();
        }
        
        return ResponseEntity.ok(userService.getAllUsers());
    }
}
```

## Frontend Integration

### JavaScript/React Example
```javascript
// Store JWT after login
const login = async (username, password) => {
    const response = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    });
    
    const data = await response.json();
    
    // Store JWT in localStorage
    localStorage.setItem('token', data.token);
};

// Send JWT with API requests
const fetchUserProfile = async () => {
    const token = localStorage.getItem('token');
    
    const response = await fetch('/api/profile', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    
    return response.json();
};

// Axios interceptor for automatic token inclusion
axios.interceptors.request.use(config => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});
```

## State Management with JWT

### Storing User State in JWT
```java
public String generateTokenWithState(User user, ShoppingCart cart) {
    Map<String, Object> claims = new HashMap<>();
    claims.put("userId", user.getId());
    claims.put("username", user.getUsername());
    claims.put("role", user.getRole());
    
    // Store application state in JWT
    claims.put("cartItems", cart.getItems().size());
    claims.put("preferences", user.getPreferences());
    claims.put("lastLogin", user.getLastLogin());
    
    return createToken(claims);
}
```

### Reading State from JWT
```java
@GetMapping("/cart/count")
public ResponseEntity<Integer> getCartCount(HttpServletRequest request) {
    String token = extractToken(request);
    Claims claims = jwtService.extractClaims(token);
    
    // Get cart count from JWT (no database call!)
    Integer cartItems = claims.get("cartItems", Integer.class);
    
    return ResponseEntity.ok(cartItems);
}
```

## JWT vs Session Comparison

| JWT | Session |
|-----|---------|
| **Stateless** - No server storage | **Stateful** - Server stores session |
| **Scalable** - Works across servers | **Sticky sessions** or shared storage needed |
| **Self-contained** - All info in token | **Lightweight** - Only session ID stored |
| **Cannot revoke** - Valid until expiry | **Can revoke** - Delete from server |
| **Larger size** - Contains user data | **Smaller** - Just session ID |
| **No database lookup** - Fast | **Database lookup** - Slower |

## Security Considerations

### 1. Token Storage
```javascript
// ❌ Bad - XSS vulnerable
localStorage.setItem('token', jwt);

// ✅ Better - HttpOnly cookie
// Set by server, not accessible via JavaScript
response.cookie('token', jwt, { 
    httpOnly: true, 
    secure: true, 
    sameSite: 'strict' 
});
```

## Handling JWT Expiration

### Problem with JWT Expiration
- JWT tokens have expiration time for security
- Once expired, user gets logged out
- User has to login again (bad UX)
- **Solution**: Refresh Token Pattern

### 1. Refresh Token Pattern

#### Token Pair Structure:
```java
public class TokenPair {
    private String accessToken;   // Short-lived (15 minutes)
    private String refreshToken;  // Long-lived (7 days)
    
    // getters and setters
}
```

#### Login - Generate Token Pair:
```java
@PostMapping("/login")
public ResponseEntity<TokenPair> login(@RequestBody LoginRequest request) {
    User user = userService.authenticate(request.getUsername(), request.getPassword());
    
    if (user != null) {
        // Generate both tokens
        String accessToken = jwtService.generateAccessToken(user);   // 15 min
        String refreshToken = jwtService.generateRefreshToken(user); // 7 days
        
        // Store refresh token in database
        refreshTokenService.save(new RefreshToken(refreshToken, user.getId()));
        
        return ResponseEntity.ok(new TokenPair(accessToken, refreshToken));
    }
    
    return ResponseEntity.status(401).build();
}
```

#### Token Generation:
```java
@Service
public class JwtService {
    
    public String generateAccessToken(User user) {
        return Jwts.builder()
            .setSubject(user.getUsername())
            .claim("userId", user.getId())
            .claim("role", user.getRole())
            .setIssuedAt(new Date())
            .setExpiration(new Date(System.currentTimeMillis() + 15 * 60 * 1000)) // 15 minutes
            .signWith(SignatureAlgorithm.HS256, ACCESS_TOKEN_SECRET)
            .compact();
    }
    
    public String generateRefreshToken(User user) {
        return Jwts.builder()
            .setSubject(user.getUsername())
            .claim("userId", user.getId())
            .claim("tokenType", "refresh")
            .setIssuedAt(new Date())
            .setExpiration(new Date(System.currentTimeMillis() + 7 * 24 * 60 * 60 * 1000)) // 7 days
            .signWith(SignatureAlgorithm.HS256, REFRESH_TOKEN_SECRET)
            .compact();
    }
}
```

### 2. Refresh Token Endpoint

```java
@PostMapping("/refresh")
public ResponseEntity<TokenPair> refreshToken(@RequestBody RefreshRequest request) {
    String refreshToken = request.getRefreshToken();
    
    try {
        // 1. Validate refresh token
        Claims claims = Jwts.parser()
            .setSigningKey(REFRESH_TOKEN_SECRET)
            .parseClaimsJws(refreshToken)
            .getBody();
        
        // 2. Check if refresh token exists in database
        if (!refreshTokenService.exists(refreshToken)) {
            return ResponseEntity.status(401).body("Invalid refresh token");
        }
        
        // 3. Get user and generate new tokens
        Long userId = claims.get("userId", Long.class);
        User user = userService.findById(userId);
        
        String newAccessToken = jwtService.generateAccessToken(user);
        String newRefreshToken = jwtService.generateRefreshToken(user);
        
        // 4. Replace old refresh token with new one
        refreshTokenService.delete(refreshToken);
        refreshTokenService.save(new RefreshToken(newRefreshToken, userId));
        
        return ResponseEntity.ok(new TokenPair(newAccessToken, newRefreshToken));
        
    } catch (ExpiredJwtException e) {
        // Refresh token expired - user must login again
        return ResponseEntity.status(401).body("Refresh token expired");
    } catch (Exception e) {
        return ResponseEntity.status(401).body("Invalid refresh token");
    }
}
```

### 3. Frontend Handling

#### Automatic Token Refresh:
```javascript
class AuthService {
    constructor() {
        this.accessToken = localStorage.getItem('accessToken');
        this.refreshToken = localStorage.getItem('refreshToken');
    }
    
    async makeApiCall(url, options = {}) {
        // Add access token to request
        options.headers = {
            ...options.headers,
            'Authorization': `Bearer ${this.accessToken}`
        };
        
        let response = await fetch(url, options);
        
        // If access token expired (401), try to refresh
        if (response.status === 401) {
            const refreshed = await this.refreshAccessToken();
            
            if (refreshed) {
                // Retry original request with new token
                options.headers['Authorization'] = `Bearer ${this.accessToken}`;
                response = await fetch(url, options);
            } else {
                // Refresh failed - redirect to login
                this.logout();
                window.location.href = '/login';
            }
        }
        
        return response;
    }
    
    async refreshAccessToken() {
        try {
            const response = await fetch('/api/refresh', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refreshToken: this.refreshToken })
            });
            
            if (response.ok) {
                const tokens = await response.json();
                
                // Update stored tokens
                this.accessToken = tokens.accessToken;
                this.refreshToken = tokens.refreshToken;
                
                localStorage.setItem('accessToken', tokens.accessToken);
                localStorage.setItem('refreshToken', tokens.refreshToken);
                
                return true;
            }
            
            return false;
        } catch (error) {
            return false;
        }
    }
    
    logout() {
        this.accessToken = null;
        this.refreshToken = null;
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
    }
}

// Usage
const authService = new AuthService();

// All API calls automatically handle token refresh
authService.makeApiCall('/api/profile')
    .then(response => response.json())
    .then(data => console.log(data));
```

#### Axios Interceptor for Auto-Refresh:
```javascript
// Request interceptor - add token
axios.interceptors.request.use(config => {
    const token = localStorage.getItem('accessToken');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Response interceptor - handle expiration
axios.interceptors.response.use(
    response => response,
    async error => {
        const originalRequest = error.config;
        
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;
            
            try {
                // Try to refresh token
                const refreshToken = localStorage.getItem('refreshToken');
                const response = await axios.post('/api/refresh', { refreshToken });
                
                const { accessToken, refreshToken: newRefreshToken } = response.data;
                
                // Update stored tokens
                localStorage.setItem('accessToken', accessToken);
                localStorage.setItem('refreshToken', newRefreshToken);
                
                // Retry original request
                originalRequest.headers.Authorization = `Bearer ${accessToken}`;
                return axios(originalRequest);
                
            } catch (refreshError) {
                // Refresh failed - logout
                localStorage.removeItem('accessToken');
                localStorage.removeItem('refreshToken');
                window.location.href = '/login';
            }
        }
        
        return Promise.reject(error);
    }
);
```

### 4. Alternative Approaches

#### Silent Refresh (Background):
```javascript
class TokenManager {
    constructor() {
        this.startSilentRefresh();
    }
    
    startSilentRefresh() {
        // Refresh token 5 minutes before expiry
        const refreshInterval = (15 - 5) * 60 * 1000; // 10 minutes
        
        setInterval(async () => {
            await this.silentRefresh();
        }, refreshInterval);
    }
    
    async silentRefresh() {
        const refreshToken = localStorage.getItem('refreshToken');
        if (!refreshToken) return;
        
        try {
            const response = await fetch('/api/refresh', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refreshToken })
            });
            
            if (response.ok) {
                const tokens = await response.json();
                localStorage.setItem('accessToken', tokens.accessToken);
                localStorage.setItem('refreshToken', tokens.refreshToken);
            }
        } catch (error) {
            console.log('Silent refresh failed');
        }
    }
}
```

#### Sliding Session (Extend on Activity):
```java
@PostMapping("/extend-session")
public ResponseEntity<TokenPair> extendSession(@RequestHeader("Authorization") String authHeader) {
    String token = authHeader.substring(7);
    
    if (jwtService.isTokenValid(token)) {
        Claims claims = jwtService.extractClaims(token);
        Long userId = claims.get("userId", Long.class);
        User user = userService.findById(userId);
        
        // Generate new tokens with extended expiry
        String newAccessToken = jwtService.generateAccessToken(user);
        String newRefreshToken = jwtService.generateRefreshToken(user);
        
        return ResponseEntity.ok(new TokenPair(newAccessToken, newRefreshToken));
    }
    
    return ResponseEntity.status(401).build();
}
```

### 5. Security Considerations

#### Refresh Token Storage:
```java
@Entity
public class RefreshToken {
    @Id
    private String token;
    private Long userId;
    private LocalDateTime createdAt;
    private LocalDateTime expiresAt;
    private boolean revoked;
    
    // getters and setters
}

@Service
public class RefreshTokenService {
    
    public void revokeAllUserTokens(Long userId) {
        // Revoke all refresh tokens for user (logout from all devices)
        refreshTokenRepository.revokeByUserId(userId);
    }
    
    public void revokeToken(String token) {
        // Revoke specific token
        refreshTokenRepository.revokeToken(token);
    }
}
```

### Summary: JWT Expiration Strategies

| Strategy | Pros | Cons | Use Case |
|----------|------|------|----------|
| **Refresh Token** | Secure, good UX | Complex implementation | Production apps |
| **Silent Refresh** | Seamless UX | Background requests | Single-page apps |
| **Sliding Session** | Simple | Less secure | Internal tools |
| **Short-lived only** | Very secure | Poor UX | High-security apps |

**Best Practice**: Use refresh token pattern with short-lived access tokens (15 min) and longer-lived refresh tokens (7 days).

### 3. Sensitive Data
```java
// ❌ Don't store sensitive data in JWT
claims.put("password", user.getPassword());
claims.put("creditCard", user.getCreditCard());

// ✅ Store only necessary, non-sensitive data
claims.put("userId", user.getId());
claims.put("role", user.getRole());
claims.put("permissions", user.getPermissions());
```

## Best Practices

1. **Keep JWT small** - Only essential claims
2. **Use HTTPS** - Prevent token interception
3. **Set expiration** - Short-lived tokens
4. **Validate on every request** - Check signature and expiry
5. **Use refresh tokens** - For long-term sessions
6. **Store securely** - HttpOnly cookies preferred
7. **Handle token expiry** - Graceful refresh mechanism

## Common Interview Questions

**Q: How does JWT achieve stateless authentication?**
A: JWT contains all user information, so server doesn't need to store session data

**Q: What happens if JWT is compromised?**
A: Token remains valid until expiry. Use short expiration times and refresh tokens

**Q: JWT vs Session - when to use which?**
A: JWT for stateless APIs, microservices. Sessions for traditional web apps with server-side rendering

**Q: How do you handle JWT expiration?**
A: Use refresh tokens to get new access tokens without re-login
