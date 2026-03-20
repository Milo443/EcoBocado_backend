from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.auth import decode_access_token

auth_scheme = HTTPBearer()

async def get_current_user(token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    payload = decode_access_token(token.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload
