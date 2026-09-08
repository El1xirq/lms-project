from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher

from app.config import settings
from app.exceptions.domain import InvalidTokenException


password_hash = PasswordHash(hashers=[BcryptHasher()])


def create_access_token(user_id: int, role: str, email: str) -> str:
    """Create access token JWT"""
    access_data = {}

    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire)
    access_data.update({'sub': str(user_id), 'email': email, 'role': role, 'exp': int(expire.timestamp()), 'type': 'access'})

    access_token = jwt.encode(access_data, settings.secret_key, settings.algorithm)
    return access_token


def create_refresh_token(user_id: int, role: str, email: str) -> str:
    """Create refresh token JWT"""
    refresh_data = {}

    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire)
    refresh_data.update({'sub': str(user_id), 'role': role, 'email': email, 'exp': int(expire.timestamp()), 'type': 'refresh'})

    refresh_token = jwt.encode(refresh_data, settings.secret_key, settings.algorithm)
    return refresh_token


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
        raise InvalidTokenException()


def verify_token(token: str,  token_type: str = "access") -> dict:
    payload = decode_token(token)
    type_data = payload.get('type')

    if type_data != token_type:
        raise InvalidTokenException()
    return payload
   
        

def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, encoded_password: str) -> bool:
    return password_hash.verify(password, hash=encoded_password)




