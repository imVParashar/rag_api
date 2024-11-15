from flask import Blueprint, request, jsonify
from functools import wraps
from config import SECRET_KEY
import jwt

#function to verify the JWT token
def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None

        # Check if token is passed in the headers
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]  # Bearer <token>

        if not token:
            return jsonify({'message': 'Token is missing!'}), 403

        try:
            # Decode the token
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = decoded_token['user']  # Extract user from the token payload
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401

        # Attach the user to the request context so we can access it in the endpoint
        request.current_user = current_user
        return f(*args, **kwargs)

    return decorator
