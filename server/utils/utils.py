import string
import re
import dotenv
import os
from aiosmtplib import SMTP

dotenv.load_dotenv("server/.env")


def check_all(username: str, password: str, email: str | None = None) -> str | bool:
    if username == "":
        return "The username input field is empty"
    if password == "":
        return "The password input field is empty"

    for symbol in username:
        if symbol not in string.ascii_letters + string.digits + "_-":
            return "Unsupported characters in username"
    if len(username) < 4:
        return "The length of the username must be longer than 3 characters"
    elif len(username) > 20:
        return "Username length should not be longer than 20 characters"

    for symbol in password:
        if symbol not in string.ascii_letters + string.digits + "_-":
            return "Unsupported characters in password"
    if len(password) < 5:
        return "The length of the password must be longer than 4 characters"
    elif len(username) > 25:
        return "Password length should not be longer than 25 characters"

    if email is not None:
        if email == "":
            return "The email input field is empty"

        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
            return "Incorrect email"

    return True


async def send_email(email: str, subject: str, text: str) -> None:
    smtp = SMTP(hostname="smtp.gmail.com", port=465, use_tls=True)
    await smtp.connect()
    await smtp.login(os.getenv("EMAIL_NAME"), os.getenv("EMAIL_PASS"))
    await smtp.sendmail(os.getenv("EMAIL_NAME"), email, f"Subject: {subject}\n\n{text}")
    await smtp.quit()
