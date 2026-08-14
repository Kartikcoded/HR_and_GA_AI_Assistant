from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from app.auth.security import decode_access_token

bearer_scheme = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> dict:
    """Verify the JWT and return the user's identity/role as a dict."""
    token = credentials.credentials
    try:
        payload = decode_access_token(token)
        return {
            "user_id": int(payload["sub"]),
            "employee_id": payload["employee_id"],
            "role": payload["role"],
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )