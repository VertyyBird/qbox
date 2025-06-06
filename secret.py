# This is just an easy way to generate the secret key for your .env file.
import secrets
print(secrets.token_hex(16))
