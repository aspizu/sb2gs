class UnwrapError(Exception):
    pass


def unwrap[T](value: T | None) -> T:
    if value is None:
        raise UnwrapError
    return value
