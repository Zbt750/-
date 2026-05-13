# utils/jwt_utils.py
from datetime import datetime, timedelta, UTC

from fastapi import HTTPException
from jose import jwt

# 固定的密钥和算法（实际部署要改，现在先这样）
SECRET_KEY = "my_super_secret_key_change_me_later"
ALGORITHM = "HS256"
TOKEN_EXPIRE_DAYS = 30   # 30天后过期

def create_access_token(user_id: int):
    """根据用户ID生成token"""
    expire = datetime.now(UTC) + timedelta(days=TOKEN_EXPIRE_DAYS)
    payload = {"sub": str(user_id), "exp": expire}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token
#解码token
def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.JWTError:
        return None