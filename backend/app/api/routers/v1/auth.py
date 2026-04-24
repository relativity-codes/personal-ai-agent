import logging
from fastapi import APIRouter, Depends, HTTPException, Request, status, Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from app.config import settings
from app.core.security import create_access_token, set_access_cookies
from app.db.models.user import User
from app.db.session import get_session
from app.services.user_service import UserService
from app.api.routers.v1.user_router import UserRead
from app.utils.logger import log_exception

logger = logging.getLogger(__name__)

router = APIRouter()

class GoogleLoginRequest(BaseModel):
    id_token: str

@router.post("/auth/google", response_model=UserRead)
async def auth_google(
    login_request: GoogleLoginRequest,
    response: Response,
    session: AsyncSession = Depends(get_session),
):
    """Handle Google ID token-based authentication."""
    try:
        # Verify the ID token against Google's public keys
        id_info = id_token.verify_oauth2_token(
            login_request.id_token, google_requests.Request(), settings.GOOGLE_CLIENT_ID
        )
    except ValueError as e:
        log_exception(logger, e, context="Google login token verification failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google ID token: {e}",
        )
    except Exception as e:
        log_exception(logger, e, context="Google login failed unexpectedly")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during Google authentication",
        )

    # Get or create user based on the verified token information
    user = await UserService.get_or_create_user_from_google(session, id_info)

    # Create our own app-specific JWT and set it in a cookie
    jwt_token = create_access_token(str(user.id))
    set_access_cookies(response, jwt_token)
    
    return user


@router.post("/auth/logout")
async def logout(response: Response):
    """Clear the access token cookie."""
    response.delete_cookie("access_token")
    return {"message": "Logged out successfully"}


@router.get("/users/me", response_model=UserRead)
async def read_users_me(request: Request):
    """Get the currently authenticated user."""
    return request.state.user
