import bcrypt

def generate_hash(password):
    """Generate a bcrypt hash for the given password"""
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    return hashed_password.decode()  # Decode to store as a string

if __name__ == "__main__":
    password = input("Enter the password to hash: ")
    hashed_password = generate_hash(password)
    print(f"Hashed password: {hashed_password}")
    print("Add this hash to your config.yaml file.")
