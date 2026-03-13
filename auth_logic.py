import bcrypt


# Hashes the password
def hash_password(password: str):

    #! Upper bound for password length (71), should be added to /signup
    pwd_bytes = password.encode("utf-8")[:71]
    hashed = bcrypt.hashpw(pwd_bytes, bcrypt.gensalt())

    return hashed.decode("utf-8")


# Verifies whether the password is correct
def verify_password(plain_password: str, hashed_password: str):

    password_bytes = plain_password.encode("utf-8")[:71]
    hash_bytes = hashed_password.encode("utf-8")

    return bcrypt.checkpw(password_bytes, hash_bytes)
