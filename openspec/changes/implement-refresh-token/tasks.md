## Backend

- [x] 1.1 Add `REFRESH_TOKEN_EXPIRE_DAYS` config (default 7) in `Backend/app/config.py`
- [x] 1.2 Add `create_refresh_token()` in `Backend/app/auth.py` with `type: refresh` claim
- [x] 1.3 Update `decode_token()` to return `type` field
- [x] 1.4 Add `refresh_token` field to `Token` schema in `Backend/app/schemas.py`
- [x] 1.5 Add `TokenRefresh` request schema in `Backend/app/schemas.py`
- [x] 1.6 Update `POST /auth/login` to return both `access_token` and `refresh_token`
- [x] 1.7 Add `POST /auth/refresh` endpoint with token rotation

## Frontend

- [x] 2.1 Add 401 error interceptor in `ApiService` that triggers token refresh
- [x] 2.2 Implement retry logic for the original failed request after refresh succeeds
- [x] 2.3 Handle refresh failure: clear tokens and redirect to `/login`

## Verification

- [ ] 3.1 Test refresh flow: login → wait for 401 → verify auto-refresh and retry
- [ ] 3.2 Test expired refresh token returns proper error
- [ ] 3.3 Verify token rotation: old refresh token cannot be reused
