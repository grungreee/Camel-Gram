from app.utils.requests import make_request
import hashlib


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


async def handle_register(username: str, password: str, email: str) -> None:
    try:
        if not all([username, password, email]):
            print("All fields must be filled!")
            return

        user: dict = {
            "username": username,
            "password": hash_password(password),
            "email": email,
        }

        response_status, response = await make_request(endpoint="start_register", data=user)

        if response_status == 200:
            print(response)

    except Exception as e:
        print(f"Error: {str(e)}")
