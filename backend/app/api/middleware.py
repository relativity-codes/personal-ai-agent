from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, Awaitable
from starlette.responses import Response
import jwt

from app.config import settings
from app.db.repositories.user_repository import UserRepository
from app.db.session import async_session_factory

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # Paths that do not require authentication
        path = request.url.path
        allowed_prefixes = ["/api/v1/auth", "/_next", "/static", "/favicon.ico"]
        allowed_paths = ["/", "/docs", "/redoc", "/openapi.json"]
        
        if (
            settings.DEV_AUTH_BYPASS or
            path in allowed_paths or 
            any(path.startswith(prefix) for prefix in allowed_prefixes) or
            any(path.endswith(ext) for ext in [".css", ".js", ".png", ".jpg", ".jpeg", ".svg", ".ico", ".woff", ".woff2"])
        ):
            return await call_next(request)

        access_token = request.cookies.get("access_token")

        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            payload = jwt.decode(
                access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            user_id: str = payload.get("sub")
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
                )
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

        async with async_session_factory() as session:
            user = await UserRepository.get_by_id(session, user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
                )
            request.state.user = user

        response = await call_next(request)
        return response
