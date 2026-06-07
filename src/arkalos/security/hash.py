
import bcrypt



class Hash:
    """Laravel-style password hashing"""
    
    @staticmethod
    def make(password: str, rounds: int = 12) -> str:
        """Create a hash of the given password"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=rounds)).decode('utf-8')
    
    @staticmethod
    def check(password: str, hashed: str) -> bool:
        """Check if the given password matches the hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            return False
    
    @staticmethod
    def needsRehash(hashed: str, rounds: int = 12) -> bool:
        """Check if the given hash needs to be rehashed"""
        try:
            # Extract cost from bcrypt hash
            parts = hashed.split('$')
            if len(parts) >= 3:
                current_rounds = int(parts[2])
                return current_rounds < rounds
        except Exception:
            pass
        return True