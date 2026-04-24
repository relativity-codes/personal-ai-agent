from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, Awaitable
from starlette.responses import Response, JSONResponse
import jwt

from app.config import settings
from app.db.repositories.user_repository import UserRepository
from app.db.session import async_session_factory
from app.utils.logger import log_exception
import logging

logger = logging.getLogger(__name__)

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # Paths that do not require authentication
        path = request.url.path
        allowed_prefixes = ["/api/v1/auth", "/_next", "/static", "/favicon.ico", "/health"]
        allowed_paths = ["/", "/docs", "/redoc", "/openapi.json"]
        
        if (
            not path.startswith("/api") or
            any(path.startswith(prefix) for prefix in allowed_prefixes) or
            path in allowed_paths or
            any(path.endswith(ext) for ext in [".css", ".js", ".png", ".jpg", ".jpeg", ".svg", ".ico", ".woff", ".woff2"])
        ):
            return await call_next(request)

        access_token = request.cookies.get("access_token")

        if not access_token:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Not authenticated, Please login again"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            payload = jwt.decode(
                access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            user_id: str = payload.get("sub")
            if user_id is None:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Invalid token, Please login again"}
                )
        except jwt.PyJWTError as e:
            log_exception(logger, e, context="JWT decode failed in AuthMiddleware")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid token, Please login again"}
            )

        async with async_session_factory() as session:
            try:
                # user_id is coming from token 'sub', which might be the ID or google_id depending on how it's created
                # But here UserRepository expects ID (UUID)
                from app.api.deps import parse_uuid
                uid = parse_uuid(user_id)
                user = await UserRepository.get_by_id(session, uid)
                if not user:
                    logger.warning(f"User {user_id} from token not found in database")
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={"detail": "User not found"}
                    )
                request.state.user = user
            except Exception as e:
                logger.error(f"Error fetching user in middleware: {e}")
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Authentication failed"}
                )

        response = await call_next(request)
        return response
