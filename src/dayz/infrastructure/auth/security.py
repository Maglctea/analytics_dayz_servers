import hashlib
from datetime import timedelta, datetime
from typing import Optional

import pytz
from jose import jwt


def hash_secret(secret: str):
    return hashlib.shake_256(secret.encode()).hexdigest(64)


def generate_jwt_token(
        user_id: int,
        algorithm: str,
        secret_key: str,
        expires_delta_minutes: int = 5
):
    moscow_tz = pytz.timezone('Europe/Moscow')
    data = {
        'user_id': user_id,
        'exp': datetime.now(tz=moscow_tz) + timedelta(minutes=expires_delta_minutes)
    }

    encoded_jwt = jwt.encode(
        claims=data,
        key=secret_key,
        algorithm=algorithm
    )
    return encoded_jwt


def parse_jwt_token(
        token: str,
        algorithm: str,
        secret_key: str,
) -> Optional[dict]:
    data = jwt.decode(
        token=token,
        key=secret_key,
        algorithms=[algorithm],
    )
    return data

