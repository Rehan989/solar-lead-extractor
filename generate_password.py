import streamlit_authenticator as stauth

def generate_hash(password):
    """Generate a password hash using bcrypt"""
    hashed_password = stauth.Hasher([password]).generate()[0]
    return hashed_password

if __name__ == "__main__":
    password = input("Enter the password to hash: ")
    hashed_password = generate_hash(password)
    print(f"Hashed password: {hashed_password}")
    print("Add this hash to your config.yaml file.") 