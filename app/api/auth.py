from fastapi import APIRouter, status, Depends, Response, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.auth_schema import RegistrationData, TokenResponse, RegistrationRequest, UserResponse
from app.crud.user import create_user, get_user_by_email, get_user_by_id
from app.utils.security import get_password_hash, create_access_token, create_refresh_token, verify_password, verify_token
from app.database import SessionDep
from app.config import settings
from app.exceptions.domain import InvalidTokenException, NotFoundException
from app.dependencies.auth import get_current_user


router = APIRouter(prefix='/auth', tags=['Аuthentication'])

@router.post('/register', response_model=TokenResponse)
async def register_user(user_data: RegistrationRequest, session: SessionDep, response: Response):
    password_hash = get_password_hash(user_data.password)
    user = RegistrationData(**user_data.model_dump(exclude={"password"}), hashed_password=password_hash)

    result = await create_user(user, session)

    access_token = create_access_token(user_id=result.id, email=result.email, role=result.role)
    refresh_token = create_refresh_token(user_id=result.id, role=result.role, email=result.email)

    response.set_cookie('refresh_token', refresh_token, 
                            secure= not settings.debug, 
                            httponly=True, 
                            samesite="strict")

    return TokenResponse(access_token=access_token)


@router.post('/login', response_model=TokenResponse)
async def login_user(session: SessionDep, response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    email = form_data.username.lower()
    password = form_data.password

    user = await get_user_by_email(email, session)
    if user is None:
        raise InvalidTokenException(detail='Invalid credentials')

    if not verify_password(password=password, encoded_password=user.hashed_password):
        raise InvalidTokenException(detail='Invalid credentials')
    
    
    access_token = create_access_token(user_id=user.id, email=user.email, role=user.role)
    refresh_token = create_refresh_token(user_id=user.id, role=user.role, email=user.email)

    response.set_cookie('refresh_token', refresh_token, 
                        secure= not settings.debug, 
                        httponly=True, 
                        samesite="strict")

    return TokenResponse(access_token=access_token)


@router.post('/refresh', response_model=TokenResponse)
async def refresh_token_user(request: Request, session: SessionDep):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise InvalidTokenException(detail='Refresh token not found')
    
    refresh_token_verify = verify_token(refresh_token, token_type='refresh')
    sub = refresh_token_verify.get('sub')
    if sub is None:
        raise InvalidTokenException(detail='Invalid token payload')

    try:
        user_id = int(sub)
    except (TypeError, ValueError):
        raise InvalidTokenException(detail='Invalid token payload')

    try:
        user = await get_user_by_id(user_id, session)
    except NotFoundException:
        raise InvalidTokenException(detail='User is inactive or does not exist')

    access_token = create_access_token(
        user_id=user.id,
        role=user.role,
        email=user.email,
    )

    return TokenResponse(access_token=access_token)


@router.post('/logout', status_code=status.HTTP_204_NO_CONTENT)
async def logout_user(response: Response):
    response.delete_cookie("refresh_token")
    return None
    
    
@router.get('/me', response_model=UserResponse)
async def get_me(user = Depends(get_current_user)):
    return user


