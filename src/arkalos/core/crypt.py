
from arkalos.security.crypt import Crypt as CryptService
from arkalos.core.registry import Registry

Registry.register('crypt', CryptService, True)

def Crypt() -> CryptService:
    return Registry.get('crypt')

def encryptString(payload: str) -> str:
    return Crypt().encryptString(payload)

def decryptString(encrypted_value: str) -> str:
    return Crypt().decryptString(encrypted_value)
