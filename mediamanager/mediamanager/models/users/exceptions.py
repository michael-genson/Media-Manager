class UserAuthenticationError(Exception):
    def __init__(self, message: str = ""):
        super().__init__(message or "Unable to authenticate user")


class InvalidPasswordError(UserAuthenticationError):
    def __init__(self):
        super().__init__("Invalid password")


class InvalidTokenError(UserAuthenticationError):
    def __init__(self):
        super().__init__("Invalid token")


class UserDoesntExistError(UserAuthenticationError):
    def __init__(self):
        super().__init__("User doesn't exist")


###


class UserAlreadyExistsError(Exception):
    def __init__(self):
        super().__init__("Unable to create user; user already exists")
