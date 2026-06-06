## Architecture

Both access and refresh tokens are stateless JWTs signed with the same `JWT_SECRET` but different expiry and a `type` claim to distinguish them.

```
access_token  → {"sub": "username", "type": "access",  "exp": 30min}
refresh_token → {"sub": "username", "type": "refresh", "exp": 7d}
```

### Backend

**`Backend/app/auth.py`:**
- `create_refresh_token(data, expires_delta)` — same as `create_access_token` but with `"type": "refresh"` claim and longer default expiry
- `decode_token(token)` — updated to return `token_data` including the `type` field; raises `JWTError` if token type doesn't match expected

**`Backend/app/schemas.py`:**
- `Token` schema → add `refresh_token: str`
- New `TokenRefresh` request schema with `refresh_token: str`

**`Backend/app/main.py`:**
- `POST /auth/login` → add `refresh_token` to response
- `POST /auth/refresh` → receives `{"refresh_token": "..."}`, decodes it, verifies `type == "refresh"`, issues new pair, revokes old refresh (rotation)

### Token Rotation

Each refresh invalidates the old refresh token (stateless: client simply discards it). This limits the damage if a refresh token is leaked. The client receives a new `access_token` + `refresh_token` pair on every refresh call.

### Frontend

**`Ventas/lib/services/api_service.dart`:**
- Add `onError` interceptor that checks for 401 status
- On 401, attempt to call `AuthService.refreshToken()`
- If refresh succeeds, retry the original failed request with the new token
- If refresh fails, clear tokens and redirect to login

**Flow:**
```
Request → 401 → interceptor catches →
  read refresh_token from storage →
  POST /auth/refresh →
    success → save new pair → retry original request
    failure → logout → redirect to /login
```

### Security

- Refresh tokens are JWTs, not opaque strings — no DB storage needed
- Token rotation reduces the window for replay attacks
- Same `JWT_SECRET` is used; if compromised, both token types are affected
- `type` claim prevents using a refresh token as an access token and vice versa
