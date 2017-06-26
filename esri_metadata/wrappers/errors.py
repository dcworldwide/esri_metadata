
class InvalidValueError(ValueError):
    """Raised when trying to parse a value that is invalid."""
    pass


class InvalidStructureError(Exception):
    """Raised when the XML doesn't match what is expected."""
    pass


class UnboundElementError(Exception):
    """Raised when a Wrapper instance is being used in a way that it needs to be bound to an XML object but it is not."""
    pass
