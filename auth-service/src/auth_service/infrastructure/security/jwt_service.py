from datetime import datetime, timedelta, timezone
from uuid import uuid4

from jose import JWTError, jwt

from auth_service.domain.services.token_service import IssuedToken, TokenClaims


class JWTService:
    token_lifetime = timedelta(hours=1)

    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm

    def issue_token(self, user_id: int) -> IssuedToken:
        now = datetime.now(timezone.utc).replace(microsecond=0)
        expires_at = now + self.token_lifetime
        token_id = str(uuid4())
        claims = TokenClaims(user_id, token_id, expires_at)
        encoded_token = jwt.encode(
            {
                "sub": str(user_id),
                "jti": token_id,
                "iat": int(now.timestamp()),
                "exp": int(expires_at.timestamp()),
            },
            self.secret_key,
            algorithm=self.algorithm,
        )
        return IssuedToken(encoded_token, claims)

    def decode_token(self, encoded_token: str) -> TokenClaims | None:
        try:
            payload = jwt.decode(
                encoded_token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"require_exp": True, "require_sub": True, "require_jti": True},
            )
            user_id = int(payload["sub"])
            token_id = str(payload["jti"])
            expires_at = datetime.fromtimestamp(int(payload["exp"]), timezone.utc)
            if user_id < 1 or not token_id:
                return None
            return TokenClaims(user_id, token_id, expires_at)
        except (JWTError, KeyError, TypeError, ValueError, OverflowError):
            return None