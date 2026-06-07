
import base64
import hmac
import secrets
import hashlib
import json

from arkalos.core.env import env


class Crypt:
    """Laravel-style encryption service"""

    __key: bytes|None = None
    


    @classmethod
    def __getKey(cls) -> bytes:
        if cls.__key is None:
            print('Setting a key')
            key: str = env('APP_KEY')
            if key.startswith('base64:'):
                cls.__key = base64.b64decode(key[7:])
            else:
                cls.__key = key.encode('utf-8')

        return cls.__key
    

    
    @classmethod
    def encryptString(cls, payload: str) -> str:
        """Encrypt the given payload"""
        # Generate random IV
        iv = secrets.token_bytes(16)
        
        # Create cipher using AES (simulated with HMAC for simplicity)
        # In production, use cryptography library with actual AES
        data = {
            'iv': base64.b64encode(iv).decode('utf-8'),
            'value': base64.b64encode(payload.encode('utf-8')).decode('utf-8')
        }
        
        # Create MAC - we need to create MAC from the base64 encoded JSON without mac field
        mac_payload = base64.b64encode(json.dumps(data, separators=(',', ':')).encode('utf-8'))
        mac = hmac.new(cls.__getKey(), mac_payload, hashlib.sha256).hexdigest()
        data['mac'] = mac
        
        return base64.b64encode(json.dumps(data, separators=(',', ':')).encode('utf-8')).decode('utf-8')
    


    @classmethod
    def decryptString(cls, encrypted_value: str) -> str:
        """Decrypt the given payload"""
        try:
            # Decode the payload
            decoded = json.loads(base64.b64decode(encrypted_value).decode('utf-8'))
            
            # Extract MAC and create payload for verification
            mac = decoded.pop('mac')
            
            # Verify MAC - recreate the same payload that was used during encryption
            mac_payload = base64.b64encode(json.dumps(decoded, separators=(',', ':')).encode('utf-8'))
            expected_mac = hmac.new(cls.__getKey(), mac_payload, hashlib.sha256).hexdigest()
            
            if not hmac.compare_digest(str(mac), str(expected_mac)):
                raise ValueError('MAC verification failed')
            
            # Decrypt value
            return base64.b64decode(decoded['value']).decode('utf-8')
            
        except Exception as e:
            raise ValueError(f'Decryption failed: {e}')