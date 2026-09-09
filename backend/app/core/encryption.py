"""
对称加密工具（用于加密存储AI配置的api_key等敏感字段）
"""
import base64
import hashlib
from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings

# 由SECRET_KEY派生出稳定的Fernet密钥，避免额外引入新的环境变量
_derived_key = base64.urlsafe_b64encode(hashlib.sha256(settings.SECRET_KEY.encode()).digest())
_fernet = Fernet(_derived_key)


def encrypt_text(plain_text: str) -> str:
    """加密文本"""
    return _fernet.encrypt(plain_text.encode()).decode()


def decrypt_text(encrypted_text: str) -> str:
    """解密文本"""
    try:
        return _fernet.decrypt(encrypted_text.encode()).decode()
    except InvalidToken:
        raise ValueError("Invalid encrypted value")
