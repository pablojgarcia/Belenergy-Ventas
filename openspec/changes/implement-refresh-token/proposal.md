## Why

The current JWT access token expires in 30 minutes with no way to refresh it. When the token expires, the user is forced to log in again, which is a poor UX for a sales tool used throughout the day. The frontend already has `refreshToken()` logic and stores a `refresh_token`, but the backend has no endpoint to support it.

## What Changes

**Backend:**
- Add `REFRESH_TOKEN_EXPIRE_DAYS` config (default 7)
- Add `create_refresh_token()` function that issues a long-lived JWT
- Update `POST /auth/login` to return both `access_token` and `refresh_token`
- Add `POST /auth/refresh` endpoint that validates the refresh token and issues a new access + refresh pair (token rotation)

**Frontend:**
- Add 401 interceptor in `ApiService` that catches expired token errors, calls `AuthService.refreshToken()`, and retries the original request

## Capabilities

### New
- `refresh-token-endpoint`: Backend endpoint to exchange a valid refresh token for a new access token
- `auto-refresh-interceptor`: Frontend Dio interceptor that transparently refreshes expired tokens

### Modified
- `auth-login`: Login response now includes `refresh_token`
- `token-schemas`: `Token` schema includes `refresh_token`; new `TokenRefresh` schema for the refresh request

## Impact

- Backwards-compatible: existing `access_token`-only clients continue to work (login still returns `access_token`)
- No DB changes required: tokens are stateless JWT
- Improved UX: users stay logged in across sessions up to 7 days without re-entering credentials
