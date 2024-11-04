import random
import string

def generate_secret_key(length=50):
    """Generate a random secret key."""
    characters = string.ascii_letters + string.digits + string.punctuation
    secret_key = ''.join(random.choice(characters) for _ in range(length))
    return secret_key

if __name__ == "__main__":
    secret_key = generate_secret_key()
    print(secret_key)