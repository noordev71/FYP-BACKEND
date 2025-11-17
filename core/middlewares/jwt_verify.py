import jwt
from fyp_original_backend import settings

class JwtVerify:
    def __init__(self):
        self.secret_key = settings.SECRET_KEY

    def verify_jwt_token(self, token):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            # Token has expired
            return None
        except jwt.InvalidTokenError:
            # Token is invalid
            return None