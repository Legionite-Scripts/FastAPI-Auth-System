import jwt
from datetime import datetime, timedelta, timezone
from decouple import config
from jwt import ExpiredSignatureError, InvalidTokenError

# Load secret key from the .env file
SECRET_KEY = config("JWT_SECRET_KEY")

# JWT expiration time (e.g., 30 minutes)
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def createAccessToken(data: dict, expires_delta: timedelta = None):
    """
    Create a JWT access token.

    :param data: Payload to encode into the JWT (usually user information).
    :param expires_delta: Optional expiration time for the token.
    :return: Encoded JWT token as a string.
    """
    to_encode = data.copy()

    # Set the expiration time
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=15
        )  # Default to 15 minutes if not provided

    to_encode.update({"exp": expire})  # Add expiration time to the payload
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

    return encoded_jwt


def createResetToken(email: str, expires_delta: timedelta = timedelta(hours=1)):
    """
    Generate a password reset token (JWT) for a given user email.

    :param email: User's email address.
    :param expires_delta: Expiration time for the token (default is 1 hour).
    :return: Encoded JWT token as a string.
    """
    to_encode = {"sub": email}  # Add user's email to the token payload
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

    return encoded_jwt


def decodeResetToken(token: str):
    """
    Decode and verify the password reset token (JWT).

    :param token: The JWT token to decode.
    :return: Decoded email from the token if valid, otherwise None.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload.get("sub")  # Return the user's email
    except ExpiredSignatureError:
        return None  # Token expired
    except InvalidTokenError:
        return None  # Invalid token
