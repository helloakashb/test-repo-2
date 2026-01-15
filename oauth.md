# OAuth 2.0 - Behind the Scenes

## What is OAuth 2.0?

OAuth 2.0 is an authorization framework that allows third-party applications to access user resources without exposing credentials. It's the "Login with Google/Facebook" you see everywhere.

## Key Players

- **Resource Owner**: The user who owns the data
- **Client**: The app requesting access (e.g., a mobile app)
- **Authorization Server**: Issues tokens (e.g., Google's auth server)
- **Resource Server**: Hosts the protected data (e.g., Google Drive API)

## How It Works

### 1. Authorization Request
```
User clicks "Login with Google" → Client redirects to Authorization Server
```

### 2. User Authorization
```
User logs in and grants permissions → Authorization Server shows consent screen
```

### 3. Authorization Grant
```
Authorization Server redirects back with authorization code
URL: https://client.com/callback?code=ABC123&state=xyz
```

### 4. Access Token Request
```
POST /token
{
  "grant_type": "authorization_code",
  "code": "ABC123",
  "client_id": "your_client_id",
  "client_secret": "your_secret",
  "redirect_uri": "https://client.com/callback"
}
```

### 5. Access Token Response
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "1//04...",
  "scope": "read write"
}
```

### 6. Resource Access
```
GET /api/user/profile
Authorization: Bearer eyJhbGciOiJSUzI1NiIs...
```

## Grant Types

### Authorization Code Flow
- Most secure for web apps
- Uses authorization code + client secret

### Implicit Flow
- For SPAs (deprecated)
- Direct token in URL fragment

### Client Credentials
- Machine-to-machine
- No user involved

### PKCE (Proof Key for Code Exchange)
- Enhanced security for mobile/SPA
- Uses code verifier/challenge

## Security Features

- **Scopes**: Limit access permissions
- **State Parameter**: Prevents CSRF attacks
- **Short-lived Tokens**: Reduce exposure risk
- **Refresh Tokens**: Get new access tokens
- **HTTPS Only**: All communication encrypted

## Detailed Example: Login to abc.com with Facebook

### Step 1: User Clicks "Login with Facebook"
```
User visits: https://abc.com/login
Clicks: "Login with Facebook" button
```

### Step 2: abc.com Redirects to Facebook
```
abc.com redirects browser to:
https://www.facebook.com/v18.0/dialog/oauth?
  client_id=123456789012345
  &redirect_uri=https://abc.com/auth/facebook/callback
  &scope=email,public_profile
  &response_type=code
  &state=random_csrf_token_xyz123
```

**What's happening:**
- `client_id`: abc.com's registered Facebook app ID
- `redirect_uri`: Where Facebook sends user back
- `scope`: What permissions abc.com wants (email, profile)
- `state`: Security token to prevent CSRF attacks

### Step 3: Facebook Shows Login/Consent
```
If user not logged in → Facebook login page
If logged in → Facebook shows consent screen:
"abc.com wants to access your public profile and email address"
[Cancel] [Continue as John]
```

### Step 4: User Grants Permission
```
User clicks "Continue as John"
Facebook validates the request and generates authorization code
```

### Step 5: Facebook Redirects Back to abc.com
```
Facebook redirects browser to:
https://abc.com/auth/facebook/callback?
  code=AQBx7g2F8h9k3m...
  &state=random_csrf_token_xyz123
```

**abc.com validates:**
- State parameter matches (CSRF protection)
- Authorization code is present

### Step 6: abc.com Exchanges Code for Token (Backend)
```
POST https://graph.facebook.com/v18.0/oauth/access_token
Content-Type: application/x-www-form-urlencoded

client_id=123456789012345
&client_secret=abc123secret456def
&redirect_uri=https://abc.com/auth/facebook/callback
&code=AQBx7g2F8h9k3m...
```

**Facebook responds:**
```json
{
  "access_token": "EAABwzLixnjYBAO...",
  "token_type": "bearer",
  "expires_in": 5183944
}
```

### Step 7: abc.com Gets User Info
```
GET https://graph.facebook.com/me?fields=id,name,email
Authorization: Bearer EAABwzLixnjYBAO...
```

**Facebook API responds:**
```json
{
  "id": "10157142905014711",
  "name": "John Doe",
  "email": "john.doe@email.com"
}
```

### Step 8: abc.com Creates/Logs In User
```
abc.com checks if user exists by Facebook ID or email
If exists → Log them in
If new → Create account with Facebook data
Set session cookie and redirect to dashboard
```

## Security Deep Dive

### Why Authorization Code Flow?
```
❌ Direct Token: facebook.com → abc.com (visible in URL)
✅ Code Exchange: facebook.com → abc.com → facebook.com (server-to-server)
```

### State Parameter Protection
```
Without state:
1. Attacker gets authorization code
2. Tricks user to visit abc.com/callback?code=STOLEN_CODE
3. User gets logged into attacker's account

With state:
1. abc.com generates random state: xyz123
2. Facebook returns same state: xyz123  
3. abc.com validates state matches → Safe
```

### PKCE Enhancement (for SPAs/Mobile)
```
1. Generate code_verifier: random 43-128 chars
2. Create code_challenge: SHA256(code_verifier)
3. Send challenge in auth request
4. Send verifier in token exchange
5. Facebook validates: SHA256(verifier) == challenge
```

## Why OAuth 2.0?

- **No password sharing**: Apps never see user passwords
- **Limited access**: Scoped permissions
- **Revocable**: Users can revoke access anytime
- **Standardized**: Works across platforms
