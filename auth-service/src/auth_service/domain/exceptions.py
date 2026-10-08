class InvalidUserDataError(ValueError):
    pass


class UserAlreadyExistsError(ValueError):
    pass


class InvalidCredentialsError(ValueError):
    pass


class InvalidTokenError(ValueError):
    pass