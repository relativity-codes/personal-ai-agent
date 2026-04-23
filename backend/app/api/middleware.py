from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseFunction
from starlette.responses import Response
import jwt

from app.config import settings
from app.db.repositories.user_repository import UserRepository
from app.db.session import SessionLocal

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseFunction
    ) -> Response:
        # Paths that do not require authentication
        allowed_paths = ["/", "/docs", "/redoc", "/openapi.json"]
        if request.url.path in allowed_paths or request.url.path.startswith("/app/auth"):
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

        async with SessionLocal() as session:
            user = await UserRepository.get_by_id(session, user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
                )
            request.state.user = user

        response = await call_next(request)
        return response
